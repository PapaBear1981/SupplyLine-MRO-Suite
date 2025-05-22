"""
Migration script to add cycle count notifications table
"""
import sqlite3
import os
from datetime import datetime

def run_migration():
    """
    Adds the cycle_count_notifications table to the database
    """
    # Get database path
    # Try different possible database paths
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'tools.db'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'supplyline.db')
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {db_path}")
            break

    if not db_path:
        raise FileNotFoundError("Could not find the database file")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create cycle_count_notifications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cycle_count_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL,
            reference_id INTEGER,
            reference_type TEXT,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create index on user_id for faster queries
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_cycle_count_notifications_user_id
        ON cycle_count_notifications (user_id)
        ''')

        # Create index on is_read for faster filtering
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_cycle_count_notifications_is_read
        ON cycle_count_notifications (is_read)
        ''')

        # Commit changes
        conn.commit()
        print(f"[{datetime.now()}] Successfully created cycle_count_notifications table")

    except Exception as e:
        # Roll back changes on error
        conn.rollback()
        print(f"[{datetime.now()}] Error creating cycle_count_notifications table: {str(e)}")
        raise
    finally:
        # Close connection
        conn.close()

if __name__ == "__main__":
    run_migration()
