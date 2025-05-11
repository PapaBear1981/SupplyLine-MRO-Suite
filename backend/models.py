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
    status = db.Column(db.String, nullable=True, default='available')  # available, checked_out, maintenance, retired
    status_reason = db.Column(db.String, nullable=True)  # Reason for maintenance or retirement
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
    avatar = db.Column(db.String, nullable=True)  # Store the path or URL to the avatar image

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
            'created_at': self.created_at.isoformat(),
            'avatar': self.avatar
        }

class Checkout(db.Model):
    __tablename__ = 'checkouts'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    expected_return_date = db.Column(db.DateTime)
    tool = db.relationship('Tool')
    user = db.relationship('User')

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
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime, nullable=True)
    minimum_stock_level = db.Column(db.Float, nullable=True)  # Threshold for low stock alert
    notes = db.Column(db.String)

    # These columns might not exist in older databases, so we'll handle them in the to_dict method
    try:
        is_archived = db.Column(db.Boolean, default=False)  # Whether the chemical is archived
        archived_reason = db.Column(db.String, nullable=True)  # Reason for archiving (expired, depleted, etc.)
        archived_date = db.Column(db.DateTime, nullable=True)  # When the chemical was archived
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

        return result

    def is_expired(self):
        if not self.expiration_date:
            return False
        return datetime.utcnow() > self.expiration_date

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
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
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