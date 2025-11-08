"""
Migration script to add requested_quantity column to chemicals table.
This column stores the quantity requested when creating a reorder request.
"""

import sqlite3
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.config import Config
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
except ImportError:
    # Fallback for when running inside Docker container
    from config import Config
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')


def run_migration():
    """Add requested_quantity column to chemicals table."""
    
    print(f"Connecting to database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(chemicals)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'requested_quantity' in columns:
            print("✓ Column 'requested_quantity' already exists in chemicals table")
            conn.close()
            return True
        
        # Add the requested_quantity column
        print("Adding 'requested_quantity' column to chemicals table...")
        cursor.execute("""
            ALTER TABLE chemicals 
            ADD COLUMN requested_quantity INTEGER
        """)
        
        conn.commit()
        print("✓ Successfully added 'requested_quantity' column")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(chemicals)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'requested_quantity' in columns:
            print("✓ Verified: Column 'requested_quantity' exists in chemicals table")
        else:
            print("✗ Error: Column 'requested_quantity' was not added")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add requested_quantity to chemicals table")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n✓ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)

