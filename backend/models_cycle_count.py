from datetime import datetime
from models import db, Tool, Chemical

class CycleCountSchedule(db.Model):
    __tablename__ = 'cycle_count_schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    frequency = db.Column(db.String, nullable=False)  # daily, weekly, monthly, quarterly, annual
    method = db.Column(db.String, nullable=False)     # ABC, random, location, category
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    batches = db.relationship('CycleCountBatch', backref='schedule', lazy=True)

    def to_dict(self, include_batches=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'frequency': self.frequency,
            'method': self.method,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else 'Unknown',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

        if include_batches:
            data['batches'] = [batch.to_dict() for batch in self.batches]

        return data

class CycleCountBatch(db.Model):
    __tablename__ = 'cycle_count_batches'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('cycle_count_schedules.id'), nullable=True)
    name = db.Column(db.String, nullable=False)
    status = db.Column(
        db.String,
        nullable=False,
        default='pending'
    )  # pending, in_progress, completed, cancelled
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.String)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    items = db.relationship('CycleCountItem', backref='batch', lazy=True)

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'name': self.name,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else 'Unknown',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes,
            'item_count': len(self.items) if self.items else 0,
            'completed_count': sum(1 for item in self.items if item.status == 'counted') if self.items else 0
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data

class CycleCountItem(db.Model):
    __tablename__ = 'cycle_count_items'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('cycle_count_batches.id'), nullable=False)
    item_type = db.Column(db.String, nullable=False)  # tool, chemical
    item_id = db.Column(db.Integer, nullable=False)
    expected_quantity = db.Column(db.Float)
    expected_location = db.Column(db.String)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String, nullable=False)  # pending, counted, skipped
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    results = db.relationship('CycleCountResult', backref='item', lazy=True)

    def to_dict(self, include_results=False):
        # Get the actual item (tool or chemical)
        item_details = None
        if self.item_type == 'tool':
            tool = Tool.query.get(self.item_id)
            if tool is not None:
                item_details = {
                    'id': tool.id,
                    'number': tool.tool_number,
                    'serial': tool.serial_number,
                    'description': tool.description,
                    'location': tool.location,
                    'category': tool.category,
                    'status': tool.status
                }
            else:
                item_details = {'error': 'Tool not found'}
        elif self.item_type == 'chemical':
            chemical = Chemical.query.get(self.item_id)
            if chemical is not None:
                item_details = {
                    'id': chemical.id,
                    'part_number': chemical.part_number,
                    'lot_number': chemical.lot_number,
                    'description': chemical.description,
                    'quantity': chemical.quantity,
                    'unit': chemical.unit,
                    'location': chemical.location,
                    'category': chemical.category,
                    'status': chemical.status
                }
            else:
                item_details = {'error': 'Chemical not found'}

        data = {
            'id': self.id,
            'batch_id': self.batch_id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'item_details': item_details,
            'expected_quantity': self.expected_quantity,
            'expected_location': self.expected_location,
            'assigned_to': self.assigned_to,
            'assignee_name': self.assignee.name if self.assignee else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_results:
            data['results'] = [result.to_dict() for result in self.results]

        return data

class CycleCountResult(db.Model):
    __tablename__ = 'cycle_count_results'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('cycle_count_items.id'), nullable=False)
    counted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    counted_at = db.Column(db.DateTime, default=datetime.utcnow)
    actual_quantity = db.Column(db.Float)
    actual_location = db.Column(db.String)
    condition = db.Column(db.String)
    notes = db.Column(db.String)
    has_discrepancy = db.Column(db.Boolean, default=False)
    discrepancy_type = db.Column(db.String)  # quantity, location, condition, missing, extra
    discrepancy_notes = db.Column(db.String)

    # Relationships
    counter = db.relationship('User', foreign_keys=[counted_by])
    adjustments = db.relationship('CycleCountAdjustment', backref='result', lazy=True)

    def to_dict(self, include_adjustments=False):
        data = {
            'id': self.id,
            'item_id': self.item_id,
            'counted_by': self.counted_by,
            'counter_name': self.counter.name if self.counter else 'Unknown',
            'counted_at': self.counted_at.isoformat(),
            'actual_quantity': self.actual_quantity,
            'actual_location': self.actual_location,
            'condition': self.condition,
            'notes': self.notes,
            'has_discrepancy': self.has_discrepancy,
            'discrepancy_type': self.discrepancy_type,
            'discrepancy_notes': self.discrepancy_notes
        }

        if include_adjustments:
            data['adjustments'] = [adjustment.to_dict() for adjustment in self.adjustments]

        return data

class CycleCountAdjustment(db.Model):
    __tablename__ = 'cycle_count_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('cycle_count_results.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_at = db.Column(db.DateTime, default=datetime.utcnow)
    adjustment_type = db.Column(db.String, nullable=False)  # quantity, location, condition, status
    old_value = db.Column(db.String)
    new_value = db.Column(db.String)
    notes = db.Column(db.String)

    # Relationships
    approver = db.relationship('User', foreign_keys=[approved_by])

    def to_dict(self):
        return {
            'id': self.id,
            'result_id': self.result_id,
            'approved_by': self.approved_by,
            'approver_name': self.approver.name if self.approver else 'Unknown',
            'approved_at': self.approved_at.isoformat(),
            'adjustment_type': self.adjustment_type,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'notes': self.notes
        }
