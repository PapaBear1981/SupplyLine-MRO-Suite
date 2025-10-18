import sqlite3
import os

def run_migration():
    """
    Migration to add parent_lot_number and lot_sequence columns to chemicals table.
    These columns support the partial transfer feature for tracking lot lineage.
    """
    # Get the database path
    # Try different possible database paths
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'tools.db'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {db_path}")
            break

    if not db_path:
        raise FileNotFoundError("Could not find the database file")

    print(f"Using database at: {db_path}")

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the columns already exist
    cursor.execute("PRAGMA table_info(chemicals)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Add parent_lot_number column if it doesn't exist
    if 'parent_lot_number' not in column_names:
        cursor.execute("ALTER TABLE chemicals ADD COLUMN parent_lot_number TEXT")
        print("Added 'parent_lot_number' column to chemicals table")
    else:
        print("'parent_lot_number' column already exists in chemicals table")

    # Add lot_sequence column if it doesn't exist
    if 'lot_sequence' not in column_names:
        cursor.execute("ALTER TABLE chemicals ADD COLUMN lot_sequence INTEGER DEFAULT 0")
        print("Added 'lot_sequence' column to chemicals table")
    else:
        print("'lot_sequence' column already exists in chemicals table")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("The chemicals table now supports partial transfer tracking with:")
    print("  - parent_lot_number: Tracks the parent lot when a chemical is split")
    print("  - lot_sequence: Counts how many child lots have been created from this lot")

if __name__ == "__main__":
    run_migration()

