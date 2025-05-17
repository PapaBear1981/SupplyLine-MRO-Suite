"""
Migration script to add ip_address column to registration_requests table

This script adds the ip_address column to the registration_requests table
for security auditing purposes.
"""

import sqlite3
import os
import sys

def migrate_database():
    """
    Add ip_address column to registration_requests table if it doesn't exist
    """
    # Get database path from environment or use default
    if os.path.exists('/database'):
        db_path = os.path.join('/database', 'tools.db')
    else:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
    
    print(f"Using database path: {db_path}")
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if registration_requests table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registration_requests'")
        if not cursor.fetchone():
            print("registration_requests table does not exist, skipping migration")
            return
        
        # Check if ip_address column already exists
        cursor.execute("PRAGMA table_info(registration_requests)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ip_address' not in columns:
            print("Adding ip_address column to registration_requests table")
            cursor.execute("ALTER TABLE registration_requests ADD COLUMN ip_address TEXT")
            conn.commit()
            print("Migration completed successfully")
        else:
            print("ip_address column already exists in registration_requests table")
    
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
