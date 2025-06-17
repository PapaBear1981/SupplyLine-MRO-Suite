#!/usr/bin/env python3
"""
Simple Cloud SQL Database Initialization Script
This script initializes the PostgreSQL database on Google Cloud SQL
with the required tables and initial admin user.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize Cloud SQL database with tables and admin user."""
    
    # Set environment variables for Cloud SQL connection
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DB_HOST'] = '/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db'
    os.environ['DB_USER'] = 'supplyline_user'
    os.environ['DB_NAME'] = 'supplyline'
    
    try:
        # Import after setting environment variables
        sys.path.append('/app')
        from app import create_app
        from models import db
        
        logger.info("Creating Flask app...")
        app = create_app()
        
        with app.app_context():
            logger.info("Testing database connection...")
            
            # Test basic connection
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            logger.info("✓ Database connection successful")
            
            # Create all tables
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("✓ Database tables created")
            
            # Create admin user
            logger.info("Creating admin user...")
            from utils.admin_init import create_secure_admin
            success, message, password = create_secure_admin()
            
            if success:
                logger.info(f"✓ Admin user created: {message}")
                if password:
                    logger.info(f"Generated admin password: {password}")
            else:
                logger.warning(f"Admin user creation: {message}")
            
            logger.info("✓ Database initialization completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
