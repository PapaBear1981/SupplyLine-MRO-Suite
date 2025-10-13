"""
Routes for Kit Reorder Request Management

This module provides API endpoints for managing reorder requests for kits.
"""

from flask import request, jsonify
from models import db, AuditLog
from models_kits import Kit, KitReorderRequest, KitExpendable, KitItem
from datetime import datetime
from auth import jwt_required, department_required
from utils.error_handler import handle_errors, ValidationError
import logging

logger = logging.getLogger(__name__)

materials_required = department_required('Materials')


def register_kit_reorder_routes(app):
    """Register all kit reorder routes"""
    
    @app.route('/api/kits/<int:kit_id>/reorder', methods=['POST'])
    @jwt_required
    @handle_errors
    def create_reorder_request(kit_id):
        """Create a reorder request for a kit"""
        kit = Kit.query.get_or_404(kit_id)
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get('part_number'):
            raise ValidationError('Part number is required')
        if not data.get('description'):
            raise ValidationError('Description is required')
        if not data.get('quantity_requested'):
            raise ValidationError('Quantity requested is required')
        
        # Create reorder request
        reorder = KitReorderRequest(
            kit_id=kit_id,
            item_type=data.get('item_type', 'expendable'),
            item_id=data.get('item_id'),
            part_number=data['part_number'],
            description=data['description'],
            quantity_requested=float(data['quantity_requested']),
            priority=data.get('priority', 'medium'),
            requested_by=request.current_user['user_id'],
            status='pending',
            notes=data.get('notes', ''),
            is_automatic=False
        )
        
        db.session.add(reorder)
        db.session.commit()
        
        # Log action
        log = AuditLog(
            action_type='kit_reorder_requested',
            action_details=f'Reorder requested for kit {kit.name}: {reorder.part_number}'
        )
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Reorder request created: ID {reorder.id}")
        return jsonify(reorder.to_dict()), 201
    
    @app.route('/api/reorder-requests', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_reorder_requests():
        """Get all reorder requests with optional filtering"""
        kit_id = request.args.get('kit_id', type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        is_automatic = request.args.get('is_automatic')
        
        query = KitReorderRequest.query
        
        if kit_id:
            query = query.filter_by(kit_id=kit_id)
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        if is_automatic is not None:
            query = query.filter_by(is_automatic=is_automatic.lower() == 'true')
        
        reorders = query.order_by(
            KitReorderRequest.priority.desc(),
            KitReorderRequest.requested_date.desc()
        ).all()
        
        return jsonify([reorder.to_dict() for reorder in reorders]), 200
    
    @app.route('/api/reorder-requests/<int:id>', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_reorder_request(id):
        """Get reorder request details"""
        reorder = KitReorderRequest.query.get_or_404(id)
        return jsonify(reorder.to_dict()), 200
    
    @app.route('/api/reorder-requests/<int:id>/approve', methods=['PUT'])
    @materials_required
    @handle_errors
    def approve_reorder_request(id):
        """Approve a reorder request"""
        reorder = KitReorderRequest.query.get_or_404(id)
        
        if reorder.status != 'pending':
            raise ValidationError('Can only approve pending requests')
        
        reorder.status = 'approved'
        reorder.approved_by = request.current_user['user_id']
        reorder.approved_date = datetime.now()
        
        db.session.commit()
        
        # Log action
        log = AuditLog(
            action_type='kit_reorder_approved',
            action_details=f'Reorder request approved: ID {reorder.id}'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(reorder.to_dict()), 200
    
    @app.route('/api/reorder-requests/<int:id>/order', methods=['PUT'])
    @materials_required
    @handle_errors
    def mark_reorder_ordered(id):
        """Mark a reorder request as ordered"""
        reorder = KitReorderRequest.query.get_or_404(id)
        
        if reorder.status not in ['pending', 'approved']:
            raise ValidationError('Can only mark pending or approved requests as ordered')
        
        reorder.status = 'ordered'
        
        db.session.commit()
        
        # Log action
        log = AuditLog(
            action_type='kit_reorder_ordered',
            action_details=f'Reorder request marked as ordered: ID {reorder.id}'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(reorder.to_dict()), 200
    
    @app.route('/api/reorder-requests/<int:id>/fulfill', methods=['PUT'])
    @materials_required
    @handle_errors
    def fulfill_reorder_request(id):
        """Mark a reorder request as fulfilled"""
        reorder = KitReorderRequest.query.get_or_404(id)

        if reorder.status != 'ordered':
            raise ValidationError('Can only fulfill ordered requests')

        # Get box_id from request body
        data = request.get_json()
        box_id = data.get('box_id')

        if not box_id:
            raise ValidationError('box_id is required to fulfill reorder')

        # Verify box belongs to the kit
        from models_kits import KitBox
        box = KitBox.query.filter_by(id=box_id, kit_id=reorder.kit_id).first()
        if not box:
            raise ValidationError('Invalid box_id for this kit')

        reorder.status = 'fulfilled'
        reorder.fulfillment_date = datetime.now()

        # Update or create item based on type
        if reorder.item_type == 'expendable':
            if reorder.item_id:
                # Update existing expendable
                expendable = KitExpendable.query.get(reorder.item_id)
                if expendable:
                    expendable.quantity += reorder.quantity_requested
                    expendable.status = 'available'
                    expendable.box_id = box_id
            else:
                # Create new expendable
                expendable = KitExpendable(
                    kit_id=reorder.kit_id,
                    box_id=box_id,
                    part_number=reorder.part_number,
                    description=reorder.description,
                    quantity=reorder.quantity_requested,
                    unit='ea',
                    location=f'Box {box.box_number}',
                    status='available'
                )
                db.session.add(expendable)

        elif reorder.item_type in ['tool', 'chemical']:
            if reorder.item_id:
                # Update existing item
                item = KitItem.query.get(reorder.item_id)
                if item:
                    item.quantity += int(reorder.quantity_requested)
                    item.status = 'available'
                    item.box_id = box_id
            else:
                # Create new item
                item = KitItem(
                    kit_id=reorder.kit_id,
                    box_id=box_id,
                    item_type=reorder.item_type,
                    part_number=reorder.part_number,
                    description=reorder.description,
                    quantity=int(reorder.quantity_requested),
                    location=f'Box {box.box_number}',
                    status='available'
                )
                db.session.add(item)

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type='kit_reorder_fulfilled',
            action_details=f'Reorder request fulfilled: ID {reorder.id}, added to box {box.box_number}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reorder.to_dict()), 200
    
    @app.route('/api/reorder-requests/<int:id>/cancel', methods=['PUT'])
    @jwt_required
    @handle_errors
    def cancel_reorder_request(id):
        """Cancel a reorder request"""
        reorder = KitReorderRequest.query.get_or_404(id)
        
        if reorder.status in ['fulfilled', 'cancelled']:
            raise ValidationError('Cannot cancel fulfilled or already cancelled requests')
        
        # Check if user has permission to cancel
        user_id = request.current_user['user_id']
        is_admin = request.current_user.get('is_admin', False)
        is_materials = request.current_user.get('department') == 'Materials'
        
        if not (is_admin or is_materials or reorder.requested_by == user_id):
            raise ValidationError('You do not have permission to cancel this request')
        
        reorder.status = 'cancelled'
        
        db.session.commit()
        
        # Log action
        log = AuditLog(
            action_type='kit_reorder_cancelled',
            action_details=f'Reorder request cancelled: ID {reorder.id}'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(reorder.to_dict()), 200
    
    @app.route('/api/reorder-requests/<int:id>', methods=['PUT'])
    @jwt_required
    @handle_errors
    def update_reorder_request(id):
        """Update a reorder request"""
        reorder = KitReorderRequest.query.get_or_404(id)
        data = request.get_json() or {}
        
        # Only allow updates to pending requests
        if reorder.status != 'pending':
            raise ValidationError('Can only update pending requests')
        
        # Check if user has permission to update
        user_id = request.current_user['user_id']
        is_admin = request.current_user.get('is_admin', False)
        is_materials = request.current_user.get('department') == 'Materials'
        
        if not (is_admin or is_materials or reorder.requested_by == user_id):
            raise ValidationError('You do not have permission to update this request')
        
        # Update fields
        if 'quantity_requested' in data:
            reorder.quantity_requested = float(data['quantity_requested'])
        if 'priority' in data:
            reorder.priority = data['priority']
        if 'notes' in data:
            reorder.notes = data['notes']
        
        db.session.commit()
        
        return jsonify(reorder.to_dict()), 200

