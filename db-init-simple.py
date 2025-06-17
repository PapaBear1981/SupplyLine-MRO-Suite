#!/usr/bin/env python3
"""
Simple Database Initialization Script for Cloud Run Job
This script creates the admin user in the existing database.
"""

import os
import sys
import logging
import psycopg2
from werkzeug.security import generate_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_admin_user():
    """Initialize admin user in the database."""
    
    # Database connection parameters
    db_params = {
        'host': '/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db',
        'database': 'supplyline',
        'user': 'supplyline_user',
        'password': os.environ.get('DB_PASSWORD', '')
    }
    
    try:
        logger.info("Connecting to database...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE employee_number = 'ADMIN001'")
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            logger.info("Admin user already exists")
            return True
        
        # Create admin user
        logger.info("Creating admin user...")
        admin_password_hash = generate_password_hash('admin123')
        
        cursor.execute("""
            INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, ('System Administrator', 'ADMIN001', 'IT', admin_password_hash, True, True))
        
        conn.commit()
        logger.info("✓ Admin user created successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_admin_user()
    sys.exit(0 if success else 1)
