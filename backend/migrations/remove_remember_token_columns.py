import sqlite3
import os


def run_migration():
    """Remove remember_token columns from users table"""
    # Determine database path
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

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [c[1] for c in columns]

    version = sqlite3.sqlite_version_info

    try:
        if version >= (3, 35, 0):
            if 'remember_token' in column_names:
                cursor.execute("ALTER TABLE users DROP COLUMN remember_token")
                print("Dropped column remember_token")
            if 'remember_token_expiry' in column_names:
                cursor.execute("ALTER TABLE users DROP COLUMN remember_token_expiry")
                print("Dropped column remember_token_expiry")
            conn.commit()
        else:
            print("SQLite version too old for DROP COLUMN. Manual migration required.")
            return False
    finally:
        conn.close()
    return True


if __name__ == "__main__":
    run_migration()
