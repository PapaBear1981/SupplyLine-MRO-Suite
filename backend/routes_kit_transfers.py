"""
Routes for Kit Transfer Management

This module provides API endpoints for managing transfers between kits and warehouses.
"""

from flask import request, jsonify
from models import db, AuditLog
from models_kits import Kit, KitItem, KitExpendable, KitTransfer
from datetime import datetime
from auth import jwt_required, department_required
from utils.error_handler import handle_errors, ValidationError
import logging

logger = logging.getLogger(__name__)

materials_required = department_required('Materials')


def register_kit_transfer_routes(app):
    """Register all kit transfer routes"""

    @app.route('/api/transfers', methods=['POST'])
    @materials_required
    @handle_errors
    def create_transfer():
        """Initiate and complete a transfer between kits or between kit and warehouse"""
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['item_type', 'item_id', 'from_location_type', 'from_location_id',
                          'to_location_type', 'to_location_id', 'quantity']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')

        quantity = float(data['quantity'])

        # Validate locations
        if data['from_location_type'] not in ['kit', 'warehouse']:
            raise ValidationError('Invalid from_location_type')
        if data['to_location_type'] not in ['kit', 'warehouse']:
            raise ValidationError('Invalid to_location_type')

        # Get source item and verify quantity
        source_item = None
        if data['from_location_type'] == 'kit':
            if data['item_type'] == 'expendable':
                source_item = KitExpendable.query.get(data['item_id'])
            else:
                source_item = KitItem.query.get(data['item_id'])

            if not source_item:
                raise ValidationError('Source item not found')

            if source_item.quantity < quantity:
                raise ValidationError(f'Insufficient quantity. Available: {source_item.quantity}')

        # Create transfer record
        transfer = KitTransfer(
            item_type=data['item_type'],
            item_id=data['item_id'],
            from_location_type=data['from_location_type'],
            from_location_id=data['from_location_id'],
            to_location_type=data['to_location_type'],
            to_location_id=data['to_location_id'],
            quantity=quantity,
            transferred_by=request.current_user['user_id'],
            status='completed',  # Changed from 'pending' to 'completed'
            notes=data.get('notes', ''),
            completed_date=datetime.now()  # Set completion date
        )

        # Update source location - remove item from source
        if data['from_location_type'] == 'kit' and source_item:
            source_item.quantity -= quantity
            if source_item.quantity <= 0:
                # Remove the item completely if quantity is 0
                db.session.delete(source_item)

        # Update destination location - add item to destination
        if data['to_location_type'] == 'kit':
            dest_kit = Kit.query.get(data['to_location_id'])
            if not dest_kit:
                raise ValidationError('Destination kit not found')

            if data['item_type'] == 'expendable':
                # For expendables, check if same part number exists in destination
                dest_item = KitExpendable.query.filter_by(
                    kit_id=data['to_location_id'],
                    part_number=source_item.part_number if source_item else None
                ).first()

                if dest_item:
                    # Add to existing expendable
                    dest_item.quantity += quantity
                else:
                    # Create new expendable in destination kit
                    # Get first available box or create in loose
                    dest_box = dest_kit.boxes[0] if dest_kit.boxes else None
                    if not dest_box:
                        raise ValidationError('Destination kit has no boxes')

                    new_expendable = KitExpendable(
                        kit_id=data['to_location_id'],
                        box_id=dest_box.id,
                        part_number=source_item.part_number,
                        description=source_item.description,
                        quantity=quantity,
                        unit=source_item.unit,
                        location_in_box=source_item.location_in_box
                    )
                    db.session.add(new_expendable)
            else:
                # For tools/chemicals, check if same item exists in destination
                dest_item = KitItem.query.filter_by(
                    kit_id=data['to_location_id'],
                    item_id=data['item_id'],
                    item_type=data['item_type']
                ).first()

                if dest_item:
                    # Add to existing item
                    dest_item.quantity += quantity
                else:
                    # Create new item in destination kit
                    dest_box = dest_kit.boxes[0] if dest_kit.boxes else None
                    if not dest_box:
                        raise ValidationError('Destination kit has no boxes')

                    new_item = KitItem(
                        kit_id=data['to_location_id'],
                        box_id=dest_box.id,
                        item_type=data['item_type'],
                        item_id=data['item_id'],
                        quantity=quantity,
                        status='available'
                    )
                    db.session.add(new_item)

        db.session.add(transfer)
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type='kit_transfer_completed',
            action_details=f'Transfer completed: {data["item_type"]} from {data["from_location_type"]} to {data["to_location_type"]}'
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Transfer created and completed: ID {transfer.id}")
        return jsonify(transfer.to_dict()), 201

    @app.route('/api/transfers', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_transfers():
        """Get all transfers with optional filtering"""
        status = request.args.get('status')
        from_kit_id = request.args.get('from_kit_id', type=int)
        to_kit_id = request.args.get('to_kit_id', type=int)

        query = KitTransfer.query

        if status:
            query = query.filter_by(status=status)

        if from_kit_id:
            query = query.filter_by(from_location_type='kit', from_location_id=from_kit_id)

        if to_kit_id:
            query = query.filter_by(to_location_type='kit', to_location_id=to_kit_id)

        transfers = query.order_by(KitTransfer.transfer_date.desc()).all()

        return jsonify([transfer.to_dict() for transfer in transfers]), 200

    @app.route('/api/transfers/<int:id>', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_transfer(id):
        """Get transfer details"""
        transfer = KitTransfer.query.get_or_404(id)
        return jsonify(transfer.to_dict()), 200

    @app.route('/api/transfers/<int:id>/complete', methods=['PUT'])
    @materials_required
    @handle_errors
    def complete_transfer(id):
        """Complete a transfer"""
        transfer = KitTransfer.query.get_or_404(id)

        if transfer.status != 'pending':
            raise ValidationError('Transfer is not in pending status')

        # Update source location
        if transfer.from_location_type == 'kit':
            if transfer.item_type == 'expendable':
                source_item = KitExpendable.query.get(transfer.item_id)
            else:
                source_item = KitItem.query.get(transfer.item_id)

            if source_item:
                source_item.quantity -= transfer.quantity
                if source_item.quantity <= 0:
                    source_item.status = 'transferred'

        # Update destination location
        if transfer.to_location_type == 'kit':
            # Check if item already exists in destination kit
            if transfer.item_type == 'expendable':
                dest_item = KitExpendable.query.filter_by(
                    kit_id=transfer.to_location_id,
                    part_number=source_item.part_number if source_item else None
                ).first()

                if dest_item:
                    dest_item.quantity += transfer.quantity
                else:
                    # Create new item in destination kit
                    # This would require additional logic to get box_id
                    pass
            else:
                dest_item = KitItem.query.filter_by(
                    kit_id=transfer.to_location_id,
                    item_id=transfer.item_id,
                    item_type=transfer.item_type
                ).first()

                if dest_item:
                    dest_item.quantity += transfer.quantity
                else:
                    # Create new item in destination kit
                    pass

        # Update transfer status
        transfer.status = 'completed'
        transfer.completed_date = datetime.now()

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type='kit_transfer_completed',
            action_details=f'Transfer completed: ID {transfer.id}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(transfer.to_dict()), 200

    @app.route('/api/transfers/<int:id>/cancel', methods=['PUT'])
    @materials_required
    @handle_errors
    def cancel_transfer(id):
        """Cancel a transfer"""
        transfer = KitTransfer.query.get_or_404(id)

        if transfer.status != 'pending':
            raise ValidationError('Can only cancel pending transfers')

        transfer.status = 'cancelled'
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type='kit_transfer_cancelled',
            action_details=f'Transfer cancelled: ID {transfer.id}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(transfer.to_dict()), 200
