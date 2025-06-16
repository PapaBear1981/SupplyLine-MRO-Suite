#!/usr/bin/env python3
"""
Fix corrupted datetime data in the database
"""
import sqlite3
import os
from datetime import datetime

def fix_datetime_corruption():
    """Fix corrupted datetime fields in the database"""
    
    # Get database path
    db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
    print(f"Fixing database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Backup the database first
        backup_path = db_path + '.backup_before_datetime_fix'
        print(f"Creating backup at: {backup_path}")
        
        with open(db_path, 'rb') as source:
            with open(backup_path, 'wb') as backup:
                backup.write(source.read())
        
        print("Backup created successfully")
        
        # Find all users with ISO format strings in datetime fields
        print("\n=== FIXING CORRUPTED DATETIME FIELDS ===")
        
        # Fix created_at field
        cursor.execute("SELECT id, employee_number, created_at FROM users WHERE created_at LIKE '%T%:%'")
        corrupted_created = cursor.fetchall()
        
        if corrupted_created:
            print(f"Found {len(corrupted_created)} users with corrupted created_at field")
            for user_id, emp_num, created_at_str in corrupted_created:
                try:
                    # Parse the ISO string and convert to SQLite datetime format
                    dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    # Convert to naive datetime (remove timezone info) for SQLite
                    dt_naive = dt.replace(tzinfo=None)
                    # Format as SQLite datetime string
                    sqlite_datetime = dt_naive.strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    # Update the record
                    cursor.execute("UPDATE users SET created_at = ? WHERE id = ?", (sqlite_datetime, user_id))
                    print(f"  Fixed User {user_id} ({emp_num}): {created_at_str} -> {sqlite_datetime}")
                    
                except Exception as e:
                    print(f"  ERROR fixing User {user_id} ({emp_num}): {str(e)}")
        
        # Fix account_locked_until field
        cursor.execute("SELECT id, employee_number, account_locked_until FROM users WHERE account_locked_until LIKE '%T%:%'")
        corrupted_locked = cursor.fetchall()
        
        if corrupted_locked:
            print(f"Found {len(corrupted_locked)} users with corrupted account_locked_until field")
            for user_id, emp_num, locked_until_str in corrupted_locked:
                try:
                    dt = datetime.fromisoformat(locked_until_str.replace('Z', '+00:00'))
                    dt_naive = dt.replace(tzinfo=None)
                    sqlite_datetime = dt_naive.strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    cursor.execute("UPDATE users SET account_locked_until = ? WHERE id = ?", (sqlite_datetime, user_id))
                    print(f"  Fixed User {user_id} ({emp_num}) account_locked_until: {locked_until_str} -> {sqlite_datetime}")
                    
                except Exception as e:
                    print(f"  ERROR fixing User {user_id} ({emp_num}) account_locked_until: {str(e)}")
        
        # Fix last_failed_login field
        cursor.execute("SELECT id, employee_number, last_failed_login FROM users WHERE last_failed_login LIKE '%T%:%'")
        corrupted_failed = cursor.fetchall()
        
        if corrupted_failed:
            print(f"Found {len(corrupted_failed)} users with corrupted last_failed_login field")
            for user_id, emp_num, failed_login_str in corrupted_failed:
                try:
                    dt = datetime.fromisoformat(failed_login_str.replace('Z', '+00:00'))
                    dt_naive = dt.replace(tzinfo=None)
                    sqlite_datetime = dt_naive.strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    cursor.execute("UPDATE users SET last_failed_login = ? WHERE id = ?", (sqlite_datetime, user_id))
                    print(f"  Fixed User {user_id} ({emp_num}) last_failed_login: {failed_login_str} -> {sqlite_datetime}")
                    
                except Exception as e:
                    print(f"  ERROR fixing User {user_id} ({emp_num}) last_failed_login: {str(e)}")
        
        # Commit all changes
        conn.commit()
        
        # Verify the fix
        print("\n=== VERIFYING FIX ===")
        cursor.execute("SELECT id, employee_number, created_at FROM users WHERE created_at LIKE '%T%:%'")
        remaining_iso = cursor.fetchall()
        
        if remaining_iso:
            print(f"WARNING: {len(remaining_iso)} users still have ISO format strings in created_at")
            for user_id, emp_num, created_at in remaining_iso:
                print(f"  User {user_id} ({emp_num}): {created_at}")
        else:
            print("✓ All created_at fields fixed successfully")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"✓ Total users in database: {total_users}")
        
        conn.close()
        
        print("\n=== FIX COMPLETED SUCCESSFULLY ===")
        print(f"Database backup saved at: {backup_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing database: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_datetime_corruption()
    if success:
        print("\n✓ Datetime corruption fix completed successfully!")
        print("You can now restart the application and test the users API.")
    else:
        print("\n✗ Datetime corruption fix failed!")
        print("Please check the error messages above.")
