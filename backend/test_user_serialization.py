"""
Test script to isolate user serialization issues
"""
import sys
import os
import sqlite3
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_database_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

def test_user_serialization():
    """Test user serialization to find the issue"""
    db_path = get_database_path()

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all users with their basic info
        cursor.execute("SELECT id, name, employee_number, created_at FROM users")
        users = cursor.fetchall()
        print(f"Found {len(users)} users")

        for user_id, name, emp_num, created_at in users:
            print(f"\nTesting user: {name} ({emp_num})")
            print(f"  User created_at: {created_at}")

            # Get user roles
            cursor.execute("""
                SELECT r.id, r.name, r.created_at, ur.created_at as user_role_created_at
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ?
            """, (user_id,))

            user_roles = cursor.fetchall()
            print(f"  User has {len(user_roles)} roles")

            for role_id, role_name, role_created_at, ur_created_at in user_roles:
                print(f"    Role: {role_name} (ID: {role_id})")
                print(f"      Role created_at: {role_created_at}")
                print(f"      UserRole created_at: {ur_created_at}")

                # Check if any datetime strings look malformed
                for dt_str in [created_at, role_created_at, ur_created_at]:
                    if dt_str and isinstance(dt_str, str):
                        try:
                            # Try to parse the datetime
                            if 'T' in dt_str:
                                datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                            print(f"        DateTime '{dt_str}' is valid")
                        except Exception as dt_error:
                            print(f"        ERROR: DateTime '{dt_str}' is invalid: {dt_error}")
                            return False

        conn.close()
        print("\nAll user datetime data is valid!")
        return True

    except Exception as e:
        print(f"Error testing user serialization: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    success = test_user_serialization()
    if success:
        print("\nUser serialization test completed successfully!")
    else:
        print("\nUser serialization test found issues!")
