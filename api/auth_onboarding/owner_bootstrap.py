"""Owner bootstrap signup - one-time global owner creation"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
import os

from .models import User
from .security import hash_password, create_access_token
from .routes import get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


class OwnerBootstrapRequest(BaseModel):
    email: EmailStr
    password: str
    code: str


@router.post("/owner-signup", status_code=status.HTTP_201_CREATED)
def owner_signup(
    request: OwnerBootstrapRequest, session: Session = Depends(get_session)
):
    """One-time owner bootstrap signup (protected by email + code)"""
    # Check environment variables
    owner_email = os.getenv("OWNER_BOOTSTRAP_EMAIL")
    owner_code = os.getenv("OWNER_BOOTSTRAP_CODE")

    if not owner_email or not owner_code:
        raise HTTPException(
            status_code=503,
            detail="Owner bootstrap not configured. Set OWNER_BOOTSTRAP_EMAIL and OWNER_BOOTSTRAP_CODE",
        )

    # Verify email
    if owner_email != str(request.email):
        raise HTTPException(status_code=403, detail="Not allowed")

    # Verify code
    if owner_code != request.code:
        raise HTTPException(status_code=403, detail="Invalid code")

    # Check if owner already exists
    existing_owner = session.exec(
        select(User).where(User.is_global_owner == True)
    ).first()

    if existing_owner:
        raise HTTPException(
            status_code=409,
            detail="Global owner already exists. Use /api/auth/login instead.",
        )

    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    # Create global owner
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="global_owner",
        tenant_id=None,
        is_global_owner=True,
    )
    session.add(user)
    session.flush()  # Get user.id
    session.commit()

    # Return token
    return {
        "access_token": create_access_token(
            user.email, user.id, user.role, tenant_id=None
        ),
        "user_id": user.id,
        "role": "global_owner",
        "email": user.email,
    }
