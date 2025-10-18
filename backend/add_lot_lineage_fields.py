#!/usr/bin/env python3
"""
Migration script to add lot lineage tracking fields to the chemicals table.
Adds parent_lot_number and lot_sequence columns.
"""

import sqlite3
import os
import sys

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')

def migrate():
    """Add lot lineage fields to chemicals table"""
    print(f"Connecting to database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(chemicals)")
        columns = [col[1] for col in cursor.fetchall()]
        
        changes_made = False
        
        # Add parent_lot_number column if it doesn't exist
        if 'parent_lot_number' not in columns:
            print("Adding parent_lot_number column...")
            cursor.execute("""
                ALTER TABLE chemicals 
                ADD COLUMN parent_lot_number TEXT
            """)
            changes_made = True
            print("✓ parent_lot_number column added")
        else:
            print("✓ parent_lot_number column already exists")
        
        # Add lot_sequence column if it doesn't exist
        if 'lot_sequence' not in columns:
            print("Adding lot_sequence column...")
            cursor.execute("""
                ALTER TABLE chemicals 
                ADD COLUMN lot_sequence INTEGER DEFAULT 0
            """)
            changes_made = True
            print("✓ lot_sequence column added")
        else:
            print("✓ lot_sequence column already exists")
        
        if changes_made:
            # Initialize lot_sequence to 0 for all existing chemicals
            cursor.execute("""
                UPDATE chemicals 
                SET lot_sequence = 0 
                WHERE lot_sequence IS NULL
            """)
            print(f"✓ Initialized lot_sequence for {cursor.rowcount} existing chemicals")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Chemical Lot Lineage Migration")
    print("=" * 60)
    migrate()

