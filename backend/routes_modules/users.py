"""
User Management Routes for SupplyLine MRO Suite

This module provides endpoints for:
- User CRUD operations (Create, Read, Update, Delete)
- User search and filtering
- User account management (unlock, deactivate)
- User audit logs and activity tracking
"""

import logging
from datetime import datetime, timezone
from flask import request, jsonify, session
from models import db, User, AuditLog
from auth import admin_required, tool_manager_required
from utils.error_handler import handle_errors

logger = logging.getLogger(__name__)


def register_user_routes(app):
    """Register user management routes"""

    @app.route('/api/users', methods=['GET', 'POST'])
    def users_route():
        """Main users endpoint for listing and creating users"""
        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'User management privileges required'}), 403

        if request.method == 'GET':
            # Check if there's a search query for employee number
            search_query = request.args.get('q')

            # Check if we should include lockout info (admin only)
            include_lockout_info = session.get('is_admin', False)

            if search_query:
                # Search for users by employee number
                search_term = f'%{search_query}%'
                users = User.query.filter(User.employee_number.like(search_term)).all()
                return jsonify([u.to_dict(include_roles=True, include_lockout_info=include_lockout_info) for u in users])
            else:
                # Get all users, including inactive ones
                users = User.query.all()
                return jsonify([u.to_dict(include_roles=True, include_lockout_info=include_lockout_info) for u in users])

        # POST - Create a new user
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['name', 'employee_number', 'department']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if user with same employee number already exists
        if User.query.filter_by(employee_number=data['employee_number']).first():
            return jsonify({'error': 'A user with this employee number already exists'}), 400

        # Create new user
        u = User(
            name=data.get('name'),
            employee_number=data.get('employee_number'),
            department=data.get('department'),
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True)
        )

        # Set password if provided
        if data.get('password'):
            u.set_password(data['password'])

        db.session.add(u)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='create_user',
            action_details=f'Created user {u.id} ({u.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(u.to_dict()), 201

    @app.route('/api/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def user_detail_route(id):
        """Individual user management endpoint"""
        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'User management privileges required'}), 403

        user = User.query.get_or_404(id)

        if request.method == 'GET':
            # Include lockout info if admin
            include_lockout_info = session.get('is_admin', False)
            return jsonify(user.to_dict(include_roles=True, include_lockout_info=include_lockout_info))

        elif request.method == 'PUT':
            # Update user
            data = request.get_json() or {}

            # Check if employee number is being changed and if it conflicts
            if 'employee_number' in data and data['employee_number'] != user.employee_number:
                existing_user = User.query.filter_by(employee_number=data['employee_number']).first()
                if existing_user:
                    return jsonify({'error': 'A user with this employee number already exists'}), 400

            # Update fields
            if 'name' in data:
                user.name = data['name']
            if 'employee_number' in data:
                user.employee_number = data['employee_number']
            if 'department' in data:
                user.department = data['department']
            if 'is_admin' in data and session.get('is_admin', False):  # Only admins can change admin status
                user.is_admin = data['is_admin']
            if 'is_active' in data:
                user.is_active = data['is_active']

            # Update password if provided
            if data.get('password'):
                user.set_password(data['password'])

            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='update_user',
                action_details=f'Updated user {user.id} ({user.name})'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify(user.to_dict())

        elif request.method == 'DELETE':
            # Only admins can delete users
            if not session.get('is_admin', False):
                return jsonify({'error': 'Admin privileges required to delete users'}), 403

            # Instead of deleting, deactivate the user to preserve history
            user.is_active = False
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='deactivate_user',
                action_details=f'Deactivated user {user.id} ({user.name})'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({'message': f'User {user.name} deactivated successfully'})

    @app.route('/api/users/<int:id>/unlock', methods=['POST'])
    @admin_required
    def unlock_user_account(id):
        """Unlock a user account that has been locked due to failed login attempts."""
        # Get the user
        user = User.query.get_or_404(id)

        # Check if user account is actually locked
        if not getattr(user, 'is_locked', False):
            return jsonify({'error': 'User account is not locked'}), 400

        # Unlock the account
        user.is_locked = False
        user.failed_login_attempts = 0
        user.locked_until = None

        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='unlock_user_account',
            action_details=f'Unlocked user account {user.id} ({user.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': f'User account {user.name} unlocked successfully',
            'user_id': user.id,
            'is_locked': user.is_locked
        }), 200

    @app.route('/api/audit/users/<int:user_id>', methods=['GET'])
    def user_audit_logs_route(user_id):
        """Get audit logs for a specific user"""
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get audit logs for the specific user
        logs = AuditLog.query.filter(
            AuditLog.action_details.like(f'%user {user_id}%')
        ).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

        # Get total count for pagination
        total_count = AuditLog.query.filter(
            AuditLog.action_details.like(f'%user {user_id}%')
        ).count()

        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })
