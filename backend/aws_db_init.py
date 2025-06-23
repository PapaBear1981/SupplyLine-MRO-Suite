#!/usr/bin/env python3
"""
AWS Database Initialization Script for SupplyLine MRO Suite

This script initializes the database for AWS deployment with proper error handling,
migration support, and rollback capabilities.
"""

import os
import sys
import logging
import time
from datetime import datetime
from flask import Flask
from sqlalchemy import text, inspect
from models import db, User, Tool, Chemical, AuditLog
from config import Config
from utils.admin_init import create_secure_admin

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/db_init.log')
    ]
)
logger = logging.getLogger(__name__)


def wait_for_database(app, max_retries=30, retry_delay=5):
    """Wait for database to be available with retries"""
    logger.info("Waiting for database to be available...")
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Try to connect to the database
                db.engine.execute(text('SELECT 1'))
                logger.info("Database connection successful!")
                return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Database is not available.")
                return False
    
    return False


def check_database_exists(app):
    """Check if database tables already exist"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Check for key tables
            required_tables = ['users', 'tools', 'chemicals', 'audit_log']
            existing_tables = [table for table in required_tables if table in tables]
            
            logger.info(f"Found existing tables: {existing_tables}")
            return len(existing_tables) > 0, existing_tables
            
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return False, []


def create_database_tables(app):
    """Create all database tables"""
    try:
        with app.app_context():
            logger.info("Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False


def create_sample_data(app):
    """Create sample data for testing"""
    try:
        with app.app_context():
            logger.info("Creating sample data...")
            
            # Check if sample data already exists
            if Tool.query.first() or Chemical.query.first():
                logger.info("Sample data already exists, skipping...")
                return True
            
            # Create sample tools
            sample_tools = [
                Tool(
                    tool_number='TEST001',
                    serial_number='SN123456',
                    description='Test tool for error handling validation',
                    category='General',
                    location='N/A',
                    status='available'
                ),
                Tool(
                    tool_number='TOOL001',
                    serial_number='sdf45',
                    description='Test Tool',
                    category='General',
                    location='N/A',
                    status='available'
                )
            ]
            
            # Create sample chemicals
            sample_chemicals = [
                Chemical(
                    part_number='CHEM001',
                    lot_number='LOT123',
                    description='Test Chem',
                    manufacturer='Acme',
                    quantity=5,
                    unit='each',
                    expiration_date=datetime(2025, 7, 10),
                    status='available'
                )
            ]
            
            # Add sample data
            for tool in sample_tools:
                db.session.add(tool)
            
            for chemical in sample_chemicals:
                db.session.add(chemical)
            
            db.session.commit()
            logger.info("Sample data created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        db.session.rollback()
        return False


def run_migrations(app):
    """Run any pending database migrations"""
    try:
        with app.app_context():
            logger.info("Running database migrations...")
            
            # Import and run migrations
            try:
                from migrate_reorder_fields import migrate_database as migrate_reorder
                migrate_reorder()
                logger.info("Reorder fields migration completed")
            except Exception as e:
                logger.warning(f"Reorder fields migration failed (may not be needed): {str(e)}")
            
            try:
                from migrate_database_constraints import migrate_database as migrate_constraints
                migrate_constraints()
                logger.info("Database constraints migration completed")
            except Exception as e:
                logger.warning(f"Database constraints migration failed (may not be needed): {str(e)}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False


def initialize_aws_database():
    """Main function to initialize AWS database"""
    logger.info("Starting AWS database initialization...")
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize database
        db.init_app(app)
        
        # Wait for database to be available
        if not wait_for_database(app):
            logger.error("Database is not available. Exiting.")
            return False
        
        # Check if database already exists
        db_exists, existing_tables = check_database_exists(app)
        
        if db_exists:
            logger.info("Database tables already exist. Running migrations only...")
            success = run_migrations(app)
        else:
            logger.info("Database is empty. Creating tables and initial data...")
            
            # Create tables
            if not create_database_tables(app):
                return False
            
            # Create admin user
            with app.app_context():
                success, message, password = create_secure_admin()
                if success:
                    logger.info(f"Admin user creation: {message}")
                    if password:
                        logger.warning("=" * 60)
                        logger.warning("IMPORTANT: Generated admin password")
                        logger.warning(f"Username: ADMIN001")
                        logger.warning(f"Password: {password}")
                        logger.warning("Please change the password after first login!")
                        logger.warning("=" * 60)
                else:
                    logger.error(f"Admin user creation failed: {message}")
                    return False
            
            # Create sample data
            if not create_sample_data(app):
                logger.warning("Sample data creation failed, but continuing...")
            
            # Run migrations
            if not run_migrations(app):
                logger.warning("Migrations failed, but continuing...")
        
        logger.info("AWS database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"AWS database initialization failed: {str(e)}")
        return False


if __name__ == '__main__':
    success = initialize_aws_database()
    sys.exit(0 if success else 1)
