"""
Migration script to add is_active column to users table
"""
import sqlite3
import os

def run_migration():
    # Get the database path
    db_path = os.path.join('database', 'tools.db')

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
        if 'is_active' not in column_names:
            # Add the is_active column with default value of 1 (True)
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            conn.commit()
            column_added = True
            print("Successfully added is_active column to users table")
        else:
            print("Column is_active already exists in users table")

        # Ensure all existing users have is_active set to 1 (True)
        cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
        rows_updated = cursor.rowcount
        conn.commit()
        print(f"Updated {rows_updated} users to have is_active = 1")

        # Verify all users have is_active set
        cursor.execute("SELECT id, name, is_active FROM users")
        users = cursor.fetchall()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"User ID: {user[0]}, Name: {user[1]}, Active: {user[2]}")

        # Close the connection
        conn.close()
        return True
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    run_migration()
