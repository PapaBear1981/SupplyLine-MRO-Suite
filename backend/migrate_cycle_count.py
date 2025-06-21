#!/usr/bin/env python3
"""
Cycle Count Database Migration Script for SupplyLine MRO Suite

This script creates the cycle count database tables that are required for
the cycle count functionality.

Usage:
    python migrate_cycle_count.py [environment]

Where environment is one of: development, production (default: development)
"""

import os
import sys
import logging
from flask import Flask
from models import db
from models_cycle_count import (
    CycleCountSchedule, CycleCountBatch, CycleCountItem,
    CycleCountResult, CycleCountAdjustment
)
from config import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_cycle_count_tables(app):
    """Create cycle count database tables"""
    try:
        with app.app_context():
            logger.info("Creating cycle count database tables...")
            
            # Create the cycle count tables
            # This will only create tables that don't already exist
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'cycle_count_schedules',
                'cycle_count_batches',
                'cycle_count_items',
                'cycle_count_results',
                'cycle_count_adjustments'
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
            
            logger.info("All cycle count tables created successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error creating cycle count tables: {str(e)}")
        return False


def verify_cycle_count_functionality(app):
    """Verify that cycle count functionality is working"""
    try:
        with app.app_context():
            logger.info("Verifying cycle count functionality...")
            
            # Test basic queries
            schedules_count = CycleCountSchedule.query.count()
            batches_count = CycleCountBatch.query.count()
            items_count = CycleCountItem.query.count()
            results_count = CycleCountResult.query.count()
            adjustments_count = CycleCountAdjustment.query.count()
            
            logger.info(f"Current cycle count data:")
            logger.info(f"  Schedules: {schedules_count}")
            logger.info(f"  Batches: {batches_count}")
            logger.info(f"  Items: {items_count}")
            logger.info(f"  Results: {results_count}")
            logger.info(f"  Adjustments: {adjustments_count}")
            
            logger.info("Cycle count functionality verification completed!")
            return True
            
    except Exception as e:
        logger.error(f"Error verifying cycle count functionality: {str(e)}")
        return False


def main():
    """Main migration function"""
    # Get environment from command line argument
    env = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    if env not in config:
        logger.error(f"Invalid environment: {env}")
        logger.error(f"Valid environments: {list(config.keys())}")
        sys.exit(1)
    
    logger.info(f"Starting cycle count migration for environment: {env}")
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config[env])
        
        # Initialize database
        db.init_app(app)
        
        # Create cycle count tables
        if not create_cycle_count_tables(app):
            logger.error("Failed to create cycle count tables")
            sys.exit(1)
        
        # Verify functionality
        if not verify_cycle_count_functionality(app):
            logger.error("Failed to verify cycle count functionality")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("CYCLE COUNT MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("The following cycle count features are now available:")
        logger.info("- Cycle count schedule management")
        logger.info("- Count batch generation and tracking")
        logger.info("- Item counting and discrepancy management")
        logger.info("- Count result recording and adjustments")
        logger.info("- Advanced analytics and reporting")
        logger.info("=" * 60)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
