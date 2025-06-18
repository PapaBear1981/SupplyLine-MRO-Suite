#!/usr/bin/env python3
"""
Emergency migration script that can be run directly on the Cloud Run instance.
This script creates the missing database tables to fix issue #339.
"""

import os
import sys
import psycopg
from datetime import datetime

def run_emergency_migration():
    """Run the emergency database migration"""
    
    print("=== EMERGENCY DATABASE MIGRATION ===")
    print(f"Timestamp: {datetime.now()}")
    
    # Get database connection details from environment
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD', '').strip()
    db_name = os.environ.get('DB_NAME', 'supplyline')
    db_host = os.environ.get('DB_HOST')
    
    if not all([db_user, db_password, db_name, db_host]):
        return {
            'status': 'error',
            'message': 'Missing database environment variables',
            'details': {
                'DB_USER': bool(db_user),
                'DB_PASSWORD': bool(db_password),
                'DB_NAME': bool(db_name),
                'DB_HOST': bool(db_host)
            }
        }
    
    print(f"Connecting to database: {db_name} as {db_user}")
    print(f"Using host: {db_host}")
    
    try:
        # Connect to database
        if db_host.startswith('/cloudsql/'):
            # Unix socket connection
            conn = psycopg.connect(
                user=db_user,
                password=db_password,
                dbname=db_name,
                host=db_host
            )
        else:
            # TCP connection
            db_port = os.environ.get('DB_PORT', '5432')
            conn = psycopg.connect(
                user=db_user,
                password=db_password,
                dbname=db_name,
                host=db_host,
                port=db_port
            )
        
        print("✅ Connected to database successfully!")
        
        # Migration SQL
        migration_sql = """
        -- Create checkouts table
        CREATE TABLE IF NOT EXISTS checkouts (
            id SERIAL PRIMARY KEY,
            tool_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            return_date TIMESTAMP,
            expected_return_date TIMESTAMP,
            return_condition TEXT,
            returned_by TEXT,
            found BOOLEAN DEFAULT FALSE,
            return_notes TEXT,
            FOREIGN KEY (tool_id) REFERENCES tools(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Create user_activity table
        CREATE TABLE IF NOT EXISTS user_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Create announcements table
        CREATE TABLE IF NOT EXISTS announcements (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium',
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiration_date TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        -- Create announcement_reads table
        CREATE TABLE IF NOT EXISTS announcement_reads (
            id SERIAL PRIMARY KEY,
            announcement_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (announcement_id) REFERENCES announcements(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Create audit_log table (if it doesn't exist)
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            action_type TEXT NOT NULL,
            action_details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_checkouts_tool_id ON checkouts(tool_id);
        CREATE INDEX IF NOT EXISTS idx_checkouts_user_id ON checkouts(user_id);
        CREATE INDEX IF NOT EXISTS idx_checkouts_return_date ON checkouts(return_date);
        CREATE INDEX IF NOT EXISTS idx_checkouts_expected_return_date ON checkouts(expected_return_date);

        CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp);

        CREATE INDEX IF NOT EXISTS idx_announcements_created_by ON announcements(created_by);
        CREATE INDEX IF NOT EXISTS idx_announcements_is_active ON announcements(is_active);
        CREATE INDEX IF NOT EXISTS idx_announcements_expiration_date ON announcements(expiration_date);

        CREATE INDEX IF NOT EXISTS idx_announcement_reads_announcement_id ON announcement_reads(announcement_id);
        CREATE INDEX IF NOT EXISTS idx_announcement_reads_user_id ON announcement_reads(user_id);
        """
        
        # Execute migration
        with conn.cursor() as cursor:
            print("🔄 Executing migration SQL...")
            cursor.execute(migration_sql)
            conn.commit()
            print("✅ Migration executed successfully!")
            
            # Verify tables were created
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('checkouts', 'user_activity', 'announcements', 'announcement_reads', 'audit_log')
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            print(f"✅ Verified tables exist: {table_names}")
            
            conn.close()
            
            return {
                'status': 'success',
                'message': 'Database migration completed successfully!',
                'tables_created': table_names,
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return {
            'status': 'error',
            'message': f'Migration failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    result = run_emergency_migration()
    print(f"\nResult: {result}")
    if result['status'] == 'error':
        sys.exit(1)
