"""
Checkout and Return Management Routes for SupplyLine MRO Suite

This module provides endpoints for:
- Checkout CRUD operations (Create, Read, Update, Delete)
- Tool return processing
- Checkout history and tracking
- Overdue checkout management
- User-specific checkout queries
"""

import logging
from datetime import datetime, timedelta
from flask import request, jsonify, session
from models import db, Tool, User, Checkout, AuditLog, UserActivity
from auth import login_required, tool_manager_required
from utils.error_handler import handle_errors

logger = logging.getLogger(__name__)


def register_checkout_routes(app):
    """Register checkout and return management routes"""

    @app.route('/api/checkouts', methods=['GET', 'POST'])
    def checkouts_route():
        """Main checkouts endpoint for listing and creating checkouts"""
        try:
            if request.method == 'GET':
                checkouts = Checkout.query.all()
                return jsonify([{
                    'id': c.id,
                    'tool_id': c.tool_id,
                    'tool_number': c.tool.tool_number if c.tool else 'Unknown',
                    'serial_number': c.tool.serial_number if c.tool else 'Unknown',
                    'description': c.tool.description if c.tool else '',
                    'user_id': c.user_id,
                    'user_name': c.user.name if c.user else 'Unknown',
                    'user_department': c.user.department if c.user else 'Unknown',
                    'checkout_date': c.checkout_date.isoformat(),
                    'return_date': c.return_date.isoformat() if c.return_date else None,
                    'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                    'purpose': c.purpose,
                    'notes': c.notes,
                    'status': 'Returned' if c.return_date else 'Checked Out'
                } for c in checkouts])

            # POST - Create new checkout
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['tool_id', 'user_id']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Check if tool exists and is available
            tool = Tool.query.get(data['tool_id'])
            if not tool:
                return jsonify({'error': 'Tool not found'}), 404

            # Check if tool is already checked out
            existing_checkout = Checkout.query.filter_by(tool_id=data['tool_id'], return_date=None).first()
            if existing_checkout:
                return jsonify({'error': 'Tool is already checked out'}), 400

            # Check if tool is available (not in maintenance or retired)
            if hasattr(tool, 'status') and tool.status in ['maintenance', 'retired']:
                return jsonify({'error': f'Tool is not available for checkout (status: {tool.status})'}), 400

            # Check if user exists
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Create checkout
            checkout = Checkout(
                tool_id=data['tool_id'],
                user_id=data['user_id'],
                checkout_date=datetime.now(),
                expected_return_date=datetime.now() + timedelta(days=data.get('expected_days', 7)),
                purpose=data.get('purpose', ''),
                notes=data.get('notes', '')
            )

            db.session.add(checkout)
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='checkout_tool',
                action_details=f'Tool {tool.tool_number} checked out to {user.name}'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'id': checkout.id,
                'message': 'Tool checked out successfully',
                'checkout': {
                    'id': checkout.id,
                    'tool_id': checkout.tool_id,
                    'tool_number': tool.tool_number,
                    'user_id': checkout.user_id,
                    'user_name': user.name,
                    'checkout_date': checkout.checkout_date.isoformat(),
                    'expected_return_date': checkout.expected_return_date.isoformat() if checkout.expected_return_date else None
                }
            }), 201

        except Exception as e:
            logger.error(f"Error in checkouts route: {str(e)}")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

    @app.route('/api/checkouts/<int:id>/return', methods=['POST', 'PUT'])
    def return_route(id):
        """Process tool return"""
        try:
            print(f"Received tool return request for checkout ID: {id}, method: {request.method}")

            # Check if user is admin or Materials department
            if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
                return jsonify({'error': 'Tool management privileges required'}), 403

            # Get the checkout record
            checkout = Checkout.query.get_or_404(id)

            # Check if already returned
            if checkout.return_date:
                return jsonify({'error': 'Tool has already been returned'}), 400

            # Get return data
            data = request.get_json() or {}

            # Update checkout record
            checkout.return_date = datetime.now()
            checkout.return_condition = data.get('condition', 'Good')
            checkout.return_notes = data.get('notes', '')
            checkout.returned_by = session.get('user_id')

            # Update tool condition if provided
            if data.get('condition') and checkout.tool:
                checkout.tool.condition = data['condition']

            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='return_tool',
                action_details=f'Tool {checkout.tool.tool_number if checkout.tool else "Unknown"} returned by {checkout.user.name if checkout.user else "Unknown"}'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'message': 'Tool returned successfully',
                'checkout_id': checkout.id,
                'return_date': checkout.return_date.isoformat(),
                'condition': checkout.return_condition
            }), 200

        except Exception as e:
            logger.error(f"Error in return route: {str(e)}")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

    @app.route('/api/checkouts/user', methods=['GET'])
    @login_required
    def get_user_checkouts():
        """Get checkouts for the current user"""
        # Get the current user's checkouts from JWT token
        user_id = request.current_user['user_id']
        # Get all checkouts for the user (both active and past)
        checkouts = Checkout.query.filter_by(user_id=user_id).all()

        return jsonify([{
            'id': c.id,
            'tool_id': c.tool_id,
            'tool_number': c.tool.tool_number if c.tool else 'Unknown',
            'serial_number': c.tool.serial_number if c.tool else 'Unknown',
            'description': c.tool.description if c.tool else '',
            'status': 'Checked Out' if not c.return_date else 'Returned',
            'checkout_date': c.checkout_date.isoformat(),
            'return_date': c.return_date.isoformat() if c.return_date else None,
            'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None
        } for c in checkouts]), 200

    @app.route('/api/checkouts/overdue', methods=['GET'])
    @tool_manager_required
    def get_overdue_checkouts():
        """Get all overdue checkouts"""
        # Get all overdue checkouts (expected_return_date < current date and not returned)
        now = datetime.now()
        overdue_checkouts = Checkout.query.filter(
            Checkout.return_date.is_(None),
            Checkout.expected_return_date < now
        ).all()

        result = []
        for c in overdue_checkouts:
            # Calculate days overdue
            expected_date = c.expected_return_date
            days_overdue = (now - expected_date).days if expected_date else 0

            result.append({
                'id': c.id,
                'tool_id': c.tool_id,
                'tool_number': c.tool.tool_number if c.tool else 'Unknown',
                'serial_number': c.tool.serial_number if c.tool else 'Unknown',
                'description': c.tool.description if c.tool else '',
                'user_id': c.user_id,
                'user_name': c.user.name if c.user else 'Unknown',
                'checkout_date': c.checkout_date.isoformat(),
                'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                'days_overdue': days_overdue
            })

        return jsonify(result), 200

    # Tool checkout history endpoint is handled by routes/tools.py to avoid duplication

    @app.route('/api/checkouts/<int:id>/details', methods=['GET'])
    def get_checkout_details(id):
        """Get detailed information about a specific checkout transaction"""
        checkout = Checkout.query.get_or_404(id)

        # Get tool and user information
        tool = checkout.tool
        user = checkout.user

        # Calculate duration if returned
        duration_days = None
        if checkout.return_date:
            duration_days = (checkout.return_date - checkout.checkout_date).days

        # Check if overdue
        is_overdue = (checkout.return_date is None and
                     checkout.expected_return_date and
                     checkout.expected_return_date < datetime.now())

        return jsonify({
            'id': checkout.id,
            'tool': {
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'category': tool.category,
                'location': tool.location
            } if tool else None,
            'user': {
                'id': user.id,
                'name': user.name,
                'employee_number': user.employee_number,
                'department': user.department
            } if user else None,
            'checkout_date': checkout.checkout_date.isoformat(),
            'return_date': checkout.return_date.isoformat() if checkout.return_date else None,
            'expected_return_date': checkout.expected_return_date.isoformat() if checkout.expected_return_date else None,
            'condition_at_return': getattr(checkout, 'return_condition', None),
            'returned_by': getattr(checkout, 'returned_by', None),
            'found': getattr(checkout, 'found', None),
            'return_notes': getattr(checkout, 'return_notes', None),
            'duration_days': duration_days,
            'is_overdue': is_overdue,
            'status': 'Returned' if checkout.return_date else ('Overdue' if is_overdue else 'Checked Out')
        }), 200
