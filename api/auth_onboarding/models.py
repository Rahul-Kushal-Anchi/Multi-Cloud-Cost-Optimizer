"""Multi-tenant database models for SaaS application"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, create_engine
import os

if TYPE_CHECKING:
    from sqlmodel.relationship import Relationship

class Tenant(SQLModel, table=True):
    """Tenant/company model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: Optional[str] = None  # URL-friendly identifier
    plan: str = "starter"  # starter | pro | enterprise
    status: str = "trialing"  # trialing | active | past_due | canceled
    aws_role_arn: Optional[str] = None
    external_id: Optional[str] = None
    cur_bucket: Optional[str] = None
    cur_prefix: Optional[str] = None
    athena_workgroup: Optional[str] = "primary"
    athena_db: Optional[str] = None
    athena_table: Optional[str] = None
    athena_results_bucket: Optional[str] = None
    athena_results_prefix: Optional[str] = None
    region: Optional[str] = "us-east-1"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    users: list["User"] = Relationship(back_populates="tenant")


class User(SQLModel, table=True):
    """User model for tenant access"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password_hash: str
    role: str = "member"  # owner | admin | member | global_owner
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")  # None for global_owner
    is_global_owner: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    tenant: Optional[Tenant] = Relationship(back_populates="users")


class Invite(SQLModel, table=True):
    """Invite model for team member invitations"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    email: str
    role: str = "member"  # admin | member
    token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    """Audit log for tenant actions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    actor_user_id: Optional[int] = None
    action: str  # 'assume_role', 'query_athena', 'connect_aws', etc.
    action_metadata: Optional[str] = Field(default="{}", sa_column_kwargs={"name": "metadata"})  # Store as 'metadata' in DB but use 'action_metadata' in code
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Note: Database initialization happens in routes.py on startup

