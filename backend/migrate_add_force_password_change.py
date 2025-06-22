#!/usr/bin/env python3
"""
Migration script to add force_password_change column to users table
"""

import os
import sys
import logging
from flask import Flask
from models import db
from config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_force_password_change_column():
    """Add force_password_change column to users table if it doesn't exist"""
    try:
        # Check if column already exists
        result = db.engine.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='force_password_change'
        """)
        
        if result.fetchone():
            logger.info("Column 'force_password_change' already exists in users table")
            return True
        
        # Add the column
        logger.info("Adding 'force_password_change' column to users table...")
        db.engine.execute("""
            ALTER TABLE users 
            ADD COLUMN force_password_change BOOLEAN DEFAULT FALSE
        """)
        
        logger.info("Column 'force_password_change' added successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error adding force_password_change column: {str(e)}")
        return False


def main():
    """Run the migration"""
    try:
        # Get config from environment or use development
        config_name = os.environ.get('FLASK_ENV', 'development')
        
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config[config_name])
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            logger.info(f"Running migration with config: {config_name}")
            
            if add_force_password_change_column():
                logger.info("Migration completed successfully!")
                return True
            else:
                logger.error("Migration failed!")
                return False
                
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
