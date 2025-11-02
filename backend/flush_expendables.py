"""
Flush all expendables from the database to prepare for reseeding.
This script removes all Expendable records and their associated KitItem records.
"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Expendable
from models_kits import KitItem


def flush_expendables():
    """Remove all expendables and their kit items."""
    app = create_app()

    with app.app_context():
        print("🗑️  Flushing expendables from database...")

        # First, delete all KitItems that reference expendables
        kit_items_deleted = KitItem.query.filter_by(item_type="expendable").delete()
        print(f"   ✓ Deleted {kit_items_deleted} kit_items referencing expendables")

        # Then delete all Expendable records
        expendables_deleted = Expendable.query.delete()
        print(f"   ✓ Deleted {expendables_deleted} expendable records")

        # Commit the changes
        db.session.commit()
        print("✅ Expendables flushed successfully!")

        return kit_items_deleted, expendables_deleted

if __name__ == "__main__":
    flush_expendables()

