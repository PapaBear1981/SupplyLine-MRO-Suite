"""
Clean up old user request orders from the database.

This script removes ProcurementOrder records that were created as user requests,
while preserving orders that are tied to kits or chemicals.

Orders to KEEP:
- Orders with kit_id set (kit-related orders)
- Orders with reference_type containing 'chemical' or 'reorder'
- Orders with order_type = 'kit'

Orders to DELETE:
- All other orders (user-submitted requests)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import and_, or_

from app import create_app
from models import AuditLog, ProcurementOrder, ProcurementOrderMessage, db


def cleanup_old_request_orders():
    """Remove old user request orders while preserving kit and chemical orders."""
    app = create_app()

    with app.app_context():
        # First, let's see what we have
        total_orders = ProcurementOrder.query.count()
        print(f"Total orders in database: {total_orders}")

        # Count orders by type
        kit_orders = ProcurementOrder.query.filter(ProcurementOrder.kit_id.isnot(None)).count()
        print(f"Kit-related orders (have kit_id): {kit_orders}")

        chemical_orders = ProcurementOrder.query.filter(
            ProcurementOrder.reference_type.ilike("%chemical%")
        ).count()
        print(f"Chemical-related orders (reference_type contains 'chemical'): {chemical_orders}")

        reorder_orders = ProcurementOrder.query.filter(
            ProcurementOrder.reference_type.ilike("%reorder%")
        ).count()
        print(f"Reorder-related orders (reference_type contains 'reorder'): {reorder_orders}")

        kit_type_orders = ProcurementOrder.query.filter(
            ProcurementOrder.order_type == "kit"
        ).count()
        print(f"Kit type orders (order_type = 'kit'): {kit_type_orders}")

        # Find orders to DELETE (user requests - NOT kit or chemical related)
        # Keep orders if:
        # - kit_id is not null (kit order)
        # - OR order_type = 'chemical' (chemical orders)
        # - OR order_type = 'kit'
        # - OR reference_type contains 'chemical' or 'reorder'
        orders_to_delete = ProcurementOrder.query.filter(
            and_(
                ProcurementOrder.kit_id.is_(None),
                ProcurementOrder.order_type != "chemical",
                ProcurementOrder.order_type != "kit",
                or_(
                    ProcurementOrder.reference_type.is_(None),
                    and_(
                        ~ProcurementOrder.reference_type.ilike("%chemical%"),
                        ~ProcurementOrder.reference_type.ilike("%reorder%"),
                    ),
                ),
            )
        ).all()

        count_to_delete = len(orders_to_delete)
        print(f"\nOrders to DELETE (user requests): {count_to_delete}")

        if count_to_delete == 0:
            print("No user request orders to clean up.")
            return

        # Show some details about what will be deleted
        print("\nSample of orders to be deleted:")
        for order in orders_to_delete[:5]:
            print(f"  - ID: {order.id}, Title: {order.title}, Type: {order.order_type}, "
                  f"Kit ID: {order.kit_id}, Ref Type: {order.reference_type}")

        if count_to_delete > 5:
            print(f"  ... and {count_to_delete - 5} more")

        # Confirm before deletion
        print(f"\n⚠️  WARNING: This will permanently delete {count_to_delete} orders and their messages.")
        print("Orders tied to kits or chemicals will be preserved.")
        response = input("Do you want to proceed? (yes/no): ").strip().lower()

        if response != "yes":
            print("Cleanup cancelled.")
            return

        # Delete the orders (messages will be cascade-deleted)
        deleted_count = 0
        for order in orders_to_delete:
            # Count messages for this order
            message_count = order.messages.count() if order.messages else 0
            db.session.delete(order)
            deleted_count += 1

        # Log the cleanup action
        audit = AuditLog(
            action_type="CLEANUP_OLD_REQUESTS",
            action_details=f"Deleted {deleted_count} old user request orders from the database",
        )
        db.session.add(audit)

        db.session.commit()

        print(f"\n✅ Successfully deleted {deleted_count} old user request orders.")
        print("Kit and chemical orders have been preserved.")

        # Verify final count
        remaining_orders = ProcurementOrder.query.count()
        print(f"Remaining orders in database: {remaining_orders}")


if __name__ == "__main__":
    cleanup_old_request_orders()
