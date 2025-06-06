import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
db_path = os.path.abspath(db_path)

print(f"Using database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the category column already exists
cursor.execute("PRAGMA table_info(tools)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'category' not in column_names:
    # Add the category column to the tools table
    cursor.execute("ALTER TABLE tools ADD COLUMN category TEXT DEFAULT 'General'")
    print("Added 'category' column to tools table")
else:
    print("'category' column already exists in tools table")

# Commit the changes and close the connection
conn.commit()
conn.close()
