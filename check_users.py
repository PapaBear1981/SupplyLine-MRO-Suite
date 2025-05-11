import os
import sqlite3

# Define the database path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'tools.db'))
print(f"Database path: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check users
cursor.execute("SELECT id, name, employee_number, department, is_admin FROM users")
users = cursor.fetchall()
print("Users in database:")
for user in users:
    print(f"  ID: {user[0]}, Name: {user[1]}, Employee #: {user[2]}, Department: {user[3]}, Admin: {user[4]}")

# Close the connection
conn.close()
