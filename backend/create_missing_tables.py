#!/usr/bin/env python3
"""
Database migration script to create missing tables that are causing 500 errors.
This script uses SQLAlchemy and the Flask app context to create tables in a 
database-agnostic way (works with both SQLite and PostgreSQL).
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Tool, Checkout, UserActivity, Announcement, AnnouncementRead
from models import AuditLog, ToolCalibration, CalibrationStandard, ToolCalibrationStandard
from models import Chemical, ChemicalIssuance, ToolServiceRecord

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    try:
        # Try to query the table - if it doesn't exist, this will raise an exception
        result = db.engine.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        result.close()
        return True
    except Exception:
        return False

def get_existing_tables():
    """Get list of existing tables in the database"""
    try:
        # Get table names from the database metadata
        inspector = db.inspect(db.engine)
        return inspector.get_table_names()
    except Exception as e:
        print(f"Error getting table names: {e}")
        return []

def create_missing_tables():
    """Create any missing tables using SQLAlchemy models"""
    
    print("=== Database Migration: Creating Missing Tables ===")
    print(f"Timestamp: {datetime.now()}")
    
    # Create Flask app and get database context
    app = create_app()
    
    with app.app_context():
        print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        
        # Get existing tables before migration
        existing_tables_before = get_existing_tables()
        print(f"Existing tables before migration: {existing_tables_before}")
        
        # List of all model classes that should have tables
        required_models = [
            ('users', User),
            ('tools', Tool),
            ('checkouts', Checkout),
            ('user_activity', UserActivity),
            ('announcements', Announcement),
            ('announcement_reads', AnnouncementRead),
            ('audit_log', AuditLog),
            ('tool_calibrations', ToolCalibration),
            ('calibration_standards', CalibrationStandard),
            ('tool_calibration_standards', ToolCalibrationStandard),
            ('chemicals', Chemical),
            ('chemical_issuances', ChemicalIssuance),
            ('tool_service_records', ToolServiceRecord)
        ]
        
        # Check which tables are missing
        missing_tables = []
        for table_name, model_class in required_models:
            if table_name not in existing_tables_before:
                missing_tables.append((table_name, model_class))
                print(f"❌ Missing table: {table_name}")
            else:
                print(f"✅ Table exists: {table_name}")
        
        if not missing_tables:
            print("🎉 All required tables already exist!")
            return True
        
        print(f"\n📝 Creating {len(missing_tables)} missing tables...")
        
        try:
            # Create all tables defined in models
            # This is safe to run multiple times - it only creates missing tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Verify tables were created
            existing_tables_after = get_existing_tables()
            print(f"Existing tables after migration: {existing_tables_after}")
            
            # Check if all required tables now exist
            success = True
            for table_name, _ in required_models:
                if table_name in existing_tables_after:
                    print(f"✅ Verified: {table_name} table exists")
                else:
                    print(f"❌ Failed: {table_name} table still missing")
                    success = False
            
            if success:
                print("\n🎉 Migration completed successfully!")
                print("All required tables are now present in the database.")
                
                # Test database connectivity with a simple query
                try:
                    user_count = User.query.count()
                    print(f"✅ Database connectivity test passed. User count: {user_count}")
                except Exception as e:
                    print(f"⚠️  Database connectivity test failed: {e}")
                    
            else:
                print("\n❌ Migration completed with errors!")
                print("Some tables are still missing.")
                
            return success
            
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function to run the migration"""
    try:
        success = create_missing_tables()
        if success:
            print("\n✅ Migration script completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Migration script failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_migration_web():
    """Web-accessible function to run the migration"""
    try:
        success = create_missing_tables()
        if success:
            return {"status": "success", "message": "Migration completed successfully!"}
        else:
            return {"status": "error", "message": "Migration failed!"}
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"Fatal error: {str(e)}",
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    main()
