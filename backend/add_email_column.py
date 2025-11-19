"""
Migration script to add email column to users table
Run this with: python add_email_column.py
"""
import sqlite3
import os

# Get the database path
db_path = os.environ.get('DATABASE_PATH', '/database/tools.db')

print(f"Connecting to database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if email column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'email' in columns:
        print("Email column already exists. No migration needed.")
    else:
        print("Adding email column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
        print("Email column added successfully!")
        
except Exception as e:
    print(f"Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()
    print("Migration complete.")
