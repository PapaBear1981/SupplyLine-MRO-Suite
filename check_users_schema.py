import os
import sqlite3

# Define the database path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'tools.db'))

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check schema of users table
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("Users table schema:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

# Close the connection
conn.close()
