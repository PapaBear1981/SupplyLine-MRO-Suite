#!/usr/bin/env python3
"""
Reset admin password for SupplyLine MRO Suite
This script will reset the admin password to a known value
"""

import os
import sys
import logging
from flask import Flask
from config import Config
from models import db, User
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for password reset"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def reset_admin_password():
    """Reset the admin password to a known value"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find the admin user
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            
            if not admin_user:
                logger.error("❌ Admin user ADMIN001 not found in database")
                return False
            
            logger.info(f"📋 Admin user found: ID={admin_user.id}, Employee Number={admin_user.employee_number}")
            logger.info(f"👤 Name: {admin_user.name}")
            logger.info(f"🏢 Department: {admin_user.department}")

            # Reset password to a known value
            new_password = "password123"
            logger.info(f"🔑 Setting new password: {new_password}")
            
            # Generate new password hash
            admin_user.password_hash = generate_password_hash(new_password)
            
            # Reset failed login attempts and unlock account
            admin_user.failed_login_attempts = 0
            admin_user.last_failed_login = None
            
            # Save changes
            db.session.commit()
            
            logger.info("✅ Admin password has been reset successfully!")
            logger.info(f"🔓 Failed login attempts reset: {admin_user.failed_login_attempts}")
            logger.info(f"🔑 New password hash: {admin_user.password_hash[:50]}...")
            
            # Verify the password works
            from werkzeug.security import check_password_hash
            verification = check_password_hash(admin_user.password_hash, new_password)
            logger.info(f"✅ Password verification: {verification}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reset admin password: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    logger.info("🔐 Starting admin password reset...")
    
    if reset_admin_password():
        logger.info("✅ Admin password reset completed successfully!")
        logger.info("🎯 You can now login with:")
        logger.info("   Employee Number: ADMIN001")
        logger.info("   Password: password123")
        sys.exit(0)
    else:
        logger.error("❌ Admin password reset failed!")
        sys.exit(1)
