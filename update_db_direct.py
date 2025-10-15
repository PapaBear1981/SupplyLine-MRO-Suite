#!/usr/bin/env python3
"""Direct database update using SQLite - bypasses Flask app"""
import sqlite3
from werkzeug.security import generate_password_hash

# Database path
db_path = 'database/tools.db'

# New password
new_password = 'Caden1234!'

# Generate password hash
password_hash = generate_password_hash(new_password)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update admin password
cursor.execute("""
    UPDATE user 
    SET password_hash = ? 
    WHERE employee_number = 'ADMIN001'
""", (password_hash,))

# Check if update was successful
if cursor.rowcount > 0:
    conn.commit()
    print("✅ SUCCESS: Password updated!")
    print(f"   Employee Number: ADMIN001")
    print(f"   New Password: {new_password}")
    print(f"   Password Hash: {password_hash[:50]}...")
    
    # Verify the update
    cursor.execute("SELECT employee_number, email, is_active FROM user WHERE employee_number = 'ADMIN001'")
    result = cursor.fetchone()
    if result:
        print(f"\n✅ Verified admin user exists:")
        print(f"   Employee Number: {result[0]}")
        print(f"   Email: {result[1]}")
        print(f"   Active: {result[2]}")
else:
    print("❌ ERROR: Admin user not found!")
    print("   Checking if user table exists...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    if cursor.fetchone():
        print("   ✅ User table exists")
        cursor.execute("SELECT employee_number FROM user")
        users = cursor.fetchall()
        print(f"   Found {len(users)} users in database:")
        for user in users:
            print(f"      - {user[0]}")
    else:
        print("   ❌ User table does not exist!")

conn.close()

