"""
Migration: Add procurement_order_id to chemicals table

This migration adds a procurement_order_id foreign key to link chemicals
to procurement orders for integrated order management.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()

def run_migration():
    """Add procurement_order_id column to chemicals table"""
    with app.app_context():
        print("=" * 60)
        print("Running migration: Add procurement_order_id to chemicals")
        print("=" * 60)
        
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('chemicals')
                WHERE name = 'procurement_order_id'
            """))
            column_exists = result.fetchone()[0] > 0
            
            if column_exists:
                print("✓ procurement_order_id column already exists in chemicals table")
                print("\n" + "=" * 60)
                print("Migration already applied!")
                print("=" * 60)
                return
            
            print("Adding procurement_order_id column to chemicals table...")
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE chemicals 
                ADD COLUMN procurement_order_id INTEGER
            """))
            
            # Create index for better query performance
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chemicals_procurement_order_id 
                ON chemicals(procurement_order_id)
            """))
            
            db.session.commit()
            print("✓ Successfully added procurement_order_id column to chemicals table")
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error during migration: {str(e)}")
            print("\n" + "=" * 60)
            print("Migration failed!")
            print("=" * 60)
            raise

if __name__ == "__main__":
    run_migration()

