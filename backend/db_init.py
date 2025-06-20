"""
Database Initialization Script for SupplyLine MRO Suite

This script initializes the PostgreSQL database with all required tables
and creates an initial admin user.
"""

import os
import sys
import logging
from flask import Flask
from models import db, User, Role, Permission, UserRole, RolePermission
from config import config
from werkzeug.security import generate_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user():
    """Create initial admin user if none exists"""
    try:
        # Check if any admin user exists
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            logger.info(f"Admin user already exists: {admin_user.name} ({admin_user.employee_number})")
            return True, "Admin user already exists", None
        
        # Create default admin user
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_user = User(
            name='System Administrator',
            employee_number='ADMIN001',
            department='IT',
            password_hash=generate_password_hash(admin_password),
            is_admin=True,
            is_active=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        logger.info(f"Created admin user: {admin_user.name} ({admin_user.employee_number})")
        return True, "Admin user created successfully", admin_password
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.session.rollback()
        return False, f"Error creating admin user: {str(e)}", None


def create_default_roles_and_permissions():
    """Create default roles and permissions"""
    try:
        # Define default permissions
        default_permissions = [
            ('view_tools', 'View tools and equipment'),
            ('manage_tools', 'Add, edit, and delete tools'),
            ('checkout_tools', 'Check out and return tools'),
            ('view_chemicals', 'View chemical inventory'),
            ('manage_chemicals', 'Add, edit, and delete chemicals'),
            ('issue_chemicals', 'Issue chemicals to users'),
            ('view_reports', 'View reports and analytics'),
            ('manage_users', 'Add, edit, and delete users'),
            ('view_audit_logs', 'View audit logs'),
            ('manage_calibration', 'Manage tool calibration'),
            ('view_announcements', 'View announcements'),
            ('manage_announcements', 'Create and manage announcements'),
        ]
        
        # Create permissions if they don't exist
        for perm_name, perm_desc in default_permissions:
            permission = Permission.query.filter_by(name=perm_name).first()
            if not permission:
                permission = Permission(name=perm_name, description=perm_desc)
                db.session.add(permission)
                logger.info(f"Created permission: {perm_name}")
        
        # Define default roles
        default_roles = [
            ('admin', 'Administrator', [p[0] for p in default_permissions]),
            ('tool_manager', 'Tool Manager', [
                'view_tools', 'manage_tools', 'checkout_tools', 'view_reports',
                'manage_calibration', 'view_announcements'
            ]),
            ('materials_manager', 'Materials Manager', [
                'view_chemicals', 'manage_chemicals', 'issue_chemicals', 'view_reports',
                'view_announcements'
            ]),
            ('user', 'Regular User', [
                'view_tools', 'checkout_tools', 'view_announcements'
            ])
        ]
        
        # Create roles if they don't exist
        for role_name, role_desc, role_permissions in default_roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=role_desc)
                db.session.add(role)
                db.session.flush()  # Get the role ID
                
                # Add permissions to role
                for perm_name in role_permissions:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
                        db.session.add(role_perm)
                
                logger.info(f"Created role: {role_name} with {len(role_permissions)} permissions")
        
        db.session.commit()
        return True, "Roles and permissions created successfully"
        
    except Exception as e:
        logger.error(f"Error creating roles and permissions: {str(e)}")
        db.session.rollback()
        return False, f"Error creating roles and permissions: {str(e)}"


def init_database(config_name='development'):
    """Initialize the database with all tables and default data"""
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config[config_name])
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            logger.info("Creating database tables...")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Create default roles and permissions
            success, message = create_default_roles_and_permissions()
            if not success:
                logger.error(message)
                return False
            
            # Create admin user
            success, message, password = create_admin_user()
            if not success:
                logger.error(message)
                return False
            
            if password:
                logger.warning("=" * 60)
                logger.warning("IMPORTANT: Default admin credentials created")
                logger.warning(f"Username: ADMIN001")
                logger.warning(f"Password: {password}")
                logger.warning("Please change the password after first login!")
                logger.warning("=" * 60)
            
            logger.info("Database initialization completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False


if __name__ == '__main__':
    # Get config from environment or use development
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    logger.info(f"Initializing database with config: {config_name}")
    
    if init_database(config_name):
        logger.info("Database initialization completed successfully!")
        sys.exit(0)
    else:
        logger.error("Database initialization failed!")
        sys.exit(1)
