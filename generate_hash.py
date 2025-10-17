#!/usr/bin/env python3
"""Generate password hash for Caden1234!"""
from werkzeug.security import generate_password_hash

password = "Caden1234!"
hash_value = generate_password_hash(password)
print(f"Password: {password}")
print(f"Hash: {hash_value}")
print("\nTo update the database manually, run:")
print(f"UPDATE user SET password_hash = '{hash_value}' WHERE employee_number = 'ADMIN001';")

