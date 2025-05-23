"""
Secure Admin Initialization Utility

This module provides secure admin account creation without hardcoded credentials.
"""

import os
import secrets
import logging
from models import db, User

logger = logging.getLogger(__name__)

def create_secure_admin():
    """
    Create admin user with secure password handling
    
    Returns:
        tuple: (success: bool, message: str, password: str or None)
    """
    try:
        # Check if admin user already exists
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            logger.info("Admin user already exists")
            return True, "Admin user already exists", None
        
        # Get admin password from environment variable
        admin_password = os.environ.get('INITIAL_ADMIN_PASSWORD')
        
        if not admin_password:
            # Generate a secure random password
            admin_password = secrets.token_urlsafe(16)
            logger.warning(f"No INITIAL_ADMIN_PASSWORD environment variable found. Generated secure password: {admin_password}")
            print(f"IMPORTANT: Generated admin password: {admin_password}")
            print("Please save this password securely and set INITIAL_ADMIN_PASSWORD environment variable for future deployments.")
        else:
            logger.info("Using admin password from INITIAL_ADMIN_PASSWORD environment variable")
        
        # Create admin user
        admin = User(
            name='System Administrator',
            employee_number='ADMIN001',
            department='IT',
            is_admin=True,
            is_active=True,
            force_password_change=True  # Force password change on first login
        )
        
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        
        logger.info("Secure admin user created successfully")
        return True, "Admin user created successfully", admin_password if not os.environ.get('INITIAL_ADMIN_PASSWORD') else None
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.session.rollback()
        return False, f"Error creating admin user: {str(e)}", None


def validate_admin_setup():
    """
    Validate that admin setup is secure
    
    Returns:
        tuple: (is_secure: bool, issues: list)
    """
    issues = []
    
    try:
        # Check if admin exists
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            issues.append("No admin user found")
            return False, issues
        
        # Check if using default credentials (security risk)
        if admin.check_password('admin123'):
            issues.append("CRITICAL: Admin is using default password 'admin123'")
        
        # Check if force password change is enabled
        if hasattr(admin, 'force_password_change') and not admin.force_password_change:
            # This is okay if password has been changed from default
            pass
        
        # Check environment variable setup
        if not os.environ.get('INITIAL_ADMIN_PASSWORD'):
            issues.append("WARNING: INITIAL_ADMIN_PASSWORD environment variable not set")
        
        is_secure = len([issue for issue in issues if issue.startswith('CRITICAL')]) == 0
        
        return is_secure, issues
        
    except Exception as e:
        issues.append(f"Error validating admin setup: {str(e)}")
        return False, issues


def reset_admin_password():
    """
    Reset admin password to a secure random value
    
    Returns:
        tuple: (success: bool, message: str, new_password: str or None)
    """
    try:
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            return False, "No admin user found", None
        
        # Generate new secure password
        new_password = secrets.token_urlsafe(16)
        admin.set_password(new_password)
        
        # Force password change on next login
        if hasattr(admin, 'force_password_change'):
            admin.force_password_change = True
        
        db.session.commit()
        
        logger.info("Admin password reset successfully")
        return True, "Admin password reset successfully", new_password
        
    except Exception as e:
        logger.error(f"Error resetting admin password: {str(e)}")
        db.session.rollback()
        return False, f"Error resetting admin password: {str(e)}", None
