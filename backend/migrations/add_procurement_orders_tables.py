"""Create procurement order management tables."""

import os
import sys

from sqlalchemy import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import ProcurementOrder, ProcurementOrderMessage, db


def migrate():
    """Create procurement order tables if they do not already exist."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())

        created_tables = []

        if ProcurementOrder.__tablename__ not in tables:
            print("Creating procurement_orders table...")
            ProcurementOrder.__table__.create(db.engine)
            created_tables.append(ProcurementOrder.__tablename__)
        else:
            print("procurement_orders table already exists.")

        if ProcurementOrderMessage.__tablename__ not in tables:
            print("Creating procurement_order_messages table...")
            ProcurementOrderMessage.__table__.create(db.engine)
            created_tables.append(ProcurementOrderMessage.__tablename__)
        else:
            print("procurement_order_messages table already exists.")

        if created_tables:
            print("Created tables: " + ", ".join(created_tables))
        else:
            print("No new tables created; all procurement order tables already exist.")


if __name__ == "__main__":
    migrate()
