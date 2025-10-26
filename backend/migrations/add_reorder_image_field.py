"""
Migration to add image_path field to kit_reorder_requests table
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
    """Add image_path column to kit_reorder_requests table"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if kit_reorder_requests table exists
        if 'kit_reorder_requests' not in inspector.get_table_names():
            logger.warning("kit_reorder_requests table does not exist yet")
            return False
        
        # Get existing columns
        columns = {column['name'] for column in inspector.get_columns('kit_reorder_requests')}
        
        # Add image_path column if it doesn't exist
        if 'image_path' not in columns:
            logger.info("Adding image_path column to kit_reorder_requests table")
            
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE kit_reorder_requests ADD COLUMN image_path VARCHAR(500)"
                ))
                conn.commit()
            
            logger.info("Successfully added image_path column")
            return True
        else:
            logger.info("image_path column already exists")
            return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    success = run_migration()
    sys.exit(0 if success else 1)

