#!/usr/bin/env python3
"""
Check the actual datetime field values in the database
"""
import sqlite3
import os

def check_database_datetime_fields():
    """Check what's actually stored in the datetime fields"""
    
    # Get database path
    db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check users table datetime fields
        print("\n=== USERS TABLE ===")
        cursor.execute("SELECT id, employee_number, created_at, account_locked_until, last_failed_login FROM users LIMIT 5")
        users = cursor.fetchall()
        
        for user_id, emp_num, created_at, locked_until, last_failed in users:
            print(f"User {user_id} ({emp_num}):")
            print(f"  created_at: {created_at} (type: {type(created_at)})")
            print(f"  account_locked_until: {locked_until} (type: {type(locked_until)})")
            print(f"  last_failed_login: {last_failed} (type: {type(last_failed)})")
            print()
        
        # Check if any datetime fields contain the problematic string
        print("\n=== SEARCHING FOR PROBLEMATIC DATETIME STRING ===")
        problematic_string = '2025-06-16T12:22:44.275702'
        
        # Check created_at
        cursor.execute("SELECT id, employee_number, created_at FROM users WHERE created_at = ?", (problematic_string,))
        matches = cursor.fetchall()
        if matches:
            print(f"Found {len(matches)} users with created_at = '{problematic_string}':")
            for user_id, emp_num, created_at in matches:
                print(f"  User {user_id} ({emp_num}): created_at = {created_at}")
        
        # Check account_locked_until
        cursor.execute("SELECT id, employee_number, account_locked_until FROM users WHERE account_locked_until = ?", (problematic_string,))
        matches = cursor.fetchall()
        if matches:
            print(f"Found {len(matches)} users with account_locked_until = '{problematic_string}':")
            for user_id, emp_num, locked_until in matches:
                print(f"  User {user_id} ({emp_num}): account_locked_until = {locked_until}")
        
        # Check last_failed_login
        cursor.execute("SELECT id, employee_number, last_failed_login FROM users WHERE last_failed_login = ?", (problematic_string,))
        matches = cursor.fetchall()
        if matches:
            print(f"Found {len(matches)} users with last_failed_login = '{problematic_string}':")
            for user_id, emp_num, last_failed in matches:
                print(f"  User {user_id} ({emp_num}): last_failed_login = {last_failed}")
        
        # Check for any datetime fields that contain ISO format strings
        print("\n=== CHECKING FOR ISO FORMAT STRINGS IN DATETIME FIELDS ===")
        cursor.execute("SELECT id, employee_number, created_at FROM users WHERE created_at LIKE '%T%:%'")
        iso_created = cursor.fetchall()
        if iso_created:
            print(f"Found {len(iso_created)} users with ISO format strings in created_at:")
            for user_id, emp_num, created_at in iso_created:
                print(f"  User {user_id} ({emp_num}): created_at = {created_at}")
        
        cursor.execute("SELECT id, employee_number, account_locked_until FROM users WHERE account_locked_until LIKE '%T%:%'")
        iso_locked = cursor.fetchall()
        if iso_locked:
            print(f"Found {len(iso_locked)} users with ISO format strings in account_locked_until:")
            for user_id, emp_num, locked_until in iso_locked:
                print(f"  User {user_id} ({emp_num}): account_locked_until = {locked_until}")
        
        cursor.execute("SELECT id, employee_number, last_failed_login FROM users WHERE last_failed_login LIKE '%T%:%'")
        iso_failed = cursor.fetchall()
        if iso_failed:
            print(f"Found {len(iso_failed)} users with ISO format strings in last_failed_login:")
            for user_id, emp_num, last_failed in iso_failed:
                print(f"  User {user_id} ({emp_num}): last_failed_login = {last_failed}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")

if __name__ == "__main__":
    check_database_datetime_fields()
