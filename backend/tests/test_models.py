"""
Tests for database models
"""

import pytest
from datetime import datetime, timedelta, timezone
from models import User, Tool, Chemical, Checkout, Role, Permission, UserRole, RolePermission
from werkzeug.security import check_password_hash


class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            name='Test User',
            employee_number='TEST001',
            department='Testing',
            is_admin=False,
            is_active=True
        )
        user.set_password('testpassword123')
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.name == 'Test User'
        assert user.employee_number == 'TEST001'
        assert user.check_password('testpassword123')
        assert not user.check_password('wrongpassword')
    
    def test_user_password_hashing(self, db_session):
        """Test password hashing and verification"""
        user = User(
            name='Password Test',
            employee_number='PASS001',
            department='Testing'
        )
        
        password = 'securepassword123!'
        user.set_password(password)
        
        # Password should be hashed
        assert user.password_hash != password
        assert len(user.password_hash) > 50  # Hashed passwords are long
        
        # Should verify correctly
        assert user.check_password(password)
        assert not user.check_password('wrongpassword')
    
    def test_user_reset_token(self, db_session):
        """Test password reset token functionality"""
        user = User(
            name='Reset Test',
            employee_number='RESET001',
            department='Testing'
        )
        user.set_password('test123')
        db_session.add(user)
        db_session.commit()
        
        # Generate reset token
        token = user.generate_reset_token()
        
        assert token is not None
        assert len(token) == 6  # 6-digit code
        assert token.isdigit()
        assert user.reset_token is not None
        assert user.reset_token_expiry is not None
        
        # Verify token
        assert user.check_reset_token(token)
        assert not user.check_reset_token('123456')
        
        # Clear token
        user.clear_reset_token()
        assert user.reset_token is None
        assert user.reset_token_expiry is None
    
    def test_user_remember_token(self, db_session):
        """Test remember me token functionality"""
        user = User(
            name='Remember Test',
            employee_number='REMEMBER001',
            department='Testing'
        )
        user.set_password('test123')
        db_session.add(user)
        db_session.commit()
        
        # Generate remember token
        token = user.generate_remember_token()
        
        assert token is not None
        assert len(token) == 64  # 32 bytes hex = 64 chars
        assert user.remember_token is not None
        assert user.remember_token_expiry is not None
        
        # Verify token
        assert user.check_remember_token(token)
        assert not user.check_remember_token('invalid_token')
        
        # Clear token
        user.clear_remember_token()
        assert user.remember_token is None
        assert user.remember_token_expiry is None
    
    def test_user_account_lockout(self, db_session):
        """Test account lockout functionality"""
        user = User(
            name='Lockout Test',
            employee_number='LOCKOUT001',
            department='Testing'
        )
        user.set_password('test123')
        db_session.add(user)
        db_session.commit()
        
        # Initially not locked
        assert not user.is_locked()
        assert not user.is_account_locked()
        assert user.failed_login_attempts == 0
        
        # Increment failed attempts
        user.increment_failed_login()
        assert user.failed_login_attempts == 1
        assert user.last_failed_login is not None
        
        # Lock account
        user.lock_account(minutes=15)
        assert user.is_locked()
        assert user.is_account_locked()
        assert user.account_locked_until is not None
        
        # Check remaining time
        remaining = user.get_lockout_remaining_time()
        assert remaining > 0
        assert remaining <= 15 * 60  # 15 minutes in seconds
        
        # Unlock account
        user.unlock_account()
        assert not user.is_locked()
        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None
    
    def test_user_to_dict(self, db_session):
        """Test user serialization"""
        user = User(
            name='Dict Test',
            employee_number='DICT001',
            department='Testing',
            is_admin=True,
            is_active=True
        )
        user.set_password('test123')
        db_session.add(user)
        db_session.commit()
        
        # Basic serialization
        data = user.to_dict()
        
        assert data['name'] == 'Dict Test'
        assert data['employee_number'] == 'DICT001'
        assert data['department'] == 'Testing'
        assert data['is_admin'] is True
        assert data['is_active'] is True
        assert 'created_at' in data
        
        # With lockout info
        data_with_lockout = user.to_dict(include_lockout_info=True)
        
        assert 'failed_login_attempts' in data_with_lockout
        assert 'account_locked' in data_with_lockout


class TestToolModel:
    """Test Tool model functionality"""
    
    def test_create_tool(self, db_session):
        """Test creating a tool"""
        tool = Tool(
            tool_number='T001',
            serial_number='S001',
            description='Test Tool',
            condition='Good',
            location='Lab A',
            category='Testing',
            status='available'
        )
        
        db_session.add(tool)
        db_session.commit()
        
        assert tool.id is not None
        assert tool.tool_number == 'T001'
        assert tool.status == 'available'
        assert tool.created_at is not None
    
    def test_tool_calibration_status(self, db_session):
        """Test tool calibration status updates"""
        tool = Tool(
            tool_number='T002',
            serial_number='S002',
            description='Calibrated Tool',
            requires_calibration=True,
            calibration_frequency_days=365
        )
        
        # Set next calibration date in the future (more than 30 days)
        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        tool.next_calibration_date = future_date

        tool.update_calibration_status()
        assert tool.calibration_status == 'current'
        
        # Set next calibration date in near future (due soon)
        soon_date = datetime.now(timezone.utc) + timedelta(days=15)
        tool.next_calibration_date = soon_date
        
        tool.update_calibration_status()
        assert tool.calibration_status == 'due_soon'
        
        # Set next calibration date in the past (overdue)
        past_date = datetime.now(timezone.utc) - timedelta(days=10)
        tool.next_calibration_date = past_date
        
        tool.update_calibration_status()
        assert tool.calibration_status == 'overdue'
    
    def test_tool_to_dict(self, db_session):
        """Test tool serialization"""
        tool = Tool(
            tool_number='T003',
            serial_number='S003',
            description='Serialization Test Tool',
            condition='Excellent',
            location='Lab B',
            category='Testing',
            status='available'
        )
        
        db_session.add(tool)
        db_session.commit()
        
        data = tool.to_dict()
        
        assert data['tool_number'] == 'T003'
        assert data['description'] == 'Serialization Test Tool'
        assert data['condition'] == 'Excellent'
        assert data['status'] == 'available'
        assert 'created_at' in data


class TestChemicalModel:
    """Test Chemical model functionality"""
    
    def test_create_chemical(self, db_session):
        """Test creating a chemical"""
        chemical = Chemical(
            part_number='C001',
            lot_number='L001',
            description='Test Chemical',
            manufacturer='Test Manufacturer',
            quantity=100.0,
            unit='ml',
            location='Storage A',
            category='Testing',
            status='available'
        )
        
        db_session.add(chemical)
        db_session.commit()
        
        assert chemical.id is not None
        assert chemical.part_number == 'C001'
        assert chemical.quantity == 100.0
        assert chemical.status == 'available'
    
    def test_chemical_expiration(self, db_session):
        """Test chemical expiration functionality"""
        chemical = Chemical(
            part_number='C002',
            lot_number='L002',
            description='Expiring Chemical',
            quantity=50.0,
            unit='ml'
        )
        
        # Set expiration date in the past
        past_date = datetime.now(timezone.utc) - timedelta(days=10)
        chemical.expiration_date = past_date
        
        assert chemical.is_expired()
        
        # Set expiration date in the future
        future_date = datetime.now(timezone.utc) + timedelta(days=10)
        chemical.expiration_date = future_date
        
        assert not chemical.is_expired()
        assert chemical.is_expiring_soon(30)  # Within 30 days
        assert not chemical.is_expiring_soon(5)  # Not within 5 days
    
    def test_chemical_low_stock(self, db_session):
        """Test chemical low stock detection"""
        chemical = Chemical(
            part_number='C003',
            lot_number='L003',
            description='Low Stock Chemical',
            quantity=5.0,
            unit='ml',
            minimum_stock_level=10.0
        )
        
        assert chemical.is_low_stock()
        
        chemical.quantity = 15.0
        assert not chemical.is_low_stock()


class TestCheckoutModel:
    """Test Checkout model functionality"""
    
    def test_create_checkout(self, db_session, test_tool, regular_user):
        """Test creating a checkout"""
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            expected_return_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        db_session.add(checkout)
        db_session.commit()
        
        assert checkout.id is not None
        assert checkout.tool_id == test_tool.id
        assert checkout.user_id == regular_user.id
        assert checkout.checkout_date is not None
        assert checkout.return_date is None  # Not returned yet


class TestRolePermissionModel:
    """Test Role and Permission models"""
    
    def test_create_role_with_permissions(self, db_session):
        """Test creating roles with permissions"""
        # Create permissions
        view_perm = Permission(name='view_tools', description='View tools')
        manage_perm = Permission(name='manage_tools', description='Manage tools')
        
        db_session.add(view_perm)
        db_session.add(manage_perm)
        db_session.flush()
        
        # Create role
        admin_role = Role(name='admin', description='Administrator')
        db_session.add(admin_role)
        db_session.flush()
        
        # Add permissions to role
        role_perm1 = RolePermission(role_id=admin_role.id, permission_id=view_perm.id)
        role_perm2 = RolePermission(role_id=admin_role.id, permission_id=manage_perm.id)
        
        db_session.add(role_perm1)
        db_session.add(role_perm2)
        db_session.commit()
        
        # Verify relationships
        assert len(admin_role.permissions) == 2
        assert view_perm in admin_role.permissions
        assert manage_perm in admin_role.permissions
