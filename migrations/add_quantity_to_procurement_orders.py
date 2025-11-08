#!/usr/bin/env python3
"""
Migration: Add quantity and unit columns to procurement_orders table

This migration adds:
- quantity (INTEGER) - Order quantity for chemicals and other items
- unit (VARCHAR(20)) - Unit of measurement (e.g., mL, Gallon, each)
"""

import os
import sys
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Get the database path, checking both local and Docker environments."""
    # Check if running in Docker (volume mounted at /database)
    docker_db_path = "/database/tools.db"
    if os.path.exists(docker_db_path):
        return docker_db_path

    # Local development path
    local_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "tools.db")
    if os.path.exists(local_db_path):
        return local_db_path

    raise FileNotFoundError("Database file not found in expected locations")

def run_migration():
    """Add quantity and unit columns to procurement_orders table."""
    db_path = get_db_path()
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(procurement_orders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        columns_to_add = []
        if 'quantity' not in columns:
            columns_to_add.append(('quantity', 'INTEGER'))
        else:
            print("✓ Column 'quantity' already exists in procurement_orders table")
        
        if 'unit' not in columns:
            columns_to_add.append(('unit', 'VARCHAR(20)'))
        else:
            print("✓ Column 'unit' already exists in procurement_orders table")
        
        if not columns_to_add:
            print("✓ All columns already exist. No migration needed.")
            return True
        
        # Add the columns
        for column_name, column_type in columns_to_add:
            print(f"Adding column '{column_name}' to procurement_orders table...")
            cursor.execute(f"""
                ALTER TABLE procurement_orders 
                ADD COLUMN {column_name} {column_type}
            """)
            print(f"✓ Successfully added '{column_name}' column")
        
        conn.commit()
        
        # Verify the columns were added
        cursor.execute("PRAGMA table_info(procurement_orders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        for column_name, _ in columns_to_add:
            if column_name in columns:
                print(f"✓ Verified: Column '{column_name}' exists in procurement_orders table")
            else:
                print(f"✗ Error: Column '{column_name}' was not added successfully")
                return False
        
        print("\n✓ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

