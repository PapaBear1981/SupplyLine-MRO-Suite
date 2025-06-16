#!/usr/bin/env python3
"""
Fix Admin Permissions Script
This script fixes the admin user permissions and sets up proper RBAC roles.
"""

import os
import sys
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Role, Permission, UserRole, RolePermission
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_admin_user():
    """Fix the admin user to have proper permissions."""
    try:
        # Get the admin user
        admin_user = User.query.filter_by(employee_number='ADMIN001').first()
        
        if not admin_user:
            logger.error("Admin user ADMIN001 not found!")
            return False
            
        logger.info(f"Found admin user: {admin_user.name}")
        logger.info(f"Current department: {admin_user.department}")
        logger.info(f"Is admin: {admin_user.is_admin}")
        
        # Fix the department to 'Materials' so existing decorators work
        admin_user.department = 'Materials'
        admin_user.is_admin = True
        admin_user.is_active = True
        
        db.session.commit()
        logger.info("✓ Updated admin user department to 'Materials'")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing admin user: {e}")
        db.session.rollback()
        return False

def setup_rbac_system():
    """Set up the RBAC system with proper roles and permissions."""
    try:
        # Create default permissions if they don't exist
        default_permissions = [
            ('user.view', 'View users', 'User Management'),
            ('user.create', 'Create users', 'User Management'),
            ('user.edit', 'Edit users', 'User Management'),
            ('user.delete', 'Delete users', 'User Management'),
            
            ('tool.view', 'View tools', 'Tool Management'),
            ('tool.create', 'Create tools', 'Tool Management'),
            ('tool.edit', 'Edit tools', 'Tool Management'),
            ('tool.delete', 'Delete tools', 'Tool Management'),
            ('tool.checkout', 'Checkout tools', 'Tool Management'),
            ('tool.return', 'Return tools', 'Tool Management'),
            ('tool.manage', 'Manage tools', 'Tool Management'),
            
            ('chemical.view', 'View chemicals', 'Chemical Management'),
            ('chemical.create', 'Create chemicals', 'Chemical Management'),
            ('chemical.edit', 'Edit chemicals', 'Chemical Management'),
            ('chemical.delete', 'Delete chemicals', 'Chemical Management'),
            ('chemical.issue', 'Issue chemicals', 'Chemical Management'),
            ('chemical.manage', 'Manage chemicals', 'Chemical Management'),
            
            ('calibration.view', 'View calibrations', 'Calibration Management'),
            ('calibration.create', 'Create calibrations', 'Calibration Management'),
            ('calibration.edit', 'Edit calibrations', 'Calibration Management'),
            ('calibration.delete', 'Delete calibrations', 'Calibration Management'),
            
            ('report.view', 'View reports', 'Reporting'),
            ('report.generate', 'Generate reports', 'Reporting'),
            
            ('admin.dashboard', 'Access admin dashboard', 'Administration'),
            ('admin.settings', 'Manage settings', 'Administration'),
            ('admin.announcements', 'Manage announcements', 'Administration'),
        ]
        
        for perm_name, perm_desc, perm_category in default_permissions:
            existing_perm = Permission.query.filter_by(name=perm_name).first()
            if not existing_perm:
                permission = Permission(
                    name=perm_name,
                    description=perm_desc,
                    category=perm_category
                )
                db.session.add(permission)
                logger.info(f"Created permission: {perm_name}")
        
        db.session.commit()
        
        # Create default roles if they don't exist
        default_roles = [
            ('Administrator', 'Full system access with all permissions', True),
            ('Materials Manager', 'Can manage tools, chemicals, and users', True),
            ('Maintenance User', 'Basic access to view and checkout tools', True)
        ]
        
        for role_name, role_desc, is_system in default_roles:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                role = Role(
                    name=role_name,
                    description=role_desc,
                    is_system_role=is_system
                )
                db.session.add(role)
                logger.info(f"Created role: {role_name}")
        
        db.session.commit()
        
        # Assign all permissions to Administrator role
        admin_role = Role.query.filter_by(name='Administrator').first()
        if admin_role:
            # Clear existing permissions
            RolePermission.query.filter_by(role_id=admin_role.id).delete()
            
            # Add all permissions to admin role
            all_permissions = Permission.query.all()
            for permission in all_permissions:
                role_perm = RolePermission(role_id=admin_role.id, permission_id=permission.id)
                db.session.add(role_perm)
            
            logger.info(f"Assigned {len(all_permissions)} permissions to Administrator role")
        
        # Assign specific permissions to Materials Manager role
        materials_role = Role.query.filter_by(name='Materials Manager').first()
        if materials_role:
            # Clear existing permissions
            RolePermission.query.filter_by(role_id=materials_role.id).delete()
            
            # Add specific permissions
            materials_permissions = [
                'user.view', 'tool.view', 'tool.create', 'tool.edit', 'tool.delete', 
                'tool.checkout', 'tool.return', 'tool.manage',
                'chemical.view', 'chemical.create', 'chemical.edit', 'chemical.delete', 
                'chemical.issue', 'chemical.manage',
                'calibration.view', 'calibration.create', 'calibration.edit', 'calibration.delete',
                'report.view', 'report.generate'
            ]
            
            for perm_name in materials_permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission:
                    role_perm = RolePermission(role_id=materials_role.id, permission_id=permission.id)
                    db.session.add(role_perm)
            
            logger.info(f"Assigned {len(materials_permissions)} permissions to Materials Manager role")
        
        db.session.commit()
        
        # Assign Administrator role to admin user
        admin_user = User.query.filter_by(employee_number='ADMIN001').first()
        admin_role = Role.query.filter_by(name='Administrator').first()
        
        if admin_user and admin_role:
            # Clear existing roles
            UserRole.query.filter_by(user_id=admin_user.id).delete()
            
            # Assign Administrator role
            user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.session.add(user_role)
            
            logger.info("Assigned Administrator role to admin user")
        
        db.session.commit()
        logger.info("✓ RBAC system setup completed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up RBAC system: {e}")
        db.session.rollback()
        return False

def verify_admin_permissions():
    """Verify that the admin user has proper permissions."""
    try:
        admin_user = User.query.filter_by(employee_number='ADMIN001').first()
        
        if not admin_user:
            logger.error("Admin user not found!")
            return False
        
        logger.info(f"Admin user verification:")
        logger.info(f"  Name: {admin_user.name}")
        logger.info(f"  Employee Number: {admin_user.employee_number}")
        logger.info(f"  Department: {admin_user.department}")
        logger.info(f"  Is Admin: {admin_user.is_admin}")
        logger.info(f"  Is Active: {admin_user.is_active}")
        
        # Check roles
        roles = [ur.role for ur in admin_user.user_roles]
        logger.info(f"  Roles: {[r.name for r in roles]}")
        
        # Check permissions
        permissions = admin_user.get_permissions()
        logger.info(f"  Permissions: {len(permissions)} total")
        
        # Check specific permissions
        key_permissions = ['tool.manage', 'chemical.manage', 'user.edit']
        for perm in key_permissions:
            has_perm = admin_user.has_permission(perm)
            logger.info(f"    {perm}: {'✓' if has_perm else '✗'}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying admin permissions: {e}")
        return False

def main():
    """Main function to fix admin permissions."""
    logger.info("Starting admin permissions fix...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Fix admin user
            if not fix_admin_user():
                logger.error("Failed to fix admin user")
                return False
            
            # Setup RBAC system
            if not setup_rbac_system():
                logger.error("Failed to setup RBAC system")
                return False
            
            # Verify permissions
            if not verify_admin_permissions():
                logger.error("Failed to verify admin permissions")
                return False
            
            logger.info("✓ Admin permissions fix completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error in main: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
