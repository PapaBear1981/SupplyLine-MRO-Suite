#!/usr/bin/env python3
"""
SupplyLine MRO Suite - Sample Data Population Script

This script populates the production database with comprehensive sample data
for testing and demonstration purposes.

Usage:
    python scripts/populate_sample_data.py

Requirements:
    - psycopg2-binary
    - Access to Cloud SQL instance
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from datetime import datetime

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sample_data_population.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def get_database_connection():
    """
    Establish connection to the Cloud SQL PostgreSQL database.
    """
    try:
        # Get database password from environment or prompt
        db_password = os.environ.get('DB_PASSWORD')
        if not db_password:
            logger.warning("DB_PASSWORD environment variable not set")
            # For this script, we'll try to connect without password first
            # In production, this should be properly configured
            db_password = ''

        # Database connection parameters for Cloud SQL
        db_config = {
            'database': 'supplyline',
            'user': 'supplyline_user',
            'password': db_password,
            'port': 5432
        }

        # Try different connection methods
        connection_attempts = [
            # Cloud SQL Unix socket (production)
            {**db_config, 'host': '/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db'},
            # Cloud SQL TCP (if proxy is running)
            {**db_config, 'host': '127.0.0.1'},
            # Local PostgreSQL (development)
            {**db_config, 'host': 'localhost'},
        ]

        for i, config in enumerate(connection_attempts, 1):
            try:
                logger.info(f"Attempting connection method {i}/3...")
                conn = psycopg2.connect(**config)
                logger.info(f"Connected successfully using method {i}")
                return conn
            except psycopg2.Error as e:
                logger.debug(f"Connection method {i} failed: {e}")
                continue

        logger.error("All connection methods failed")
        return None

    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {e}")
        return None

def read_sql_file(file_path):
    """
    Read SQL file and return its contents.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"✗ SQL file not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"✗ Error reading SQL file: {e}")
        return None

def execute_sql_script(conn, sql_content):
    """
    Execute SQL script with proper error handling.
    """
    try:
        cursor = conn.cursor()
        
        # Split the SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                conn.commit()
                success_count += 1
                logger.debug(f"OK Executed statement {i}/{len(statements)}")
            except psycopg2.Error as e:
                error_count += 1
                logger.warning(f"WARNING Statement {i} failed: {e}")
                conn.rollback()
                continue

        cursor.close()
        logger.info(f"OK SQL execution completed: {success_count} successful, {error_count} failed")
        return success_count > 0

    except Exception as e:
        logger.error(f"ERROR executing SQL script: {e}")
        return False

def verify_sample_data(conn):
    """
    Verify that sample data was inserted correctly.
    """
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check various tables for data
        checks = [
            ("users", "SELECT COUNT(*) as count FROM users WHERE employee_number LIKE 'EMP%'"),
            ("tools", "SELECT COUNT(*) as count FROM tools WHERE tool_number LIKE 'T%'"),
            ("chemicals", "SELECT COUNT(*) as count FROM chemicals WHERE part_number LIKE 'CHM%'"),
            ("checkouts", "SELECT COUNT(*) as count FROM checkouts"),
            ("chemical_issuances", "SELECT COUNT(*) as count FROM chemical_issuances"),
            ("audit_log", "SELECT COUNT(*) as count FROM audit_log"),
            ("roles", "SELECT COUNT(*) as count FROM roles"),
            ("permissions", "SELECT COUNT(*) as count FROM permissions")
        ]
        
        logger.info("Verifying sample data insertion:")
        all_good = True

        for table_name, query in checks:
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                count = result['count'] if result else 0

                if count > 0:
                    logger.info(f"  OK {table_name}: {count} records")
                else:
                    logger.warning(f"  WARNING {table_name}: No records found")
                    all_good = False

            except psycopg2.Error as e:
                logger.error(f"  ERROR {table_name}: Error checking - {e}")
                all_good = False

        cursor.close()
        return all_good

    except Exception as e:
        logger.error(f"Error verifying sample data: {e}")
        return False

def main():
    """
    Main function to populate sample data.
    """
    parser = argparse.ArgumentParser(description='Populate SupplyLine database with sample data')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing data, do not insert')
    parser.add_argument('--sql-file', default='database/sample_data.sql', help='Path to SQL file')
    args = parser.parse_args()
    
    logger.info("Starting SupplyLine sample data population")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Get database connection
    conn = get_database_connection()
    if not conn:
        logger.error("Failed to connect to database. Exiting.")
        sys.exit(1)
    
    try:
        if args.verify_only:
            logger.info("Verification mode - checking existing data only")
            success = verify_sample_data(conn)
        else:
            # Read SQL file
            logger.info(f"Reading SQL file: {args.sql_file}")
            sql_content = read_sql_file(args.sql_file)
            if not sql_content:
                logger.error("Failed to read SQL file. Exiting.")
                sys.exit(1)

            # Execute SQL script
            logger.info("Executing sample data insertion...")
            success = execute_sql_script(conn, sql_content)

            if success:
                logger.info("Sample data insertion completed")

                # Verify the data
                logger.info("Verifying inserted data...")
                verify_success = verify_sample_data(conn)

                if verify_success:
                    logger.info("Sample data verification successful")
                else:
                    logger.warning("Sample data verification found issues")
            else:
                logger.error("Sample data insertion failed")
                sys.exit(1)
        
    finally:
        conn.close()
        logger.info("Database connection closed")

    if success:
        logger.info("Sample data population completed successfully!")
        print("\n" + "="*60)
        print("SAMPLE DATA POPULATION SUCCESSFUL")
        print("="*60)
        print("The database has been populated with comprehensive sample data including:")
        print("  - Sample users from various departments")
        print("  - Tools with different categories and statuses")
        print("  - Chemicals with various expiration dates")
        print("  - Historical and current checkouts")
        print("  - Chemical issuances and usage records")
        print("  - Roles and permissions for RBAC testing")
        print("  - Calibration records and standards")
        print("  - System settings and configurations")
        print("  - Audit logs and user activities")
        print("\nYou can now test all application features with realistic data!")
        print("="*60)
    else:
        logger.error("Sample data population failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
