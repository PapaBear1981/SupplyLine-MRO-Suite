"""
Migration script to add new fields to the Checkout model for improved return tool functionality.
This script adds the following fields:
- return_condition: The condition of the tool when returned
- returned_by: Who returned the tool (can be different from the user who checked it out)
- found: Boolean indicating if the tool was found on the production floor
- return_notes: Additional notes about the return
"""

import sqlite3
import os
import sys

# Get the database path
db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database')
db_path = os.path.join(db_dir, 'tools.db')

def run_migration():
    print("Starting migration to add return fields to Checkout model...")

    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(checkouts)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add return_condition column if it doesn't exist
        if 'return_condition' not in columns:
            print("Adding return_condition column...")
            cursor.execute("ALTER TABLE checkouts ADD COLUMN return_condition TEXT")
        else:
            print("return_condition column already exists")

        # Add returned_by column if it doesn't exist
        if 'returned_by' not in columns:
            print("Adding returned_by column...")
            cursor.execute("ALTER TABLE checkouts ADD COLUMN returned_by TEXT")
        else:
            print("returned_by column already exists")

        # Add found column if it doesn't exist
        if 'found' not in columns:
            print("Adding found column...")
            cursor.execute("ALTER TABLE checkouts ADD COLUMN found BOOLEAN DEFAULT 0")
        else:
            print("found column already exists")

        # Add return_notes column if it doesn't exist
        if 'return_notes' not in columns:
            print("Adding return_notes column...")
            cursor.execute("ALTER TABLE checkouts ADD COLUMN return_notes TEXT")
        else:
            print("return_notes column already exists")

        # Commit the changes
        conn.commit()
        print("Migration completed successfully")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
