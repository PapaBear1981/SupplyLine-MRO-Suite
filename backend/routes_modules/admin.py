"""
Admin Dashboard Routes for SupplyLine MRO Suite

This module provides endpoints for:
- Admin dashboard statistics and analytics
- User registration request management
- System administration functions
"""

import logging
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, session
from models import db, User, Tool, Checkout, AuditLog, UserActivity
from auth import admin_required
from sqlalchemy import func

logger = logging.getLogger(__name__)


def register_admin_routes(app):
    """Register admin dashboard and management routes"""

    @app.route('/api/admin/dashboard', methods=['GET'])
    @admin_required
    def admin_dashboard():
        """Main admin dashboard endpoint"""
        print("Admin dashboard endpoint called")
        return jsonify({
            'status': 'success',
            'message': 'Admin dashboard is accessible',
            'timestamp': datetime.now().isoformat()
        }), 200

    @app.route('/api/admin/dashboard/test', methods=['GET'])
    def admin_dashboard_test():
        """Test endpoint for admin dashboard connectivity"""
        print("Admin dashboard test endpoint called")
        return jsonify({
            'status': 'success',
            'message': 'Admin dashboard test endpoint works',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/admin/registration-requests', methods=['GET'])
    @admin_required
    def get_registration_requests():
        """Get user registration requests with optional status filtering"""
        from models import RegistrationRequest

        # Get status filter (default to 'pending')
        status = request.args.get('status', 'pending')

        if status == 'all':
            requests = RegistrationRequest.query.order_by(RegistrationRequest.created_at.desc()).all()
        else:
            requests = RegistrationRequest.query.filter_by(status=status).order_by(RegistrationRequest.created_at.desc()).all()

        return jsonify([req.to_dict() for req in requests]), 200

    @app.route('/api/admin/registration-requests/<int:id>/approve', methods=['POST'])
    @admin_required
    def approve_registration_request(id):
        """Approve a user registration request and create the user account"""
        from models import RegistrationRequest

        # Get the registration request
        reg_request = RegistrationRequest.query.get_or_404(id)

        # Check if it's already processed
        if reg_request.status != 'pending':
            return jsonify({'error': f'Registration request is already {reg_request.status}'}), 400

        # Create a new user from the registration request
        user = User(
            name=reg_request.name,
            employee_number=reg_request.employee_number,
            department=reg_request.department,
            password_hash=reg_request.password_hash,  # Copy the hashed password
            is_admin=False,
            is_active=True
        )

        # Update the registration request status
        reg_request.status = 'approved'
        reg_request.processed_at = datetime.now(timezone.utc)
        reg_request.processed_by = session['user_id']
        reg_request.admin_notes = request.json.get('notes', '')

        # Save changes
        db.session.add(user)
        db.session.commit()

        # Log the approval
        log = AuditLog(
            action_type='approve_registration',
            action_details=f'Approved registration request {reg_request.id} ({reg_request.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': 'Registration request approved',
            'user_id': user.id,
            'request_id': reg_request.id
        }), 200

    @app.route('/api/admin/registration-requests/<int:id>/deny', methods=['POST'])
    @admin_required
    def deny_registration_request(id):
        """Deny a user registration request"""
        from models import RegistrationRequest

        # Get the registration request
        reg_request = RegistrationRequest.query.get_or_404(id)

        # Check if it's already processed
        if reg_request.status != 'pending':
            return jsonify({'error': f'Registration request is already {reg_request.status}'}), 400

        # Update the registration request status
        reg_request.status = 'denied'
        reg_request.processed_at = datetime.now(timezone.utc)
        reg_request.processed_by = session['user_id']
        reg_request.admin_notes = request.json.get('notes', '')

        # Save changes
        db.session.commit()

        # Log the denial
        log = AuditLog(
            action_type='deny_registration',
            action_details=f'Denied registration request {reg_request.id} ({reg_request.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': 'Registration request denied',
            'request_id': reg_request.id
        }), 200

    @app.route('/api/admin/dashboard/stats', methods=['GET'])
    @admin_required
    def get_admin_dashboard_stats():
        """Get comprehensive dashboard statistics for admin overview"""
        print("Admin dashboard stats endpoint called")
        print(f"Session: {session}")
        print(f"User ID in session: {session.get('user_id')}")
        print(f"Is admin in session: {session.get('is_admin')}")

        # Get counts from various tables
        user_count = User.query.count()
        print(f"User count: {user_count}")
        active_user_count = User.query.filter_by(is_active=True).count()
        print(f"Active user count: {active_user_count}")
        tool_count = Tool.query.count()
        print(f"Tool count: {tool_count}")
        available_tool_count = Tool.query.filter_by(status='available').count()
        print(f"Available tool count: {available_tool_count}")
        checkout_count = Checkout.query.count()
        print(f"Checkout count: {checkout_count}")
        active_checkout_count = Checkout.query.filter(Checkout.return_date.is_(None)).count()
        print(f"Active checkout count: {active_checkout_count}")

        # Get pending registration requests count
        from models import RegistrationRequest
        pending_requests_count = RegistrationRequest.query.filter_by(status='pending').count()

        # Get recent activity
        recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

        # Get system activity over time (last 30 days)
        start_date = datetime.now() - timedelta(days=30)

        # Get activity counts by day
        daily_activity = db.session.query(
            func.date(AuditLog.timestamp).label('date'),
            func.count().label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            func.date(AuditLog.timestamp)
        ).all()

        # Format the results
        activity_data = [{
            'date': str(day.date),
            'count': day.count
        } for day in daily_activity]

        # Get department distribution
        dept_distribution = db.session.query(
            User.department.label('department'),
            func.count(User.id).label('count')
        ).group_by(
            User.department
        ).all()

        dept_data = [{
            'name': dept.department or 'Unknown',
            'value': dept.count
        } for dept in dept_distribution]

        return jsonify({
            'counts': {
                'users': user_count,
                'activeUsers': active_user_count,
                'tools': tool_count,
                'availableTools': available_tool_count,
                'checkouts': checkout_count,
                'activeCheckouts': active_checkout_count,
                'pendingRegistrations': pending_requests_count
            },
            'recentActivity': [{
                'id': log.id,
                'action_type': log.action_type,
                'action_details': log.action_details,
                'timestamp': log.timestamp.isoformat()
            } for log in recent_logs],
            'activityOverTime': activity_data,
            'departmentDistribution': dept_data
        }), 200
