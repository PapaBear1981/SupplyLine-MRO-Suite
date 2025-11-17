"""Create multi-item user request tables for supporting multiple items per request."""

import os
import sys

from sqlalchemy import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import RequestItem, UserRequest, UserRequestMessage, db


def migrate():
    """Create user request tables if they do not already exist."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())

        created_tables = []

        if UserRequest.__tablename__ not in tables:
            print("Creating user_requests table...")
            UserRequest.__table__.create(db.engine)
            created_tables.append(UserRequest.__tablename__)
        else:
            print("user_requests table already exists.")

        if RequestItem.__tablename__ not in tables:
            print("Creating request_items table...")
            RequestItem.__table__.create(db.engine)
            created_tables.append(RequestItem.__tablename__)
        else:
            print("request_items table already exists.")

        if UserRequestMessage.__tablename__ not in tables:
            print("Creating user_request_messages table...")
            UserRequestMessage.__table__.create(db.engine)
            created_tables.append(UserRequestMessage.__tablename__)
        else:
            print("user_request_messages table already exists.")

        if created_tables:
            print("Created tables: " + ", ".join(created_tables))
        else:
            print("No new tables created; all multi-item request tables already exist.")


if __name__ == "__main__":
    migrate()
