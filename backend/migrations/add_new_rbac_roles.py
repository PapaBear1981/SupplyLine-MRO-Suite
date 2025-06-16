"""
Migration script to add new RBAC roles and permissions for User, Lead, and Mechanic roles
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
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database', 'tools.db'))

def run_migration():
    """Add new RBAC roles and permissions"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if new roles already exist
        cursor.execute("SELECT COUNT(*) FROM roles WHERE name IN ('User', 'Lead', 'Mechanic')")
        existing_roles = cursor.fetchone()[0]
        
        if existing_roles > 0:
            logger.info("New roles already exist, skipping role creation")
        else:
            # Add new roles
            new_roles = [
                ('User', 'Standard employee access with basic permissions', 1),
                ('Lead', 'Supervisory access with additional management permissions', 1),
                ('Mechanic', 'Limited technician access for tools and checkouts only', 1)
            ]
            
            cursor.executemany(
                "INSERT INTO roles (name, description, is_system_role) VALUES (?, ?, ?)",
                new_roles
            )
            logger.info("Created new roles: User, Lead, Mechanic")

        # Get role IDs
        cursor.execute("SELECT id, name FROM roles WHERE name IN ('User', 'Lead', 'Mechanic', 'Administrator')")
        role_mapping = {name: id for id, name in cursor.fetchall()}
        
        # Check if new permissions already exist
        new_permission_names = [
            'dashboard.view', 'tool.view', 'tool.checkout', 'checkout.manage_own',
            'checkout.view_all', 'chemical.view', 'chemical.issue', 'cycle_count.view',
            'cycle_count.participate', 'calibration.view', 'calibration.manage',
            'report.view', 'report.generate'
        ]
        
        cursor.execute(f"SELECT COUNT(*) FROM permissions WHERE name IN ({','.join(['?' for _ in new_permission_names])})", new_permission_names)
        existing_permissions = cursor.fetchone()[0]
        
        if existing_permissions < len(new_permission_names):
            # Add new permissions
            new_permissions = [
                ('dashboard.view', 'View dashboard', 'Dashboard'),
                ('tool.view', 'View tools', 'Tools'),
                ('tool.checkout', 'Checkout tools', 'Tools'),
                ('checkout.manage_own', 'Manage own checkouts', 'Checkouts'),
                ('checkout.view_all', 'View all checkouts', 'Checkouts'),
                ('chemical.view', 'View chemicals', 'Chemicals'),
                ('chemical.issue', 'Issue chemicals', 'Chemicals'),
                ('cycle_count.view', 'View cycle counts', 'Cycle Counts'),
                ('cycle_count.participate', 'Participate in cycle counts', 'Cycle Counts'),
                ('calibration.view', 'View calibrations', 'Calibrations'),
                ('calibration.manage', 'Manage calibrations', 'Calibrations'),
                ('report.view', 'View reports', 'Reports'),
                ('report.generate', 'Generate reports', 'Reports')
            ]
            
            # Insert only permissions that don't exist
            for perm in new_permissions:
                cursor.execute("SELECT COUNT(*) FROM permissions WHERE name = ?", (perm[0],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO permissions (name, description, category) VALUES (?, ?, ?)",
                        perm
                    )
            
            logger.info("Added new permissions")

        # Get permission IDs
        cursor.execute("SELECT id, name FROM permissions")
        permission_mapping = {name: id for id, name in cursor.fetchall()}

        # Clear existing role permissions for new roles to avoid duplicates
        if 'User' in role_mapping:
            cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_mapping['User'],))
        if 'Lead' in role_mapping:
            cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_mapping['Lead'],))
        if 'Mechanic' in role_mapping:
            cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_mapping['Mechanic'],))

        # Assign permissions to User role
        if 'User' in role_mapping:
            user_permissions = [
                'dashboard.view', 'tool.view', 'tool.checkout', 'checkout.manage_own',
                'checkout.view_all', 'chemical.view', 'chemical.issue',
                'cycle_count.view', 'cycle_count.participate'
            ]
            
            for perm_name in user_permissions:
                if perm_name in permission_mapping:
                    cursor.execute(
                        "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                        (role_mapping['User'], permission_mapping[perm_name])
                    )
            logger.info("Assigned permissions to User role")

        # Assign permissions to Lead role (includes all User permissions plus additional ones)
        if 'Lead' in role_mapping:
            lead_permissions = [
                'dashboard.view', 'tool.view', 'tool.checkout', 'checkout.manage_own',
                'checkout.view_all', 'chemical.view', 'chemical.issue',
                'cycle_count.view', 'cycle_count.participate',
                'calibration.view', 'calibration.manage', 'report.view', 'report.generate'
            ]
            
            for perm_name in lead_permissions:
                if perm_name in permission_mapping:
                    cursor.execute(
                        "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                        (role_mapping['Lead'], permission_mapping[perm_name])
                    )
            logger.info("Assigned permissions to Lead role")

        # Assign permissions to Mechanic role
        if 'Mechanic' in role_mapping:
            mechanic_permissions = [
                'tool.view', 'checkout.manage_own'
            ]
            
            for perm_name in mechanic_permissions:
                if perm_name in permission_mapping:
                    cursor.execute(
                        "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                        (role_mapping['Mechanic'], permission_mapping[perm_name])
                    )
            logger.info("Assigned permissions to Mechanic role")

        conn.commit()
        conn.close()
        
        logger.info("RBAC roles and permissions migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during RBAC migration: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = run_migration()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
