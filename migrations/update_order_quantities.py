#!/usr/bin/env python3
"""
Update existing procurement orders with quantity data from their associated chemicals.
"""
import os
import sys
import sqlite3

def get_db_path():
    """Get the database path, checking both local and Docker environments."""
    # Check if running in Docker (volume mounted at /database)
    docker_db_path = "/database/tools.db"
    if os.path.exists(docker_db_path):
        return docker_db_path

    # Local development path
    local_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "tools.db")
    if os.path.exists(local_db_path):
        return local_db_path

    raise FileNotFoundError("Database file not found in expected locations")

def update_order_quantities():
    """Update procurement orders with quantity data from chemicals."""
    db_path = get_db_path()
    print(f"Using database: {db_path}\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all chemical orders without quantity
        cursor.execute("""
            SELECT id, title, part_number, status
            FROM procurement_orders
            WHERE order_type = 'chemical' AND quantity IS NULL
        """)
        orders = cursor.fetchall()

        print(f"Found {len(orders)} chemical orders without quantity data\n")

        updated_count = 0
        for order_id, title, part_number, status in orders:
            print(f"Processing Order ID {order_id}: {title}")
            print(f"  Part Number: {part_number}")

            # Try to find the chemical by part number
            cursor.execute("""
                SELECT unit, requested_quantity
                FROM chemicals
                WHERE part_number = ?
                LIMIT 1
            """, (part_number,))
            chemical = cursor.fetchone()

            if chemical:
                unit, requested_quantity = chemical

                # Use requested_quantity if available, otherwise use a default based on status
                if requested_quantity:
                    quantity = requested_quantity
                    print(f"  Found requested quantity: {quantity} {unit}")
                else:
                    # Default quantities based on order status
                    if status in ['received', 'closed']:
                        quantity = 5  # Assume completed orders were for 5 units
                    else:
                        quantity = 3  # Assume pending orders are for 3 units
                    print(f"  No requested quantity found, using default: {quantity} {unit}")

                # Update the order
                cursor.execute("""
                    UPDATE procurement_orders
                    SET quantity = ?, unit = ?
                    WHERE id = ?
                """, (quantity, unit, order_id))

                updated_count += 1
                print(f"  ✓ Updated with {quantity} {unit}")
            else:
                print(f"  ⚠ Warning: Could not find chemical with part number {part_number}")

            print()

        if updated_count > 0:
            conn.commit()
            print(f"✓ Successfully updated {updated_count} orders")
        else:
            print("No orders were updated")

        # Verify the updates
        print("\n--- Verification ---")
        cursor.execute("SELECT COUNT(*) FROM procurement_orders WHERE order_type = 'chemical'")
        total_count = cursor.fetchone()[0]
        print(f"Total chemical orders: {total_count}")

        cursor.execute("SELECT COUNT(*) FROM procurement_orders WHERE order_type = 'chemical' AND quantity IS NOT NULL")
        with_qty_count = cursor.fetchone()[0]
        print(f"Orders with quantity: {with_qty_count}")

        cursor.execute("SELECT COUNT(*) FROM procurement_orders WHERE order_type = 'chemical' AND quantity IS NULL")
        without_qty_count = cursor.fetchone()[0]
        print(f"Orders without quantity: {without_qty_count}")

        if with_qty_count > 0:
            print("\nOrders with quantity:")
            cursor.execute("""
                SELECT part_number, quantity, unit
                FROM procurement_orders
                WHERE order_type = 'chemical' AND quantity IS NOT NULL
            """)
            for part_number, quantity, unit in cursor.fetchall():
                print(f"  - {part_number}: {quantity} {unit}")

    finally:
        conn.close()

if __name__ == '__main__':
    update_order_quantities()

