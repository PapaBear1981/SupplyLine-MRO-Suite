"""
Script to check for corrupted datetime data in the database
"""
import sqlite3
import os
import re

def get_database_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

def check_datetime_corruption():
    """Check for corrupted datetime data"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check users table for corrupted created_at
        print("Checking users table for corrupted datetime data...")
        cursor.execute("SELECT id, name, employee_number, created_at FROM users")
        users = cursor.fetchall()
        
        corrupted_users = []
        for user_id, name, emp_num, created_at in users:
            if created_at and isinstance(created_at, str):
                # Check for malformed datetime strings
                if re.search(r'\d{2}:\d{3}:\d{2}', created_at):  # Look for patterns like 12:222:44
                    corrupted_users.append((user_id, name, emp_num, created_at))
                    print(f"CORRUPTED: User {emp_num} ({name}) has corrupted created_at: {created_at}")
        
        if not corrupted_users:
            print("No corrupted datetime data found in users table")
        
        # Check roles table
        print("\nChecking roles table for corrupted datetime data...")
        cursor.execute("SELECT id, name, created_at FROM roles")
        roles = cursor.fetchall()
        
        corrupted_roles = []
        for role_id, name, created_at in roles:
            if created_at and isinstance(created_at, str):
                if re.search(r'\d{2}:\d{3}:\d{2}', created_at):
                    corrupted_roles.append((role_id, name, created_at))
                    print(f"CORRUPTED: Role {name} has corrupted created_at: {created_at}")
        
        if not corrupted_roles:
            print("No corrupted datetime data found in roles table")
        
        # Check permissions table
        print("\nChecking permissions table for corrupted datetime data...")
        cursor.execute("SELECT id, name, created_at FROM permissions")
        permissions = cursor.fetchall()
        
        corrupted_permissions = []
        for perm_id, name, created_at in permissions:
            if created_at and isinstance(created_at, str):
                if re.search(r'\d{2}:\d{3}:\d{2}', created_at):
                    corrupted_permissions.append((perm_id, name, created_at))
                    print(f"CORRUPTED: Permission {name} has corrupted created_at: {created_at}")
        
        if not corrupted_permissions:
            print("No corrupted datetime data found in permissions table")
        
        # Check user_roles table
        print("\nChecking user_roles table for corrupted datetime data...")
        cursor.execute("SELECT id, user_id, role_id, created_at FROM user_roles")
        user_roles = cursor.fetchall()
        
        corrupted_user_roles = []
        for ur_id, user_id, role_id, created_at in user_roles:
            if created_at and isinstance(created_at, str):
                if re.search(r'\d{2}:\d{3}:\d{2}', created_at):
                    corrupted_user_roles.append((ur_id, user_id, role_id, created_at))
                    print(f"CORRUPTED: UserRole {ur_id} (user {user_id}, role {role_id}) has corrupted created_at: {created_at}")
        
        if not corrupted_user_roles:
            print("No corrupted datetime data found in user_roles table")
        
        # Summary
        total_corrupted = len(corrupted_users) + len(corrupted_roles) + len(corrupted_permissions) + len(corrupted_user_roles)
        print(f"\nSummary:")
        print(f"- Corrupted users: {len(corrupted_users)}")
        print(f"- Corrupted roles: {len(corrupted_roles)}")
        print(f"- Corrupted permissions: {len(corrupted_permissions)}")
        print(f"- Corrupted user_roles: {len(corrupted_user_roles)}")
        print(f"- Total corrupted records: {total_corrupted}")
        
        if total_corrupted > 0:
            print("\nTo fix these issues, you may need to:")
            print("1. Update the corrupted datetime strings to valid ISO format")
            print("2. Or set them to NULL if the exact time is not important")
            print("3. Run a database repair script")
        
        conn.close()
        return total_corrupted == 0

    except Exception as e:
        print(f"Error checking datetime corruption: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    success = check_datetime_corruption()
    if success:
        print("\nDatetime corruption check completed - no issues found!")
    else:
        print("\nDatetime corruption check found issues!")
