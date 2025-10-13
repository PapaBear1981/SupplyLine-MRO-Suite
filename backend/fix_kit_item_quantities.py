"""
Fix floating-point precision errors in kit item quantities.

This script rounds all kit item quantities to 2 decimal places to fix
floating-point precision errors that can occur during arithmetic operations.
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
db_path = os.path.abspath(db_path)

print(f"Connecting to database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Fix kit_items table
    print("\nFixing kit_items quantities...")
    cursor.execute("SELECT id, part_number, quantity FROM kit_items")
    items = cursor.fetchall()

    fixed_count = 0
    for item_id, part_number, quantity in items:
        # Round to whole number for tools/chemicals (they should be integers)
        rounded_quantity = round(quantity)
        if quantity != rounded_quantity:
            cursor.execute("UPDATE kit_items SET quantity = ? WHERE id = ?", (rounded_quantity, item_id))
            print(f"  Fixed item {item_id} ({part_number}): {quantity} -> {rounded_quantity}")
            fixed_count += 1

    print(f"Fixed {fixed_count} kit items")
    
    # Fix kit_expendables table
    print("\nFixing kit_expendables quantities...")
    cursor.execute("SELECT id, part_number, quantity FROM kit_expendables")
    expendables = cursor.fetchall()

    fixed_count = 0
    for expendable_id, part_number, quantity in expendables:
        # Round to whole number for expendables (they should be integers)
        rounded_quantity = round(quantity)
        if quantity != rounded_quantity:
            cursor.execute("UPDATE kit_expendables SET quantity = ? WHERE id = ?", (rounded_quantity, expendable_id))
            print(f"  Fixed expendable {expendable_id} ({part_number}): {quantity} -> {rounded_quantity}")
            fixed_count += 1

    print(f"Fixed {fixed_count} kit expendables")
    
    # Commit the changes
    conn.commit()
    print("\n✅ All quantities have been fixed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()

