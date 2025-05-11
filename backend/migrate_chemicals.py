import sqlite3
import os
from datetime import datetime

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'tools.db')
print(f"Using database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the chemicals table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chemicals'")
table_exists = cursor.fetchone()

if table_exists:
    print("Chemicals table exists, checking for columns...")
    
    # Get current columns in the chemicals table
    cursor.execute("PRAGMA table_info(chemicals)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Check if the new columns already exist
    is_archived_exists = 'is_archived' in column_names
    archived_reason_exists = 'archived_reason' in column_names
    archived_date_exists = 'archived_date' in column_names
    
    # Add the new columns if they don't exist
    if not is_archived_exists:
        print("Adding is_archived column...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN is_archived BOOLEAN DEFAULT 0")
    else:
        print("is_archived column already exists")
    
    if not archived_reason_exists:
        print("Adding archived_reason column...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN archived_reason TEXT")
    else:
        print("archived_reason column already exists")
    
    if not archived_date_exists:
        print("Adding archived_date column...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN archived_date TIMESTAMP")
    else:
        print("archived_date column already exists")
    
    # Commit the changes
    conn.commit()
    print("Migration completed successfully")
else:
    print("Chemicals table does not exist, no migration needed")

# Close the connection
conn.close()
