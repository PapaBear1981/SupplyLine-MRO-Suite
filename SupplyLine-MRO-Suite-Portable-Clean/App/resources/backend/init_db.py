from app import create_app
from models import db, User, Tool, Checkout, AuditLog
from datetime import datetime, timedelta
import os

def init_db():
    app = create_app()
    with app.app_context():
        # Check if database directory exists, create if not
        db_dir = os.path.join('/app', 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created database directory: {db_dir}")

        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        print("Database tables created")

        # Create admin user securely
        from utils.admin_init import create_secure_admin
        success, message, password = create_secure_admin()
        if success:
            print(f"Admin creation: {message}")
            if password:
                print(f"IMPORTANT: Generated admin password: {password}")
        else:
            print(f"Admin creation failed: {message}")
            return

        # Create test users
        test_users = [
            User(name='John Doe', employee_number='EMP001', department='Maintenance'),
            User(name='Jane Smith', employee_number='EMP002', department='Maintenance'),
            User(name='Bob Johnson', employee_number='EMP003', department='Materials'),
            User(name='Alice Brown', employee_number='EMP004', department='Engineering')
        ]

        for user in test_users:
            user.set_password('password123')
            db.session.add(user)

        db.session.commit()
        print("Users created")

        # Create test tools
        tools = [
            Tool(tool_number='T001', serial_number='SN001', description='Wrench Set', condition='Good', location='Toolbox A'),
            Tool(tool_number='T002', serial_number='SN002', description='Screwdriver Set', condition='New', location='Toolbox B'),
            Tool(tool_number='T003', serial_number='SN003', description='Drill', condition='Fair', location='Shelf C'),
            Tool(tool_number='T004', serial_number='SN004', description='Hammer', condition='Good', location='Toolbox A'),
            Tool(tool_number='T005', serial_number='SN005', description='Saw', condition='Poor', location='Shelf D'),
            Tool(tool_number='T006', serial_number='SN006', description='Pliers', condition='Good', location='Toolbox B'),
            Tool(tool_number='T007', serial_number='SN007', description='Measuring Tape', condition='New', location='Drawer E'),
            Tool(tool_number='T008', serial_number='SN008', description='Level', condition='Good', location='Shelf C'),
            Tool(tool_number='T009', serial_number='SN009', description='Socket Set', condition='Fair', location='Toolbox A'),
            Tool(tool_number='T010', serial_number='SN010', description='Allen Wrench Set', condition='Good', location='Drawer E')
        ]

        for tool in tools:
            db.session.add(tool)

        db.session.commit()
        print("Tools created")

        # Create some checkouts
        now = datetime.utcnow()
        checkouts = [
            # Active checkouts
            Checkout(tool_id=1, user_id=2, checkout_date=now - timedelta(days=2), expected_return_date=now + timedelta(days=5)),
            Checkout(tool_id=3, user_id=3, checkout_date=now - timedelta(days=1), expected_return_date=now + timedelta(days=3)),
            Checkout(tool_id=5, user_id=4, checkout_date=now - timedelta(days=3), expected_return_date=now - timedelta(days=1)),  # Overdue

            # Returned checkouts
            Checkout(tool_id=2, user_id=2, checkout_date=now - timedelta(days=10), return_date=now - timedelta(days=8), expected_return_date=now - timedelta(days=5)),
            Checkout(tool_id=4, user_id=3, checkout_date=now - timedelta(days=15), return_date=now - timedelta(days=12), expected_return_date=now - timedelta(days=10)),
            Checkout(tool_id=6, user_id=4, checkout_date=now - timedelta(days=20), return_date=now - timedelta(days=18), expected_return_date=now - timedelta(days=15))
        ]

        for checkout in checkouts:
            db.session.add(checkout)

        db.session.commit()
        print("Checkouts created")

        # Create audit logs
        audit_logs = [
            AuditLog(action_type='user_login', action_details='User 1 (Admin) logged in'),
            AuditLog(action_type='checkout_tool', action_details='User John Doe (ID: 2) checked out tool T001 (ID: 1)'),
            AuditLog(action_type='checkout_tool', action_details='User Bob Johnson (ID: 3) checked out tool T003 (ID: 3)'),
            AuditLog(action_type='checkout_tool', action_details='User Alice Brown (ID: 4) checked out tool T005 (ID: 5)'),
            AuditLog(action_type='return_tool', action_details='User John Doe (ID: 2) returned tool T002 (ID: 2)'),
            AuditLog(action_type='return_tool', action_details='User Bob Johnson (ID: 3) returned tool T004 (ID: 4)'),
            AuditLog(action_type='return_tool', action_details='User Alice Brown (ID: 4) returned tool T006 (ID: 6)'),
            AuditLog(action_type='create_tool', action_details='Created tool 10 (T010)')
        ]

        for log in audit_logs:
            db.session.add(log)

        db.session.commit()
        print("Audit logs created")

        print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
