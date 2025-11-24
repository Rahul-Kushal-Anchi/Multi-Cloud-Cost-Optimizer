"""
Promote an existing user to global owner (platform admin).

Usage:
  python api/scripts/make_global_owner.py akrahul211@gmail.com

If no email is passed, it will use OWNER_EMAIL below.
"""

import os
import sys

# Add parent directory to path to import from api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# --- CHANGE THIS IF YOU WANT A DEFAULT EMAIL ---
OWNER_EMAIL = "akrahul211@gmail.com"

# Import your app's DB session + User model
from sqlmodel import Session, select, create_engine
from api.auth_onboarding.models import User


def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:DevPassword123!@aws-cost-optimizer-dev-db.cqfoeyiys9fy.us-east-1.rds.amazonaws.com:5432/awscostoptimizer_dev",
    )


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else OWNER_EMAIL

    if not email:
        print("❌ No email provided. Pass it as an argument.")
        sys.exit(1)

    print(f"Connecting to database...")
    engine = create_engine(get_database_url())

    with Session(engine) as db:
        try:
            user = db.exec(select(User).where(User.email == email)).first()

            if not user:
                print(f"❌ User not found: {email}")
                sys.exit(2)

            print(f"\nCurrent status:")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Tenant ID: {user.tenant_id}")
            print(f"  Is Global Owner: {user.is_global_owner}")

            # Promote to global owner
            user.role = "global_owner"
            user.tenant_id = None
            user.is_global_owner = True

            db.add(user)
            db.commit()
            db.refresh(user)

            print(f"\n✅ Promoted to global owner: {user.email}")
            print(f"  New Role: {user.role}")
            print(f"  New Tenant ID: {user.tenant_id}")
            print(f"  New Is Global Owner: {user.is_global_owner}")
            print(
                "\n👉 Log out in the web app and log back in to get a JWT with the new role."
            )

        except Exception as e:
            db.rollback()
            print(f"❌ Error: {repr(e)}")
            import traceback

            traceback.print_exc()
            sys.exit(3)


if __name__ == "__main__":
    main()
