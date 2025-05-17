import os
import sqlite3
from datetime import datetime

def migrate_database():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"Connected to database at {db_path}")

    # Check if the tools table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tools'")
    if not cursor.fetchone():
        print("Error: tools table does not exist")
        conn.close()
        return False

    # Get the current columns in the tools table
    cursor.execute("PRAGMA table_info(tools)")
    columns = cursor.fetchall()
    column_names = [column['name'] for column in columns]

    print(f"Current columns in tools table: {', '.join(column_names)}")

    # Add calibration-related columns to the tools table if they don't exist
    new_columns = [
        ('requires_calibration', 'BOOLEAN DEFAULT 0'),
        ('calibration_frequency_days', 'INTEGER'),
        ('last_calibration_date', 'TIMESTAMP'),
        ('next_calibration_date', 'TIMESTAMP'),
        ('calibration_status', 'TEXT')
    ]

    for column_name, column_type in new_columns:
        if column_name not in column_names:
            print(f"Adding '{column_name}' column to tools table...")
            cursor.execute(f"ALTER TABLE tools ADD COLUMN {column_name} {column_type}")
        else:
            print(f"'{column_name}' column already exists in tools table")

    # Create tool_calibrations table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tool_calibrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id INTEGER NOT NULL,
        calibration_date TIMESTAMP NOT NULL,
        next_calibration_date TIMESTAMP,
        performed_by_user_id INTEGER NOT NULL,
        calibration_notes TEXT,
        calibration_status TEXT NOT NULL,
        calibration_certificate_file TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tool_id) REFERENCES tools (id),
        FOREIGN KEY (performed_by_user_id) REFERENCES users (id)
    )
    ''')
    print("Created or verified tool_calibrations table")

    # Create calibration_standards table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calibration_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        standard_number TEXT NOT NULL,
        certification_date TIMESTAMP NOT NULL,
        expiration_date TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Created or verified calibration_standards table")

    # Create tool_calibration_standards table for many-to-many relationship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tool_calibration_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calibration_id INTEGER NOT NULL,
        standard_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (calibration_id) REFERENCES tool_calibrations (id),
        FOREIGN KEY (standard_id) REFERENCES calibration_standards (id)
    )
    ''')
    print("Created or verified tool_calibration_standards table")

    # Commit the changes
    conn.commit()
    print("Schema changes committed successfully")

    # Close the connection
    conn.close()
    print("Database update completed successfully")
    return True

if __name__ == "__main__":
    migrate_database()
