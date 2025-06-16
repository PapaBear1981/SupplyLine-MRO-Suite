from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash

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
    status = db.Column(db.String, nullable=False, default='available')  # available, checked_out, maintenance, retired
    status_reason = db.Column(db.String)  # Reason for maintenance or retirement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    employee_number = db.Column(db.String, unique=True, nullable=False)
    department = db.Column(db.String)
    password_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reset_token = db.Column(db.String, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    remember_token = db.Column(db.String, nullable=True)
    remember_token_expiry = db.Column(db.DateTime, nullable=True)
    # Account lockout fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_failed_login = db.Column(db.DateTime, nullable=True)

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
        self.reset_token_expiry = datetime.now() + timedelta(hours=1)  # Valid for 1 hour
        return code

    def check_reset_token(self, token):
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return check_password_hash(self.reset_token, token)

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    def generate_remember_token(self):
        import secrets
        token = secrets.token_hex(32)
        self.remember_token = generate_password_hash(token)
        self.remember_token_expiry = datetime.utcnow() + timedelta(days=30)  # Valid for 30 days
        return token

    def check_remember_token(self, token):
        if not self.remember_token or not self.remember_token_expiry:
            return False
        if datetime.utcnow() > self.remember_token_expiry:
            return False
        return check_password_hash(self.remember_token, token)

    def clear_remember_token(self):
        self.remember_token = None
        self.remember_token_expiry = None

    def increment_failed_login(self):
        """Increment the failed login attempts counter and update the last failed login timestamp."""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
        return self.failed_login_attempts

    def reset_failed_login_attempts(self):
        """Reset the failed login attempts counter."""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        return True

    def lock_account(self, minutes=15):
        """Lock the account for the specified number of minutes."""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=minutes)
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
        return datetime.utcnow() < self.account_locked_until

    def get_lockout_remaining_time(self):
        """Get the remaining time (in seconds) until the account is unlocked."""
        if not self.account_locked_until:
            return 0
        if datetime.utcnow() >= self.account_locked_until:
            return 0
        delta = self.account_locked_until - datetime.utcnow()
        return delta.total_seconds()

    def get_permissions(self):
        """Get the user's permissions.
        For admin users, return all permissions.
        For non-admin users, return a basic set of permissions.

        This method first checks for permissions from the RBAC system.
        If no RBAC permissions are found, it falls back to a default set based on admin status.
        """
        # Try to get permissions from RBAC system first
        try:
            # Check if the user has roles with permissions
            if hasattr(self, 'roles'):
                permissions = set()
                for role in self.roles:
                    if hasattr(role, 'permissions'):
                        for permission in role.permissions:
                            permissions.add(permission.name)

                # If we found permissions through RBAC, return them
                if permissions:
                    return list(permissions)
        except AttributeError:
            # If RBAC is not set up, continue with default permissions
            pass

        # Default permissions for all users
        permissions = [
            'view_tools',
            'checkout_tools',
            'return_tools',
            'view_profile',
            'edit_profile'
        ]

        # Admin users get additional permissions
        if self.is_admin:
            admin_permissions = [
                'manage_tools',
                'manage_users',
                'view_reports',
                'manage_chemicals',
                'manage_calibrations',
                'view_admin_dashboard',
                'approve_registrations',
                'unlock_users',
                'manage_announcements'
            ]
            permissions.extend(admin_permissions)

        return permissions

    def to_dict(self, include_lockout_info=False, include_roles=False, include_permissions=False):
        data = {
            'id': self.id,
            'name': self.name,
            'employee_number': self.employee_number,
            'department': self.department,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'avatar': None  # Default value if avatar attribute doesn't exist
        }

        # Try to get avatar if it exists as an attribute
        try:
            if hasattr(self, 'avatar'):
                data['avatar'] = self.avatar
        except AttributeError:
            pass

        if include_lockout_info:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'account_locked': self.is_locked(),
                'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
                'last_failed_login': self.last_failed_login.isoformat() if self.last_failed_login else None
            })

        if include_roles:
            try:
                data['roles'] = [role.to_dict() for role in self.roles]
            except AttributeError:
                data['roles'] = []

        if include_permissions:
            data['permissions'] = self.get_permissions()

        return data

class Checkout(db.Model):
    __tablename__ = 'checkouts'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    expected_return_date = db.Column(db.DateTime)
    # New fields for improved return functionality
    return_condition = db.Column(db.String)  # Condition of the tool when returned
    returned_by = db.Column(db.String)  # Who returned the tool (can be different from the user who checked it out)
    found = db.Column(db.Boolean, default=False)  # Whether the tool was found on the production floor
    return_notes = db.Column(db.String)  # Additional notes about the return
    tool = db.relationship('Tool')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'tool_id': self.tool_id,
            'user_id': self.user_id,
            'checkout_date': self.checkout_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'expected_return_date': self.expected_return_date.isoformat() if self.expected_return_date else None,
            'return_condition': self.return_condition,
            'returned_by': self.returned_by,
            'found': self.found,
            'return_notes': self.return_notes,
            'status': 'Returned' if self.return_date else 'Checked Out'
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String, nullable=False)
    action_details = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    __tablename__ = 'user_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    ip_address = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
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

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String, nullable=False, default='medium')  # high, medium, low
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
            data['reads'] = [read.to_dict() for read in self.reads]
            data['read_count'] = len(self.reads)

        return data

class AnnouncementRead(db.Model):
    __tablename__ = 'announcement_reads'
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    announcement = db.relationship('Announcement', backref=db.backref('reads', lazy='dynamic'))
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'read_at': self.read_at.isoformat()
        }
