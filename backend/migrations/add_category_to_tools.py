import sqlite3
import os

def run_migration():
    # Get the database path
    # Try different possible database paths
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'tools.db')
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {db_path}")
            break

    if not db_path:
        raise FileNotFoundError("Could not find the database file")

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the category column already exists
    cursor.execute("PRAGMA table_info(tools)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    if 'category' not in column_names:
        # Add the category column to the tools table
        cursor.execute("ALTER TABLE tools ADD COLUMN category TEXT")
        print("Added 'category' column to tools table")
    else:
        print("'category' column already exists in tools table")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
