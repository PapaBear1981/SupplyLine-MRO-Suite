"""
Migration: Add needs_more_info field to procurement_orders table.

This migration adds a needs_more_info boolean field to track when
procurement orders need additional information from the requester.
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
    """Add needs_more_info column to procurement_orders table."""

    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)

        # Ensure table exists
        if "procurement_orders" not in inspector.get_table_names():
            logger.warning("procurement_orders table does not exist yet")
            return False

        columns = {column["name"] for column in inspector.get_columns("procurement_orders")}

        # Skip if column already present
        if "needs_more_info" in columns:
            logger.info("needs_more_info column already exists on procurement_orders")
            return True

        logger.info("Adding needs_more_info column to procurement_orders table")

        with db.engine.connect() as conn:
            conn.execute(
                text(
                    "ALTER TABLE procurement_orders "
                    "ADD COLUMN needs_more_info BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
            conn.commit()

        logger.info("Successfully added needs_more_info column to procurement_orders table")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = run_migration()
    sys.exit(0 if success else 1)
