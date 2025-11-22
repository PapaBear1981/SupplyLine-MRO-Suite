"""
Migration script to add email column to users table
"""
import sqlite3
import os

def run_migration():
    # Get the database path (migrations run from backend directory)
    db_path = os.path.join('..', 'database', 'tools.db')

    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        column_added = False
        if 'email' not in column_names:
            # Add the email column (nullable)
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            conn.commit()
            column_added = True
            print("Successfully added email column to users table")
        else:
            print("Column email already exists in users table")

        # Verify the column was added
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nUsers table schema:")
        for column in columns:
            print(f"  {column[1]}: {column[2]}")

        # Close the connection
        conn.close()
        return True
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    run_migration()
