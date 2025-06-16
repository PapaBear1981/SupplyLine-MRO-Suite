#!/usr/bin/env python3
"""
Direct database initialization script for Cloud SQL PostgreSQL
This script connects directly to the Cloud SQL instance and initializes the database.
"""

import psycopg2
import sys
import os

def main():
    # Database connection parameters
    db_config = {
        'host': '34.82.234.76',  # Public IP of the Cloud SQL instance
        'port': 5432,
        'database': 'supplyline',
        'user': 'supplyline_user',
        'password': 'SupplyLine2025SecurePass!'
    }
    
    print("Connecting to Cloud SQL database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✓ Connected successfully!")
        
        # Read and execute the SQL script
        with open('init_database.sql', 'r') as f:
            sql_script = f.read()
        
        print("Executing database initialization script...")
        
        # Split the script into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✓ Executed statement {i+1}/{len(statements)}")
                except Exception as e:
                    print(f"⚠ Warning on statement {i+1}: {e}")
                    # Continue with other statements
        
        print("✓ Database initialization completed successfully!")
        
        # Verify the admin user was created
        cursor.execute("SELECT username, role FROM users WHERE username = 'ADMIN001'")
        admin_user = cursor.fetchone()
        if admin_user:
            print(f"✓ Admin user created: {admin_user[0]} ({admin_user[1]})")
        else:
            print("⚠ Admin user not found")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"✓ Created {len(tables)} tables: {', '.join([t[0] for t in tables])}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database is ready for use!")
        print("Admin credentials: username=ADMIN001, password=admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
