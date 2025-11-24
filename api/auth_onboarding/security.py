"""JWT authentication and password hashing"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional
import os

SECRET_KEY = os.getenv(
    "APP_JWT_SECRET", "CHANGE_ME_IN_PRODUCTION"
)  # set in ECS/Secrets Manager
ALGO = "HS256"
ACCESS_MINUTES = 60 * 8  # 8 hours

# Use bcrypt_sha256 to avoid 72-byte limitation & Unicode issues
pwd_ctx = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return pwd_ctx.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return pwd_ctx.verify(password, password_hash)


class TokenData(BaseModel):
    """JWT token data structure"""

    sub: str  # email
    sub_id: Optional[int] = None  # user_id (new)
    tid: Optional[int] = None  # tenant_id (None for global_owner)
    role: str
    exp: int


def create_access_token(
    email: str, user_id: int, role: str = "admin", tenant_id: Optional[int] = None
) -> str:
    """Create a JWT access token with tenant_id, user_id, and role
    For global_owner, tenant_id should be None
    """
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_MINUTES)
    payload = {
        "sub": email,  # email for backward compatibility
        "sub_id": user_id,  # user_id for context
        "tid": tenant_id,  # None for global_owner
        "role": role,
        "exp": exp,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)


def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        return TokenData(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
