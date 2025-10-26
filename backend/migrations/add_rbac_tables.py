"""
Migration script to add RBAC tables to the database
"""
import sqlite3
import os
import sys

def run_migration():
    # Get the database path from DATABASE_URL environment variable or use default
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///database/tools.db')

    # Extract the path from the SQLite URL
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        # If it's a relative path, resolve it relative to the repository root
        if not os.path.isabs(db_path):
            # Get the repository root (3 levels up from this file: migrations -> backend -> repo root)
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(repo_root, db_path)
    else:
        # Fallback to default path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database', 'tools.db')

    print(f"Using database at: {db_path}")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create permissions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created or verified permissions table")

        # Create roles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            is_system_role BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created or verified roles table")

        # Create role_permissions table (many-to-many relationship)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE,
            UNIQUE(role_id, permission_id)
        )
        ''')
        print("Created or verified role_permissions table")

        # Create user_roles table (many-to-many relationship)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
            UNIQUE(user_id, role_id)
        )
        ''')
        print("Created or verified user_roles table")

        # Create default roles
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]

        if role_count == 0:
            # Insert default roles
            # Only Administrator is a system role - others are regular roles that can be edited/deleted
            default_roles = [
                (1, 'Administrator', 'Full system access with all permissions', 1),
                (2, 'Materials Manager', 'Can manage tools, chemicals, and users', 0),
                (3, 'Maintenance User', 'Basic access to view and checkout tools', 0)
            ]
            cursor.executemany("INSERT INTO roles (id, name, description, is_system_role) VALUES (?, ?, ?, ?)", default_roles)
            print("Created default roles")

        # Create default permissions
        cursor.execute("SELECT COUNT(*) FROM permissions")
        permission_count = cursor.fetchone()[0]
        
        if permission_count == 0:
            # Insert default permissions
            default_permissions = [
                # User management permissions
                (1, 'user.view', 'View user details', 'User Management'),
                (2, 'user.create', 'Create new users', 'User Management'),
                (3, 'user.edit', 'Edit user details', 'User Management'),
                (4, 'user.delete', 'Deactivate users', 'User Management'),
                
                # Tool management permissions
                (5, 'tool.view', 'View tool details', 'Tool Management'),
                (6, 'tool.create', 'Create new tools', 'Tool Management'),
                (7, 'tool.edit', 'Edit tool details', 'Tool Management'),
                (8, 'tool.delete', 'Delete tools', 'Tool Management'),
                (9, 'tool.checkout', 'Checkout tools', 'Tool Management'),
                (10, 'tool.return', 'Return tools', 'Tool Management'),
                (11, 'tool.service', 'Manage tool service status', 'Tool Management'),
                
                # Chemical management permissions
                (12, 'chemical.view', 'View chemical details', 'Chemical Management'),
                (13, 'chemical.create', 'Create new chemicals', 'Chemical Management'),
                (14, 'chemical.edit', 'Edit chemical details', 'Chemical Management'),
                (15, 'chemical.delete', 'Delete chemicals', 'Chemical Management'),
                (16, 'chemical.issue', 'Issue chemicals', 'Chemical Management'),
                (17, 'chemical.reorder', 'Reorder chemicals', 'Chemical Management'),
                
                # Calibration management permissions
                (18, 'calibration.view', 'View calibration details', 'Calibration Management'),
                (19, 'calibration.create', 'Create calibration records', 'Calibration Management'),
                (20, 'calibration.edit', 'Edit calibration details', 'Calibration Management'),
                (21, 'calibration.standards', 'Manage calibration standards', 'Calibration Management'),
                
                # Report permissions
                (22, 'report.view', 'View reports', 'Reporting'),
                (23, 'report.export', 'Export reports', 'Reporting'),
                
                # System permissions
                (24, 'system.settings', 'Manage system settings', 'System'),
                (25, 'system.audit', 'View audit logs', 'System'),
                (26, 'role.manage', 'Manage roles and permissions', 'System')
            ]
            cursor.executemany("INSERT INTO permissions (id, name, description, category) VALUES (?, ?, ?, ?)", default_permissions)
            print("Created default permissions")

        # Assign permissions to default roles
        cursor.execute("SELECT COUNT(*) FROM role_permissions")
        role_permission_count = cursor.fetchone()[0]
        
        if role_permission_count == 0:
            # Administrator role - all permissions
            admin_permissions = [(1, permission_id) for permission_id in range(1, 27)]
            cursor.executemany("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", admin_permissions)
            
            # Materials Manager role - specific permissions
            materials_permissions = [
                # User management (limited)
                (2, 1),  # user.view
                
                # Tool management (full)
                (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11),
                
                # Chemical management (full)
                (2, 12), (2, 13), (2, 14), (2, 15), (2, 16), (2, 17),
                
                # Calibration management (full)
                (2, 18), (2, 19), (2, 20), (2, 21),
                
                # Report permissions
                (2, 22), (2, 23)
            ]
            cursor.executemany("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", materials_permissions)
            
            # Maintenance User role - basic permissions
            maintenance_permissions = [
                # Tool management (limited)
                (3, 5),  # tool.view
                (3, 9),  # tool.checkout
                (3, 10), # tool.return
                
                # Chemical management (limited)
                (3, 12), # chemical.view
                
                # Report permissions (limited)
                (3, 22)  # report.view
            ]
            cursor.executemany("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", maintenance_permissions)
            
            print("Assigned permissions to default roles")

        # Migrate existing users to the new role system (if users table exists)
        try:
            cursor.execute("SELECT id, is_admin, department FROM users")
            users = cursor.fetchall()

            # Check if users have already been migrated
            cursor.execute("SELECT COUNT(*) FROM user_roles")
            user_role_count = cursor.fetchone()[0]

            if user_role_count == 0:
                for user_id, is_admin, department in users:
                    if is_admin:
                        # Assign Administrator role to admin users
                        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, 1))
                    elif department == 'Materials':
                        # Assign Materials Manager role to Materials department users
                        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, 2))
                    else:
                        # Assign Maintenance User role to all other users
                        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, 3))

                print(f"Migrated {len(users)} existing users to the new role system")
        except Exception as e:
            # Users table doesn't exist yet (e.g., in E2E test environment)
            # This is expected when running migrations before seeding data
            print(f"Skipping user migration (users table not found or empty): {str(e)}")

        # Commit the changes
        conn.commit()
        print("Schema changes committed successfully")

        # Close the connection
        conn.close()
        print("Database update completed successfully")
        return True
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1)
