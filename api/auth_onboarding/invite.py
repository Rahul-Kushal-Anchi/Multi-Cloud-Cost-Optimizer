"""Team member invitation system"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from datetime import datetime, timedelta
import secrets
import os

from .models import Invite, User, Tenant
from .security import hash_password, create_access_token
from .current import require_admin, get_current_ctx
from .routes import get_session

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


class InviteCreateRequest(BaseModel):
    email: EmailStr
    role: str = "member"  # admin | member


class InviteAcceptRequest(BaseModel):
    token: str
    password: str


@router.post("/invites", status_code=status.HTTP_201_CREATED)
def create_invite(
    request: InviteCreateRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Create an invite for a team member (admin/owner only)"""
    # Require admin or owner
    ctx = require_admin(authorization, session)

    # Validate role
    if request.role not in ("admin", "member"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'member'")

    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )

    # Generate unique token
    token = secrets.token_urlsafe(32)

    # Create invite (expires in 7 days)
    invite = Invite(
        tenant_id=ctx.tenant_id,
        email=request.email,
        role=request.role,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    session.add(invite)
    session.commit()

    # In production, send email here
    # For now, return token for manual testing
    return {
        "invite_token": token,
        "email": request.email,
        "role": request.role,
        "expires_at": invite.expires_at.isoformat(),
        "message": "Invite created. Share the invite_token with the user.",
    }


@router.post("/invites/accept", status_code=status.HTTP_201_CREATED)
def accept_invite(
    request: InviteAcceptRequest, session: Session = Depends(get_session)
):
    """Accept an invite and create user account"""
    # Find valid invite
    invite = session.exec(
        select(Invite).where(
            Invite.token == request.token, Invite.expires_at > datetime.utcnow()
        )
    ).first()

    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite token")

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == invite.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )

    # Verify tenant exists
    tenant = session.get(Tenant, invite.tenant_id)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant not found")

    # Check tenant status
    if tenant.status not in ("trialing", "active"):
        raise HTTPException(
            status_code=403,
            detail=f"Tenant status is {tenant.status}. Cannot accept invites.",
        )

    # Create user
    user = User(
        tenant_id=invite.tenant_id,
        email=invite.email,
        password_hash=hash_password(request.password),
        role=invite.role,
        is_global_owner=False,
    )
    session.add(user)
    session.flush()  # Get user.id

    # Delete invite
    session.delete(invite)
    session.commit()

    # Return token
    return {
        "access_token": create_access_token(
            user.email, user.id, user.role, tenant_id=user.tenant_id
        ),
        "tenant_id": user.tenant_id,
        "user_id": user.id,
        "role": user.role,
        "email": user.email,
    }
