#!/usr/bin/env python3
"""
Calibration Database Migration Script for SupplyLine MRO Suite

This script creates the calibration-related database tables that were added in v3.5.0.
Run this script to add calibration functionality to existing installations.

Usage:
    python migrate_calibration.py [environment]

Where environment is one of: development, production (default: development)
"""

import os
import sys
import logging
from flask import Flask
from models import db, ToolCalibration, CalibrationStandard, ToolCalibrationStandard
from config import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_calibration_tables(app):
    """Create calibration-related database tables"""
    try:
        with app.app_context():
            logger.info("Creating calibration database tables...")
            
            # Create the calibration tables
            # This will only create tables that don't already exist
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'tool_calibrations',
                'calibration_standards', 
                'tool_calibration_standards'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    missing_tables.append(table)
                    logger.error(f"✗ Table '{table}' missing")
            
            if missing_tables:
                logger.error(f"Migration failed - missing tables: {missing_tables}")
                return False
            
            logger.info("All calibration tables created successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error creating calibration tables: {str(e)}")
        return False


def verify_calibration_functionality(app):
    """Verify that calibration functionality is working"""
    try:
        with app.app_context():
            logger.info("Verifying calibration functionality...")
            
            # Test basic queries
            calibration_count = ToolCalibration.query.count()
            standards_count = CalibrationStandard.query.count()
            
            logger.info(f"Current calibration records: {calibration_count}")
            logger.info(f"Current calibration standards: {standards_count}")
            
            logger.info("Calibration functionality verification completed!")
            return True
            
    except Exception as e:
        logger.error(f"Error verifying calibration functionality: {str(e)}")
        return False


def main():
    """Main migration function"""
    # Get environment from command line argument
    env = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    if env not in config:
        logger.error(f"Invalid environment: {env}")
        logger.error(f"Valid environments: {list(config.keys())}")
        sys.exit(1)
    
    logger.info(f"Starting calibration migration for environment: {env}")
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config[env])
        
        # Initialize database
        db.init_app(app)
        
        # Create calibration tables
        if not create_calibration_tables(app):
            logger.error("Failed to create calibration tables")
            sys.exit(1)
        
        # Verify functionality
        if not verify_calibration_functionality(app):
            logger.error("Failed to verify calibration functionality")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("CALIBRATION MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("The following calibration features are now available:")
        logger.info("- Tool calibration tracking")
        logger.info("- Calibration standards management")
        logger.info("- Calibration history and reporting")
        logger.info("- Due date tracking and alerts")
        logger.info("=" * 60)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
