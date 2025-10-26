"""
E2E Test Data Seeding Script for SupplyLine MRO Suite

This script creates consistent test data specifically for E2E Playwright tests.
It ensures all test users, tools, chemicals, kits, and other entities exist
with predictable data that matches test expectations.

Usage:
    python seed_e2e_test_data.py

This script should be run before E2E tests to ensure a clean, consistent state.
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from flask import Flask
from models import (
    db, User, Tool, Chemical, Checkout, UserActivity, ToolCalibration,
    CalibrationStandard, AuditLog, Warehouse, Role
)
from models_kits import (
    AircraftType, Kit, KitBox, KitItem, KitExpendable,
    KitIssuance, KitTransfer, KitReorderRequest
)
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_time():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


def reset_database():
    """Drop all tables and recreate them"""
    logger.info("Resetting database...")
    db.drop_all()
    db.create_all()
    logger.info("Database reset complete")


def create_test_users():
    """Create test users that match E2E test expectations"""
    logger.info("Creating E2E test users...")
    
    users_data = [
        {
            'name': 'John Engineer',
            'employee_number': 'ADMIN001',
            'department': 'Engineering',
            'password': 'admin123',
            'is_admin': True
        },
        {
            'name': 'Regular User',
            'employee_number': 'USER001',
            'department': 'Maintenance',
            'password': 'user123',
            'is_admin': False
        },
        {
            'name': 'Materials Manager',
            'employee_number': 'MAT001',
            'department': 'Materials',
            'password': 'materials123',
            'is_admin': False
        },
        {
            'name': 'John Smith',
            'employee_number': 'MAINT001',
            'department': 'Maintenance',
            'password': 'password123',
            'is_admin': False
        },
        {
            'name': 'Engineering Tech',
            'employee_number': 'ENG001',
            'department': 'Engineering',
            'password': 'password123',
            'is_admin': False
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists (from RBAC migration)
        existing_user = User.query.filter_by(employee_number=user_data['employee_number']).first()
        if existing_user:
            logger.info(f"User already exists: {existing_user.name} ({existing_user.employee_number}), updating password...")
            existing_user.set_password(user_data['password'])
            created_users.append(existing_user)
        else:
            user = User(
                name=user_data['name'],
                employee_number=user_data['employee_number'],
                department=user_data['department'],
                is_admin=user_data['is_admin'],
                is_active=True,
                created_at=get_current_time()
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users.append(user)
            logger.info(f"Created user: {user.name} ({user.employee_number})")

    db.session.commit()

    # Assign roles to users
    logger.info("Assigning roles to test users...")
    admin_role = Role.query.filter_by(name='Administrator').first()
    maintenance_role = Role.query.filter_by(name='Maintenance User').first()
    materials_role = Role.query.filter_by(name='Materials Manager').first()

    for user in created_users:
        if user.employee_number == 'ADMIN001' and admin_role:
            if not user.has_role('Administrator'):
                user.add_role(admin_role)
                logger.info(f"  Assigned Administrator role to {user.name}")
        elif user.employee_number == 'USER001' and maintenance_role:
            if not user.has_role('Maintenance User'):
                user.add_role(maintenance_role)
                logger.info(f"  Assigned Maintenance User role to {user.name}")
        elif user.employee_number == 'MAT001' and materials_role:
            if not user.has_role('Materials Manager'):
                user.add_role(materials_role)
                logger.info(f"  Assigned Materials Manager role to {user.name}")
        elif user.employee_number in ['MAINT001', 'ENG001'] and maintenance_role:
            if not user.has_role('Maintenance User'):
                user.add_role(maintenance_role)
                logger.info(f"  Assigned Maintenance User role to {user.name}")

    db.session.commit()
    logger.info(f"Created {len(created_users)} test users with roles")
    return created_users


def create_test_warehouses(users):
    """Create test warehouses for E2E tests"""
    logger.info("Creating E2E test warehouses...")

    admin_user = next((u for u in users if u.is_admin), users[0])

    warehouses_data = [
        {
            'name': 'Main Warehouse',
            'address': '123 Main Street',
            'city': 'Seattle',
            'state': 'WA',
            'zip_code': '98101',
            'country': 'USA',
            'warehouse_type': 'main',
            'is_active': True
        },
        {
            'name': 'Satellite Warehouse A',
            'address': '456 Airport Road',
            'city': 'Portland',
            'state': 'OR',
            'zip_code': '97201',
            'country': 'USA',
            'warehouse_type': 'satellite',
            'is_active': True
        },
        {
            'name': 'Satellite Warehouse B',
            'address': '789 Hangar Drive',
            'city': 'Vancouver',
            'state': 'BC',
            'zip_code': 'V6B 1A1',
            'country': 'Canada',
            'warehouse_type': 'satellite',
            'is_active': True
        }
    ]

    created_warehouses = []
    for warehouse_data in warehouses_data:
        warehouse = Warehouse(
            name=warehouse_data['name'],
            address=warehouse_data['address'],
            city=warehouse_data['city'],
            state=warehouse_data['state'],
            zip_code=warehouse_data['zip_code'],
            country=warehouse_data['country'],
            warehouse_type=warehouse_data['warehouse_type'],
            is_active=warehouse_data['is_active'],
            created_by_id=admin_user.id,
            created_at=get_current_time(),
            updated_at=get_current_time()
        )
        db.session.add(warehouse)
        created_warehouses.append(warehouse)
        logger.info(f"Created warehouse: {warehouse.name}")

    db.session.commit()
    return created_warehouses


def create_test_tools(warehouses):
    """Create test tools for E2E tests"""
    logger.info("Creating E2E test tools...")

    # Use the main warehouse for tools
    main_warehouse = next((w for w in warehouses if w.warehouse_type == 'main'), warehouses[0])
    
    tools_data = [
        {
            'tool_number': 'T001',
            'serial_number': 'SN001',
            'description': 'Digital Multimeter',
            'condition': 'Good',
            'location': 'Tool Crib A-1',
            'category': 'Testing',
            'status': 'available'
        },
        {
            'tool_number': 'T002',
            'serial_number': 'SN002',
            'description': 'Torque Wrench',
            'condition': 'Excellent',
            'location': 'Tool Crib A-2',
            'category': 'Hand Tools',
            'status': 'available'
        },
        {
            'tool_number': 'T003',
            'serial_number': 'SN003',
            'description': 'Oscilloscope',
            'condition': 'Good',
            'location': 'Electronics Lab',
            'category': 'Testing',
            'status': 'checked_out'
        },
        {
            'tool_number': 'T004',
            'serial_number': 'SN004',
            'description': 'Impact Wrench',
            'condition': 'Good',
            'location': 'Shop Floor',
            'category': 'Power Tools',
            'status': 'available'
        },
        {
            'tool_number': 'T005',
            'serial_number': 'SN005',
            'description': 'Micrometer',
            'condition': 'Excellent',
            'location': 'Quality Lab',
            'category': 'Measuring Tools',
            'status': 'available'
        }
    ]
    
    created_tools = []
    for tool_data in tools_data:
        tool = Tool(
            tool_number=tool_data['tool_number'],
            serial_number=tool_data['serial_number'],
            description=tool_data['description'],
            condition=tool_data['condition'],
            location=tool_data['location'],
            category=tool_data['category'],
            status=tool_data['status'],
            warehouse_id=main_warehouse.id,  # Assign to main warehouse
            created_at=get_current_time()
        )
        db.session.add(tool)
        created_tools.append(tool)
        logger.info(f"Created tool: {tool.tool_number} - {tool.description}")
    
    db.session.commit()
    return created_tools


def create_test_chemicals(warehouses):
    """Create test chemicals for E2E tests"""
    logger.info("Creating E2E test chemicals...")

    # Use the main warehouse for chemicals
    main_warehouse = next((w for w in warehouses if w.warehouse_type == 'main'), warehouses[0])
    
    chemicals_data = [
        {
            'part_number': 'CHEM001',
            'lot_number': 'LOT001',
            'description': 'Cleaning Solvent',
            'manufacturer': 'ChemCo',
            'quantity': 10.0,
            'unit': 'gallons',
            'location': 'Chemical Storage A',
            'category': 'Cleaners',
            'status': 'available'
        },
        {
            'part_number': 'CHEM002',
            'lot_number': 'LOT002',
            'description': 'Lubricant',
            'manufacturer': 'LubeCo',
            'quantity': 5.0,
            'unit': 'quarts',
            'location': 'Chemical Storage B',
            'category': 'Lubricants',
            'status': 'available'
        }
    ]
    
    created_chemicals = []
    for chem_data in chemicals_data:
        chemical = Chemical(
            part_number=chem_data['part_number'],
            lot_number=chem_data['lot_number'],
            description=chem_data['description'],
            manufacturer=chem_data['manufacturer'],
            quantity=chem_data['quantity'],
            unit=chem_data['unit'],
            location=chem_data['location'],
            category=chem_data['category'],
            status=chem_data['status'],
            warehouse_id=main_warehouse.id,  # Assign to main warehouse
            date_added=get_current_time()
        )
        db.session.add(chemical)
        created_chemicals.append(chemical)
        logger.info(f"Created chemical: {chemical.part_number} - {chemical.description}")
    
    db.session.commit()
    return created_chemicals


def create_test_checkouts(users, tools):
    """Create test checkouts for E2E tests"""
    logger.info("Creating E2E test checkouts...")
    
    if not users or not tools:
        logger.warning("No users or tools available for creating checkouts")
        return []
    
    # Create an active checkout
    admin_user = next((u for u in users if u.employee_number == 'ADMIN001'), None)
    checked_out_tool = next((t for t in tools if t.status == 'checked_out'), None)
    
    if admin_user and checked_out_tool:
        checkout = Checkout(
            tool_id=checked_out_tool.id,
            user_id=admin_user.id,
            checkout_date=get_current_time() - timedelta(days=2),
            expected_return_date=get_current_time() + timedelta(days=5)
        )
        db.session.add(checkout)
        logger.info(f"Created checkout: {checked_out_tool.tool_number} to {admin_user.employee_number}")
    
    db.session.commit()
    return [checkout] if admin_user and checked_out_tool else []


def create_test_aircraft_types():
    """Create test aircraft types for kit tests"""
    logger.info("Creating E2E test aircraft types...")

    aircraft_types_data = [
        {'name': 'Boeing 737', 'description': 'B737 - Narrow-body aircraft'},
        {'name': 'Airbus A320', 'description': 'A320 - Narrow-body aircraft'},
        {'name': 'Bombardier Q400', 'description': 'Q400 - Turboprop aircraft'}
    ]

    created_types = []
    for type_data in aircraft_types_data:
        aircraft_type = AircraftType(
            name=type_data['name'],
            description=type_data['description'],
            created_at=get_current_time()
        )
        db.session.add(aircraft_type)
        created_types.append(aircraft_type)
        logger.info(f"Created aircraft type: {aircraft_type.name}")

    db.session.commit()
    return created_types


def create_test_kits(aircraft_types, users):
    """Create test kits for E2E tests"""
    logger.info("Creating E2E test kits...")
    
    if not aircraft_types or not users:
        logger.warning("No aircraft types or users available for creating kits")
        return []
    
    admin_user = next((u for u in users if u.is_admin), None)
    if not admin_user:
        logger.warning("No admin user found for creating kits")
        return []
    
    # Create a test kit for each aircraft type
    created_kits = []
    kit_codes = ['B737', 'A320', 'Q400']
    for idx, aircraft_type in enumerate(aircraft_types[:2]):  # Create 2 kits
        code = kit_codes[idx] if idx < len(kit_codes) else f'AC{idx}'
        kit = Kit(
            name=f'Kit {aircraft_type.name} - 001',
            aircraft_type_id=aircraft_type.id,
            description=f'Test kit for {aircraft_type.name}',
            status='active',
            created_by=admin_user.id,
            created_at=get_current_time()
        )
        db.session.add(kit)
        created_kits.append(kit)
        logger.info(f"Created kit: {kit.name}")

    db.session.commit()
    return created_kits


def main():
    """Main function to seed E2E test data"""
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            logger.info("=" * 60)
            logger.info("Starting E2E Test Data Seeding")
            logger.info("=" * 60)
            
            # Reset database to clean state
            reset_database()

            # Run RBAC migrations to set up roles and permissions
            logger.info("Running RBAC migrations...")
            try:
                import subprocess
                migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

                # Run RBAC tables migration
                rbac_migration = os.path.join(migrations_dir, 'add_rbac_tables.py')
                result = subprocess.run([sys.executable, rbac_migration], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"RBAC tables migration failed with exit code {result.returncode}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

                # Run page access permissions migration
                page_perms_migration = os.path.join(migrations_dir, 'add_page_access_permissions.py')
                result = subprocess.run([sys.executable, page_perms_migration], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Page access permissions migration failed with exit code {result.returncode}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

                logger.info("RBAC migration completed")
            except Exception as e:
                logger.exception("Migration failed: %s", e)

            # Create test data
            users = create_test_users()
            warehouses = create_test_warehouses(users)
            tools = create_test_tools(warehouses)
            chemicals = create_test_chemicals(warehouses)
            checkouts = create_test_checkouts(users, tools)
            aircraft_types = create_test_aircraft_types()
            kits = create_test_kits(aircraft_types, users)

            logger.info("=" * 60)
            logger.info("E2E Test Data Seeding Complete!")
            logger.info("=" * 60)
            logger.info(f"Users created: {len(users)}")
            logger.info(f"Warehouses created: {len(warehouses)}")
            logger.info(f"Tools created: {len(tools)}")
            logger.info(f"Chemicals created: {len(chemicals)}")
            logger.info(f"Checkouts created: {len(checkouts)}")
            logger.info(f"Aircraft types created: {len(aircraft_types)}")
            logger.info(f"Kits created: {len(kits)}")
            logger.info("=" * 60)
            logger.info("Test Login Credentials:")
            logger.info("Admin: ADMIN001 / admin123")
            logger.info("User: USER001 / user123")
            logger.info("Materials: MAT001 / materials123")
            logger.info("=" * 60)
            
            return True
            
    except Exception as e:
        logger.error(f"E2E test data seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if main():
        logger.info("E2E test data seeding completed successfully!")
        sys.exit(0)
    else:
        logger.error("E2E test data seeding failed!")
        sys.exit(1)

