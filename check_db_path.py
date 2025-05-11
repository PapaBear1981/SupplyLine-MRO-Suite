import os
import sqlite3

# Define the database path
db_path = os.path.join(os.path.dirname(__file__), 'database', 'tools.db')
# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(db_path), exist_ok=True)
print(f"Database path: {db_path}")
print(f"Database directory exists: {os.path.exists(os.path.dirname(db_path))}")
print(f"Database file exists: {os.path.exists(db_path)}")

# Try to connect to the database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the tools table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tools'")
    if cursor.fetchone():
        print("Tools table exists")
        
        # Check the schema of the tools table
        cursor.execute("PRAGMA table_info(tools)")
        columns = cursor.fetchall()
        print("Tools table columns:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
    else:
        print("Tools table does not exist")
    
    conn.close()
    print("Database connection successful")
except Exception as e:
    print(f"Error connecting to database: {str(e)}")
