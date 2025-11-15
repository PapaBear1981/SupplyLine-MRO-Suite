"""
Migration: Add documentation_path field to procurement_orders table.

This migration adds a documentation_path field so we can store the path to
optional supporting documentation uploaded with procurement requests.
"""

import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app import create_app
from models import db

logger = logging.getLogger(__name__)


def run_migration() -> bool:
    """Add documentation_path column to procurement_orders table."""

    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)

        # Ensure table exists
        if "procurement_orders" not in inspector.get_table_names():
            logger.warning("procurement_orders table does not exist yet")
            return False

        columns = {column["name"] for column in inspector.get_columns("procurement_orders")}

        # Skip if column already present
        if "documentation_path" in columns:
            logger.info("documentation_path column already exists on procurement_orders")
            return True

        logger.info("Adding documentation_path column to procurement_orders table")

        with db.engine.connect() as conn:
            conn.execute(
                text(
                    "ALTER TABLE procurement_orders "
                    "ADD COLUMN documentation_path VARCHAR(500)"
                )
            )
            conn.commit()

        logger.info("Successfully added documentation_path column to procurement_orders table")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = run_migration()
    sys.exit(0 if success else 1)

