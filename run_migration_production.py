#!/usr/bin/env python3
"""
Production database migration script for SupplyLine MRO Suite
This script connects directly to the production PostgreSQL database and creates missing tables.
"""

import os
import sys
import psycopg
from datetime import datetime

def get_production_db_connection():
    """Get connection to production database using environment variables"""
    
    # Production database connection details
    # These should match the Cloud Run environment variables
    db_config = {
        'user': 'supplyline_user',
        'password': 'SupplyLine2024!',  # Production password
        'dbname': 'supplyline',
        'host': '/cloudsql/supplyline-mro-suite:us-west1:supplyline-db'  # Unix socket
    }
    
    print(f"Connecting to database: {db_config['dbname']} as {db_config['user']}")
    print(f"Using Unix socket: {db_config['host']}")
    
    try:
        # Connect using psycopg (version 3)
        conn = psycopg.connect(
            user=db_config['user'],
            password=db_config['password'],
            dbname=db_config['dbname'],
            host=db_config['host']
        )
        print("✅ Successfully connected to production database!")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to production database: {e}")
        return None

def run_migration_sql(conn):
    """Run the migration SQL to create missing tables"""
    
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
    
    try:
        with conn.cursor() as cursor:
            print("🔄 Running database migration...")
            cursor.execute(migration_sql)
            conn.commit()
            print("✅ Migration SQL executed successfully!")
            
            # Verify tables were created
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('checkouts', 'user_activity', 'announcements', 'announcement_reads', 'audit_log')
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            print(f"✅ Verified tables exist: {[table[0] for table in tables]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        conn.rollback()
        return False

def test_api_endpoints():
    """Test the API endpoints to see if they're working now"""
    import requests
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    # Test endpoints without authentication (should get 401, not 500)
    endpoints = [
        "/api/checkouts/overdue",
        "/api/checkouts/user", 
        "/api/user/activity",
        "/api/announcements"
    ]
    
    print("\n🧪 Testing API endpoints...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            if response.status_code == 401:
                print(f"✅ {endpoint}: {response.status_code} (Authentication required - table exists!)")
            elif response.status_code == 500:
                print(f"❌ {endpoint}: {response.status_code} (Still broken - table missing)")
            else:
                print(f"ℹ️  {endpoint}: {response.status_code} - {response.text[:50]}")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {e}")

def main():
    """Main migration function"""
    print("=== SupplyLine MRO Suite Database Migration ===")
    print(f"Timestamp: {datetime.now()}")
    print("Target: Production PostgreSQL database")
    
    # Connect to database
    conn = get_production_db_connection()
    if not conn:
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    try:
        # Run migration
        success = run_migration_sql(conn)
        
        if success:
            print("\n🎉 Database migration completed successfully!")
            print("The following API endpoints should now work:")
            print("- /api/checkouts/overdue")
            print("- /api/checkouts/user")
            print("- /api/user/activity")
            print("- /api/announcements")
            
            # Test endpoints
            test_api_endpoints()
            
        else:
            print("\n❌ Database migration failed!")
            sys.exit(1)
            
    finally:
        conn.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
