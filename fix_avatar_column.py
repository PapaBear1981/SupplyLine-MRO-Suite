#!/usr/bin/env python3
"""
Fix Avatar Column Migration Script
This script adds the missing 'avatar' column to the users table in the Cloud SQL database.
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_avatar_column():
    """Add the missing avatar column to the users table."""
    
    # Database connection parameters (same as used in the app)
    db_config = {
        'host': '/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db',
        'database': 'supplyline',
        'user': 'supplyline_user',
        'password': 'SupplyLine2025SecurePass!'
    }
    
    try:
        logger.info("Connecting to Cloud SQL database...")
        
        # Connect to database
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("✓ Connected successfully!")
        
        # Check if avatar column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'avatar'
        """)
        
        existing_column = cursor.fetchone()
        
        if existing_column:
            logger.info("✓ Avatar column already exists in users table")
        else:
            logger.info("Adding avatar column to users table...")
            
            # Add the avatar column
            cursor.execute("""
                ALTER TABLE users ADD COLUMN avatar VARCHAR(255)
            """)
            
            logger.info("✓ Avatar column added successfully!")
        
        # Verify the column exists now
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'avatar'
        """)
        
        column_info = cursor.fetchone()
        if column_info:
            logger.info(f"✓ Verified: avatar column exists - Type: {column_info[1]}, Nullable: {column_info[2]}")
        else:
            logger.error("✗ Avatar column was not created successfully")
            return False
        
        # Show all columns in users table for verification
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        logger.info("Current users table schema:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        cursor.close()
        conn.close()
        
        logger.info("✓ Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting avatar column migration...")
    
    success = add_avatar_column()
    
    if success:
        logger.info("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Migration failed!")
        sys.exit(1)
