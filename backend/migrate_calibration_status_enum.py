#!/usr/bin/env python3
"""
Migration script to convert calibration_status from String to Enum
This migration:
1. Creates the calibration_status_enum type
2. Updates existing rows to map legacy values to new enum values
3. Alters the column to use the enum type with proper constraints
"""

import sqlite3
import os
import sys
from datetime import datetime

def get_database_path():
    """Get the database path"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for database in the parent directory's database folder
    db_path = os.path.join(script_dir, '..', 'database', 'tools.db')
    
    if not os.path.exists(db_path):
        # Alternative path
        db_path = os.path.join(script_dir, 'database', 'tools.db')
    
    return os.path.abspath(db_path)

def migrate_calibration_status_enum():
    """
    Migrate calibration_status from String to Enum with proper constraints
    """
    db_path = get_database_path()
    print(f"Connecting to database at {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Starting calibration status enum migration...")
        
        # Step 1: Check current calibration_status values
        cursor.execute("SELECT DISTINCT calibration_status FROM tool_calibrations WHERE calibration_status IS NOT NULL")
        existing_statuses = [row[0] for row in cursor.fetchall()]
        print(f"Found existing calibration statuses: {existing_statuses}")
        
        # Step 2: Update legacy values to new enum values
        status_mapping = {
            'completed': 'pass',
            'failed': 'fail', 
            'in_progress': 'limited'
        }
        
        updated_count = 0
        for old_status, new_status in status_mapping.items():
            cursor.execute(
                "UPDATE tool_calibrations SET calibration_status = ? WHERE calibration_status = ?",
                (new_status, old_status)
            )
            count = cursor.rowcount
            if count > 0:
                print(f"Updated {count} records from '{old_status}' to '{new_status}'")
                updated_count += count
        
        # Step 3: Verify all values are now valid enum values
        cursor.execute("SELECT DISTINCT calibration_status FROM tool_calibrations WHERE calibration_status IS NOT NULL")
        current_statuses = [row[0] for row in cursor.fetchall()]
        valid_statuses = {'pass', 'fail', 'limited'}
        
        invalid_statuses = set(current_statuses) - valid_statuses
        if invalid_statuses:
            print(f"ERROR: Found invalid calibration statuses after migration: {invalid_statuses}")
            print("Please manually update these values before proceeding.")
            return False
        
        print(f"All calibration statuses are now valid: {current_statuses}")
        
        # Step 4: Add a check constraint (SQLite doesn't support ALTER TABLE ADD CONSTRAINT for CHECK)
        # We'll create a new table with the constraint and copy data
        print("Creating new table with enum constraint...")
        
        # Create new table with check constraint
        cursor.execute("""
            CREATE TABLE tool_calibrations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER NOT NULL,
                calibration_date TIMESTAMP NOT NULL,
                next_calibration_date TIMESTAMP,
                performed_by_user_id INTEGER NOT NULL,
                calibration_notes TEXT,
                calibration_status TEXT NOT NULL DEFAULT 'pass' 
                    CHECK (calibration_status IN ('pass', 'fail', 'limited')),
                calibration_certificate_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tool_id) REFERENCES tools (id),
                FOREIGN KEY (performed_by_user_id) REFERENCES users (id)
            )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO tool_calibrations_new 
            SELECT * FROM tool_calibrations
        """)
        
        # Get count of copied records
        cursor.execute("SELECT COUNT(*) FROM tool_calibrations_new")
        copied_count = cursor.fetchone()[0]
        print(f"Copied {copied_count} calibration records to new table")
        
        # Drop old table and rename new table
        cursor.execute("DROP TABLE tool_calibrations")
        cursor.execute("ALTER TABLE tool_calibrations_new RENAME TO tool_calibrations")
        
        # Recreate indexes if they existed
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calibrations_tool_id 
            ON tool_calibrations(tool_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calibrations_date 
            ON tool_calibrations(calibration_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calibrations_next_date 
            ON tool_calibrations(next_calibration_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tool_calibrations_status 
            ON tool_calibrations(calibration_status)
        """)
        
        # Commit changes
        conn.commit()
        
        print(f"Migration completed successfully!")
        print(f"- Updated {updated_count} legacy status values")
        print(f"- Added CHECK constraint for calibration_status")
        print(f"- Recreated indexes")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Calibration Status Enum Migration")
    print("=" * 40)
    
    success = migrate_calibration_status_enum()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
