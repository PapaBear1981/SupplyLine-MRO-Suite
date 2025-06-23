"""Migration script to drop remember_token columns from users table"""
import sqlite3
import os


def run_migration():
    db_path = os.path.join('database', 'tools.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = [c[1] for c in cursor.fetchall()]
        altered = False
        if 'remember_token' in columns:
            cursor.execute("ALTER TABLE users DROP COLUMN remember_token")
            altered = True
            print("Dropped remember_token column")
        if 'remember_token_expiry' in columns:
            cursor.execute("ALTER TABLE users DROP COLUMN remember_token_expiry")
            altered = True
            print("Dropped remember_token_expiry column")
        if altered:
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False


if __name__ == '__main__':
    run_migration()
