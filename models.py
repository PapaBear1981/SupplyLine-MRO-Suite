from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    remember_token = db.Column(db.String, nullable=True)
    remember_token_expiry = db.Column(db.DateTime, nullable=True)

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
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)  # Valid for 1 hour
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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'employee_number': self.employee_number,
            'department': self.department,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
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
