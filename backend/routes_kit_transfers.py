"""
Routes for Kit Transfer Management

This module provides API endpoints for managing transfers between kits and warehouses.
"""

from flask import request, jsonify
from models import db, AuditLog, Chemical, Warehouse
from models_kits import Kit, KitItem, KitExpendable, KitTransfer
from datetime import datetime
from auth import jwt_required, department_required
from utils.error_handler import handle_errors, ValidationError
from utils.lot_utils import create_child_chemical
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

        quantity = int(data['quantity'])  # Integer only for chemicals

        # Validate locations
        if data['from_location_type'] not in ['kit', 'warehouse']:
            raise ValidationError('Invalid from_location_type')
        if data['to_location_type'] not in ['kit', 'warehouse']:
            raise ValidationError('Invalid to_location_type')

        # Get source item and verify quantity
        source_item = None
        source_chemical = None
        child_chemical = None  # Will be set if we create a child lot

        if data['from_location_type'] == 'warehouse' and data['item_type'] == 'chemical':
            # Handle warehouse chemical transfer with potential lot splitting
            source_chemical = Chemical.query.get(data['item_id'])
            if not source_chemical:
                raise ValidationError('Source chemical not found')

            if source_chemical.quantity < quantity:
                raise ValidationError(f'Insufficient quantity. Available: {source_chemical.quantity} {source_chemical.unit}')

            # Determine destination warehouse ID (None if transferring to kit)
            dest_warehouse_id = None
            if data['to_location_type'] == 'warehouse':
                dest_warehouse_id = data['to_location_id']

            # Check if this is a partial transfer (not the full quantity)
            is_partial_transfer = quantity < source_chemical.quantity

            logger.info(f"Transfer check: quantity={quantity}, available={source_chemical.quantity}, is_partial={is_partial_transfer}")

            if is_partial_transfer:
                logger.info(f"Creating child chemical for partial transfer")
                # Create a child chemical with new lot number
                # warehouse_id will be None if transferring to kit
                child_chemical = create_child_chemical(
                    parent_chemical=source_chemical,
                    quantity=quantity,
                    destination_warehouse_id=dest_warehouse_id
                )
                db.session.add(child_chemical)
                logger.info(f"Child chemical created: ID={child_chemical.id}, Lot={child_chemical.lot_number}")
                # The create_child_chemical function already reduces parent quantity
            else:
                logger.info(f"Full transfer - moving entire chemical")
                # Full transfer - just move the chemical
                if data['to_location_type'] == 'warehouse':
                    source_chemical.warehouse_id = dest_warehouse_id
                else:
                    # Transferring to kit - set warehouse_id to None
                    source_chemical.warehouse_id = None

        elif data['from_location_type'] == 'kit':
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
                    dest_box = dest_kit.boxes.first()
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
                # For tools/chemicals, determine which chemical ID to use
                # If we created a child chemical, use that ID; otherwise use original
                chemical_id_to_add = child_chemical.id if child_chemical else data['item_id']

                # For tools/chemicals, check if same item exists in destination
                dest_item = KitItem.query.filter_by(
                    kit_id=data['to_location_id'],
                    item_id=chemical_id_to_add,
                    item_type=data['item_type']
                ).first()

                if dest_item:
                    # Add to existing item
                    dest_item.quantity += quantity
                else:
                    # Create new item in destination kit
                    dest_box = dest_kit.boxes.first()
                    if not dest_box:
                        raise ValidationError('Destination kit has no boxes')

                    new_item = KitItem(
                        kit_id=data['to_location_id'],
                        box_id=dest_box.id,
                        item_type=data['item_type'],
                        item_id=chemical_id_to_add,  # Use child chemical ID if created
                        quantity=quantity,
                        status='available'
                    )
                    db.session.add(new_item)
        elif data['to_location_type'] == 'warehouse':
            # Handle transfer to warehouse
            dest_warehouse = Warehouse.query.get(data['to_location_id'])
            if not dest_warehouse:
                raise ValidationError('Destination warehouse not found')

            if data['item_type'] == 'chemical':
                # For chemicals transferred from kit to warehouse
                # If we have a child_chemical (from partial warehouse->kit->warehouse), use it
                # Otherwise, we need to handle the chemical from the kit
                if child_chemical:
                    # Child chemical already has correct warehouse_id set
                    pass
                else:
                    # Get the chemical being transferred from the kit
                    if source_item and hasattr(source_item, 'item_id'):
                        transferred_chemical = Chemical.query.get(source_item.item_id)
                        if transferred_chemical:
                            transferred_chemical.warehouse_id = data['to_location_id']
            elif data['item_type'] == 'tool':
                # For tools transferred from kit to warehouse
                from models import Tool
                if source_item and hasattr(source_item, 'item_id'):
                    transferred_tool = Tool.query.get(source_item.item_id)
                    if transferred_tool:
                        transferred_tool.warehouse_id = data['to_location_id']

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

        # Prepare response with child chemical info if lot was split
        response_data = transfer.to_dict()

        logger.info(f"Preparing response: child_chemical={child_chemical}, source_chemical={source_chemical}")

        if child_chemical:
            logger.info(f"Adding child chemical to response: {child_chemical.lot_number}")
            response_data['child_chemical'] = child_chemical.to_dict()
            response_data['lot_split'] = True
            response_data['parent_lot_number'] = source_chemical.lot_number if source_chemical else None
        else:
            logger.info(f"No child chemical - full transfer")
            response_data['lot_split'] = False

        logger.info(f"Response data keys: {response_data.keys()}")
        return jsonify(response_data), 201

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
