"""
Script to test RBAC permissions for different user roles
"""
import sqlite3
import os
from models import User, Role, Permission, UserRole, RolePermission

def get_database_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

def test_user_permissions():
    """Test permissions for different user roles"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test users
        test_users = ['ADMIN001', 'USER001', 'LEAD001', 'MECH001', 'MAT001']
        
        print("RBAC Permission Testing")
        print("=" * 50)
        
        for employee_number in test_users:
            print(f"\nTesting user: {employee_number}")
            print("-" * 30)
            
            # Get user info
            cursor.execute("""
                SELECT u.id, u.name, u.employee_number, u.department, u.is_admin
                FROM users u 
                WHERE u.employee_number = ?
            """, (employee_number,))
            
            user_row = cursor.fetchone()
            if not user_row:
                print(f"User {employee_number} not found")
                continue
                
            user_id, name, emp_num, department, is_admin = user_row
            print(f"Name: {name}")
            print(f"Department: {department}")
            print(f"Is Admin: {is_admin}")
            
            # Get user roles
            cursor.execute("""
                SELECT r.name, r.description
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ?
            """, (user_id,))
            
            roles = cursor.fetchall()
            if roles:
                print("Roles:")
                for role_name, role_desc in roles:
                    print(f"  - {role_name}: {role_desc}")
            else:
                print("Roles: None")
            
            # Get user permissions
            cursor.execute("""
                SELECT DISTINCT p.name, p.description, p.category
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN user_roles ur ON rp.role_id = ur.role_id
                WHERE ur.user_id = ?
                ORDER BY p.category, p.name
            """, (user_id,))
            
            permissions = cursor.fetchall()
            if permissions:
                print("Permissions:")
                current_category = None
                for perm_name, perm_desc, perm_category in permissions:
                    if current_category != perm_category:
                        current_category = perm_category
                        print(f"  {perm_category}:")
                    print(f"    - {perm_name}: {perm_desc}")
            else:
                print("Permissions: None (legacy admin permissions may apply)")

        conn.close()
        return True

    except Exception as e:
        print(f"Error testing permissions: {str(e)}")
        if conn:
            conn.close()
        return False

def test_role_hierarchy():
    """Test the role hierarchy and permission inheritance"""
    print("\n" + "=" * 50)
    print("ROLE HIERARCHY AND PERMISSIONS")
    print("=" * 50)
    
    role_permissions = {
        'Administrator': 'All system permissions (legacy admin)',
        'Lead': 'Dashboard, Tools, Checkouts, Chemicals, Calibrations, Reports, Cycle Counts',
        'User': 'Dashboard, Tools, Checkouts, Chemicals, Cycle Counts',
        'Mechanic': 'Tools (view only), Own Checkouts',
        'Materials Manager': 'Tools, Chemicals, Calibrations, Reports (legacy role)'
    }
    
    for role, permissions in role_permissions.items():
        print(f"\n{role}:")
        print(f"  Permissions: {permissions}")

if __name__ == "__main__":
    success = test_user_permissions()
    if success:
        test_role_hierarchy()
        print("\n" + "=" * 50)
        print("RBAC permission testing completed!")
        print("\nTo test in the application:")
        print("1. Login with different user credentials")
        print("2. Verify navigation menu shows appropriate options")
        print("3. Test access to restricted pages")
        print("4. Verify role assignment in User Management")
    else:
        print("\nRBAC permission testing failed!")
