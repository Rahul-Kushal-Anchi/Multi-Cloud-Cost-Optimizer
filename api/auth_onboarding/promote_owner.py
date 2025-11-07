"""Temporary endpoint to promote user to global owner - ONE-TIME USE ONLY"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
import os
from .routes import get_session
from .models import User

router = APIRouter(prefix="/api", tags=["admin"])


class PromoteRequest(BaseModel):
    email: EmailStr
    secret: str  # Simple secret to prevent unauthorized access


@router.post("/promote-to-global-owner-once")
def promote_to_global_owner_once(
    request: PromoteRequest,
    session: Session = Depends(get_session)
):
    """
    TEMPORARY: One-time endpoint to promote a user to global owner.
    DELETE THIS AFTER USE for security!
    
    Requires a secret key to prevent unauthorized access.
    """
    # Simple secret - change this to something random
    EXPECTED_SECRET = os.getenv("PROMOTE_SECRET", "change-this-secret-now")
    
    if request.secret != EXPECTED_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Find user
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {request.email}")
    
    # Check if already global owner
    if user.is_global_owner:
        return {
            "message": "User is already a global owner",
            "email": user.email,
            "role": user.role
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
        "note": "Log out and log back in to get a new token with global_owner role. DELETE THIS ENDPOINT AFTER USE!"
    }

