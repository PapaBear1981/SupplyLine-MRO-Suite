"""Create request_alerts table for notifying users when requested items are received."""

import os
import sys

from sqlalchemy import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import RequestAlert, db


def migrate():
    """Create request_alerts table if it does not already exist."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())

        if RequestAlert.__tablename__ not in tables:
            print("Creating request_alerts table...")
            RequestAlert.__table__.create(db.engine)
            print(f"Created table: {RequestAlert.__tablename__}")
        else:
            print("request_alerts table already exists.")


if __name__ == "__main__":
    migrate()
