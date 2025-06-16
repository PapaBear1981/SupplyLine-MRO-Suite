#!/usr/bin/env python3
"""
Database Initialization Job for Google Cloud SQL
This script initializes the PostgreSQL database with all required tables and admin user.
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import hashlib
import secrets
import string

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using Cloud SQL proxy or direct connection."""
    try:
        # Try Cloud SQL Unix socket first (for Cloud Run)
        if os.path.exists('/cloudsql'):
            db_config = {
                'host': '/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db',
                'database': 'supplyline',
                'user': 'supplyline_user',
                'password': os.environ.get('DB_PASSWORD', 'SupplyLine2025SecurePass!')
            }
            logger.info(f"Connecting to database via Unix socket at {db_config['host']}")
        else:
            # Use Cloud SQL Proxy or direct connection (for local development)
            db_config = {
                'host': os.environ.get('DB_HOST', '127.0.0.1'),
                'port': os.environ.get('DB_PORT', '5432'),
                'database': 'supplyline',
                'user': 'supplyline_user',
                'password': os.environ.get('DB_PASSWORD', 'SupplyLine2025SecurePass!')
            }
            logger.info(f"Connecting to database at {db_config['host']}:{db_config['port']}")

        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info("✓ Database connection successful")
        return conn

    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def create_tables(conn):
    """Create all required database tables."""
    
    tables_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100),
        department VARCHAR(50),
        is_active BOOLEAN DEFAULT true,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tools table
    CREATE TABLE IF NOT EXISTS tools (
        id SERIAL PRIMARY KEY,
        tool_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        category VARCHAR(50),
        location VARCHAR(100),
        status VARCHAR(20) DEFAULT 'available',
        condition_status VARCHAR(20) DEFAULT 'good',
        last_calibration DATE,
        next_calibration DATE,
        calibration_interval INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tool checkout/checkin history
    CREATE TABLE IF NOT EXISTS tool_transactions (
        id SERIAL PRIMARY KEY,
        tool_id INTEGER REFERENCES tools(id),
        user_id INTEGER REFERENCES users(id),
        action VARCHAR(20) NOT NULL,
        checkout_time TIMESTAMP,
        expected_return TIMESTAMP,
        actual_return TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Chemicals table
    CREATE TABLE IF NOT EXISTS chemicals (
        id SERIAL PRIMARY KEY,
        chemical_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        cas_number VARCHAR(20),
        manufacturer VARCHAR(100),
        lot_number VARCHAR(50),
        quantity DECIMAL(10,2),
        unit VARCHAR(20),
        location VARCHAR(100),
        expiration_date DATE,
        safety_data_sheet_url VARCHAR(255),
        hazard_class VARCHAR(50),
        storage_requirements TEXT,
        status VARCHAR(20) DEFAULT 'available',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Chemical usage tracking
    CREATE TABLE IF NOT EXISTS chemical_transactions (
        id SERIAL PRIMARY KEY,
        chemical_id INTEGER REFERENCES chemicals(id),
        user_id INTEGER REFERENCES users(id),
        action VARCHAR(20) NOT NULL,
        quantity_used DECIMAL(10,2),
        remaining_quantity DECIMAL(10,2),
        purpose TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Audit log
    CREATE TABLE IF NOT EXISTS audit_log (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        action VARCHAR(100) NOT NULL,
        table_name VARCHAR(50),
        record_id INTEGER,
        old_values JSONB,
        new_values JSONB,
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- System settings
    CREATE TABLE IF NOT EXISTS system_settings (
        id SERIAL PRIMARY KEY,
        setting_key VARCHAR(100) UNIQUE NOT NULL,
        setting_value TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_tools_tool_id ON tools(tool_id);
    CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status);
    CREATE INDEX IF NOT EXISTS idx_chemicals_chemical_id ON chemicals(chemical_id);
    CREATE INDEX IF NOT EXISTS idx_chemicals_expiration ON chemicals(expiration_date);
    CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
    CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(tables_sql)
        logger.info("✓ Database tables created successfully")
        cursor.close()
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

def create_admin_user(conn):
    """Create the default admin user."""
    
    try:
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE username = 'ADMIN001'")
        if cursor.fetchone():
            logger.info("Admin user already exists")
            cursor.close()
            return
        
        # Generate secure password hash
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert admin user
        insert_sql = """
        INSERT INTO users (username, password_hash, role, first_name, last_name, email, department)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            'ADMIN001',
            password_hash,
            'admin',
            'System',
            'Administrator',
            'admin@supplyline.local',
            'IT'
        ))
        
        logger.info("✓ Admin user created successfully")
        logger.info("Admin credentials: username=ADMIN001, password=admin123")
        cursor.close()
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        raise

def insert_sample_data(conn):
    """Insert some sample data for testing."""
    
    try:
        cursor = conn.cursor()
        
        # Sample tools
        tools_data = [
            ('TOOL001', 'Digital Multimeter', 'Fluke 87V Digital Multimeter', 'Electronics', 'Lab A-1', 'available', 'good'),
            ('TOOL002', 'Oscilloscope', 'Tektronix TDS2024C Oscilloscope', 'Electronics', 'Lab A-2', 'available', 'good'),
            ('TOOL003', 'Torque Wrench', 'Snap-on 3/8" Drive Torque Wrench', 'Mechanical', 'Tool Room B', 'available', 'good'),
        ]
        
        for tool_data in tools_data:
            cursor.execute("""
                INSERT INTO tools (tool_id, name, description, category, location, status, condition_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tool_id) DO NOTHING
            """, tool_data)
        
        # Sample chemicals
        chemicals_data = [
            ('CHEM001', 'Isopropyl Alcohol', '67-63-0', 'Fisher Scientific', 'LOT123', 1000.0, 'mL', 'Chemical Storage A', '2025-12-31'),
            ('CHEM002', 'Acetone', '67-64-1', 'Sigma-Aldrich', 'LOT456', 500.0, 'mL', 'Chemical Storage A', '2025-06-30'),
        ]
        
        for chem_data in chemicals_data:
            cursor.execute("""
                INSERT INTO chemicals (chemical_id, name, cas_number, manufacturer, lot_number, quantity, unit, location, expiration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chemical_id) DO NOTHING
            """, chem_data)
        
        # System settings
        settings_data = [
            ('app_name', 'SupplyLine MRO Suite', 'Application name'),
            ('version', '3.5.0', 'Application version'),
            ('maintenance_mode', 'false', 'Maintenance mode flag'),
        ]
        
        for setting_data in settings_data:
            cursor.execute("""
                INSERT INTO system_settings (setting_key, setting_value, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (setting_key) DO UPDATE SET
                setting_value = EXCLUDED.setting_value,
                updated_at = CURRENT_TIMESTAMP
            """, setting_data)
        
        logger.info("✓ Sample data inserted successfully")
        cursor.close()
        
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")
        raise

def main():
    """Main initialization function."""
    
    logger.info("Starting database initialization...")
    
    try:
        # Connect to database
        conn = get_db_connection()
        
        # Create tables
        create_tables(conn)
        
        # Create admin user
        create_admin_user(conn)
        
        # Insert sample data
        insert_sample_data(conn)
        
        # Close connection
        conn.close()
        
        logger.info("✓ Database initialization completed successfully!")
        logger.info("The SupplyLine MRO Suite database is ready for use.")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
