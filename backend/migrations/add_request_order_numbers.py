"""
Add request_number and order_number columns for easier tracking.

This migration adds:
- request_number to user_requests table (format: REQ-00001)
- order_number to procurement_orders table (format: ORD-00001)

It also assigns numbers to existing records based on their creation order.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app import create_app
from models import ProcurementOrder, UserRequest, db


def add_number_columns():
    """Add request_number and order_number columns to the database."""
    app = create_app()

    with app.app_context():
        # Check if columns already exist
        inspector = db.inspect(db.engine)

        # Check user_requests table
        user_request_columns = [col["name"] for col in inspector.get_columns("user_requests")]
        if "request_number" not in user_request_columns:
            print("Adding request_number column to user_requests table...")
            db.session.execute(text("ALTER TABLE user_requests ADD COLUMN request_number VARCHAR(20)"))
            db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_requests_request_number ON user_requests(request_number)"))
            db.session.commit()
            print("  ✓ request_number column added")
        else:
            print("  request_number column already exists")

        # Check procurement_orders table
        order_columns = [col["name"] for col in inspector.get_columns("procurement_orders")]
        if "order_number" not in order_columns:
            print("Adding order_number column to procurement_orders table...")
            db.session.execute(text("ALTER TABLE procurement_orders ADD COLUMN order_number VARCHAR(20)"))
            db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_procurement_orders_order_number ON procurement_orders(order_number)"))
            db.session.commit()
            print("  ✓ order_number column added")
        else:
            print("  order_number column already exists")

        # Assign numbers to existing user requests
        print("\nAssigning request numbers to existing requests...")
        requests = UserRequest.query.filter(
            UserRequest.request_number.is_(None)
        ).order_by(UserRequest.created_at.asc()).all()

        if requests:
            # Get the highest existing request number
            max_req = db.session.execute(
                text("SELECT MAX(CAST(SUBSTR(request_number, 5) AS INTEGER)) FROM user_requests WHERE request_number IS NOT NULL")
            ).scalar() or 0

            for i, req in enumerate(requests, start=max_req + 1):
                req.request_number = f"REQ-{i:05d}"
                print(f"  Assigned {req.request_number} to request ID {req.id}")

            db.session.commit()
            print(f"  ✓ Assigned numbers to {len(requests)} requests")
        else:
            print("  No requests need numbering")

        # Assign numbers to existing procurement orders
        print("\nAssigning order numbers to existing orders...")
        orders = ProcurementOrder.query.filter(
            ProcurementOrder.order_number.is_(None)
        ).order_by(ProcurementOrder.created_at.asc()).all()

        if orders:
            # Get the highest existing order number
            max_ord = db.session.execute(
                text("SELECT MAX(CAST(SUBSTR(order_number, 5) AS INTEGER)) FROM procurement_orders WHERE order_number IS NOT NULL")
            ).scalar() or 0

            for i, order in enumerate(orders, start=max_ord + 1):
                order.order_number = f"ORD-{i:05d}"
                print(f"  Assigned {order.order_number} to order ID {order.id}")

            db.session.commit()
            print(f"  ✓ Assigned numbers to {len(orders)} orders")
        else:
            print("  No orders need numbering")

        print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    add_number_columns()
