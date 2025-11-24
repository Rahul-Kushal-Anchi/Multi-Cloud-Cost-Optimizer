from .aws.assume_role import assume_vendor_role
from sqlmodel import Session, create_engine, select
import os

# Database for tenant lookup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas.db")
_engine = create_engine(DATABASE_URL, echo=False)


def get_tenant_session_and_meta(tenant_id: int | None = None):
    """
    Get AWS session for tenant using their configured cross-account role.
    Falls back to hardcoded values if database not available (for development).
    """
    # Try to get from database if tenant_id provided
    if tenant_id:
        try:
            with Session(_engine) as session:
                from api.auth_onboarding.models import Tenant

                tenant = session.get(Tenant, tenant_id)
                if tenant and tenant.aws_role_arn:
                    session = assume_vendor_role(
                        tenant.aws_role_arn, tenant.external_id, tenant.region
                    )
                    meta = {
                        "role_arn": tenant.aws_role_arn,
                        "external_id": tenant.external_id,
                        "region": tenant.region,
                        "athena_workgroup": tenant.athena_workgroup,
                        "athena_db": tenant.athena_db,
                        "athena_table": tenant.athena_table,
                    }
                    return session, meta
        except Exception as e:
            print(f"Warning: Could not load tenant from DB: {e}")

    # Fallback to hardcoded values (for development/demo)
    meta = {
        "role_arn": "arn:aws:iam::123456789012:role/VendorCostReadOnlyRole",
        "external_id": "external-abc123",
        "region": "us-east-1",
        "athena_workgroup": "primary",
        "athena_db": "cur_db",
        "athena_table": "cur_table",
    }
    session = assume_vendor_role(meta["role_arn"], meta["external_id"], meta["region"])
    return session, meta
