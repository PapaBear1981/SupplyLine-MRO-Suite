#!/usr/bin/env python3
"""
Database Migration Script for Mobile Warehouse/Kits System

This script creates all necessary database tables for the kits functionality:
- aircraft_types
- kits
- kit_boxes
- kit_items
- kit_expendables
- kit_issuances
- kit_transfers
- kit_reorder_requests
- kit_messages

Usage:
    python migrate_kits.py [environment]

Where environment is one of: development, production (default: development)
"""

import os
import sys
import logging
from flask import Flask
from models import db
from models_kits import (
    AircraftType, Kit, KitBox, KitItem, KitExpendable,
    KitIssuance, KitTransfer, KitReorderRequest, KitMessage
)
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_kit_tables(app):
    """Create all kit-related database tables"""
    try:
        with app.app_context():
            logger.info("Creating kit database tables...")
            
            # Create all tables (only creates missing ones)
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'aircraft_types',
                'kits',
                'kit_boxes',
                'kit_items',
                'kit_expendables',
                'kit_issuances',
                'kit_transfers',
                'kit_reorder_requests',
                'kit_messages'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    missing_tables.append(table)
                    logger.error(f"✗ Table '{table}' missing")
            
            if missing_tables:
                logger.error(f"Failed to create tables: {', '.join(missing_tables)}")
                return False
            
            logger.info("All kit tables created successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error creating kit tables: {str(e)}")
        return False


def create_indexes(app):
    """Create indexes for better query performance"""
    try:
        with app.app_context():
            logger.info("Creating indexes for kit tables...")
            
            # Get database connection
            connection = db.engine.connect()
            
            # Define indexes
            indexes = [
                # Aircraft types
                "CREATE INDEX IF NOT EXISTS idx_aircraft_types_active ON aircraft_types(is_active)",
                
                # Kits
                "CREATE INDEX IF NOT EXISTS idx_kits_aircraft_type ON kits(aircraft_type_id)",
                "CREATE INDEX IF NOT EXISTS idx_kits_status ON kits(status)",
                "CREATE INDEX IF NOT EXISTS idx_kits_created_by ON kits(created_by)",
                
                # Kit boxes
                "CREATE INDEX IF NOT EXISTS idx_kit_boxes_kit ON kit_boxes(kit_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_boxes_type ON kit_boxes(box_type)",
                
                # Kit items
                "CREATE INDEX IF NOT EXISTS idx_kit_items_kit ON kit_items(kit_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_items_box ON kit_items(box_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_items_type ON kit_items(item_type)",
                "CREATE INDEX IF NOT EXISTS idx_kit_items_status ON kit_items(status)",
                
                # Kit expendables
                "CREATE INDEX IF NOT EXISTS idx_kit_expendables_kit ON kit_expendables(kit_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_expendables_box ON kit_expendables(box_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_expendables_status ON kit_expendables(status)",
                
                # Kit issuances
                "CREATE INDEX IF NOT EXISTS idx_kit_issuances_kit ON kit_issuances(kit_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_issuances_issued_by ON kit_issuances(issued_by)",
                "CREATE INDEX IF NOT EXISTS idx_kit_issuances_date ON kit_issuances(issued_date)",
                
                # Kit transfers
                "CREATE INDEX IF NOT EXISTS idx_kit_transfers_from ON kit_transfers(from_location_type, from_location_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_transfers_to ON kit_transfers(to_location_type, to_location_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_transfers_status ON kit_transfers(status)",
                "CREATE INDEX IF NOT EXISTS idx_kit_transfers_date ON kit_transfers(transfer_date)",
                
                # Kit reorder requests
                "CREATE INDEX IF NOT EXISTS idx_kit_reorders_kit ON kit_reorder_requests(kit_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_reorders_status ON kit_reorder_requests(status)",
                "CREATE INDEX IF NOT EXISTS idx_kit_reorders_priority ON kit_reorder_requests(priority)",
                "CREATE INDEX IF NOT EXISTS idx_kit_reorders_requested_by ON kit_reorder_requests(requested_by)",
                
                # Kit messages
                "CREATE INDEX IF NOT EXISTS idx_kit_messages_kit ON kit_messages(kit_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_messages_sender ON kit_messages(sender_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_messages_recipient ON kit_messages(recipient_id)",
                "CREATE INDEX IF NOT EXISTS idx_kit_messages_read ON kit_messages(is_read)",
                "CREATE INDEX IF NOT EXISTS idx_kit_messages_request ON kit_messages(related_request_id)",
            ]
            
            # Create each index
            for index_sql in indexes:
                try:
                    connection.execute(db.text(index_sql))
                    logger.debug(f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    logger.warning(f"Index creation warning: {str(e)}")
            
            connection.close()
            logger.info("Indexes created successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        return False


def seed_default_aircraft_types(app):
    """Seed default aircraft types (Q400, RJ85, CL415)"""
    try:
        with app.app_context():
            logger.info("Seeding default aircraft types...")
            
            default_types = [
                {'name': 'Q400', 'description': 'Bombardier Q400 Turboprop'},
                {'name': 'RJ85', 'description': 'British Aerospace RJ85 Regional Jet'},
                {'name': 'CL415', 'description': 'Canadair CL-415 Water Bomber'}
            ]
            
            for type_data in default_types:
                # Check if already exists
                existing = AircraftType.query.filter_by(name=type_data['name']).first()
                if not existing:
                    aircraft_type = AircraftType(
                        name=type_data['name'],
                        description=type_data['description'],
                        is_active=True
                    )
                    db.session.add(aircraft_type)
                    logger.info(f"✓ Added aircraft type: {type_data['name']}")
                else:
                    logger.info(f"  Aircraft type already exists: {type_data['name']}")
            
            db.session.commit()
            logger.info("Default aircraft types seeded successfully!")
            return True
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding aircraft types: {str(e)}")
        return False


def verify_migration(app):
    """Verify that the migration was successful"""
    try:
        with app.app_context():
            logger.info("Verifying migration...")
            
            # Check table counts
            aircraft_count = AircraftType.query.count()
            logger.info(f"Aircraft types in database: {aircraft_count}")
            
            # Verify indexes exist
            inspector = db.inspect(db.engine)
            indexes = inspector.get_indexes('kits')
            logger.info(f"Indexes on 'kits' table: {len(indexes)}")
            
            logger.info("Migration verification complete!")
            return True
            
    except Exception as e:
        logger.error(f"Error verifying migration: {str(e)}")
        return False


def main():
    """Run the migration"""
    try:
        # Get config from environment or use development
        config_name = sys.argv[1] if len(sys.argv) > 1 else 'development'

        # Validate environment name
        valid_envs = ['development', 'production', 'testing']
        if config_name not in valid_envs:
            logger.error(f"Invalid environment: {config_name}")
            logger.error(f"Valid options: {', '.join(valid_envs)}")
            return False
        
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize database
        db.init_app(app)
        
        logger.info(f"Running kit migration with config: {config_name}")
        logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Run migration steps
        if not create_kit_tables(app):
            logger.error("Failed to create tables!")
            return False
        
        if not create_indexes(app):
            logger.warning("Failed to create some indexes (non-critical)")
        
        if not seed_default_aircraft_types(app):
            logger.warning("Failed to seed aircraft types (non-critical)")
        
        if not verify_migration(app):
            logger.warning("Migration verification had issues")
        
        logger.info("✓ Kit migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

