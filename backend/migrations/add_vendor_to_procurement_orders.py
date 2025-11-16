"""
Migration: Add vendor field to procurement_orders table

This migration adds a vendor field to track the vendor/supplier for orders.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()


def run_migration():
    """Add vendor column to procurement_orders table."""

    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*)
                FROM pragma_table_info('procurement_orders')
                WHERE name='vendor'
            """))

            column_exists = result.scalar() > 0

            if column_exists:
                print("✓ vendor column already exists in procurement_orders table")
                return True

            # Add vendor column
            print("Adding vendor column to procurement_orders table...")
            db.session.execute(text("""
                ALTER TABLE procurement_orders
                ADD COLUMN vendor VARCHAR(200)
            """))

            db.session.commit()
            print("✓ Successfully added vendor column to procurement_orders table")

            return True

        except Exception as e:
            print(f"✗ Error during migration: {e}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("Running migration: Add vendor to procurement_orders")
    print("=" * 60)

    success = run_migration()

    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)
        sys.exit(1)
