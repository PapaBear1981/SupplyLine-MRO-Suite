#!/usr/bin/env python3
"""
Verify admin password for SupplyLine MRO Suite
"""

import os
import sys
import logging
from flask import Flask
from config import Config
from models import db, User
from werkzeug.security import check_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for password verification"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def verify_password():
    """Verify the admin password"""
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
            logger.info(f"📧 Email: {admin_user.email}")
            logger.info(f"🔒 Password Hash: {admin_user.password_hash[:50]}...")
            
            # Test the password from environment variable
            test_password = os.getenv('INITIAL_ADMIN_PASSWORD', 'Freedom2025!')
            logger.info(f"🔑 Testing password: {test_password}")
            
            # Check if password matches
            password_correct = check_password_hash(admin_user.password_hash, test_password)
            logger.info(f"✅ Password verification result: {password_correct}")
            
            # Also test some common variations
            test_passwords = [
                'Freedom2025!',
                'freedom2025!',
                'FREEDOM2025!',
                'Freedom2025',
                'admin',
                'password',
                'Admin123!',
                'admin123'
            ]
            
            logger.info("🔍 Testing common password variations:")
            for pwd in test_passwords:
                result = check_password_hash(admin_user.password_hash, pwd)
                logger.info(f"   '{pwd}': {result}")
                if result:
                    logger.info(f"🎯 CORRECT PASSWORD FOUND: '{pwd}'")
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to verify password: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    logger.info("🔐 Starting password verification...")
    
    if verify_password():
        logger.info("✅ Password verification completed!")
        sys.exit(0)
    else:
        logger.error("❌ Password verification failed!")
        sys.exit(1)
