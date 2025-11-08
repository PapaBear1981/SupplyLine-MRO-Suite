from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import object_session
from werkzeug.security import check_password_hash, generate_password_hash


# Import time utilities for consistent time handling
try:
    from time_utils import get_local_timestamp

    def get_current_time():
        """
        Get current time as a naive datetime for database storage.
        Returns naive datetime to match SQLAlchemy's db.DateTime column type.
        """
        return get_local_timestamp()
except ImportError:
    def get_current_time():
        """
        Fallback to naive datetime.now() if time_utils is not available.
        Returns naive datetime to match SQLAlchemy's db.DateTime column type.
        """
        return datetime.now()

db = SQLAlchemy()


class PasswordHistory(db.Model):
    __tablename__ = "password_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=get_current_time)

    user = db.relationship("User", back_populates="password_histories")


class Tool(db.Model):
    __tablename__ = "tools"
    id = db.Column(db.Integer, primary_key=True)
    tool_number = db.Column(db.String, nullable=False)
    serial_number = db.Column(db.String, nullable=False)
    lot_number = db.Column(db.String(100), nullable=True)  # For consumable tools tracked by lot
    description = db.Column(db.String)
    condition = db.Column(db.String)
    location = db.Column(db.String)
    category = db.Column(db.String, nullable=True, default="General")
    status = db.Column(db.String, nullable=True, default="available")  # available, checked_out, maintenance, retired
    status_reason = db.Column(db.String, nullable=True)  # Reason for maintenance or retirement
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Calibration fields
    requires_calibration = db.Column(db.Boolean, default=False)
    calibration_frequency_days = db.Column(db.Integer, nullable=True)
    last_calibration_date = db.Column(db.DateTime, nullable=True)
    next_calibration_date = db.Column(db.DateTime, nullable=True)
    calibration_status = db.Column(db.String, nullable=True)  # current, due_soon, overdue, not_applicable

    # Relationships
    warehouse = db.relationship("Warehouse", back_populates="tools")

    def to_dict(self):
        return {
            "id": self.id,
            "tool_number": self.tool_number,
            "serial_number": self.serial_number,
            "lot_number": self.lot_number,
            "description": self.description,
            "condition": self.condition,
            "location": self.location,
            "category": self.category,
            "status": self.status,
            "status_reason": self.status_reason,
            "warehouse_id": self.warehouse_id,
            "warehouse_name": self.warehouse.name if self.warehouse else None,
            "created_at": self.created_at.isoformat(),
            "requires_calibration": self.requires_calibration,
            "calibration_frequency_days": self.calibration_frequency_days,
            "last_calibration_date": self.last_calibration_date.isoformat() if self.last_calibration_date else None,
            "next_calibration_date": self.next_calibration_date.isoformat() if self.next_calibration_date else None,
            "calibration_status": self.calibration_status
        }

    def update_calibration_status(self):
        """Update the calibration status based on next_calibration_date"""
        if not self.requires_calibration or not self.next_calibration_date:
            self.calibration_status = "not_applicable"
            return

        now = get_current_time()

        # If calibration is overdue
        if now > self.next_calibration_date:
            self.calibration_status = "overdue"
            return

        # If calibration is due within 30 days
        due_soon_threshold = now + timedelta(days=30)
        if now <= self.next_calibration_date <= due_soon_threshold:
            self.calibration_status = "due_soon"
            return

        # Calibration is current
        self.calibration_status = "current"


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class User(db.Model):
    __tablename__ = "users"
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
    avatar = db.Column(db.String, nullable=True)  # Store the path or URL to the avatar image
    force_password_change = db.Column(db.Boolean, default=False)
    password_changed_at = db.Column(db.DateTime, nullable=True, default=get_current_time)
    # Account lockout fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_failed_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    roles = association_proxy("user_roles", "role")
    password_histories = db.relationship(
        "PasswordHistory",
        back_populates="user",
        order_by="PasswordHistory.created_at.desc()",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Enhanced messaging relationships
    created_channels = db.relationship("Channel", back_populates="creator", foreign_keys="Channel.created_by")
    channel_memberships = db.relationship("ChannelMember", back_populates="user", cascade="all, delete-orphan")
    channel_messages = db.relationship("ChannelMessage", back_populates="sender")
    message_reactions = db.relationship("MessageReaction", back_populates="user", cascade="all, delete-orphan")
    uploaded_attachments = db.relationship("MessageAttachment", back_populates="uploader")
    attachment_downloads = db.relationship("AttachmentDownload", back_populates="user", cascade="all, delete-orphan")
    presence = db.relationship("UserPresence", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        now = get_current_time()
        self.password_changed_at = now

        session = object_session(self)
        if session is None:
            session = db.session
            session.add(self)
        elif self not in session:
            session.add(self)

        if self.id is None:
            session.flush()

        history_entry = PasswordHistory(
            user_id=self.id,
            password_hash=self.password_hash,
            created_at=now
        )
        session.add(history_entry)

        # Maintain only the most recent 5 password history records
        history_records = (
            session.query(PasswordHistory)
            .filter_by(user_id=self.id)
            .order_by(PasswordHistory.created_at.desc(), PasswordHistory.id.desc())
            .all()
        )

        for stale_record in history_records[5:]:
            session.delete(stale_record)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_password_reused(self, candidate_password, history_limit=5):
        """Check whether the candidate password matches recent password history."""
        if not self.id:
            return False

        query = self.password_histories.order_by(PasswordHistory.created_at.desc())
        if history_limit:
            query = query.limit(history_limit)

        return any(check_password_hash(history.password_hash, candidate_password) for history in query)

    def is_password_expired(self, max_age_days=90):
        """Determine if the user's password exceeds the maximum allowed age."""
        if not self.password_changed_at:
            return True

        return get_current_time() - self.password_changed_at >= timedelta(days=max_age_days)

    def generate_reset_token(self):
        import secrets

        # Generate a cryptographically secure 32-character token
        # This provides ~256 bits of entropy, making brute force attacks infeasible
        # Previous 6-digit code had only 1 million combinations (easily brute-forceable)
        code = secrets.token_urlsafe(32)  # Generates 43-character URL-safe string

        self.reset_token = generate_password_hash(code)  # Store hash of code

        # Reduced expiry time from 1 hour to 15 minutes for better security
        # Shorter window reduces the time available for brute force attacks
        self.reset_token_expiry = get_current_time() + timedelta(minutes=15)

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
        # Use explicit SQL query to avoid lazy loading issues
        # This ensures permissions are loaded even in different contexts (e.g., CI)
        from sqlalchemy import select

        # Query for all permissions through the user's roles
        stmt = select(Permission.name).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            Role, RolePermission.role_id == Role.id
        ).join(
            UserRole, Role.id == UserRole.role_id
        ).where(
            UserRole.user_id == self.id
        ).distinct()

        result = db.session.execute(stmt)
        return [row[0] for row in result]

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

    def is_account_locked(self):
        """Backward-compatible alias for lock status checks."""
        return self.is_locked()

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
            "id": self.id,
            "name": self.name,
            "employee_number": self.employee_number,
            "department": self.department,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "avatar": self.avatar,
            "force_password_change": self.force_password_change,
            "password_changed_at": self.password_changed_at.isoformat() if self.password_changed_at else None
        }

        if include_roles:
            result["roles"] = [role.to_dict() for role in self.roles]

        if include_permissions:
            result["permissions"] = self.get_permissions()

        if include_lockout_info:
            result.update({
                "failed_login_attempts": self.failed_login_attempts,
                "account_locked": self.is_locked(),
                "account_locked_until": self.account_locked_until.isoformat() if self.account_locked_until else None,
                "last_failed_login": self.last_failed_login.isoformat() if self.last_failed_login else None
            })

        return result


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False, index=True)
    value = db.Column(db.String(512), nullable=False)
    category = db.Column(db.String(64), nullable=True, index=True)
    description = db.Column(db.String(255), nullable=True)
    is_sensitive = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=get_current_time)
    updated_at = db.Column(db.DateTime, nullable=False, default=get_current_time, onupdate=get_current_time)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    updated_by = db.relationship("User", foreign_keys=[updated_by_id])

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "description": self.description,
            "is_sensitive": self.is_sensitive,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": {
                "id": self.updated_by.id,
                "name": self.updated_by.name,
                "employee_number": self.updated_by.employee_number,
            } if self.updated_by else None,
        }


class Checkout(db.Model):
    __tablename__ = "checkouts"
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    checkout_date = db.Column(db.DateTime, default=get_current_time)
    return_date = db.Column(db.DateTime)
    expected_return_date = db.Column(db.DateTime)
    tool = db.relationship("Tool")
    user = db.relationship("User")


class AuditLog(db.Model):
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String, nullable=False)
    action_details = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=get_current_time)


class UserActivity(db.Model):
    __tablename__ = "user_activity"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    activity_type = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    ip_address = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=get_current_time)
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat()
        }


class ToolServiceRecord(db.Model):
    __tablename__ = "tool_service_records"
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_type = db.Column(db.String, nullable=False)  # 'remove_maintenance', 'remove_permanent', 'return_service'
    reason = db.Column(db.String, nullable=False)
    comments = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=get_current_time)
    tool = db.relationship("Tool")
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "tool_id": self.tool_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown",
            "action_type": self.action_type,
            "reason": self.reason,
            "comments": self.comments,
            "timestamp": self.timestamp.isoformat()
        }


class ProcurementOrder(db.Model):
    """Track procurement activity for replacement tools, chemicals, and expendables."""

    __tablename__ = "procurement_orders"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    order_type = db.Column(db.String(50), nullable=False, default="tool")
    part_number = db.Column(db.String(100), nullable=True, index=True)  # Track items by part number
    description = db.Column(db.String(4000))
    priority = db.Column(db.String(20), nullable=False, default="normal")
    status = db.Column(db.String(50), nullable=False, default="new")
    reference_type = db.Column(db.String(30))
    reference_number = db.Column(db.String(100))
    tracking_number = db.Column(db.String(120))
    expected_due_date = db.Column(db.DateTime, index=True)
    completed_date = db.Column(db.DateTime)
    notes = db.Column(db.String(4000))
    kit_id = db.Column(db.Integer, db.ForeignKey("kits.id"), nullable=True, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_current_time)
    updated_at = db.Column(db.DateTime, nullable=False, default=get_current_time, onupdate=get_current_time)

    requester = db.relationship("User", foreign_keys=[requester_id])
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    kit = db.relationship("Kit", foreign_keys=[kit_id])
    messages = db.relationship(
        "ProcurementOrderMessage",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    OPEN_STATUSES = {"new", "awaiting_info", "ordered", "shipped", "in_progress"}
    CLOSED_STATUSES = {"received", "cancelled"}

    def is_closed(self) -> bool:
        return self.status in self.CLOSED_STATUSES

    def _due_state(self):
        if not self.expected_due_date:
            return "unscheduled"

        if self.is_closed():
            return "completed"

        now = get_current_time()
        if self.expected_due_date < now:
            return "late"

        if (self.expected_due_date - now).days <= 3:
            return "due_soon"

        return "on_track"

    def to_dict(self, include_messages: bool = False):
        """Serialize order for API responses."""

        latest_message = None
        message_count = 0
        if self.messages is not None:
            message_count = self.messages.count()
            if message_count:
                latest_message = self.messages.order_by(ProcurementOrderMessage.sent_date.desc()).first()

        data = {
            "id": self.id,
            "title": self.title,
            "order_type": self.order_type,
            "part_number": self.part_number,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "reference_type": self.reference_type,
            "reference_number": self.reference_number,
            "tracking_number": self.tracking_number,
            "expected_due_date": self.expected_due_date.isoformat() if self.expected_due_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "notes": self.notes,
            "kit_id": self.kit_id,
            "kit_name": self.kit.name if self.kit else None,
            "requester_id": self.requester_id,
            "requester_name": self.requester.name if self.requester else None,
            "buyer_id": self.buyer_id,
            "buyer_name": self.buyer.name if self.buyer else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": message_count,
            "latest_message_at": latest_message.sent_date.isoformat() if latest_message else None,
            "due_status": self._due_state(),
            "is_late": self._due_state() == "late",
            "days_overdue": None,
            "days_open": None,
        }

        if self.expected_due_date and not self.is_closed():
            delta = get_current_time() - self.expected_due_date
            if delta.days >= 0:
                data["days_overdue"] = delta.days

        if self.created_at:
            open_delta = get_current_time() - self.created_at
            data["days_open"] = open_delta.days

        if include_messages:
            messages_query = self.messages.order_by(ProcurementOrderMessage.sent_date.desc()) if self.messages is not None else []
            data["messages"] = [message.to_dict() for message in messages_query]

        return data


class ProcurementOrderMessage(db.Model):
    """Message thread entries associated with procurement orders."""

    __tablename__ = "procurement_order_messages"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("procurement_orders.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(5000), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    sent_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    read_date = db.Column(db.DateTime)
    parent_message_id = db.Column(db.Integer, db.ForeignKey("procurement_order_messages.id"))
    attachments = db.Column(db.String(1000))

    order = db.relationship("ProcurementOrder", back_populates="messages")
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    parent_message = db.relationship("ProcurementOrderMessage", remote_side=[id], backref="replies")

    def to_dict(self, include_replies: bool = False):
        data = {
            "id": self.id,
            "order_id": self.order_id,
            "subject": self.subject,
            "message": self.message,
            "sender_id": self.sender_id,
            "sender_name": self.sender.name if self.sender else None,
            "recipient_id": self.recipient_id,
            "recipient_name": self.recipient.name if self.recipient else None,
            "is_read": self.is_read,
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "read_date": self.read_date.isoformat() if self.read_date else None,
            "parent_message_id": self.parent_message_id,
            "attachments": self.attachments,
            "reply_count": len(self.replies) if hasattr(self, "replies") else 0,
        }

        if include_replies and hasattr(self, "replies"):
            data["replies"] = [reply.to_dict() for reply in self.replies]

        return data


class Expendable(db.Model):
    """
    Expendable model for kit-only consumable inventory.

    Expendables are consumable items that are added directly to kits without warehouse management.
    They are NOT tracked in warehouses - warehouse_id is always None.

    Key characteristics:
    - Kit-only items (no warehouse tracking)
    - MUST have EITHER lot number OR serial number (never both, never neither)
    - Can be transferred between kits
    - Full audit trail via AuditLog and transaction tracking
    - Support barcode generation for lot/serial numbers
    """
    __tablename__ = "expendables"

    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100), nullable=False, index=True)
    serial_number = db.Column(db.String(100), nullable=True, index=True)  # For serial-tracked expendables
    lot_number = db.Column(db.String(100), nullable=True, index=True)  # For lot-tracked expendables
    description = db.Column(db.String(500), nullable=False)
    manufacturer = db.Column(db.String(200))
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False, default="each")  # each, oz, ml, ft, etc.
    location = db.Column(db.String(100))
    category = db.Column(db.String(100), nullable=True, default="General")
    status = db.Column(db.String(20), nullable=False, default="available")  # available, low_stock, out_of_stock
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True, index=True)  # Always None for kit-only expendables
    date_added = db.Column(db.DateTime, default=get_current_time, nullable=False)
    minimum_stock_level = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(500))

    # Relationships - kept for backward compatibility but warehouse_id should always be None
    warehouse = db.relationship("Warehouse", back_populates="expendables")

    def __init__(self, **kwargs):
        """
        Initialize expendable and validate tracking.
        Forces warehouse_id to None for kit-only architecture.
        """
        # Force warehouse_id to None for kit-only expendables
        kwargs["warehouse_id"] = None
        super().__init__(**kwargs)
        self.validate_tracking()

    def validate_tracking(self):
        """
        Validate that EITHER serial number OR lot number is provided (never both, never neither).
        Raises ValueError if validation fails.
        """
        has_serial = bool(self.serial_number and self.serial_number.strip())
        has_lot = bool(self.lot_number and self.lot_number.strip())

        if not has_serial and not has_lot:
            raise ValueError("Expendable must have EITHER serial number OR lot number")

        if has_serial and has_lot:
            raise ValueError("Expendable cannot have both serial number AND lot number")

    def to_dict(self):
        """Convert expendable to dictionary (excludes warehouse fields for kit-only items)"""
        return {
            "id": self.id,
            "part_number": self.part_number,
            "serial_number": self.serial_number,
            "lot_number": self.lot_number,
            "description": self.description,
            "manufacturer": self.manufacturer,
            "quantity": self.quantity,
            "unit": self.unit,
            "location": self.location,
            "category": self.category,
            "status": self.status,
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "minimum_stock_level": self.minimum_stock_level,
            "notes": self.notes,
            # Include tracking type for frontend
            "tracking_type": "serial" if self.serial_number else "lot"
        }

    def is_low_stock(self):
        """Check if expendable is at or below minimum stock level"""
        if not self.minimum_stock_level:
            return False
        return self.quantity <= self.minimum_stock_level


class Chemical(db.Model):
    __tablename__ = "chemicals"
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String, nullable=False)
    lot_number = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    manufacturer = db.Column(db.String)
    quantity = db.Column(db.Integer, nullable=False, default=0)  # Integer only - no decimal quantities
    unit = db.Column(db.String, nullable=False, default="each")  # each, oz, ml, etc.
    location = db.Column(db.String)
    category = db.Column(db.String, nullable=True, default="General")  # Sealant, Paint, Adhesive, etc.
    status = db.Column(db.String, nullable=False, default="available")  # available, low_stock, out_of_stock, expired
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True, index=True)
    date_added = db.Column(db.DateTime, default=get_current_time)
    expiration_date = db.Column(db.DateTime, nullable=True)
    minimum_stock_level = db.Column(db.Integer, nullable=True)  # Threshold for low stock alert - Integer only
    notes = db.Column(db.String)

    # Lot lineage tracking for partial transfers
    parent_lot_number = db.Column(db.String, nullable=True)  # Parent lot number if this is a split lot
    lot_sequence = db.Column(db.Integer, nullable=True, default=0)  # Number of child lots created from this lot

    # These columns might not exist in older databases, so we'll handle them in the to_dict method
    try:
        is_archived = db.Column(db.Boolean, default=False)  # Whether the chemical is archived
        archived_reason = db.Column(db.String, nullable=True)  # Reason for archiving (expired, depleted, etc.)
        archived_date = db.Column(db.DateTime, nullable=True)  # When the chemical was archived

        # Reordering fields
        needs_reorder = db.Column(db.Boolean, default=False)  # Flag to indicate if the chemical needs to be reordered
        reorder_status = db.Column(db.String, nullable=True, default="not_needed")  # not_needed, needed, ordered
        reorder_date = db.Column(db.DateTime, nullable=True)  # When the reorder was placed
        requested_quantity = db.Column(db.Integer, nullable=True)  # Quantity requested for reorder
        expected_delivery_date = db.Column(db.DateTime, nullable=True)  # Expected delivery date

        # Link to procurement order for integrated order management
        procurement_order_id = db.Column(db.Integer, db.ForeignKey("procurement_orders.id"), nullable=True, index=True)
    except Exception:
        # If the columns don't exist, we'll create them later with a migration
        pass

    # Relationships
    warehouse = db.relationship("Warehouse", back_populates="chemicals")
    procurement_order = db.relationship("ProcurementOrder", foreign_keys=[procurement_order_id], backref="chemicals")

    def to_dict(self):
        result = {
            "id": self.id,
            "part_number": self.part_number,
            "lot_number": self.lot_number,
            "description": self.description,
            "manufacturer": self.manufacturer,
            "quantity": self.quantity,
            "unit": self.unit,
            "location": self.location,
            "category": self.category,
            "status": self.status,
            "warehouse_id": self.warehouse_id,
            "warehouse_name": self.warehouse.name if self.warehouse else None,
            "date_added": self.date_added.isoformat(),
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "minimum_stock_level": self.minimum_stock_level,
            "notes": self.notes,
            "parent_lot_number": self.parent_lot_number,
            "lot_sequence": self.lot_sequence or 0
        }

        # Add archive fields if they exist
        try:
            result["is_archived"] = self.is_archived
            result["archived_reason"] = self.archived_reason
            result["archived_date"] = self.archived_date.isoformat() if self.archived_date else None
        except Exception:
            # If the columns don't exist, set default values
            result["is_archived"] = False
            result["archived_reason"] = None
            result["archived_date"] = None

        # Add reordering fields if they exist
        try:
            result["needs_reorder"] = self.needs_reorder
            result["reorder_status"] = self.reorder_status
            result["reorder_date"] = self.reorder_date.isoformat() if self.reorder_date else None
            result["requested_quantity"] = self.requested_quantity
            result["expected_delivery_date"] = self.expected_delivery_date.isoformat() if self.expected_delivery_date else None
            result["procurement_order_id"] = self.procurement_order_id
        except Exception:
            # If the columns don't exist, set default values
            result["needs_reorder"] = False
            result["reorder_status"] = "not_needed"
            result["reorder_date"] = None
            result["requested_quantity"] = None
            result["expected_delivery_date"] = None

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
            if self.needs_reorder and self.reorder_status == "needed":
                return

            # If already ordered, don't change
            if self.reorder_status == "ordered":
                return

            # Mark for reorder if expired, out of stock, or at/below minimum stock level
            if self.is_expired() or self.quantity <= 0 or self.is_low_stock():
                self.needs_reorder = True
                self.reorder_status = "needed"
        except Exception:
            # If the columns don't exist, we can't update them
            pass

    def is_low_stock(self):
        if not self.minimum_stock_level:
            return False
        return self.quantity <= self.minimum_stock_level


class ChemicalIssuance(db.Model):
    __tablename__ = "chemical_issuances"
    id = db.Column(db.Integer, primary_key=True)
    chemical_id = db.Column(db.Integer, db.ForeignKey("chemicals.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Integer only - no decimal quantities
    hangar = db.Column(db.String, nullable=False)  # Location where chemical is being used
    purpose = db.Column(db.String)  # What the chemical is being used for
    issue_date = db.Column(db.DateTime, default=get_current_time)
    chemical = db.relationship("Chemical")
    user = db.relationship("User")
    returns = db.relationship(
        "ChemicalReturn",
        back_populates="issuance",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        total_returned = sum(ret.quantity for ret in self.returns) if self.returns else 0
        remaining_quantity = max(self.quantity - total_returned, 0)
        return {
            "id": self.id,
            "chemical_id": self.chemical_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown",
            "quantity": self.quantity,
            "hangar": self.hangar,
            "purpose": self.purpose,
            "issue_date": self.issue_date.isoformat(),
            "total_returned": total_returned,
            "remaining_quantity": remaining_quantity,
        }


class ChemicalReturn(db.Model):
    __tablename__ = "chemical_returns"

    id = db.Column(db.Integer, primary_key=True)
    chemical_id = db.Column(db.Integer, db.ForeignKey("chemicals.id"), nullable=False)
    issuance_id = db.Column(db.Integer, db.ForeignKey("chemical_issuances.id"), nullable=False)
    returned_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.String(1000), nullable=True)
    return_date = db.Column(db.DateTime, default=get_current_time, nullable=False)

    chemical = db.relationship("Chemical")
    issuance = db.relationship("ChemicalIssuance", back_populates="returns")
    returned_by = db.relationship("User")
    warehouse = db.relationship("Warehouse")

    def to_dict(self):
        return {
            "id": self.id,
            "chemical_id": self.chemical_id,
            "issuance_id": self.issuance_id,
            "returned_by_id": self.returned_by_id,
            "returned_by_name": self.returned_by.name if self.returned_by else "Unknown",
            "quantity": self.quantity,
            "warehouse_id": self.warehouse_id,
            "warehouse_name": self.warehouse.name if self.warehouse else None,
            "location": self.location,
            "notes": self.notes,
            "return_date": self.return_date.isoformat() if self.return_date else None,
        }


class RegistrationRequest(db.Model):
    __tablename__ = "registration_requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    employee_number = db.Column(db.String, unique=True, nullable=False)
    department = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default="pending")  # pending, approved, denied
    created_at = db.Column(db.DateTime, default=get_current_time)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_notes = db.Column(db.String, nullable=True)

    # Relationship to the admin who processed the request
    admin = db.relationship("User", foreign_keys=[processed_by])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "employee_number": self.employee_number,
            "department": self.department,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "processed_by": self.processed_by,
            "admin_notes": self.admin_notes,
            "admin_name": self.admin.name if self.admin else None
        }


class ToolCalibration(db.Model):
    __tablename__ = "tool_calibrations"
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"), nullable=False)
    calibration_date = db.Column(db.DateTime, nullable=False, default=get_current_time)
    next_calibration_date = db.Column(db.DateTime, nullable=True)
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    calibration_notes = db.Column(db.String, nullable=True)
    calibration_status = db.Column(db.String, nullable=False, default="pass")  # pass, fail, limited
    calibration_certificate_file = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    tool = db.relationship("Tool")
    performed_by = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "tool_id": self.tool_id,
            "tool_number": self.tool.tool_number if self.tool else None,
            "serial_number": self.tool.serial_number if self.tool else None,
            "description": self.tool.description if self.tool else None,
            "calibration_date": self.calibration_date.isoformat(),
            "next_calibration_date": self.next_calibration_date.isoformat() if self.next_calibration_date else None,
            "performed_by_user_id": self.performed_by_user_id,
            "performed_by_name": self.performed_by.name if self.performed_by else None,
            "calibration_notes": self.calibration_notes,
            "calibration_status": self.calibration_status,
            "calibration_certificate_file": self.calibration_certificate_file,
            "created_at": self.created_at.isoformat(),
            "standards": [standard.to_dict() for standard in self.standards] if hasattr(self, "standards") else []
        }


class CalibrationStandard(db.Model):
    __tablename__ = "calibration_standards"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    standard_number = db.Column(db.String, nullable=False)
    certification_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "standard_number": self.standard_number,
            "certification_date": self.certification_date.isoformat(),
            "expiration_date": self.expiration_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "is_expired": get_current_time() > self.expiration_date,
            "is_expiring_soon": self.is_expiring_soon()
        }

    def is_expiring_soon(self, days=30):
        """Check if the standard is expiring within the specified number of days"""
        now = get_current_time()
        expiration_threshold = now + timedelta(days=days)
        return now < self.expiration_date <= expiration_threshold


class ToolCalibrationStandard(db.Model):
    __tablename__ = "tool_calibration_standards"
    id = db.Column(db.Integer, primary_key=True)
    calibration_id = db.Column(db.Integer, db.ForeignKey("tool_calibrations.id"), nullable=False)
    standard_id = db.Column(db.Integer, db.ForeignKey("calibration_standards.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    calibration = db.relationship("ToolCalibration", backref=db.backref("calibration_standards", lazy="dynamic"))
    standard = db.relationship("CalibrationStandard")

    def to_dict(self):
        return {
            "id": self.id,
            "calibration_id": self.calibration_id,
            "standard_id": self.standard_id,
            "standard": self.standard.to_dict() if self.standard else None,
            "created_at": self.created_at.isoformat()
        }


class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    category = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    roles = association_proxy("role_permissions", "role")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    is_system_role = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    permissions = association_proxy("role_permissions", "permission")
    users = association_proxy("user_roles", "user")

    def to_dict(self, include_permissions=False):
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_system_role": self.is_system_role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        if include_permissions:
            result["permissions"] = [rp.permission.to_dict() for rp in self.role_permissions]

        return result


class RolePermission(db.Model):
    __tablename__ = "role_permissions"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    role = db.relationship("Role", backref=db.backref("role_permissions", cascade="all, delete-orphan"))
    permission = db.relationship("Permission", backref=db.backref("role_permissions", cascade="all, delete-orphan"))

    # Ensure uniqueness of role-permission pairs
    __table_args__ = (db.UniqueConstraint("role_id", "permission_id", name="_role_permission_uc"),)


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    user = db.relationship("User", backref=db.backref("user_roles", cascade="all, delete-orphan"))
    role = db.relationship("Role", backref=db.backref("user_roles", cascade="all, delete-orphan"))

    # Ensure uniqueness of user-role pairs
    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="_user_role_uc"),)


class Announcement(db.Model):
    __tablename__ = "announcements"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String, nullable=False, default="medium")  # high, medium, low
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    expiration_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    author = db.relationship("User", foreign_keys=[created_by])

    def to_dict(self, include_reads=False):
        data = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "created_by": self.created_by,
            "author_name": self.author.name if self.author else "Unknown",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "is_active": self.is_active
        }

        if include_reads and hasattr(self, "reads"):
            data["reads"] = [r.to_dict() for r in self.reads.all()]
            data["read_count"] = self.reads.count()

        return data


class AnnouncementRead(db.Model):
    __tablename__ = "announcement_reads"
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey("announcements.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    read_at = db.Column(db.DateTime, default=get_current_time)

    # Relationships
    announcement = db.relationship("Announcement", backref=db.backref("reads", lazy="dynamic"))
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint(
            "announcement_id",
            "user_id",
            name="_announcement_user_uc"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "announcement_id": self.announcement_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown",
            "read_at": self.read_at.isoformat()
        }


class InventoryTransaction(db.Model):
    """
    InventoryTransaction model for tracking all inventory movements.
    Provides complete audit trail from receipt through disposal.
    """
    __tablename__ = "inventory_transactions"

    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(20), nullable=False, index=True)  # tool, chemical, expendable
    item_id = db.Column(db.Integer, nullable=False, index=True)  # FK to respective table
    transaction_type = db.Column(db.String(50), nullable=False)  # receipt, issuance, transfer, adjustment, checkout, return, etc.
    timestamp = db.Column(db.DateTime, default=get_current_time, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quantity_change = db.Column(db.Float)  # Positive for additions, negative for removals
    location_from = db.Column(db.String(200))
    location_to = db.Column(db.String(200))
    reference_number = db.Column(db.String(100))  # Work order, PO number, etc.
    notes = db.Column(db.String(1000))
    lot_number = db.Column(db.String(100))  # Lot number at time of transaction
    serial_number = db.Column(db.String(100))  # Serial number at time of transaction

    # Relationships
    user = db.relationship("User")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "item_type": self.item_type,
            "item_id": self.item_id,
            "transaction_type": self.transaction_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown",
            "quantity_change": self.quantity_change,
            "location_from": self.location_from,
            "location_to": self.location_to,
            "reference_number": self.reference_number,
            "notes": self.notes,
            "lot_number": self.lot_number,
            "serial_number": self.serial_number
        }

    @staticmethod
    def create_transaction(item_type, item_id, transaction_type, user_id, **kwargs):
        """
        Helper method to create a transaction record.

        Args:
            item_type: Type of item (tool, chemical, expendable)
            item_id: ID of the item
            transaction_type: Type of transaction
            user_id: ID of user performing transaction
            **kwargs: Additional fields (quantity_change, location_from, location_to, etc.)

        Returns:
            InventoryTransaction instance
        """
        return InventoryTransaction(
            item_type=item_type,
            item_id=item_id,
            transaction_type=transaction_type,
            user_id=user_id,
            quantity_change=kwargs.get("quantity_change"),
            location_from=kwargs.get("location_from"),
            location_to=kwargs.get("location_to"),
            reference_number=kwargs.get("reference_number"),
            notes=kwargs.get("notes"),
            lot_number=kwargs.get("lot_number"),
            serial_number=kwargs.get("serial_number")
        )


class LotNumberSequence(db.Model):
    """
    LotNumberSequence model for auto-generating unique lot numbers.
    Format: LOT-YYMMDD-XXXX where XXXX is a daily sequential counter.
    """
    __tablename__ = "lot_number_sequences"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(8), nullable=False, unique=True, index=True)  # YYYYMMDD
    sequence_counter = db.Column(db.Integer, nullable=False, default=0)
    last_generated_at = db.Column(db.DateTime, default=get_current_time, nullable=False)

    @staticmethod
    def generate_lot_number():
        """
        Generate a unique lot number in format LOT-YYMMDD-XXXX.
        Uses atomic increment with row-level locking to ensure uniqueness.

        Returns:
            str: Generated lot number (e.g., LOT-251014-0001)
        """
        from sqlalchemy.exc import IntegrityError

        # Get current date in YYYYMMDD format
        current_date = datetime.now().strftime("%Y%m%d")

        # Get or create sequence for today with row-level locking
        sequence = (
            db.session.query(LotNumberSequence)
            .filter_by(date=current_date)
            .with_for_update()
            .first()
        )

        if not sequence:
            # Create new sequence for today
            try:
                sequence = LotNumberSequence(
                    date=current_date,
                    sequence_counter=1
                )
                db.session.add(sequence)
                db.session.flush()
            except IntegrityError:
                # Another transaction created the sequence, retry with lock
                db.session.rollback()
                sequence = (
                    db.session.query(LotNumberSequence)
                    .filter_by(date=current_date)
                    .with_for_update()
                    .first()
                )
                if sequence:
                    sequence.sequence_counter += 1
                    sequence.last_generated_at = get_current_time()
                    db.session.flush()
                else:
                    raise ValueError("Failed to create or retrieve lot number sequence")
        else:
            # Increment existing sequence
            sequence.sequence_counter += 1
            sequence.last_generated_at = get_current_time()
            db.session.flush()

        # Format: LOT-YYMMDD-XXXX
        year_short = current_date[2:4]  # YY
        month_day = current_date[4:8]   # MMDD
        counter = str(sequence.sequence_counter).zfill(4)  # XXXX

        return f"LOT-{year_short}{month_day}-{counter}"



class Warehouse(db.Model):
    """
    Warehouse model for managing physical warehouse locations.
    Warehouses store tools, chemicals, and expendables before they are transferred to kits.
    """
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True, default="USA")
    warehouse_type = db.Column(db.String(50), nullable=False, default="satellite")  # main, satellite
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    tools = db.relationship("Tool", back_populates="warehouse", lazy="dynamic")
    chemicals = db.relationship("Chemical", back_populates="warehouse", lazy="dynamic")
    expendables = db.relationship("Expendable", back_populates="warehouse", lazy="dynamic")
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    def to_dict(self, include_counts=False):
        """Convert warehouse to dictionary representation."""
        result = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "warehouse_type": self.warehouse_type,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        # Only include counts if explicitly requested to avoid N+1 queries
        if include_counts:
            try:
                result["created_by"] = self.created_by.name if self.created_by else None
                # Use direct queries instead of relationships to ensure accurate counts
                from models import Chemical, Expendable, Tool
                result["tools_count"] = Tool.query.filter_by(warehouse_id=self.id).count()
                result["chemicals_count"] = Chemical.query.filter_by(warehouse_id=self.id).count()
                result["expendables_count"] = Expendable.query.filter_by(warehouse_id=self.id).count()
            except Exception as e:
                # If queries fail, skip counts
                print(f"Error getting counts for warehouse {self.id}: {e}")
                result["created_by"] = None
                result["tools_count"] = 0
                result["chemicals_count"] = 0
                result["expendables_count"] = 0

        return result


class WarehouseTransfer(db.Model):
    """
    WarehouseTransfer model for tracking item movements between warehouses and kits.
    Provides complete audit trail for inventory transfers.
    Supports tools, chemicals, and expendables.
    """
    __tablename__ = "warehouse_transfers"

    id = db.Column(db.Integer, primary_key=True)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True, index=True)
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True, index=True)
    to_kit_id = db.Column(db.Integer, db.ForeignKey("kits.id"), nullable=True, index=True)
    from_kit_id = db.Column(db.Integer, db.ForeignKey("kits.id"), nullable=True, index=True)
    item_type = db.Column(db.String(50), nullable=False, index=True)  # tool, chemical, expendable
    item_id = db.Column(db.Integer, nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    transfer_date = db.Column(db.DateTime, default=get_current_time, nullable=False, index=True)
    transferred_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="completed", index=True)  # pending, completed, cancelled

    # Relationships
    from_warehouse = db.relationship("Warehouse", foreign_keys=[from_warehouse_id])
    to_warehouse = db.relationship("Warehouse", foreign_keys=[to_warehouse_id])
    to_kit = db.relationship("Kit", foreign_keys=[to_kit_id])
    from_kit = db.relationship("Kit", foreign_keys=[from_kit_id])
    transferred_by = db.relationship("User", foreign_keys=[transferred_by_id])

    def to_dict(self):
        """Convert transfer to dictionary representation."""
        return {
            "id": self.id,
            "from_warehouse": self.from_warehouse.name if self.from_warehouse else None,
            "to_warehouse": self.to_warehouse.name if self.to_warehouse else None,
            "to_kit": self.to_kit.name if self.to_kit else None,
            "from_kit": self.from_kit.name if self.from_kit else None,
            "item_type": self.item_type,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "transfer_date": self.transfer_date.isoformat() if self.transfer_date else None,
            "transferred_by": self.transferred_by.username if self.transferred_by else None,
            "notes": self.notes,
            "status": self.status
        }

# Import enhanced messaging models
