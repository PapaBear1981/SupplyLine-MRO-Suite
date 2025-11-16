"""
Migration to add contact information fields to warehouses table
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app import create_app
from models import db

logger = logging.getLogger(__name__)


def run_migration():
    """Add contact_person, contact_phone, and contact_email columns to warehouses table"""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)

        # Check if warehouses table exists
        if 'warehouses' not in inspector.get_table_names():
            logger.warning("warehouses table does not exist yet")
            return False

        # Get existing columns
        columns = {column['name'] for column in inspector.get_columns('warehouses')}

        # Add contact fields if they don't exist
        fields_added = False

        if 'contact_person' not in columns:
            logger.info("Adding contact_person column to warehouses table")

            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE warehouses ADD COLUMN contact_person VARCHAR(200)"
                ))
                conn.commit()

            logger.info("Successfully added contact_person column")
            fields_added = True
        else:
            logger.info("contact_person column already exists")

        if 'contact_phone' not in columns:
            logger.info("Adding contact_phone column to warehouses table")

            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE warehouses ADD COLUMN contact_phone VARCHAR(50)"
                ))
                conn.commit()

            logger.info("Successfully added contact_phone column")
            fields_added = True
        else:
            logger.info("contact_phone column already exists")

        if 'contact_email' not in columns:
            logger.info("Adding contact_email column to warehouses table")

            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE warehouses ADD COLUMN contact_email VARCHAR(200)"
                ))
                conn.commit()

            logger.info("Successfully added contact_email column")
            fields_added = True
        else:
            logger.info("contact_email column already exists")

        if fields_added:
            logger.info("Successfully added all contact fields to warehouses table")
        else:
            logger.info("All contact fields already exist in warehouses table")

        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    success = run_migration()
    sys.exit(0 if success else 1)
