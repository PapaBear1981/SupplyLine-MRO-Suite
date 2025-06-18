#!/usr/bin/env python3
"""
Database migration script to add missing columns that are causing 500 errors.
This script will add all the missing columns to make the dashboard work properly.
"""

import os
import sys
import sqlite3
from datetime import datetime

def get_database_path():
    """Get the database path"""
    # Try different possible database locations
    possible_paths = [
        '/tmp/tools.db',  # Cloud Run temporary storage
        'tools.db',       # Current directory
        'database/tools.db',  # Database subdirectory
        '../database/tools.db'  # Parent database directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If no existing database found, create in /tmp for Cloud Run
    return '/tmp/tools.db'

def migrate_database():
    """Add missing columns to the database"""
    db_path = get_database_path()
    print(f"Using database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get existing table info
        print("Checking existing database schema...")
        
        # Check chemicals table
        cursor.execute("PRAGMA table_info(chemicals)")
        chemical_columns = [column[1] for column in cursor.fetchall()]
        print(f"Chemicals table columns: {chemical_columns}")
        
        # Add missing columns to chemicals table
        missing_chemical_columns = [
            ('is_archived', 'BOOLEAN DEFAULT 0'),
            ('archived_reason', 'TEXT'),
            ('archived_date', 'TIMESTAMP'),
            ('needs_reorder', 'BOOLEAN DEFAULT 0'),
            ('reorder_status', 'TEXT DEFAULT "not_needed"'),
            ('reorder_date', 'TIMESTAMP'),
            ('expected_delivery_date', 'TIMESTAMP')
        ]
        
        for column_name, column_def in missing_chemical_columns:
            if column_name not in chemical_columns:
                print(f"Adding {column_name} column to chemicals table...")
                cursor.execute(f"ALTER TABLE chemicals ADD COLUMN {column_name} {column_def}")
        
        # Check tools table
        cursor.execute("PRAGMA table_info(tools)")
        tool_columns = [column[1] for column in cursor.fetchall()]
        print(f"Tools table columns: {tool_columns}")
        
        # Add missing columns to tools table
        missing_tool_columns = [
            ('status', 'TEXT DEFAULT "available"'),
            ('requires_calibration', 'BOOLEAN DEFAULT 0'),
            ('calibration_status', 'TEXT DEFAULT "not_applicable"'),
            ('last_calibration_date', 'TIMESTAMP'),
            ('next_calibration_date', 'TIMESTAMP'),
            ('calibration_frequency_days', 'INTEGER'),
            ('status_reason', 'TEXT')
        ]
        
        for column_name, column_def in missing_tool_columns:
            if column_name not in tool_columns:
                print(f"Adding {column_name} column to tools table...")
                cursor.execute(f"ALTER TABLE tools ADD COLUMN {column_name} {column_def}")
        
        # Check checkouts table
        cursor.execute("PRAGMA table_info(checkouts)")
        checkout_columns = [column[1] for column in cursor.fetchall()]
        print(f"Checkouts table columns: {checkout_columns}")
        
        # Add missing columns to checkouts table
        missing_checkout_columns = [
            ('expected_return_date', 'TIMESTAMP'),
            ('return_condition', 'TEXT'),
            ('returned_by', 'TEXT'),
            ('found', 'BOOLEAN DEFAULT 0'),
            ('return_notes', 'TEXT')
        ]
        
        for column_name, column_def in missing_checkout_columns:
            if column_name not in checkout_columns:
                print(f"Adding {column_name} column to checkouts table...")
                cursor.execute(f"ALTER TABLE checkouts ADD COLUMN {column_name} {column_def}")
        
        # Check users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        print(f"Users table columns: {user_columns}")
        
        # Add missing columns to users table
        missing_user_columns = [
            ('avatar', 'TEXT'),
            ('is_admin', 'BOOLEAN DEFAULT 0'),
            ('is_active', 'BOOLEAN DEFAULT 1'),
            ('failed_login_attempts', 'INTEGER DEFAULT 0'),
            ('account_locked_until', 'TIMESTAMP'),
            ('last_failed_login', 'TIMESTAMP'),
            ('reset_token', 'TEXT'),
            ('reset_token_expiry', 'TIMESTAMP'),
            ('remember_token', 'TEXT'),
            ('remember_token_expiry', 'TIMESTAMP')
        ]
        
        for column_name, column_def in missing_user_columns:
            if column_name not in user_columns:
                print(f"Adding {column_name} column to users table...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
        
        # Create missing tables if they don't exist
        print("Creating missing tables...")
        
        # Create user_activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create announcements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiration_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # Create announcement_reads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcement_reads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                announcement_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (announcement_id) REFERENCES announcements(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create tool_calibrations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_calibrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER NOT NULL,
                calibration_date TIMESTAMP NOT NULL,
                next_calibration_date TIMESTAMP,
                performed_by_user_id INTEGER NOT NULL,
                calibration_notes TEXT,
                calibration_status TEXT DEFAULT 'pass',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tool_id) REFERENCES tools(id),
                FOREIGN KEY (performed_by_user_id) REFERENCES users(id)
            )
        """)
        
        # Create calibration_standards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calibration_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                standard_number TEXT NOT NULL,
                certification_date TIMESTAMP NOT NULL,
                expiration_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create tool_calibration_standards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_calibration_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calibration_id INTEGER NOT NULL,
                standard_id INTEGER NOT NULL,
                FOREIGN KEY (calibration_id) REFERENCES tool_calibrations(id),
                FOREIGN KEY (standard_id) REFERENCES calibration_standards(id)
            )
        """)
        
        # Create chemical_issuances table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chemical_issuances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chemical_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                hangar TEXT NOT NULL,
                purpose TEXT,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chemical_id) REFERENCES chemicals(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create tool_service_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_service_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                comments TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tool_id) REFERENCES tools(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Commit all changes
        conn.commit()
        print("Database migration completed successfully!")
        
        # Print final table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables in database: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
