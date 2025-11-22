"""
Migration: Add procurement_order_id field to request_items table

This migration adds a foreign key linking request items to their procurement orders.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()


def run_migration():
    """Add procurement_order_id column to request_items table."""

    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*)
                FROM pragma_table_info('request_items')
                WHERE name='procurement_order_id'
            """))

            column_exists = result.scalar() > 0

            if column_exists:
                print("✓ procurement_order_id column already exists in request_items table")
                return True

            # Add procurement_order_id column
            print("Adding procurement_order_id column to request_items table...")
            db.session.execute(text("""
                ALTER TABLE request_items
                ADD COLUMN procurement_order_id INTEGER REFERENCES procurement_orders(id)
            """))

            db.session.commit()
            print("✓ Successfully added procurement_order_id column to request_items table")

            # Create index for better query performance
            print("Creating index on procurement_order_id...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_request_items_procurement_order_id
                ON request_items(procurement_order_id)
            """))

            db.session.commit()
            print("✓ Successfully created index on procurement_order_id")

            return True

        except Exception as e:
            print(f"✗ Error during migration: {e}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("Running migration: Add procurement_order_id to request_items")
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
