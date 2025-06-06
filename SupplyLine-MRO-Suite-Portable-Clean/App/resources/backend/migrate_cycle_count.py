import sqlite3
import os
from datetime import datetime

def migrate_database():
    """
    Add cycle count tables to the database
    """
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db')
    print(f"Database path: {db_path}")

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the tables already exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cycle_count_schedules'")
    if cursor.fetchone() is None:
        print("Creating cycle_count_schedules table...")
        cursor.execute('''
        CREATE TABLE cycle_count_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            frequency TEXT NOT NULL,  -- daily, weekly, monthly, quarterly, annual
            method TEXT NOT NULL,     -- ABC, random, location, category
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        print("Created cycle_count_schedules table")
    else:
        print("cycle_count_schedules table already exists")

    # Check if cycle_count_batches table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cycle_count_batches'")
    if cursor.fetchone() is None:
        print("Creating cycle_count_batches table...")
        cursor.execute('''
        CREATE TABLE cycle_count_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER,
            name TEXT NOT NULL,
            status TEXT NOT NULL,     -- pending, in_progress, completed, cancelled
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (schedule_id) REFERENCES cycle_count_schedules(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        print("Created cycle_count_batches table")
    else:
        print("cycle_count_batches table already exists")

    # Check if cycle_count_items table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cycle_count_items'")
    if cursor.fetchone() is None:
        print("Creating cycle_count_items table...")
        cursor.execute('''
        CREATE TABLE cycle_count_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,  -- tool, chemical
            item_id INTEGER NOT NULL,
            expected_quantity REAL,
            expected_location TEXT,
            assigned_to INTEGER,
            status TEXT NOT NULL,     -- pending, counted, skipped
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES cycle_count_batches(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
        ''')
        print("Created cycle_count_items table")
    else:
        print("cycle_count_items table already exists")

    # Check if cycle_count_results table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cycle_count_results'")
    if cursor.fetchone() is None:
        print("Creating cycle_count_results table...")
        cursor.execute('''
        CREATE TABLE cycle_count_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            counted_by INTEGER NOT NULL,
            counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actual_quantity REAL,
            actual_location TEXT,
            condition TEXT,
            notes TEXT,
            has_discrepancy BOOLEAN DEFAULT 0,
            discrepancy_type TEXT,    -- quantity, location, condition, missing, extra
            discrepancy_notes TEXT,
            FOREIGN KEY (item_id) REFERENCES cycle_count_items(id),
            FOREIGN KEY (counted_by) REFERENCES users(id)
        )
        ''')
        print("Created cycle_count_results table")
    else:
        print("cycle_count_results table already exists")

    # Check if cycle_count_adjustments table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cycle_count_adjustments'")
    if cursor.fetchone() is None:
        print("Creating cycle_count_adjustments table...")
        cursor.execute('''
        CREATE TABLE cycle_count_adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            approved_by INTEGER NOT NULL,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            adjustment_type TEXT NOT NULL,  -- quantity, location, condition, status
            old_value TEXT,
            new_value TEXT,
            notes TEXT,
            FOREIGN KEY (result_id) REFERENCES cycle_count_results(id),
            FOREIGN KEY (approved_by) REFERENCES users(id)
        )
        ''')
        print("Created cycle_count_adjustments table")
    else:
        print("cycle_count_adjustments table already exists")

    # Commit the changes
    conn.commit()
    print("Schema changes committed successfully")

    # Close the connection
    conn.close()
    print("Database migration completed successfully")

if __name__ == '__main__':
    migrate_database()
