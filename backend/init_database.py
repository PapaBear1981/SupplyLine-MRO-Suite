#!/usr/bin/env python3
"""
Database initialization script for SupplyLine MRO Suite
This script will:
1. Create all database tables
2. Create the admin user
3. Verify the setup
"""

import os
import sys
import logging
from flask import Flask
from config import Config
from models import db, User
from utils.admin_init import create_secure_admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app for database initialization"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_database():
    """Initialize the database with tables and admin user"""
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables first (for clean slate)
            logger.info("Dropping all existing tables...")

            # For PostgreSQL, we need to handle foreign key constraints
            # Use raw SQL to drop all tables with CASCADE
            if 'postgresql' in str(db.engine.url):
                logger.info("Using PostgreSQL - dropping tables with CASCADE")
                with db.engine.begin() as conn:
                    # Get all table names
                    result = conn.execute(db.text("""
                        SELECT tablename FROM pg_tables
                        WHERE schemaname = 'public'
                    """))
                    tables = [row[0] for row in result]

                    # Drop each table with CASCADE
                    for table in tables:
                        try:
                            conn.execute(db.text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                            logger.info(f"Dropped table: {table}")
                        except Exception as e:
                            logger.warning(f"Could not drop table {table}: {e}")

                    # Transaction is automatically committed when exiting the context
            else:
                # For SQLite and other databases, use the normal drop_all
                db.drop_all()

            logger.info("All tables dropped successfully")
            
            # Create all tables
            logger.info("Creating all database tables...")
            db.create_all()
            logger.info("All database tables created successfully")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
            
            # Check if admin user already exists
            existing_admin = User.query.filter_by(employee_number='ADMIN001').first()
            if existing_admin:
                logger.info("Admin user already exists, deleting old admin user...")
                db.session.delete(existing_admin)
                db.session.commit()
            
            # Create admin user
            logger.info("Creating admin user...")
            success, message, password = create_secure_admin()
            
            if success:
                logger.info("✅ Admin user created successfully!")
                if password:
                    logger.warning("🔑 ADMIN PASSWORD GENERATED:")
                    logger.warning(f"🔑 Employee Number: ADMIN001")
                    logger.warning(f"🔑 Password: {password}")
                    logger.warning("🔑 SAVE THIS PASSWORD - IT WILL NOT BE SHOWN AGAIN!")
                else:
                    logger.info("Admin user created with password from environment variable")
            else:
                logger.error(f"❌ Failed to create admin user: {message}")
                return False
            
            # Verify admin user was created
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            if admin_user:
                logger.info(f"✅ Admin user verified: ID={admin_user.id}, Employee Number={admin_user.employee_number}")
            else:
                logger.error("❌ Admin user verification failed - user not found in database")
                return False
            
            # Show database statistics
            user_count = User.query.count()
            logger.info(f"📊 Database statistics: {user_count} users total")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}", exc_info=True)
            return False

if __name__ == "__main__":
    logger.info("🚀 Starting database initialization...")
    
    if init_database():
        logger.info("✅ Database initialization completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Database initialization failed!")
        sys.exit(1)
