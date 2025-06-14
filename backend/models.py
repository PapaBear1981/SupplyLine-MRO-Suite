from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.associationproxy import association_proxy

# Import time utilities for consistent time handling
try:
    from time_utils import get_local_timestamp
    def get_current_time():
        return get_local_timestamp()
except ImportError:
    def get_current_time():
        return datetime.now()

db = SQLAlchemy()

class Tool(db.Model):
    __tablename__ = 'tools'
    id = db.Column(db.Integer, primary_key=True)
    tool_number = db.Column(db.String, nullable=False)
    serial_number = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    condition = db.Column(db.String)
    location = db.Column(db.String)
    category = db.Column(db.String, nullable=True, default='General')
    status = db.Column(db.String, nullable=True, default='available')  # available, checked_out, maintenance, retired
    status_reason = db.Column(db.String, nullable=True)  # Reason for maintenance or retirement
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Calibration fields
    requires_calibration = db.Column(db.Boolean, default=False)
    calibration_frequency_days = db.Column(db.Integer, nullable=True)
    last_calibration_date = db.Column(db.DateTime, nullable=True)
    next_calibration_date = db.Column(db.DateTime, nullable=True)
    calibration_status = db.Column(db.String, nullable=True)  # current, due_soon, overdue, not_applicable

    def to_dict(self):
        return {
            'id': self.id,
            'tool_number': self.tool_number,
            'serial_number': self.serial_number,
            'description': self.description,
            'condition': self.condition,
            'location': self.location,
            'category': self.category,
            'status': self.status,
            'status_reason': self.status_reason,
            'created_at': self.created_at.isoformat(),
            'requires_calibration': self.requires_calibration,
            'calibration_frequency_days': self.calibration_frequency_days,
            'last_calibration_date': self.last_calibration_date.isoformat() if self.last_calibration_date else None,
            'next_calibration_date': self.next_calibration_date.isoformat() if self.next_calibration_date else None,
            'calibration_status': self.calibration_status
        }

    def update_calibration_status(self):
        """Update the calibration status based on next_calibration_date"""
        if not self.requires_calibration or not self.next_calibration_date:
            self.calibration_status = 'not_applicable'
            return

        now = get_current_time()

        # If calibration is overdue
        if now > self.next_calibration_date:
            self.calibration_status = 'overdue'
            return

        # If calibration is due within 30 days
        due_soon_threshold = now + timedelta(days=30)
        if now <= self.next_calibration_date <= due_soon_threshold:
            self.calibration_status = 'due_soon'
            return

        # Calibration is current
        self.calibration_status = 'current'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    employee_number = db.Column(db.String, unique=True, nullable=False)
    department = db.Column(db.String)
    password_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_current_time)
    reset_token = db.Column(db.String, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    remember_token = db.Column(db.String, nullable=True)
    remember_token_expiry = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.String, nullable=True)  # Store the path or URL to the avatar image
    # Account lockout fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_failed_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    roles = association_proxy('user_roles', 'role')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        import secrets
        import string

        # Generate a 6-digit code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.reset_token = generate_password_hash(code)  # Store hash of code
        self.reset_token_expiry = get_current_time() + timedelta(hours=1)  # Valid for 1 hour
        return code

    def check_reset_token(self, token):
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if get_current_time() > self.reset_token_expiry:
            return False
        return check_password_hash(self.reset_token, token)

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    def generate_remember_token(self):
        import secrets
        token = secrets.token_hex(32)
        self.remember_token = generate_password_hash(token)
        self.remember_token_expiry = get_current_time() + timedelta(days=30)  # Valid for 30 days
        return token

    def check_remember_token(self, token):
        if not self.remember_token or not self.remember_token_expiry:
            return False
        if get_current_time() > self.remember_token_expiry:
            return False
        return check_password_hash(self.remember_token, token)

    def clear_remember_token(self):
        self.remember_token = None
        self.remember_token_expiry = None

    def has_role(self, role_name):
        """Check if user has a specific role by name"""
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name):
        """Check if user has a specific permission through any of their roles"""
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False

    def get_permissions(self):
        """Get all permissions for this user from all roles"""
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions)

    def add_role(self, role):
        """Add a role to this user"""
        if not any(r.id == role.id for r in self.roles):
            user_role = UserRole(user_id=self.id, role_id=role.id)
            db.session.add(user_role)

    def remove_role(self, role):
        """Remove a role from this user"""
        UserRole.query.filter_by(user_id=self.id, role_id=role.id).delete()

    def increment_failed_login(self):
        """Increment the failed login attempts counter and update the last failed login timestamp."""
        self.failed_login_attempts += 1
        self.last_failed_login = get_current_time()
        return self.failed_login_attempts

    def reset_failed_login_attempts(self):
        """Reset the failed login attempts counter."""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        return True

    def lock_account(self, minutes=15):
        """Lock the account for the specified number of minutes."""
        self.account_locked_until = get_current_time() + timedelta(minutes=minutes)
        return True

    def unlock_account(self):
        """Manually unlock the account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        return True

    def is_locked(self):
        """Check if the account is currently locked."""
        if not self.account_locked_until:
            return False
        return get_current_time() < self.account_locked_until

    def get_lockout_remaining_time(self):
        """Get the remaining time (in seconds) until the account is unlocked."""
        if not self.account_locked_until:
            return 0
        if get_current_time() >= self.account_locked_until:
            return 0
        delta = self.account_locked_until - get_current_time()
        return delta.total_seconds()

    def to_dict(self, include_roles=False, include_permissions=False, include_lockout_info=False):
        result = {
            'id': self.id,
            'name': self.name,
            'employee_number': self.employee_number,
            'department': self.department,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'avatar': self.avatar
        }

        if include_roles:
            result['roles'] = [role.to_dict() for role in self.roles]

        if include_permissions:
            result['permissions'] = self.get_permissions()

        if include_lockout_info:
            result.update({
                'failed_login_attempts': self.failed_login_attempts,
                'account_locked': self.is_locked(),
                'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
                'last_failed_login': self.last_failed_login.isoformat() if self.last_failed_login else None
            })

        return result

class Checkout(db.Model):
    __tablename__ = 'checkouts'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, default=get_current_time)
    return_date = db.Column(db.DateTime)
    expected_return_date = db.Column(db.DateTime)
    tool = db.relationship('Tool')
    user = db.relationship('User')

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String, nullable=False)
    action_details = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=get_current_time)

class UserActivity(db.Model):
    __tablename__ = 'user_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    ip_address = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=get_current_time)
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }

class ToolServiceRecord(db.Model):
    __tablename__ = 'tool_service_records'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String, nullable=False)  # 'remove_maintenance', 'remove_permanent', 'return_service'
    reason = db.Column(db.String, nullable=False)
    comments = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=get_current_time)
    tool = db.relationship('Tool')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'tool_id': self.tool_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'action_type': self.action_type,
            'reason': self.reason,
            'comments': self.comments,
            'timestamp': self.timestamp.isoformat()
        }

class Chemical(db.Model):
    __tablename__ = 'chemicals'
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String, nullable=False)
    lot_number = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    manufacturer = db.Column(db.String)
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String, nullable=False, default='each')  # each, oz, ml, etc.
    location = db.Column(db.String)
    category = db.Column(db.String, nullable=True, default='General')  # Sealant, Paint, Adhesive, etc.
    status = db.Column(db.String, nullable=False, default='available')  # available, low_stock, out_of_stock, expired
    date_added = db.Column(db.DateTime, default=get_current_time)
    expiration_date = db.Column(db.DateTime, nullable=True)
    minimum_stock_level = db.Column(db.Float, nullable=True)  # Threshold for low stock alert
    notes = db.Column(db.String)

    # These columns might not exist in older databases, so we'll handle them in the to_dict method
    try:
        is_archived = db.Column(db.Boolean, default=False)  # Whether the chemical is archived
        archived_reason = db.Column(db.String, nullable=True)  # Reason for archiving (expired, depleted, etc.)
        archived_date = db.Column(db.DateTime, nullable=True)  # When the chemical was archived

        # Reordering fields
        needs_reorder = db.Column(db.Boolean, default=False)  # Flag to indicate if the chemical needs to be reordered
        reorder_status = db.Column(db.String, nullable=True, default='not_needed')  # not_needed, needed, ordered
        reorder_date = db.Column(db.DateTime, nullable=True)  # When the reorder was placed
        expected_delivery_date = db.Column(db.DateTime, nullable=True)  # Expected delivery date
    except:
        # If the columns don't exist, we'll create them later with a migration
        pass

    def to_dict(self):
        result = {
            'id': self.id,
            'part_number': self.part_number,
            'lot_number': self.lot_number,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'quantity': self.quantity,
            'unit': self.unit,
            'location': self.location,
            'category': self.category,
            'status': self.status,
            'date_added': self.date_added.isoformat(),
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'minimum_stock_level': self.minimum_stock_level,
            'notes': self.notes
        }

        # Add archive fields if they exist
        try:
            result['is_archived'] = self.is_archived
            result['archived_reason'] = self.archived_reason
            result['archived_date'] = self.archived_date.isoformat() if self.archived_date else None
        except:
            # If the columns don't exist, set default values
            result['is_archived'] = False
            result['archived_reason'] = None
            result['archived_date'] = None

        # Add reordering fields if they exist
        try:
            result['needs_reorder'] = self.needs_reorder
            result['reorder_status'] = self.reorder_status
            result['reorder_date'] = self.reorder_date.isoformat() if self.reorder_date else None
            result['expected_delivery_date'] = self.expected_delivery_date.isoformat() if self.expected_delivery_date else None
        except:
            # If the columns don't exist, set default values
            result['needs_reorder'] = False
            result['reorder_status'] = 'not_needed'
            result['reorder_date'] = None
            result['expected_delivery_date'] = None

        return result

    def is_expired(self):
        if not self.expiration_date:
            return False
        return get_current_time() > self.expiration_date

    def is_expiring_soon(self, days=30):
        """Check if the chemical is expiring within the specified number of days"""
        if not self.expiration_date:
            return False

        # Calculate the date range
        now = get_current_time()
        expiration_threshold = now + timedelta(days=days)

        # Check if expiration date is in the future but within the threshold
        return now < self.expiration_date <= expiration_threshold

    def update_reorder_status(self):
        """Update the reorder status based on expiration, quantity, and minimum stock level"""
        try:
            # If already marked for reorder, don't change
            if self.needs_reorder and self.reorder_status == 'needed':
                return

            # If already ordered, don't change
            if self.reorder_status == 'ordered':
                return

            # Mark for reorder if expired, out of stock, or at/below minimum stock level
            if self.is_expired() or self.quantity <= 0 or self.is_low_stock():
                self.needs_reorder = True
                self.reorder_status = 'needed'
        except:
            # If the columns don't exist, we can't update them
            pass

    def is_low_stock(self):
        if not self.minimum_stock_level:
            return False
        return self.quantity <= self.minimum_stock_level

class ChemicalIssuance(db.Model):
    __tablename__ = 'chemical_issuances'
    id = db.Column(db.Integer, primary_key=True)
    chemical_id = db.Column(db.Integer, db.ForeignKey('chemicals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    hangar = db.Column(db.String, nullable=False)  # Location where chemical is being used
    purpose = db.Column(db.String)  # What the chemical is being used for
    issue_date = db.Column(db.DateTime, default=get_current_time)
    chemical = db.relationship('Chemical')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'chemical_id': self.chemical_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'quantity': self.quantity,
            'hangar': self.hangar,
            'purpose': self.purpose,
            'issue_date': self.issue_date.isoformat()
        }

class RegistrationRequest(db.Model):
    __tablename__ = 'registration_requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    employee_number = db.Column(db.String, unique=True, nullable=False)
    department = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='pending')  # pending, approved, denied
    created_at = db.Column(db.DateTime, default=get_current_time)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_notes = db.Column(db.String, nullable=True)

    # Relationship to the admin who processed the request
    admin = db.relationship('User', foreign_keys=[processed_by])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'employee_number': self.employee_number,
            'department': self.department,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processed_by': self.processed_by,
            'admin_notes': self.admin_notes,
            'admin_name': self.admin.name if self.admin else None
        }

class ToolCalibration(db.Model):
    __tablename__ = 'tool_calibrations'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    calibration_date = db.Column(db.DateTime, nullable=False, default=get_current_time)
    next_calibration_date = db.Column(db.DateTime, nullable=True)
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calibration_notes = db.Column(db.String, nullable=True)
    calibration_status = db.Column(db.String, nullable=False, default='pass')  # pass, fail, limited
    calibration_certificate_file = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    tool = db.relationship('Tool')
    performed_by = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'tool_id': self.tool_id,
            'tool_number': self.tool.tool_number if self.tool else None,
            'serial_number': self.tool.serial_number if self.tool else None,
            'description': self.tool.description if self.tool else None,
            'calibration_date': self.calibration_date.isoformat(),
            'next_calibration_date': self.next_calibration_date.isoformat() if self.next_calibration_date else None,
            'performed_by_user_id': self.performed_by_user_id,
            'performed_by_name': self.performed_by.name if self.performed_by else None,
            'calibration_notes': self.calibration_notes,
            'calibration_status': self.calibration_status,
            'calibration_certificate_file': self.calibration_certificate_file,
            'created_at': self.created_at.isoformat(),
            'standards': [standard.to_dict() for standard in self.standards] if hasattr(self, 'standards') else []
        }

class CalibrationStandard(db.Model):
    __tablename__ = 'calibration_standards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    standard_number = db.Column(db.String, nullable=False)
    certification_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'standard_number': self.standard_number,
            'certification_date': self.certification_date.isoformat(),
            'expiration_date': self.expiration_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'is_expired': get_current_time() > self.expiration_date,
            'is_expiring_soon': self.is_expiring_soon()
        }

    def is_expiring_soon(self, days=30):
        """Check if the standard is expiring within the specified number of days"""
        now = get_current_time()
        expiration_threshold = now + timedelta(days=days)
        return now < self.expiration_date <= expiration_threshold

class ToolCalibrationStandard(db.Model):
    __tablename__ = 'tool_calibration_standards'
    id = db.Column(db.Integer, primary_key=True)
    calibration_id = db.Column(db.Integer, db.ForeignKey('tool_calibrations.id'), nullable=False)
    standard_id = db.Column(db.Integer, db.ForeignKey('calibration_standards.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    calibration = db.relationship('ToolCalibration', backref=db.backref('calibration_standards', lazy='dynamic'))
    standard = db.relationship('CalibrationStandard')

    def to_dict(self):
        return {
            'id': self.id,
            'calibration_id': self.calibration_id,
            'standard_id': self.standard_id,
            'standard': self.standard.to_dict() if self.standard else None,
            'created_at': self.created_at.isoformat()
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    category = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    roles = association_proxy('role_permissions', 'role')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    is_system_role = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    permissions = association_proxy('role_permissions', 'permission')
    users = association_proxy('user_roles', 'user')

    def to_dict(self, include_permissions=False):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system_role': self.is_system_role,
            'created_at': self.created_at.isoformat()
        }

        if include_permissions:
            result['permissions'] = [rp.permission.to_dict() for rp in self.role_permissions]

        return result

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    role = db.relationship('Role', backref=db.backref('role_permissions', cascade='all, delete-orphan'))
    permission = db.relationship('Permission', backref=db.backref('role_permissions', cascade='all, delete-orphan'))

    # Ensure uniqueness of role-permission pairs
    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id', name='_role_permission_uc'),)

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    user = db.relationship('User', backref=db.backref('user_roles', cascade='all, delete-orphan'))
    role = db.relationship('Role', backref=db.backref('user_roles', cascade='all, delete-orphan'))

    # Ensure uniqueness of user-role pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String, nullable=False, default='medium')  # high, medium, low
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    expiration_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    author = db.relationship('User', foreign_keys=[created_by])

    def to_dict(self, include_reads=False):
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'created_by': self.created_by,
            'author_name': self.author.name if self.author else 'Unknown',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'is_active': self.is_active
        }

        if include_reads and hasattr(self, 'reads'):
            data['reads'] = [r.to_dict() for r in self.reads.all()]
            data['read_count'] = self.reads.count()

        return data

class AnnouncementRead(db.Model):
    __tablename__ = 'announcement_reads'
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    announcement = db.relationship('Announcement', backref=db.backref('reads', lazy='dynamic'))
    user = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint(
            'announcement_id',
            'user_id',
            name='_announcement_user_uc'
        ),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'read_at': self.read_at.isoformat()
        }