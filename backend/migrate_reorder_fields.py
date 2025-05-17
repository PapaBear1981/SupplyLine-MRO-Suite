import sqlite3
import os
from datetime import datetime

def migrate_database():
    """
    Add reordering fields to the chemicals table if they don't exist
    """
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the columns already exist
    cursor.execute("PRAGMA table_info(chemicals)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add the new columns if they don't exist
    if 'needs_reorder' not in columns:
        print("Adding 'needs_reorder' column to chemicals table...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN needs_reorder BOOLEAN DEFAULT 0")

    if 'reorder_status' not in columns:
        print("Adding 'reorder_status' column to chemicals table...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN reorder_status TEXT DEFAULT 'not_needed'")

    if 'reorder_date' not in columns:
        print("Adding 'reorder_date' column to chemicals table...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN reorder_date TIMESTAMP")

    if 'expected_delivery_date' not in columns:
        print("Adding 'expected_delivery_date' column to chemicals table...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN expected_delivery_date TIMESTAMP")

    # Update reorder status for expired, out-of-stock, or low-stock chemicals
    print("Updating reorder status for expired, out-of-stock, or low-stock chemicals...")
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        UPDATE chemicals
        SET needs_reorder = 1, reorder_status = 'needed'
        WHERE (expiration_date IS NOT NULL AND expiration_date < ?)
           OR quantity <= 0
           OR (minimum_stock_level IS NOT NULL AND quantity <= minimum_stock_level)
    """, (now,))

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
