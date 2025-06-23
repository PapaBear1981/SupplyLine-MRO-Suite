#!/usr/bin/env python3
"""
Admin account unlock script for SupplyLine MRO Suite
This script will unlock the admin account if it's locked due to failed login attempts
"""

import os
import sys
import logging
from flask import Flask
from config import Config
from models import db, User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for admin unlock"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def unlock_admin():
    """Unlock the admin account"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find the admin user
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            
            if not admin_user:
                logger.error("❌ Admin user ADMIN001 not found in database")
                return False
            
            logger.info(f"📋 Admin user found: ID={admin_user.id}, Employee Number={admin_user.employee_number}")
            
            # Check current lockout status
            if admin_user.is_locked():
                remaining_time = admin_user.get_lockout_remaining_time()
                logger.info(f"🔒 Admin account is currently locked for {remaining_time:.0f} more seconds")
                
                # Unlock the account
                admin_user.unlock_account()
                db.session.commit()
                
                logger.info("🔓 Admin account has been unlocked successfully!")
                logger.info(f"✅ Failed login attempts reset: {admin_user.failed_login_attempts}")
                
            else:
                logger.info("✅ Admin account is not locked")
                logger.info(f"📊 Current failed login attempts: {admin_user.failed_login_attempts}")
                
                # Reset failed attempts anyway for good measure
                if admin_user.failed_login_attempts > 0:
                    admin_user.reset_failed_login_attempts()
                    db.session.commit()
                    logger.info("🔄 Reset failed login attempts to 0")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unlock admin account: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    logger.info("🔓 Starting admin account unlock...")
    
    if unlock_admin():
        logger.info("✅ Admin account unlock completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Admin account unlock failed!")
        sys.exit(1)
