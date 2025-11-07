"""Current context and role-based access control"""
from fastapi import Depends, HTTPException, Header
from sqlmodel import Session
from typing import Optional
from .security import decode_token
from .models import User
from .routes import get_session

class CurrentContext:
    """Current user context from JWT token"""
    def __init__(self, tenant_id: Optional[int], user_id: int, user_email: str, role: str):
        self.tenant_id = tenant_id  # None for global_owner
        self.user_id = user_id
        self.user_email = user_email
        self.role = role

def get_current_ctx(
    authorization: str = Header(...),
    session: Session = Depends(get_session)
) -> CurrentContext:
    """Get current context from JWT token (tenant_id, user_id, role)
    Handles both tenant users and global_owner (tid=None)
    """
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ", 1)[1]
    token_data = decode_token(token)
    
    # Get user to verify they still exist and get user_id
    from sqlmodel import select
    
    # For global_owner, tenant_id is None
    if token_data.role == "global_owner":
        user = session.exec(
            select(User).where(
                User.email == token_data.sub,
                User.is_global_owner == True
            )
        ).first()
        tenant_id = None
    else:
        if token_data.tid is None:
            raise HTTPException(status_code=401, detail="Invalid token: tenant_id required for non-global users")
        user = session.exec(
            select(User).where(
                User.email == token_data.sub,
                User.tenant_id == token_data.tid
            )
        ).first()
        tenant_id = token_data.tid
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return CurrentContext(
        tenant_id=tenant_id,
        user_id=user.id,
        user_email=token_data.sub,
        role=token_data.role
    )

def require_owner(authorization: str = Header(...), session: Session = Depends(get_session)) -> CurrentContext:
    """Require owner role"""
    ctx = get_current_ctx(authorization, session)
    if ctx.role != "owner":
        raise HTTPException(status_code=403, detail="Owner role required")
    return ctx

def require_admin(authorization: str = Header(...), session: Session = Depends(get_session)) -> CurrentContext:
    """Require admin or owner role"""
    ctx = get_current_ctx(authorization, session)
    if ctx.role not in ("owner", "admin", "global_owner"):
        raise HTTPException(status_code=403, detail="Admin or owner role required")
    return ctx

def require_global_owner(authorization: str = Header(...), session: Session = Depends(get_session)) -> CurrentContext:
    """Require global_owner role"""
    ctx = get_current_ctx(authorization, session)
    if ctx.role != "global_owner":
        raise HTTPException(status_code=403, detail="Global owner role required")
    return ctx

