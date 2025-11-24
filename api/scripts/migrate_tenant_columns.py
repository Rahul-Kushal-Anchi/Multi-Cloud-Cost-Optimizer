"""
Migration script to add missing columns to tenant table.
Run this inside the ECS container or locally with database access.
"""

import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

print("Connecting to database...")
engine = create_engine(DATABASE_URL)

# Columns to add to tenant table
columns_to_add = [
    ("slug", "VARCHAR(255)"),
    ("plan", "VARCHAR(50) DEFAULT 'starter'"),
    ("status", "VARCHAR(50) DEFAULT 'trialing'"),
]

with engine.connect() as conn:
    # Check existing columns
    result = conn.execute(
        text(
            """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'tenant'
    """
        )
    )
    existing_columns = {row[0] for row in result.fetchall()}
    print(f"Existing columns: {sorted(existing_columns)}")

    # Add missing columns
    for col_name, col_def in columns_to_add:
        if col_name not in existing_columns:
            print(f"Adding column: {col_name}...")
            try:
                conn.execute(
                    text(f"ALTER TABLE tenant ADD COLUMN {col_name} {col_def}")
                )
                conn.commit()
                print(f"✅ Added column: {col_name}")
            except Exception as e:
                print(f"❌ Error adding {col_name}: {e}")
                conn.rollback()
        else:
            print(f"✅ Column {col_name} already exists")

    # Update existing rows with default values if needed
    print("\nUpdating existing rows with default values...")
    conn.execute(
        text(
            """
        UPDATE tenant 
        SET plan = 'starter' 
        WHERE plan IS NULL
    """
        )
    )
    conn.execute(
        text(
            """
        UPDATE tenant 
        SET status = 'trialing' 
        WHERE status IS NULL
    """
        )
    )
    conn.commit()
    print("✅ Updated existing rows")

print("\n✅ Migration completed!")
