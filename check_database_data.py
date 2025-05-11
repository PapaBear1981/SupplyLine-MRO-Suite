import os
import sqlite3

# Define the database path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'tools.db'))
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables in database: {[table[0] for table in tables]}")

# Check data in tools table
cursor.execute("SELECT COUNT(*) FROM tools")
tool_count = cursor.fetchone()[0]
print(f"Number of tools in database: {tool_count}")

if tool_count > 0:
    cursor.execute("SELECT id, tool_number, serial_number, description, status FROM tools LIMIT 5")
    tools = cursor.fetchall()
    print("Sample tools:")
    for tool in tools:
        print(f"  ID: {tool[0]}, Tool #: {tool[1]}, Serial #: {tool[2]}, Description: {tool[3]}, Status: {tool[4]}")

# Check data in users table
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"Number of users in database: {user_count}")

if user_count > 0:
    cursor.execute("SELECT id, name, email, department, role FROM users LIMIT 5")
    users = cursor.fetchall()
    print("Sample users:")
    for user in users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Department: {user[3]}, Role: {user[4]}")

# Check data in checkouts table
cursor.execute("SELECT COUNT(*) FROM checkouts")
checkout_count = cursor.fetchone()[0]
print(f"Number of checkouts in database: {checkout_count}")

# Close the connection
conn.close()
