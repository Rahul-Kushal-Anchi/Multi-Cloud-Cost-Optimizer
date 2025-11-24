"""
Add is_global_owner column to users table if it doesn't exist.
This script can be run inside the ECS container or locally.
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

print("Connecting to database...")
engine = create_engine(DATABASE_URL)

# SQL to add the column if it doesn't exist
# PostgreSQL syntax
sql = """
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user' 
        AND column_name = 'is_global_owner'
    ) THEN
        ALTER TABLE "user" ADD COLUMN is_global_owner BOOLEAN DEFAULT FALSE;
        PRINT 'Column is_global_owner added successfully';
    ELSE
        PRINT 'Column is_global_owner already exists';
    END IF;
END $$;
"""

# Try PostgreSQL-style first
try:
    with engine.connect() as conn:
        # PostgreSQL doesn't support DO blocks in regular execute, use execute_driver_sql or execute(text())
        # Let's use a simpler approach
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name = 'is_global_owner'
        """
            )
        )
        exists = result.fetchone() is not None

        if not exists:
            print("Adding is_global_owner column...")
            conn.execute(
                text(
                    'ALTER TABLE "user" ADD COLUMN is_global_owner BOOLEAN DEFAULT FALSE'
                )
            )
            conn.commit()
            print("✅ Column is_global_owner added successfully")
        else:
            print("✅ Column is_global_owner already exists")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("Migration completed!")
