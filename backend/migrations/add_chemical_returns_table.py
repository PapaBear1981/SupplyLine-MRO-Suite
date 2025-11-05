"""
Migration script to add the chemical_returns table for tracking chemical returns.

This script creates the chemical_returns table with the following fields:
- id: Primary key
- chemical_id: Foreign key to chemicals table
- issuance_id: Foreign key to chemical_issuances table
- returned_by_id: Foreign key to users table (who returned the chemical)
- quantity: Amount returned
- warehouse_id: Foreign key to warehouses table (optional)
- location: Storage location (optional)
- notes: Additional notes about the return (optional)
- return_date: Timestamp of when the return was recorded
"""

import sqlite3
import os
import sys


def run_migration():
    """Execute the migration to add the chemical_returns table."""
    # Get the database path
    db_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'database'
    )
    db_path = os.path.join(db_dir, 'tools.db')

    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the table already exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chemical_returns'"
        )
        if cursor.fetchone():
            print("✓ chemical_returns table already exists - skipping creation")
            conn.close()
            return

        print("Creating chemical_returns table...")

        # Create the chemical_returns table
        cursor.execute("""
            CREATE TABLE chemical_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chemical_id INTEGER NOT NULL,
                issuance_id INTEGER NOT NULL,
                returned_by_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                warehouse_id INTEGER,
                location VARCHAR(200),
                notes VARCHAR(1000),
                return_date DATETIME NOT NULL,
                FOREIGN KEY (chemical_id) REFERENCES chemicals(id),
                FOREIGN KEY (issuance_id) REFERENCES chemical_issuances(id),
                FOREIGN KEY (returned_by_id) REFERENCES users(id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
            )
        """)

        # Create indexes for better query performance
        print("Creating indexes...")
        cursor.execute(
            "CREATE INDEX idx_chemical_returns_chemical_id ON chemical_returns(chemical_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_chemical_returns_issuance_id ON chemical_returns(issuance_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_chemical_returns_return_date ON chemical_returns(return_date)"
        )

        # Commit the changes
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - chemical_returns table created")
        print("   - Indexes created for optimal query performance")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Chemical Returns Table Migration")
    print("=" * 60)
    run_migration()
    print("=" * 60)

