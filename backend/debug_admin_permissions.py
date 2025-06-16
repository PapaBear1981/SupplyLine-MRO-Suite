"""
Debug script to check admin user permissions
"""
import sqlite3
import os

def get_database_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

def debug_admin_permissions():
    """Debug admin user permissions"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get admin user
        cursor.execute("SELECT id, name, employee_number, is_admin FROM users WHERE employee_number = 'ADMIN001'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("Admin user ADMIN001 not found!")
            return False
            
        user_id, name, emp_num, is_admin = admin_user
        print(f"Admin User: {name} ({emp_num})")
        print(f"User ID: {user_id}")
        print(f"Is Admin: {is_admin}")
        
        # Get user roles
        cursor.execute("""
            SELECT r.id, r.name, r.description
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = ?
        """, (user_id,))
        
        roles = cursor.fetchall()
        print(f"\nUser Roles ({len(roles)}):")
        for role_id, role_name, role_desc in roles:
            print(f"  - {role_name} (ID: {role_id}): {role_desc}")
            
            # Get permissions for this role
            cursor.execute("""
                SELECT p.name, p.description, p.category
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                ORDER BY p.category, p.name
            """, (role_id,))
            
            permissions = cursor.fetchall()
            print(f"    Permissions ({len(permissions)}):")
            current_category = None
            for perm_name, perm_desc, perm_category in permissions:
                if current_category != perm_category:
                    current_category = perm_category
                    print(f"      {perm_category}:")
                print(f"        - {perm_name}: {perm_desc}")
        
        # Check specifically for role.manage permission
        cursor.execute("""
            SELECT COUNT(*) FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = ? AND p.name = 'role.manage'
        """, (user_id,))
        
        has_role_manage = cursor.fetchone()[0] > 0
        print(f"\nHas 'role.manage' permission: {has_role_manage}")
        
        # Check if role.manage permission exists at all
        cursor.execute("SELECT id, name, description FROM permissions WHERE name = 'role.manage'")
        role_manage_perm = cursor.fetchone()
        if role_manage_perm:
            print(f"role.manage permission exists: ID {role_manage_perm[0]}")
        else:
            print("role.manage permission does NOT exist!")
        
        conn.close()
        return True

    except Exception as e:
        print(f"Error debugging admin permissions: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    debug_admin_permissions()
