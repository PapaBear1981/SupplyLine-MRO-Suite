"""
Script to fix admin role permissions - add missing role management permissions
"""
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

def get_database_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

def fix_admin_permissions():
    """Add missing role management permissions to Administrator role"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get Administrator role ID
        cursor.execute("SELECT id FROM roles WHERE name = 'Administrator'")
        admin_role = cursor.fetchone()
        if not admin_role:
            print("Administrator role not found!")
            return False
        
        admin_role_id = admin_role[0]
        print(f"Administrator role ID: {admin_role_id}")

        # Check if role management permissions exist, if not create them
        role_permissions = [
            ('role.manage', 'Manage roles and permissions', 'Role Management'),
            ('role.view', 'View roles and permissions', 'Role Management'),
            ('role.create', 'Create new roles', 'Role Management'),
            ('role.edit', 'Edit existing roles', 'Role Management'),
            ('role.delete', 'Delete roles', 'Role Management'),
            ('system.audit', 'View system audit logs', 'System'),
            ('system.settings', 'Manage system settings', 'System')
        ]

        for perm_name, perm_desc, perm_category in role_permissions:
            # Check if permission exists
            cursor.execute("SELECT id FROM permissions WHERE name = ?", (perm_name,))
            permission = cursor.fetchone()
            
            if not permission:
                # Create the permission
                cursor.execute("""
                    INSERT INTO permissions (name, description, category, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                """, (perm_name, perm_desc, perm_category))
                permission_id = cursor.lastrowid
                print(f"Created permission: {perm_name}")
            else:
                permission_id = permission[0]
                print(f"Permission exists: {perm_name}")

            # Check if admin role already has this permission
            cursor.execute("""
                SELECT id FROM role_permissions 
                WHERE role_id = ? AND permission_id = ?
            """, (admin_role_id, permission_id))
            
            if not cursor.fetchone():
                # Add permission to admin role
                cursor.execute("""
                    INSERT INTO role_permissions (role_id, permission_id, created_at)
                    VALUES (?, ?, datetime('now'))
                """, (admin_role_id, permission_id))
                print(f"Added permission {perm_name} to Administrator role")
            else:
                print(f"Administrator already has permission: {perm_name}")

        # Verify admin has all permissions
        cursor.execute("""
            SELECT p.name, p.description, p.category
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = ?
            ORDER BY p.category, p.name
        """, (admin_role_id,))
        
        admin_permissions = cursor.fetchall()
        print(f"\nAdministrator role now has {len(admin_permissions)} permissions:")
        
        current_category = None
        for perm_name, perm_desc, perm_category in admin_permissions:
            if current_category != perm_category:
                current_category = perm_category
                print(f"\n{perm_category}:")
            print(f"  - {perm_name}")

        conn.commit()
        conn.close()
        
        print("\nAdmin role permissions fixed successfully!")
        return True

    except Exception as e:
        print(f"Error fixing admin permissions: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = fix_admin_permissions()
    if success:
        print("\nAdmin role permissions fix completed!")
        print("The Administrator role now has access to:")
        print("- Role Management")
        print("- System Settings") 
        print("- Audit Logs")
        print("- All other admin functions")
    else:
        print("\nAdmin role permissions fix failed!")
