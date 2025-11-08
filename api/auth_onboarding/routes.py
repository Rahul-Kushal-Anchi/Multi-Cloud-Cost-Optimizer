"""Multi-tenant auth and onboarding routes"""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Optional
from datetime import datetime
import os
import json

from .models import Tenant, User, AuditLog
from .security import hash_password, verify_password, create_access_token, decode_token

try:
    from api.secure.aws.assume_role import assume_vendor_role
except ImportError:
    from secure.aws.assume_role import assume_vendor_role

router = APIRouter(prefix="/api", tags=["auth", "onboarding"])

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas.db")  # swap to Postgres in prod
engine = create_engine(DATABASE_URL, echo=False)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session


# Initialize database tables
def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# --- Auth Request Models ---
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    company: str

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str):
        """Validate password length and encoding"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode("utf-8")) > 256:
            raise ValueError("Password too long (max 256 bytes)")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ConnectAWSRequest(BaseModel):
    aws_role_arn: str
    external_id: str
    cur_bucket: Optional[str] = None
    cur_prefix: Optional[str] = "cur/"
    athena_workgroup: Optional[str] = "primary"
    athena_db: Optional[str] = None
    athena_table: Optional[str] = None
    athena_results_bucket: Optional[str] = None
    athena_results_prefix: Optional[str] = "athena-results/"
    region: Optional[str] = "us-east-1"


# --- Auth Endpoints ---
@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, session: Session = Depends(get_session)):
    """Public signup - creates a new tenant and owner user"""
    import re
    import unicodedata
    
    # Check if public signup is allowed
    allow_public = os.getenv("ALLOW_PUBLIC_SIGNUP", "true").lower() == "true"
    if not allow_public:
        raise HTTPException(
            status_code=403,
            detail="Public signup is disabled. Please contact support for an invitation."
        )
    
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Generate slug from company name (better slugify)
    def slugify(name: str) -> str:
        # Normalize unicode
        s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
        s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
        return s or "tenant"
    
    slug = slugify(request.company)
    
    # Ensure slug is unique
    suffix = 1
    base_slug = slug
    while session.exec(select(Tenant).where(Tenant.slug == slug)).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    
    # Create tenant with plan and status
    tenant = Tenant(
        name=request.company,
        slug=slug,
        plan="starter",
        status="trialing"
    )
    session.add(tenant)
    session.flush()  # Get tenant.id
    
    # Create owner user (first user is owner)
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="owner",
        tenant_id=tenant.id,
        is_global_owner=False
    )
    session.add(user)
    session.flush()  # Get user.id
    session.commit()
    
    # Return token with user_id
    return {
        "access_token": create_access_token(user.email, user.id, user.role, tenant_id=tenant.id),
        "tenant_id": tenant.id,
        "user_id": user.id,
        "role": user.role,
        "email": user.email,
        "slug": slug
    }


@router.post("/auth/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Log in an existing user"""
    user = session.exec(select(User).where(User.email == request.email)).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check tenant status
    tenant = session.get(Tenant, user.tenant_id)
    if tenant and tenant.status not in ("trialing", "active"):
        raise HTTPException(
            status_code=403,
            detail=f"Tenant status is {tenant.status}. Please contact support."
        )
    
    # Handle global_owner (no tenant_id)
    tenant_id = user.tenant_id if not user.is_global_owner else None
    
    return {
        "access_token": create_access_token(user.email, user.id, user.role, tenant_id=tenant_id),
        "tenant_id": user.tenant_id,
        "user_id": user.id,
        "role": user.role,
        "email": user.email
    }


# --- Auth Dependency for Protected Routes ---
async def get_current_tenant(
    authorization: str = Header(...),
    session: Session = Depends(get_session)
) -> Tenant:
    """Get current tenant from JWT token"""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ", 1)[1]
    token_data = decode_token(token)
    
    tenant = session.get(Tenant, token_data.tid)
    if not tenant:
        raise HTTPException(status_code=401, detail="Tenant not found")
    
    return tenant


# --- Onboarding Endpoints ---
@router.post("/tenants/connect")
def connect_aws(
    request: ConnectAWSRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: Session = Depends(get_session),
    authorization: str = Header(...)
):
    """Connect tenant to AWS billing via cross-account role (with validation)"""
    from .current import get_current_ctx
    from .models import AuditLog
    # Get current user context for audit log
    try:
        ctx = get_current_ctx(authorization, session)
        user_id = ctx.user_id
    except:
        user_id = None
    
    # Validate AssumeRole before saving (fail fast)
    target_region = request.region or tenant.region or "us-east-1"

    try:
        test_session = assume_vendor_role(
            request.aws_role_arn,
            request.external_id,
            target_region
        )
        # Test the connection by calling GetCallerIdentity
        sts = test_session.client("sts", region_name=target_region)
        identity = sts.get_caller_identity()
        if not identity.get("Account"):
            raise Exception("Unable to get account identity")
    except Exception as e:
        # Log failed attempt
        audit = AuditLog(
            tenant_id=tenant.id,
            actor_user_id=user_id,
            action="connect_aws",
            action_metadata=json.dumps({"error": str(e), "role_arn": request.aws_role_arn})
        )
        session.add(audit)
        session.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Cannot AssumeRole: {str(e)}. Please verify the Role ARN and External ID."
        )
    
    # Update tenant with AWS connection details
    # Update tenant with AWS connection details
    tenant.aws_role_arn = request.aws_role_arn
    tenant.external_id = request.external_id
    tenant.region = target_region
    if request.cur_bucket:
        tenant.cur_bucket = request.cur_bucket
    if request.cur_prefix:
        tenant.cur_prefix = request.cur_prefix or "cur/"
    if request.athena_workgroup:
        tenant.athena_workgroup = request.athena_workgroup or "primary"
    if request.athena_db:
        tenant.athena_db = request.athena_db
    if request.athena_table:
        tenant.athena_table = request.athena_table
    if request.athena_results_bucket:
        tenant.athena_results_bucket = request.athena_results_bucket
    if request.athena_results_prefix:
        tenant.athena_results_prefix = request.athena_results_prefix or "athena-results/"
    
    session.add(tenant)
    
    # Log successful connection
    audit = AuditLog(
        tenant_id=tenant.id,
        actor_user_id=user_id,
        action="connect_aws",
        action_metadata=json.dumps({"role_arn": request.aws_role_arn, "status": "success"})
    )
    session.add(audit)
    session.commit()
    
    return {
        "ok": True,
        "message": "AWS connection configured successfully",
        "tenant_id": tenant.id
    }


@router.get("/tenants/me")
def get_tenant_info(
    authorization: str = Header(...),
    session: Session = Depends(get_session)
):
    """Get current tenant information or global owner context"""
    from .current import get_current_ctx

    ctx = get_current_ctx(authorization, session)

    # Global owner has no tenant_id; return role context instead of 401
    if ctx.role == "global_owner" or ctx.tenant_id is None:
        return {
            "tenant": None,
            "role": ctx.role,
            "is_global_owner": True,
            "hasConnection": False
        }

    tenant = session.get(Tenant, ctx.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan,
            "status": tenant.status,
            "hasConnection": bool(tenant.aws_role_arn and tenant.athena_db and tenant.athena_table)
        },
        "role": ctx.role,
        "is_global_owner": False
    }


@router.post("/promote-user-once")
@router.get("/promote-user-once")  # Also support GET
def promote_user_once(
    email: str = "akrahul211@gmail.com",
    secret: str = "change-this-secret-now",
    session: Session = Depends(get_session)
):
    """TEMPORARY: Promote user to global owner - DELETE AFTER USE"""
    if secret != "change-this-secret-now":
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    try:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {email}")
        
        user.role = "global_owner"
        user.tenant_id = None
        user.is_global_owner = True
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "message": "Successfully promoted to global owner",
            "email": user.email,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "is_global_owner": user.is_global_owner
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tenants/external-id/rotate")
def rotate_external_id(
    tenant: Tenant = Depends(get_current_tenant),
    session: Session = Depends(get_session),
    authorization: str = Header(...)
):
    """Rotate External ID for current tenant (owner/admin only)"""
    from .current import get_current_ctx, require_admin
    from .models import AuditLog
    import uuid
    import json
    
    # Require admin or owner role
    ctx = require_admin(authorization, session)
    
    # Generate new External ID
    new_external_id = str(uuid.uuid4()).upper()
    
    # Update tenant
    tenant.external_id = new_external_id
    session.add(tenant)
    
    # Log the action
    audit = AuditLog(
        tenant_id=tenant.id,
        actor_user_id=ctx.user_id,
        action="rotate_external_id",
        action_metadata=json.dumps({"rotated_by": ctx.user_email})
    )
    session.add(audit)
    session.commit()
    
    return {
        "ok": True,
        "tenant_id": tenant.id,
        "new_external_id": new_external_id,
        "message": "External ID rotated successfully. Update your CloudFormation stack with the new External ID."
    }

