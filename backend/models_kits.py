"""
Database Models for Mobile Warehouse/Kits System

This module contains all database models related to the Mobile Warehouse (Kits) functionality,
including aircraft types, kits, boxes, items, transfers, reorders, and messaging.
"""

from datetime import datetime
from models import db, get_current_time


class AircraftType(db.Model):
    """
    Aircraft Type model for categorizing kits by aircraft type.
    Examples: Q400, RJ85, CL415
    """
    __tablename__ = 'aircraft_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    
    # Relationships
    kits = db.relationship('Kit', back_populates='aircraft_type', lazy='dynamic')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'kit_count': self.kits.filter_by(status='active').count() if self.kits else 0
        }


class Kit(db.Model):
    """
    Kit model representing a mobile warehouse.
    Each kit is associated with an aircraft type and contains boxes of items.
    """
    __tablename__ = 'kits'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    aircraft_type_id = db.Column(db.Integer, db.ForeignKey('aircraft_types.id'), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, maintenance
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    aircraft_type = db.relationship('AircraftType', back_populates='kits')
    creator = db.relationship('User', foreign_keys=[created_by])
    boxes = db.relationship('KitBox', back_populates='kit', lazy='dynamic', cascade='all, delete-orphan')
    items = db.relationship('KitItem', back_populates='kit', lazy='dynamic', cascade='all, delete-orphan')
    expendables = db.relationship('KitExpendable', back_populates='kit', lazy='dynamic', cascade='all, delete-orphan')
    issuances = db.relationship('KitIssuance', back_populates='kit', lazy='dynamic', cascade='all, delete-orphan')
    reorder_requests = db.relationship('KitReorderRequest', back_populates='kit', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('KitMessage', back_populates='kit', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'aircraft_type_id': self.aircraft_type_id,
            'aircraft_type_name': self.aircraft_type.name if self.aircraft_type else None,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'box_count': self.boxes.count() if self.boxes else 0,
            'item_count': self.items.count() + self.expendables.count() if self.items and self.expendables else 0
        }
        
        if include_details:
            data['boxes'] = [box.to_dict() for box in self.boxes.all()] if self.boxes else []
            data['pending_reorders'] = self.reorder_requests.filter_by(status='pending').count() if self.reorder_requests else 0
            data['unread_messages'] = self.messages.filter_by(is_read=False).count() if self.messages else 0
        
        return data


class KitBox(db.Model):
    """
    KitBox model representing a physical box within a kit.
    Each box has a type: expendable, tooling, consumable, loose, or floor.
    """
    __tablename__ = 'kit_boxes'
    
    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'), nullable=False)
    box_number = db.Column(db.String(20), nullable=False)  # e.g., "Box1", "Box2", "Loose", "Floor"
    box_type = db.Column(db.String(20), nullable=False)  # expendable, tooling, consumable, loose, floor
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    
    # Relationships
    kit = db.relationship('Kit', back_populates='boxes')
    items = db.relationship('KitItem', back_populates='box', lazy='dynamic', cascade='all, delete-orphan')
    expendables = db.relationship('KitExpendable', back_populates='box', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint: kit_id + box_number must be unique
    __table_args__ = (
        db.UniqueConstraint('kit_id', 'box_number', name='uix_kit_box_number'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'kit_id': self.kit_id,
            'box_number': self.box_number,
            'box_type': self.box_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'item_count': (self.items.count() if self.items else 0) + (self.expendables.count() if self.expendables else 0)
        }


class KitItem(db.Model):
    """
    KitItem model representing tools or chemicals transferred into a kit.
    Links to existing Tool or Chemical records.
    """
    __tablename__ = 'kit_items'
    
    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('kit_boxes.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # tool, chemical
    item_id = db.Column(db.Integer, nullable=False)  # FK to tools.id or chemicals.id
    part_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    lot_number = db.Column(db.String(100))
    description = db.Column(db.String(500))
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    location = db.Column(db.String(100))  # Location within the box
    status = db.Column(db.String(20), nullable=False, default='available')  # available, issued, maintenance
    added_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    last_updated = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)
    
    # Relationships
    kit = db.relationship('Kit', back_populates='items')
    box = db.relationship('KitBox', back_populates='items')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'kit_id': self.kit_id,
            'box_id': self.box_id,
            'box_number': self.box.box_number if self.box else None,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'part_number': self.part_number,
            'serial_number': self.serial_number,
            'lot_number': self.lot_number,
            'description': self.description,
            'quantity': self.quantity,
            'location': self.location,
            'status': self.status,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class KitExpendable(db.Model):
    """
    KitExpendable model for manually added expendable items.
    These are not linked to existing inventory records.
    Expendables can be tracked by lot number, serial number, or both.
    """
    __tablename__ = 'kit_expendables'

    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('kit_boxes.id'), nullable=False)
    part_number = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100))
    lot_number = db.Column(db.String(100))
    tracking_type = db.Column(db.String(20), nullable=False, default='lot')  # lot, serial, both
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False, default='each')  # each, oz, ml, etc.
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), nullable=False, default='available')  # available, low_stock, out_of_stock
    minimum_stock_level = db.Column(db.Float)
    added_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    last_updated = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)

    # Relationships
    kit = db.relationship('Kit', back_populates='expendables')
    box = db.relationship('KitBox', back_populates='expendables')

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'kit_id': self.kit_id,
            'box_id': self.box_id,
            'box_number': self.box.box_number if self.box else None,
            'part_number': self.part_number,
            'serial_number': self.serial_number,
            'lot_number': self.lot_number,
            'tracking_type': self.tracking_type,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'location': self.location,
            'status': self.status,
            'minimum_stock_level': self.minimum_stock_level,
            'is_low_stock': self.is_low_stock(),
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

    def is_low_stock(self):
        """Check if expendable is at or below minimum stock level"""
        if self.minimum_stock_level is None:
            return False
        return self.quantity <= self.minimum_stock_level

    def validate_tracking(self):
        """
        Validate that appropriate tracking identifiers are present based on tracking_type.

        Returns:
            tuple: (is_valid, error_message)
        """
        if self.tracking_type == 'lot':
            if not self.lot_number:
                return False, "Lot number is required for lot-tracked expendables"
        elif self.tracking_type == 'serial':
            if not self.serial_number:
                return False, "Serial number is required for serial-tracked expendables"
        elif self.tracking_type == 'both':
            if not self.lot_number or not self.serial_number:
                return False, "Both lot number and serial number are required for dual-tracked expendables"
        else:
            return False, f"Invalid tracking_type: {self.tracking_type}"

        return True, None


class KitIssuance(db.Model):
    """
    KitIssuance model for tracking items issued from kits.
    Records all issuances for audit and reorder purposes.
    """
    __tablename__ = 'kit_issuances'

    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # tool, chemical, expendable
    item_id = db.Column(db.Integer, nullable=False)  # FK to kit_items.id or kit_expendables.id
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(500))
    work_order = db.Column(db.String(100))
    issued_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    notes = db.Column(db.String(1000))

    # Relationships
    kit = db.relationship('Kit', back_populates='issuances')
    issuer = db.relationship('User', foreign_keys=[issued_by])

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'kit_id': self.kit_id,
            'kit_name': self.kit.name if self.kit else None,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'issued_by': self.issued_by,
            'issuer_name': self.issuer.name if self.issuer else None,
            'quantity': self.quantity,
            'purpose': self.purpose,
            'work_order': self.work_order,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'notes': self.notes
        }


class KitTransfer(db.Model):
    """
    KitTransfer model for tracking transfers between kits and warehouses.
    Supports kit-to-kit, kit-to-warehouse, and warehouse-to-kit transfers.
    """
    __tablename__ = 'kit_transfers'

    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(20), nullable=False)  # tool, chemical, expendable
    item_id = db.Column(db.Integer, nullable=False)
    from_location_type = db.Column(db.String(20), nullable=False)  # kit, warehouse
    from_location_id = db.Column(db.Integer, nullable=False)  # kit_id or warehouse identifier
    to_location_type = db.Column(db.String(20), nullable=False)  # kit, warehouse
    to_location_id = db.Column(db.Integer, nullable=False)  # kit_id or warehouse identifier
    quantity = db.Column(db.Float, nullable=False)
    transferred_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transfer_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, cancelled
    completed_date = db.Column(db.DateTime)
    notes = db.Column(db.String(1000))

    # Relationships
    transferrer = db.relationship('User', foreign_keys=[transferred_by])

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'from_location_type': self.from_location_type,
            'from_location_id': self.from_location_id,
            'to_location_type': self.to_location_type,
            'to_location_id': self.to_location_id,
            'quantity': self.quantity,
            'transferred_by': self.transferred_by,
            'transferrer_name': self.transferrer.name if self.transferrer else None,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'status': self.status,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'notes': self.notes
        }


class KitReorderRequest(db.Model):
    """
    KitReorderRequest model for tracking reorder requests.
    Can be automatically generated or manually created.
    """
    __tablename__ = 'kit_reorder_requests'

    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # tool, chemical, expendable
    item_id = db.Column(db.Integer)  # Nullable for new items
    part_number = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity_requested = db.Column(db.Float, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, urgent
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, ordered, fulfilled, cancelled
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_date = db.Column(db.DateTime)
    fulfillment_date = db.Column(db.DateTime)
    notes = db.Column(db.String(1000))
    is_automatic = db.Column(db.Boolean, default=False)  # True if auto-generated

    # Relationships
    kit = db.relationship('Kit', back_populates='reorder_requests')
    requester = db.relationship('User', foreign_keys=[requested_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    messages = db.relationship('KitMessage', back_populates='related_request', lazy='dynamic')

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'kit_id': self.kit_id,
            'kit_name': self.kit.name if self.kit else None,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'part_number': self.part_number,
            'description': self.description,
            'quantity_requested': self.quantity_requested,
            'priority': self.priority,
            'requested_by': self.requested_by,
            'requester_name': self.requester.name if self.requester else None,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'status': self.status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.name if self.approver else None,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'fulfillment_date': self.fulfillment_date.isoformat() if self.fulfillment_date else None,
            'notes': self.notes,
            'is_automatic': self.is_automatic,
            'message_count': self.messages.count() if self.messages else 0
        }


class KitMessage(db.Model):
    """
    KitMessage model for messaging between mechanics and stores personnel.
    Supports threading and attachments.
    """
    __tablename__ = 'kit_messages'

    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'), nullable=False)
    related_request_id = db.Column(db.Integer, db.ForeignKey('kit_reorder_requests.id'))  # Optional link to reorder request
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Nullable for broadcast messages
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(5000), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    sent_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    read_date = db.Column(db.DateTime)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('kit_messages.id'))  # For threading
    attachments = db.Column(db.String(1000))  # JSON string of attachment paths

    # Relationships
    kit = db.relationship('Kit', back_populates='messages')
    related_request = db.relationship('KitReorderRequest', back_populates='messages')
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    parent_message = db.relationship('KitMessage', remote_side=[id], backref='replies')

    def to_dict(self, include_replies=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'kit_id': self.kit_id,
            'kit_name': self.kit.name if self.kit else None,
            'related_request_id': self.related_request_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name if self.sender else None,
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient.name if self.recipient else None,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'sent_date': self.sent_date.isoformat() if self.sent_date else None,
            'read_date': self.read_date.isoformat() if self.read_date else None,
            'parent_message_id': self.parent_message_id,
            'attachments': self.attachments,
            'reply_count': len(self.replies) if hasattr(self, 'replies') else 0
        }

        if include_replies and hasattr(self, 'replies'):
            data['replies'] = [reply.to_dict() for reply in self.replies]

        return data

