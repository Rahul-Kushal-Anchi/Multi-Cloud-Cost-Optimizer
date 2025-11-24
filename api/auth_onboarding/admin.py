"""Admin endpoints for tenant management"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
import json

from .models import Tenant, User, AuditLog
from .current import (
    require_admin,
    require_global_owner,
    CurrentContext,
    get_current_ctx,
)
from .routes import get_session, ConnectAWSRequest

try:
    from api.secure.aws.assume_role import assume_vendor_role
except ImportError:
    from secure.aws.assume_role import assume_vendor_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


class TenantListResponse(BaseModel):
    """Tenant list item"""

    id: int
    name: str
    slug: Optional[str]
    plan: str
    status: str
    hasConnection: bool
    created_at: datetime
    user_count: int
    aws_role_arn: Optional[str] = None
    external_id: Optional[str] = None
    cur_bucket: Optional[str] = None
    cur_prefix: Optional[str] = None
    athena_workgroup: Optional[str] = None
    athena_db: Optional[str] = None
    athena_table: Optional[str] = None
    athena_results_bucket: Optional[str] = None
    athena_results_prefix: Optional[str] = None
    region: Optional[str] = None


@router.get("/tenants")
def list_tenants(
    authorization: str = Header(...), session: Session = Depends(get_session)
) -> List[TenantListResponse]:
    """List all tenants (global owner only)"""
    ctx = require_global_owner(authorization, session)
    tenants = session.exec(select(Tenant)).all()

    result = []
    for tenant in tenants:
        user_count = session.exec(select(User).where(User.tenant_id == tenant.id)).all()

        result.append(
            TenantListResponse(
                id=tenant.id,
                name=tenant.name,
                slug=tenant.slug,
                plan=tenant.plan,
                status=tenant.status,
                hasConnection=bool(
                    tenant.aws_role_arn and tenant.athena_db and tenant.athena_table
                ),
                created_at=tenant.created_at,
                user_count=len(user_count),
                aws_role_arn=tenant.aws_role_arn,
                external_id=tenant.external_id,
                cur_bucket=tenant.cur_bucket,
                cur_prefix=tenant.cur_prefix,
                athena_workgroup=tenant.athena_workgroup,
                athena_db=tenant.athena_db,
                athena_table=tenant.athena_table,
                athena_results_bucket=tenant.athena_results_bucket,
                athena_results_prefix=tenant.athena_results_prefix,
                region=tenant.region,
            )
        )

    return result


@router.post("/tenants/{tenant_id}/rotate-external-id")
def rotate_external_id(
    tenant_id: int,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Rotate External ID for a tenant (global owner only)"""
    ctx = require_global_owner(authorization, session)
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Generate new External ID
    new_external_id = str(uuid.uuid4()).upper()

    # Update tenant
    tenant.external_id = new_external_id
    session.add(tenant)

    # Log the action
    audit = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=ctx.user_id,
        action="rotate_external_id",
        action_metadata=json.dumps({"rotated_by": ctx.user_email}),
    )
    session.add(audit)
    session.commit()

    return {
        "ok": True,
        "tenant_id": tenant_id,
        "new_external_id": new_external_id,
        "message": "External ID rotated successfully. Client must update their CloudFormation stack.",
    }


@router.post("/tenants/{tenant_id}/aws-connection")
def update_tenant_aws_connection(
    tenant_id: int,
    request: ConnectAWSRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """
    Configure AWS CUR connection details for a tenant (global owner only).
    Validates the role by performing an STS GetCallerIdentity call via AssumeRole.
    """
    ctx = require_global_owner(authorization, session)
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Validate AssumeRole works before persisting
    try:
        aws_session = assume_vendor_role(
            request.aws_role_arn,
            request.external_id,
            request.region or tenant.region or "us-east-1",
        )
        sts = aws_session.client(
            "sts", region_name=request.region or tenant.region or "us-east-1"
        )
        sts.get_caller_identity()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot AssumeRole with provided credentials: {exc}",
        )

    # Update tenant fields
    tenant.aws_role_arn = request.aws_role_arn
    tenant.external_id = request.external_id
    tenant.cur_bucket = request.cur_bucket
    tenant.cur_prefix = request.cur_prefix
    tenant.athena_workgroup = request.athena_workgroup
    tenant.athena_db = request.athena_db
    tenant.athena_table = request.athena_table
    tenant.athena_results_bucket = request.athena_results_bucket
    tenant.athena_results_prefix = request.athena_results_prefix
    tenant.region = request.region

    session.add(tenant)

    audit = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=ctx.user_id,
        action="update_aws_connection",
        action_metadata=json.dumps({"updated_by": ctx.user_email}),
    )
    session.add(audit)
    session.commit()
    session.refresh(tenant)

    return {
        "ok": True,
        "tenant_id": tenant_id,
        "message": "AWS connection saved successfully.",
        "hasConnection": True,
    }


@router.post("/tenants/{tenant_id}/disable")
def disable_tenant(
    tenant_id: int,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Disable a tenant (set status to canceled) - global owner only"""
    ctx = require_global_owner(authorization, session)
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Update tenant status
    tenant.status = "canceled"
    session.add(tenant)

    # Log the action
    audit = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=ctx.user_id,
        action="disable_tenant",
        action_metadata=json.dumps({"disabled_by": ctx.user_email}),
    )
    session.add(audit)
    session.commit()

    return {
        "ok": True,
        "tenant_id": tenant_id,
        "status": "canceled",
        "message": "Tenant disabled successfully",
    }


@router.post("/tenants/{tenant_id}/activate")
def activate_tenant(
    tenant_id: int,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Activate a tenant (set status to active) - global owner only"""
    ctx = require_global_owner(authorization, session)
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Update tenant status
    tenant.status = "active"
    session.add(tenant)

    # Log the action
    audit = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=ctx.user_id,
        action="activate_tenant",
        action_metadata=json.dumps({"activated_by": ctx.user_email}),
    )
    session.add(audit)
    session.commit()

    return {
        "ok": True,
        "tenant_id": tenant_id,
        "status": "active",
        "message": "Tenant activated successfully",
    }


@router.get("/audit/{tenant_id}")
def get_audit_logs(
    tenant_id: int,
    limit: int = 50,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Get audit logs for a tenant (admin or owner only)"""
    # Require admin or owner
    ctx = require_admin(authorization, session)

    # Verify tenant exists and user has access
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Check access: owner can see all, admin can see their own tenant
    if ctx.role != "owner" and ctx.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    logs = session.exec(
        select(AuditLog)
        .where(AuditLog.tenant_id == tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    ).all()

    return {
        "tenant_id": tenant_id,
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "actor_user_id": log.actor_user_id,
                "metadata": (
                    json.loads(log.action_metadata) if log.action_metadata else {}
                ),
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
    }


class PromoteToGlobalOwnerRequest(BaseModel):
    email: EmailStr


@router.post("/promote-to-global-owner")
def promote_to_global_owner(
    request: PromoteToGlobalOwnerRequest,
    session: Session = Depends(get_session),
    authorization: str = Header(...),
):
    """
    Temporary endpoint to promote a user to global owner.
    Requires admin/owner role to use (for security, you can restrict this later).
    """
    # Allow any authenticated admin/owner to promote (for initial setup)
    ctx = get_current_ctx(authorization, session)

    if ctx.role not in ("admin", "owner", "global_owner"):
        raise HTTPException(status_code=403, detail="Admin or owner role required")

    # Find user
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {request.email}")

    # Check if already global owner
    if user.is_global_owner:
        return {
            "message": "User is already a global owner",
            "email": user.email,
            "role": user.role,
        }

    # Promote to global owner
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
        "is_global_owner": user.is_global_owner,
        "note": "Log out and log back in to get a new token with global_owner role",
    }
