"""
Migration script to add account lockout fields to the User model.
Run this script to update the database schema.
"""

import sqlite3
import os
import sys
from datetime import datetime

# Get the database path from the environment or use the default
if os.path.exists('/database'):
    db_path = os.path.join('/database', 'tools.db')
else:
    db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

print(f"Using database path: {db_path}")

# Check if the database file exists
if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    sys.exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the columns already exist
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

# Add the new columns if they don't exist
columns_to_add = []
if 'failed_login_attempts' not in column_names:
    columns_to_add.append(('failed_login_attempts', 'INTEGER DEFAULT 0'))
if 'account_locked_until' not in column_names:
    columns_to_add.append(('account_locked_until', 'TIMESTAMP'))
if 'last_failed_login' not in column_names:
    columns_to_add.append(('last_failed_login', 'TIMESTAMP'))

# Execute the ALTER TABLE statements
for column_name, column_type in columns_to_add:
    print(f"Adding column {column_name} to users table...")
    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")

# Commit the changes
conn.commit()

# Verify the changes
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]
print("\nCurrent columns in users table:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

# Close the connection
conn.close()

print("\nMigration completed successfully!")
