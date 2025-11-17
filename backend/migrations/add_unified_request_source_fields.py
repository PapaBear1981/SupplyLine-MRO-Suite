"""Add source tracking fields to request_items for unified request system.

This migration adds fields to track the origin of request items:
- source_type: manual, chemical_reorder, or kit_reorder
- chemical_id: FK to chemicals table for chemical reorders
- kit_id: ID of kit for kit reorders
- kit_reorder_request_id: Reference to KitReorderRequest
"""

import os
import sys

from sqlalchemy import inspect, text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db


def migrate():
    """Add source tracking columns to request_items table."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)

        # Check if request_items table exists
        tables = set(inspector.get_table_names())
        if "request_items" not in tables:
            print("request_items table does not exist. Please run add_multi_item_request_tables migration first.")
            return

        # Get existing columns
        columns = {col["name"] for col in inspector.get_columns("request_items")}

        added_columns = []

        # Add source_type column
        if "source_type" not in columns:
            print("Adding source_type column...")
            db.session.execute(
                text("ALTER TABLE request_items ADD COLUMN source_type VARCHAR(50) NOT NULL DEFAULT 'manual'")
            )
            added_columns.append("source_type")
        else:
            print("source_type column already exists.")

        # Add chemical_id column
        if "chemical_id" not in columns:
            print("Adding chemical_id column...")
            db.session.execute(
                text("ALTER TABLE request_items ADD COLUMN chemical_id INTEGER NULL")
            )
            # Add foreign key constraint
            db.session.execute(
                text("CREATE INDEX IF NOT EXISTS idx_request_items_chemical_id ON request_items(chemical_id)")
            )
            added_columns.append("chemical_id")
        else:
            print("chemical_id column already exists.")

        # Add kit_id column
        if "kit_id" not in columns:
            print("Adding kit_id column...")
            db.session.execute(
                text("ALTER TABLE request_items ADD COLUMN kit_id INTEGER NULL")
            )
            db.session.execute(
                text("CREATE INDEX IF NOT EXISTS idx_request_items_kit_id ON request_items(kit_id)")
            )
            added_columns.append("kit_id")
        else:
            print("kit_id column already exists.")

        # Add kit_reorder_request_id column
        if "kit_reorder_request_id" not in columns:
            print("Adding kit_reorder_request_id column...")
            db.session.execute(
                text("ALTER TABLE request_items ADD COLUMN kit_reorder_request_id INTEGER NULL")
            )
            db.session.execute(
                text("CREATE INDEX IF NOT EXISTS idx_request_items_kit_reorder_request_id ON request_items(kit_reorder_request_id)")
            )
            added_columns.append("kit_reorder_request_id")
        else:
            print("kit_reorder_request_id column already exists.")

        db.session.commit()

        if added_columns:
            print(f"Added columns: {', '.join(added_columns)}")
        else:
            print("No new columns added; all source tracking fields already exist.")


if __name__ == "__main__":
    migrate()
