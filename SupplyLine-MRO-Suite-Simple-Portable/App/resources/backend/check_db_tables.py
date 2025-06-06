import sqlite3
import os

# Try different possible database paths
possible_paths = [
    os.path.join(os.path.dirname(__file__), 'app.db'),
    os.path.join(os.path.dirname(__file__), 'database.db'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'tools.db')
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        print(f"Found database at: {db_path}")
        break

if not db_path:
    print("Could not find the database file")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(f"- {table[0]}")
    
    # Get columns for each table
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"  Columns in {table[0]}:")
    for column in columns:
        print(f"    - {column[1]} ({column[2]})")

# Close the connection
conn.close()
