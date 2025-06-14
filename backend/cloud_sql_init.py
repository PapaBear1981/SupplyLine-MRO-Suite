#!/usr/bin/env python3
"""
Cloud SQL Database Initialization Script for SupplyLine MRO Suite

This script initializes the PostgreSQL database on Google Cloud SQL
with the required tables and initial data.
"""

import os
import sys
from app import create_app
from models import db, User, Tool, AuditLog

def init_cloud_sql():
    """Initialize Cloud SQL database with tables and initial data."""
    
    # Ensure we're using the production configuration
    os.environ['FLASK_ENV'] = 'production'
    
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Create all tables
            db.create_all()
            print("✓ Database tables created")
            
            # Check if admin user already exists
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            if not admin_user:
                # Create admin user securely
                from utils.admin_init import create_secure_admin
                success, message, password = create_secure_admin()
                if success:
                    print(f"✓ Admin creation: {message}")
                    if password:
                        print(f"⚠️  IMPORTANT: Generated admin password: {password}")
                        print("⚠️  Please save this password securely!")
                else:
                    print(f"✗ Admin creation failed: {message}")
                    return False
            else:
                print("✓ Admin user already exists")
            
            # Create sample users if they don't exist
            sample_users = [
                ('John Doe', 'EMP001', 'Maintenance'),
                ('Jane Smith', 'EMP002', 'Maintenance'),
                ('Bob Johnson', 'EMP003', 'Materials'),
                ('Alice Brown', 'EMP004', 'Engineering')
            ]
            
            users_created = 0
            for name, emp_num, dept in sample_users:
                if not User.query.filter_by(employee_number=emp_num).first():
                    user = User(name=name, employee_number=emp_num, department=dept)
                    user.set_password('password123')
                    db.session.add(user)
                    users_created += 1
            
            if users_created > 0:
                db.session.commit()
                print(f"✓ Created {users_created} sample users")
            else:
                print("✓ Sample users already exist")
            
            # Create sample tools if they don't exist
            sample_tools = [
                ('T001', 'SN001', 'Wrench Set', 'Good', 'Toolbox A'),
                ('T002', 'SN002', 'Screwdriver Set', 'New', 'Toolbox B'),
                ('T003', 'SN003', 'Drill', 'Fair', 'Shelf C'),
                ('T004', 'SN004', 'Hammer', 'Good', 'Toolbox A'),
                ('T005', 'SN005', 'Saw', 'Poor', 'Shelf D'),
                ('T006', 'SN006', 'Pliers', 'Good', 'Toolbox B'),
                ('T007', 'SN007', 'Measuring Tape', 'New', 'Drawer E'),
                ('T008', 'SN008', 'Level', 'Good', 'Shelf C'),
                ('T009', 'SN009', 'Socket Set', 'Fair', 'Toolbox A'),
                ('T010', 'SN010', 'Allen Wrench Set', 'Good', 'Drawer E')
            ]
            
            tools_created = 0
            for tool_num, serial, desc, condition, location in sample_tools:
                if not Tool.query.filter_by(tool_number=tool_num).first():
                    tool = Tool(
                        tool_number=tool_num,
                        serial_number=serial,
                        description=desc,
                        condition=condition,
                        location=location
                    )
                    db.session.add(tool)
                    tools_created += 1
            
            if tools_created > 0:
                db.session.commit()
                print(f"✓ Created {tools_created} sample tools")
            else:
                print("✓ Sample tools already exist")
            
            # Create initial audit log entry
            if not AuditLog.query.first():
                initial_log = AuditLog(
                    action_type='system_init',
                    action_details='Cloud SQL database initialized'
                )
                db.session.add(initial_log)
                db.session.commit()
                print("✓ Initial audit log created")
            else:
                print("✓ Audit logs already exist")
            
            print("\n🎉 Cloud SQL database initialization completed successfully!")
            print("\nNext steps:")
            print("1. Update your Cloud Run service environment variables")
            print("2. Deploy your application")
            print("3. Test the application with the admin credentials")
            
            return True
            
        except Exception as e:
            print(f"✗ Database initialization failed: {str(e)}")
            return False

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("✗ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables and try again.")
        return False
    
    print("✓ All required environment variables are set")
    return True

if __name__ == "__main__":
    print("SupplyLine MRO Suite - Cloud SQL Database Initialization")
    print("=" * 60)
    
    if not check_environment():
        sys.exit(1)
    
    if init_cloud_sql():
        sys.exit(0)
    else:
        sys.exit(1)
