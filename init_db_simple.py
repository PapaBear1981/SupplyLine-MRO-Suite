#!/usr/bin/env python3
"""
Simple database initialization script for Cloud SQL
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user(conn):
    """Create the admin user with hashed password."""
    try:
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE employee_number = 'ADMIN001'")
        if cursor.fetchone():
            logger.info("Admin user already exists")
            return True
        
        # Create admin user with bcrypt hashed password for 'admin123'
        # This is the bcrypt hash for 'admin123'
        admin_password_hash = '$2b$12$LQv3c1yqBWVHxkd0LQ4lqe7tvyIpd9Oy.4oWdqMBnQb5qDpDNF.1e'
        
        cursor.execute("""
            INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, ('System Administrator', 'ADMIN001', 'Administration', admin_password_hash, True, True))
        
        logger.info("✓ Admin user created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        return False

def init_database():
    """Initialize the database with tables and admin user."""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db',
            database='supplyline',
            user='supplyline_user',
            password='SupplyLine2025SecurePass!'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info("✓ Connected to database")
        
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                employee_number VARCHAR(50) UNIQUE NOT NULL,
                department VARCHAR(100),
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                reset_token VARCHAR(255),
                reset_token_expiry TIMESTAMP,
                remember_token VARCHAR(255),
                remember_token_expiry TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                avatar VARCHAR(255)
            )
        """)
        logger.info("✓ Users table created")
        
        # Create tools table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id SERIAL PRIMARY KEY,
                tool_number VARCHAR(50) UNIQUE NOT NULL,
                serial_number VARCHAR(100),
                description TEXT,
                condition VARCHAR(50),
                location VARCHAR(100),
                status VARCHAR(50) DEFAULT 'available',
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        logger.info("✓ Tools table created")
        
        # Create audit_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                action_type VARCHAR(100) NOT NULL,
                action_details TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        logger.info("✓ Audit log table created")
        
        # Create admin user
        if create_admin_user(conn):
            logger.info("✓ Database initialization completed successfully")
            return True
        else:
            logger.error("✗ Failed to create admin user")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if init_database():
        print("🎉 Database initialization completed!")
        sys.exit(0)
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)
