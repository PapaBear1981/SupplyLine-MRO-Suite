"""
Migration script to move all tools to Main warehouse in Spokane, WA
"""
import sqlite3
import os
from datetime import datetime

def move_tools_to_spokane():
    """Move all tools to Main warehouse in Spokane, WA"""
    # Get database path
    db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'tools.db'))

    print(f"Using database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Find the Spokane warehouse
        cursor.execute("""
            SELECT id, name, city, state
            FROM warehouses
            WHERE name = 'Main' AND city = 'Spokane' AND state = 'WA'
        """)
        spokane_warehouse = cursor.fetchone()

        if not spokane_warehouse:
            print("ERROR: Main warehouse in Spokane, WA not found!")
            return False

        spokane_id, spokane_name, spokane_city, spokane_state = spokane_warehouse
        print(f"Found Spokane warehouse: ID {spokane_id} - {spokane_name}, {spokane_city}, {spokane_state}")

        # Get all tools
        cursor.execute("SELECT id, tool_number, description, warehouse_id FROM tools")
        all_tools = cursor.fetchall()
        print(f"\nFound {len(all_tools)} total tools")

        # Count tools by current warehouse
        cursor.execute("""
            SELECT warehouse_id, COUNT(*)
            FROM tools
            GROUP BY warehouse_id
        """)
        tools_by_warehouse = cursor.fetchall()

        print("\nCurrent distribution:")
        for warehouse_id, count in tools_by_warehouse:
            if warehouse_id is None:
                print(f"  No warehouse: {count} tools")
            else:
                cursor.execute("SELECT name, city, state FROM warehouses WHERE id = ?", (warehouse_id,))
                warehouse = cursor.fetchone()
                if warehouse:
                    print(f"  {warehouse[0]} ({warehouse[1]}, {warehouse[2]}): {count} tools")

        # Move all tools to Spokane warehouse
        moved_count = 0
        for tool_id, tool_number, description, old_warehouse_id in all_tools:
            old_warehouse_name = "No warehouse"

            if old_warehouse_id:
                cursor.execute("SELECT name, city, state FROM warehouses WHERE id = ?", (old_warehouse_id,))
                old_warehouse = cursor.fetchone()
                if old_warehouse:
                    old_warehouse_name = f"{old_warehouse[0]} ({old_warehouse[1]}, {old_warehouse[2]})"

            # Update tool warehouse
            cursor.execute("""
                UPDATE tools
                SET warehouse_id = ?
                WHERE id = ?
            """, (spokane_id, tool_id))

            # Create audit log entry
            cursor.execute("""
                INSERT INTO audit_log (action_type, action_details, timestamp)
                VALUES (?, ?, ?)
            """, (
                'tool_warehouse_migration',
                f'Tool {tool_number} ({description}) moved from {old_warehouse_name} to {spokane_name} ({spokane_city}, {spokane_state})',
                datetime.now().isoformat()
            ))

            moved_count += 1
            print(f"  Moved: {tool_number} - {description}")

        # Commit all changes
        conn.commit()

        print(f"\n✅ Successfully moved {moved_count} tools to {spokane_name} in {spokane_city}, {spokane_state}")

        # Verify the migration
        print("\nVerifying migration...")
        cursor.execute("SELECT COUNT(*) FROM tools WHERE warehouse_id = ?", (spokane_id,))
        spokane_tools = cursor.fetchone()[0]
        print(f"Tools now in Spokane warehouse: {spokane_tools}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Tool Warehouse Migration Script")
    print("Moving all tools to Main warehouse in Spokane, WA")
    print("=" * 60)
    print()
    
    success = move_tools_to_spokane()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

