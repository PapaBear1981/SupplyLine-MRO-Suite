"""
Routes for Kit Transfer Management

This module provides API endpoints for managing transfers between kits and warehouses.
"""

from flask import request, jsonify
from models import db, AuditLog, Chemical, Warehouse, Tool
from models_kits import Kit, KitItem, KitExpendable, KitTransfer, KitBox
from datetime import datetime
from auth import jwt_required, department_required
from utils.error_handler import handle_errors, ValidationError
from utils.lot_utils import create_child_chemical
from utils.transaction_helper import record_transaction
import logging

logger = logging.getLogger(__name__)

materials_required = department_required('Materials')


def register_kit_transfer_routes(app):
    """Register all kit transfer routes"""

    @app.route('/api/transfers', methods=['POST'])
    @materials_required
    @handle_errors
    def create_transfer():
        """Initiate a transfer. Kit-involving transfers remain pending until explicitly completed."""
        data = request.get_json() or {}

        required_fields = [
            'item_type',
            'item_id',
            'from_location_type',
            'from_location_id',
            'to_location_type',
            'to_location_id',
            'quantity'
        ]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')

        try:
            quantity = float(data['quantity'])
        except (TypeError, ValueError):
            raise ValidationError('Quantity must be a number')

        if quantity <= 0:
            raise ValidationError('Quantity must be greater than zero')

        from_type = data['from_location_type']
        to_type = data['to_location_type']

        if from_type not in {'kit', 'warehouse'}:
            raise ValidationError('Invalid from_location_type')
        if to_type not in {'kit', 'warehouse'}:
            raise ValidationError('Invalid to_location_type')

        # Validate source and destination locations
        if from_type == 'kit':
            source_kit = Kit.query.get(data['from_location_id'])
            if not source_kit:
                raise ValidationError('Source kit not found')
        else:
            source_warehouse = Warehouse.query.get(data['from_location_id'])
            if not source_warehouse:
                raise ValidationError('Source warehouse not found')

        if to_type == 'kit':
            dest_kit = Kit.query.get(data['to_location_id'])
            if not dest_kit:
                raise ValidationError('Destination kit not found')
        else:
            dest_warehouse = Warehouse.query.get(data['to_location_id'])
            if not dest_warehouse:
                raise ValidationError('Destination warehouse not found')

        # Validate source item availability
        if from_type == 'kit':
            if data['item_type'] == 'expendable':
                source_item = KitExpendable.query.get(data['item_id'])
            else:
                source_item = KitItem.query.get(data['item_id'])

            if not source_item or source_item.kit_id != data['from_location_id']:
                raise ValidationError('Source item not found')

            if source_item.quantity < quantity:
                raise ValidationError(f'Insufficient quantity. Available: {source_item.quantity}')

        elif from_type == 'warehouse':
            if data['item_type'] == 'chemical':
                chemical = Chemical.query.get(data['item_id'])
                if not chemical:
                    raise ValidationError('Source chemical not found')
                if chemical.quantity < quantity:
                    raise ValidationError(f'Insufficient quantity. Available: {chemical.quantity}')
            elif data['item_type'] == 'tool':
                tool = Tool.query.get(data['item_id'])
                if not tool:
                    raise ValidationError('Tool not found')
                if tool.warehouse_id != data['from_location_id']:
                    raise ValidationError('Tool is not in the source warehouse')
                if quantity != 1:
                    raise ValidationError('Tool transfers must have a quantity of 1')

        # Determine the item reference stored in the transfer record.
        transfer_item_id = data['item_id']
        if from_type == 'kit' and data['item_type'] != 'expendable':
            kit_item = KitItem.query.get(data['item_id'])
            if not kit_item:
                raise ValidationError('Source item not found')
            transfer_item_id = kit_item.item_id

        transfer = KitTransfer(
            item_type=data['item_type'],
            item_id=transfer_item_id,
            from_location_type=from_type,
            from_location_id=data['from_location_id'],
            to_location_type=to_type,
            to_location_id=data['to_location_id'],
            quantity=quantity,
            transferred_by=request.current_user['user_id'],
            notes=data.get('notes', '')
        )

        db.session.add(transfer)
        db.session.flush()

        creation_log = AuditLog(
            action_type='kit_transfer_created',
            action_details=(
                f"Transfer created: {data['item_type']} from {from_type} {data['from_location_id']} "
                f"to {to_type} {data['to_location_id']}"
            )
        )
        db.session.add(creation_log)
        db.session.commit()

        auto_complete = from_type == 'warehouse' and to_type == 'warehouse'

        if auto_complete:
            response_data = _complete_transfer_internal(
                transfer.id,
                request.current_user['user_id'],
                box_id=data.get('box_id')
            )
        else:
            response_data = transfer.to_dict()
            response_data['lot_split'] = False

        logger.info(
            'Transfer created',
            extra={
                'transfer_id': transfer.id,
                'from_type': from_type,
                'to_type': to_type,
                'auto_complete': auto_complete
            }
        )

        return jsonify(response_data), 201

    def _complete_transfer_internal(transfer_id, user_id, box_id=None):
        """Complete the transfer identified by transfer_id and return its serialized data."""
        transfer = KitTransfer.query.get_or_404(transfer_id)

        if transfer.status != 'pending':
            raise ValidationError('Transfer is not in pending status')

        quantity = transfer.quantity
        if quantity <= 0:
            raise ValidationError('Transfer quantity must be greater than zero')

        source_item = None
        source_item_snapshot = {}
        source_chemical = None
        child_chemical = None

        if transfer.from_location_type == 'kit':
            if transfer.item_type == 'expendable':
                source_item = KitExpendable.query.get(transfer.item_id)
                if not source_item or source_item.kit_id != transfer.from_location_id:
                    raise ValidationError('Source item not found')
                if source_item.quantity < quantity:
                    raise ValidationError(f'Insufficient quantity. Available: {source_item.quantity}')
                source_item_snapshot = {
                    'part_number': source_item.part_number,
                    'description': source_item.description,
                    'unit': source_item.unit,
                    'location': source_item.location,
                    'serial_number': source_item.serial_number,
                    'lot_number': source_item.lot_number,
                    'tracking_type': source_item.tracking_type
                }
            else:
                kit_item = KitItem.query.filter_by(
                    kit_id=transfer.from_location_id,
                    item_type=transfer.item_type,
                    item_id=transfer.item_id
                ).first()
                if not kit_item:
                    raise ValidationError('Source item not found')
                if kit_item.quantity < quantity:
                    raise ValidationError(f'Insufficient quantity. Available: {kit_item.quantity}')
                source_item = kit_item
                source_item_snapshot = {
                    'part_number': kit_item.part_number,
                    'description': kit_item.description,
                    'serial_number': kit_item.serial_number,
                    'lot_number': kit_item.lot_number,
                    'location': kit_item.location,
                    'item_id': kit_item.item_id,
                    'item_type': kit_item.item_type
                }
        elif transfer.from_location_type == 'warehouse':
            if transfer.item_type == 'chemical':
                source_chemical = Chemical.query.get(transfer.item_id)
                if not source_chemical:
                    raise ValidationError('Source chemical not found')
                if source_chemical.quantity < quantity:
                    raise ValidationError(f'Insufficient quantity. Available: {source_chemical.quantity}')

                dest_warehouse_id = transfer.to_location_id if transfer.to_location_type == 'warehouse' else None
                is_partial_transfer = quantity < source_chemical.quantity

                if transfer.to_location_type == 'kit' and is_partial_transfer:
                    child_chemical = create_child_chemical(
                        parent_chemical=source_chemical,
                        quantity=quantity,
                        destination_warehouse_id=dest_warehouse_id
                    )
                    db.session.add(child_chemical)
                    db.session.flush()
                else:
                    if transfer.to_location_type == 'warehouse':
                        source_chemical.warehouse_id = dest_warehouse_id
                    else:
                        source_chemical.warehouse_id = None

            elif transfer.item_type == 'tool':
                tool = Tool.query.get(transfer.item_id)
                if not tool:
                    raise ValidationError('Tool not found')
                if tool.warehouse_id != transfer.from_location_id:
                    raise ValidationError('Tool is not in the source warehouse')
                if quantity != 1:
                    raise ValidationError('Tool transfers must have a quantity of 1')

                if transfer.to_location_type == 'warehouse':
                    tool.warehouse_id = transfer.to_location_id
                else:
                    tool.warehouse_id = None

        if transfer.from_location_type == 'kit' and source_item:
            source_item.quantity -= quantity
            if transfer.item_type == 'expendable':
                if source_item.quantity <= 0:
                    db.session.delete(source_item)
            else:
                if source_item.quantity <= 0:
                    source_item.status = 'transferred'

        if transfer.to_location_type == 'kit':
            dest_kit = Kit.query.get(transfer.to_location_id)
            if not dest_kit:
                raise ValidationError('Destination kit not found')

            dest_box = None
            if box_id:
                dest_box = KitBox.query.filter_by(id=box_id, kit_id=transfer.to_location_id).first()
                if not dest_box:
                    raise ValidationError('Specified box not found in destination kit')
            else:
                dest_box = dest_kit.boxes.first()
                if not dest_box:
                    box_type_map = {
                        'expendable': 'expendable',
                        'tool': 'tool',
                        'chemical': 'chemical'
                    }
                    dest_box = KitBox(
                        kit_id=dest_kit.id,
                        box_number='1',
                        box_type=box_type_map.get(transfer.item_type, 'general'),
                        description='Auto-created transfer box'
                    )
                    db.session.add(dest_box)
                    db.session.flush()

            if transfer.item_type == 'expendable':
                q = KitExpendable.query.filter_by(
                    kit_id=transfer.to_location_id,
                    box_id=dest_box.id,
                    part_number=source_item_snapshot.get('part_number'),
                    tracking_type=source_item_snapshot.get('tracking_type', 'none'),
                    unit=source_item_snapshot.get('unit', 'each')
                )

                tracking_type = (source_item_snapshot.get('tracking_type') or 'none').lower()
                if tracking_type == 'lot':
                    q = q.filter_by(lot_number=source_item_snapshot.get('lot_number'), serial_number=None)
                elif tracking_type == 'serial':
                    q = q.filter_by(serial_number=source_item_snapshot.get('serial_number'), lot_number=None)
                else:
                    q = q.filter_by(lot_number=None, serial_number=None)

                dest_item = q.first()

                if dest_item:
                    dest_item.quantity += quantity
                else:
                    new_expendable = KitExpendable(
                        kit_id=transfer.to_location_id,
                        box_id=dest_box.id,
                        part_number=source_item_snapshot.get('part_number'),
                        description=source_item_snapshot.get('description', ''),
                        quantity=quantity,
                        unit=source_item_snapshot.get('unit', 'each'),
                        location=source_item_snapshot.get('location', ''),
                        serial_number=source_item_snapshot.get('serial_number'),
                        lot_number=source_item_snapshot.get('lot_number'),
                        tracking_type=tracking_type
                    )
                    db.session.add(new_expendable)
            else:
                actual_item_id = source_item_snapshot.get('item_id', transfer.item_id)
                if transfer.item_type == 'tool':
                    actual_item = Tool.query.get(actual_item_id)
                    if not actual_item:
                        raise ValidationError('Tool not found')
                else:
                    if transfer.item_type == 'chemical' and child_chemical:
                        actual_item = child_chemical
                    else:
                        actual_item = Chemical.query.get(actual_item_id)
                        if not actual_item:
                            raise ValidationError('Chemical not found')

                new_item = KitItem(
                    kit_id=transfer.to_location_id,
                    box_id=dest_box.id,
                    item_type=transfer.item_type,
                    item_id=actual_item.id,
                    part_number=getattr(actual_item, 'part_number', source_item_snapshot.get('part_number')),
                    serial_number=getattr(actual_item, 'serial_number', source_item_snapshot.get('serial_number')),
                    lot_number=getattr(actual_item, 'lot_number', source_item_snapshot.get('lot_number')),
                    description=getattr(actual_item, 'description', source_item_snapshot.get('description', '')),
                    quantity=quantity,
                    location=source_item_snapshot.get('location', ''),
                    status='available'
                )
                db.session.add(new_item)

        elif transfer.to_location_type == 'warehouse':
            dest_warehouse = Warehouse.query.get(transfer.to_location_id)
            if not dest_warehouse:
                raise ValidationError('Destination warehouse not found')

            if transfer.item_type == 'chemical' and source_item and hasattr(source_item, 'item_id'):
                transferred_chemical = Chemical.query.get(source_item.item_id)
                if transferred_chemical:
                    transferred_chemical.warehouse_id = transfer.to_location_id
            elif transfer.item_type == 'tool' and source_item and hasattr(source_item, 'item_id'):
                transferred_tool = Tool.query.get(source_item.item_id)
                if transferred_tool:
                    transferred_tool.warehouse_id = transfer.to_location_id

        transfer.status = 'completed'
        transfer.completed_date = datetime.now()

        db.session.commit()

        if transfer.from_location_type == 'warehouse' and transfer.to_location_type == 'warehouse':
            from_warehouse = Warehouse.query.get(transfer.from_location_id)
            to_warehouse = Warehouse.query.get(transfer.to_location_id)
            if from_warehouse and to_warehouse:
                record_transaction(
                    item_type=transfer.item_type,
                    item_id=transfer.item_id,
                    transaction_type='transfer',
                    user_id=user_id,
                    quantity_change=0,
                    location_from=from_warehouse.name,
                    location_to=to_warehouse.name,
                    notes='Warehouse to warehouse transfer'
                )

        log = AuditLog(
            action_type='kit_transfer_completed',
            action_details=f'Transfer completed: ID {transfer.id}'
        )
        db.session.add(log)
        db.session.commit()

        response = transfer.to_dict()
        response['lot_split'] = bool(child_chemical)
        if child_chemical:
            response['child_chemical'] = child_chemical.to_dict()
            response['parent_lot_number'] = source_chemical.lot_number if source_chemical else None

        return response

    @app.route('/api/transfers/<int:id>/complete', methods=['PUT'])
    @materials_required
    @handle_errors
    def complete_transfer(id):
        """Complete a transfer"""
        data = request.get_json(silent=True) or {}
        response = _complete_transfer_internal(id, request.current_user['user_id'], box_id=data.get('box_id'))
        return jsonify(response), 200
    @app.route('/api/transfers', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_transfers():
        """Get all transfers with optional filtering"""
        from sqlalchemy import or_

        status = request.args.get('status')
        kit_id = request.args.get('kit_id', type=int)  # Kit as either source or destination
        from_kit_id = request.args.get('from_kit_id', type=int)
        to_kit_id = request.args.get('to_kit_id', type=int)

        query = KitTransfer.query

        if status:
            query = query.filter_by(status=status)

        # If kit_id is provided, match transfers where kit is either source OR destination
        if kit_id:
            query = query.filter(
                or_(
                    (KitTransfer.from_location_type == 'kit') & (KitTransfer.from_location_id == kit_id),
                    (KitTransfer.to_location_type == 'kit') & (KitTransfer.to_location_id == kit_id)
                )
            )
        else:
            # Otherwise use the specific from/to filters
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
