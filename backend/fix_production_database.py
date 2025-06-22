#!/usr/bin/env python3
"""
Production Database Fix Script for SupplyLine MRO Suite

This script addresses common database issues in production deployments:
1. Creates missing calibration tables
2. Ensures admin user has proper is_admin flag
3. Verifies all required tables exist
4. Fixes common database schema issues

Usage:
    python fix_production_database.py [environment]

Where environment is one of: development, production (default: production)
"""

import os
import sys
import logging
from flask import Flask
from models import db, User, Tool, ToolCalibration, CalibrationStandard, ToolCalibrationStandard
from models_cycle_count import (
    CycleCountSchedule, CycleCountBatch, CycleCountItem,
    CycleCountResult, CycleCountAdjustment
)
from config import config
from werkzeug.security import generate_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_and_create_tables(app):
    """Check for missing tables and create them"""
    try:
        with app.app_context():
            logger.info("Checking database tables...")
            
            # Get current tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"Existing tables: {existing_tables}")
            
            # Create all tables (only creates missing ones)
            db.create_all()
            
            # Check again after creation
            inspector = db.inspect(db.engine)
            existing_tables_after = inspector.get_table_names()
            
            required_tables = [
                'users', 'tools', 'checkouts', 'chemicals', 'audit_log',
                'tool_calibrations', 'calibration_standards', 'tool_calibration_standards',
                'cycle_count_schedules', 'cycle_count_batches', 'cycle_count_items',
                'cycle_count_results', 'cycle_count_adjustments'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables_after:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    missing_tables.append(table)
                    logger.error(f"✗ Table '{table}' missing")
            
            if missing_tables:
                logger.error(f"Still missing tables: {missing_tables}")
                return False
            
            logger.info("All required tables exist!")
            return True
            
    except Exception as e:
        logger.error(f"Error checking/creating tables: {str(e)}")
        return False


def fix_admin_user(app):
    """Ensure admin user has proper is_admin flag"""
    try:
        with app.app_context():
            logger.info("Checking admin user configuration...")
            
            # Find ADMIN001 user
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            
            if not admin_user:
                logger.warning("ADMIN001 user not found, creating...")
                admin_user = User(
                    name='System Administrator',
                    employee_number='ADMIN001',
                    department='Administration',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Created ADMIN001 user with admin privileges")
            else:
                # Check if is_admin is properly set
                if not admin_user.is_admin:
                    logger.warning("ADMIN001 user exists but is_admin is False, fixing...")
                    admin_user.is_admin = True
                    db.session.commit()
                    logger.info("Fixed ADMIN001 user admin privileges")
                else:
                    logger.info("✓ ADMIN001 user has proper admin privileges")
                
                # Also ensure department is set correctly for fallback logic
                if admin_user.department not in ['Administration', 'IT']:
                    logger.warning(f"ADMIN001 department is '{admin_user.department}', updating to 'Administration'")
                    admin_user.department = 'Administration'
                    db.session.commit()
                    logger.info("Updated ADMIN001 department to 'Administration'")
            
            return True
            
    except Exception as e:
        logger.error(f"Error fixing admin user: {str(e)}")
        return False


def verify_database_functionality(app):
    """Verify basic database functionality"""
    try:
        with app.app_context():
            logger.info("Verifying database functionality...")
            
            # Test basic queries
            user_count = User.query.count()
            tool_count = Tool.query.count()
            calibration_count = ToolCalibration.query.count()
            standards_count = CalibrationStandard.query.count()
            cycle_schedules_count = CycleCountSchedule.query.count()
            cycle_batches_count = CycleCountBatch.query.count()

            logger.info(f"Database statistics:")
            logger.info(f"  Users: {user_count}")
            logger.info(f"  Tools: {tool_count}")
            logger.info(f"  Calibration records: {calibration_count}")
            logger.info(f"  Calibration standards: {standards_count}")
            logger.info(f"  Cycle count schedules: {cycle_schedules_count}")
            logger.info(f"  Cycle count batches: {cycle_batches_count}")
            
            # Test admin user
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            if admin_user:
                logger.info(f"  Admin user: {admin_user.name} (is_admin: {admin_user.is_admin}, department: {admin_user.department})")
            else:
                logger.error("  Admin user not found!")
                return False
            
            logger.info("Database functionality verification completed!")
            return True
            
    except Exception as e:
        logger.error(f"Error verifying database functionality: {str(e)}")
        return False


def main():
    """Main fix function"""
    # Get environment from command line argument
    env = sys.argv[1] if len(sys.argv) > 1 else 'production'
    
    if env not in config:
        logger.error(f"Invalid environment: {env}")
        logger.error(f"Valid environments: {list(config.keys())}")
        sys.exit(1)
    
    logger.info(f"Starting database fix for environment: {env}")
    logger.info("=" * 60)
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config[env])
        
        # Initialize database
        db.init_app(app)
        
        # Step 1: Check and create missing tables
        logger.info("STEP 1: Checking and creating missing tables...")
        if not check_and_create_tables(app):
            logger.error("Failed to create required tables")
            sys.exit(1)
        
        # Step 2: Fix admin user
        logger.info("STEP 2: Fixing admin user configuration...")
        if not fix_admin_user(app):
            logger.error("Failed to fix admin user")
            sys.exit(1)
        
        # Step 3: Verify functionality
        logger.info("STEP 3: Verifying database functionality...")
        if not verify_database_functionality(app):
            logger.error("Database functionality verification failed")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("DATABASE FIX COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("Fixed issues:")
        logger.info("✓ All required database tables created (including calibration and cycle count)")
        logger.info("✓ Admin user (ADMIN001) configured properly")
        logger.info("✓ Database functionality verified")
        logger.info("=" * 60)
        logger.info("You can now restart the application to apply the fixes.")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Database fix failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
