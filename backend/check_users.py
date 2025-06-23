#!/usr/bin/env python3
"""
Check all users in the database for SupplyLine MRO Suite
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
    """Create Flask app for user check"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def check_users():
    """Check all users in the database"""
    app = create_app()

    with app.app_context():
        try:
            # Get all users
            users = User.query.all()

            logger.info(f"📊 Total users in database: {len(users)}")

            for user in users:
                logger.info(f"👤 User ID: {user.id}")
                logger.info(f"   Employee Number: {user.employee_number}")
                logger.info(f"   Name: {user.name}")
                logger.info(f"   Department: {user.department}")
                logger.info(f"   Email: {user.email}")
                logger.info(f"   Active: {user.is_active}")
                logger.info(f"   Admin: {user.is_admin}")
                logger.info(f"   Failed Login Attempts: {user.failed_login_attempts}")
                logger.info(f"   Last Failed Login: {user.last_failed_login}")
                logger.info(f"   Is Locked: {user.is_locked()}")
                if user.is_locked():
                    remaining = user.get_lockout_remaining_time()
                    logger.info(f"   Lockout Remaining: {remaining:.0f} seconds")
                logger.info(f"   Created: {user.created_at}")
                logger.info("   " + "="*50)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to check users: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    logger.info("👥 Checking all users in database...")

    if check_users():
        logger.info("✅ User check completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ User check failed!")
        sys.exit(1)
