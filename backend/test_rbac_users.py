"""
Script to create test users with different roles for RBAC testing
"""
import sqlite3
import os
import hashlib
from datetime import datetime

def get_database_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """Create test users with different roles"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get role IDs
        cursor.execute("SELECT id, name FROM roles")
        roles = {name: id for id, name in cursor.fetchall()}
        print(f"Available roles: {roles}")

        # Test users to create
        test_users = [
            {
                'name': 'John User',
                'employee_number': 'USER001',
                'department': 'Maintenance',
                'password': 'user123',
                'role': 'User'
            },
            {
                'name': 'Jane Lead',
                'employee_number': 'LEAD001',
                'department': 'Maintenance',
                'password': 'lead123',
                'role': 'Lead'
            },
            {
                'name': 'Mike Mechanic',
                'employee_number': 'MECH001',
                'department': 'Maintenance',
                'password': 'mech123',
                'role': 'Mechanic'
            },
            {
                'name': 'Sarah Materials',
                'employee_number': 'MAT001',
                'department': 'Materials',
                'password': 'mat123',
                'role': 'User'
            }
        ]

        for user_data in test_users:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE employee_number = ?", (user_data['employee_number'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                user_id = existing_user[0]
                print(f"User {user_data['employee_number']} already exists, updating role...")
            else:
                # Create new user
                hashed_password = hash_password(user_data['password'])
                cursor.execute("""
                    INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['name'],
                    user_data['employee_number'],
                    user_data['department'],
                    hashed_password,
                    False,  # is_admin
                    True,   # is_active
                    datetime.now().isoformat()
                ))
                user_id = cursor.lastrowid
                print(f"Created user {user_data['employee_number']} with ID {user_id}")

            # Assign role to user
            role_name = user_data['role']
            if role_name in roles:
                role_id = roles[role_name]
                
                # Remove existing roles for this user
                cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
                
                # Add new role
                cursor.execute("""
                    INSERT INTO user_roles (user_id, role_id, created_at)
                    VALUES (?, ?, ?)
                """, (user_id, role_id, datetime.now().isoformat()))
                
                print(f"Assigned role '{role_name}' to user {user_data['employee_number']}")
            else:
                print(f"Role '{role_name}' not found for user {user_data['employee_number']}")

        conn.commit()
        conn.close()
        
        print("\nTest users created successfully!")
        print("\nTest Credentials:")
        for user_data in test_users:
            print(f"- {user_data['role']}: {user_data['employee_number']} / {user_data['password']}")
        
        return True

    except Exception as e:
        print(f"Error creating test users: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = create_test_users()
    if success:
        print("\nRBAC test users setup completed!")
    else:
        print("\nRBAC test users setup failed!")
