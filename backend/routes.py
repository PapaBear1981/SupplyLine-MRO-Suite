from flask import request, jsonify, session, make_response
from models import db, Tool, User, Checkout, AuditLog, UserActivity
from datetime import datetime, timedelta
from functools import wraps
import secrets
import string

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if not session.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def tool_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Allow access for admins or Materials department users
        if session.get('is_admin', False) or session.get('department') == 'Materials':
            return f(*args, **kwargs)

        return jsonify({'error': 'Tool management privileges required'}), 403
    return decorated_function

def register_routes(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # Create admin user if none exists
        if User.query.filter_by(is_admin=True).first() is None:
            admin = User(
                name='Admin',
                employee_number='ADMIN001',
                department='IT',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with employee number ADMIN001 and password admin123")

    @app.route('/api/tools', methods=['GET', 'POST'])
    def tools_route():
        # GET - List all tools
        if request.method == 'GET':
            tools = Tool.query.all()

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()
            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = 'checked_out'

            return jsonify([{
                'id': t.id,
                'tool_number': t.tool_number,
                'serial_number': t.serial_number,
                'description': t.description,
                'condition': t.condition,
                'location': t.location,
                'status': tool_status.get(t.id, 'available'),
                'created_at': t.created_at.isoformat()
            } for t in tools])

        # POST - Create new tool (requires tool manager privileges)
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403

        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['tool_number', 'serial_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if tool number already exists
        if Tool.query.filter_by(tool_number=data['tool_number']).first():
            return jsonify({'error': 'Tool number already exists'}), 400

        # Create new tool
        t = Tool(
            tool_number=data.get('tool_number'),
            serial_number=data.get('serial_number'),
            description=data.get('description'),
            condition=data.get('condition'),
            location=data.get('location')
        )
        db.session.add(t)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='create_tool',
            action_details=f'Created tool {t.id} ({t.tool_number})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'id': t.id,
            'tool_number': t.tool_number,
            'message': 'Tool created successfully'
        }), 201

    @app.route('/api/tools/<int:id>', methods=['GET'])
    def get_tool(id):
        tool = Tool.query.get_or_404(id)

        # Check if tool is currently checked out
        active_checkout = Checkout.query.filter_by(tool_id=id, return_date=None).first()
        status = 'checked_out' if active_checkout else 'available'

        return jsonify({
            'id': tool.id,
            'tool_number': tool.tool_number,
            'serial_number': tool.serial_number,
            'description': tool.description,
            'condition': tool.condition,
            'location': tool.location,
            'status': status,
            'created_at': tool.created_at.isoformat()
        })

    @app.route('/api/users', methods=['GET', 'POST'])
    def users_route():
        if request.method == 'GET':
            users = User.query.all()
            return jsonify([{
                'id': u.id,
                'name': u.name,
                'employee_number': u.employee_number,
                'department': u.department,
                'created_at': u.created_at.isoformat()
            } for u in users])
        data = request.get_json() or {}
        u = User(
            name=data.get('name'),
            employee_number=data.get('employee_number'),
            department=data.get('department'),
            password_hash=data.get('password_hash')
        )
        db.session.add(u)
        db.session.commit()
        log = AuditLog(
            action_type='create_user',
            action_details=f'Created user {u.id}'
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'id': u.id}), 201

    @app.route('/api/checkouts', methods=['GET', 'POST'])
    def checkouts_route():
        if request.method == 'GET':
            checkouts = Checkout.query.all()
            return jsonify([{
                'id': c.id,
                'tool_id': c.tool_id,
                'tool_number': c.tool.tool_number if c.tool else 'Unknown',
                'user_id': c.user_id,
                'user_name': c.user.name if c.user else 'Unknown',
                'checkout_date': c.checkout_date.isoformat(),
                'return_date': c.return_date.isoformat() if c.return_date else None
            } for c in checkouts])

        # POST - Create new checkout
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['tool_id', 'user_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate tool exists
        tool_id = data.get('tool_id')
        tool = Tool.query.get(tool_id)
        if not tool:
            return jsonify({'error': f'Tool with ID {tool_id} does not exist'}), 404

        # Validate user exists
        user_id = data.get('user_id')
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User with ID {user_id} does not exist'}), 404

        # Check if tool is already checked out
        active_checkout = Checkout.query.filter_by(tool_id=tool_id, return_date=None).first()
        if active_checkout:
            return jsonify({'error': f'Tool {tool.tool_number} is already checked out'}), 400

        # Create checkout
        c = Checkout(
            tool_id=tool_id,
            user_id=user_id
        )
        db.session.add(c)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='checkout_tool',
            action_details=f'User {user.name} (ID: {user_id}) checked out tool {tool.tool_number} (ID: {tool_id})'
        )
        db.session.add(log)

        # Add user activity
        if 'user_id' in session:
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='tool_checkout',
                description=f'Checked out tool {tool.tool_number}',
                ip_address=request.remote_addr
            )
            db.session.add(activity)

        db.session.commit()

        return jsonify({
            'id': c.id,
            'message': f'Tool {tool.tool_number} checked out successfully'
        }), 201

    @app.route('/api/checkouts/<int:id>/return', methods=['POST'])
    def return_route(id):
        # Validate checkout exists
        c = Checkout.query.get_or_404(id)

        # Check if already returned
        if c.return_date:
            return jsonify({'error': 'This tool has already been returned'}), 400

        # Get tool and user info for better logging
        tool = Tool.query.get(c.tool_id)
        user = User.query.get(c.user_id)

        # Mark as returned
        c.return_date = datetime.now(datetime.timezone.utc)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='return_tool',
            action_details=f'User {user.name if user else "Unknown"} (ID: {c.user_id}) returned tool {tool.tool_number if tool else "Unknown"} (ID: {c.tool_id})'
        )
        db.session.add(log)

        # Add user activity
        if 'user_id' in session:
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='tool_return',
                description=f'Returned tool {tool.tool_number if tool else "Unknown"}',
                ip_address=request.remote_addr
            )
            db.session.add(activity)

        db.session.commit()

        return jsonify({
            'id': c.id,
            'message': f'Tool {tool.tool_number if tool else "Unknown"} returned successfully'
        }), 200

    @app.route('/api/audit', methods=['GET'])
    @admin_required
    def audit_route():
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
        return jsonify([{
            'id': a.id,
            'action_type': a.action_type,
            'action_details': a.action_details,
            'timestamp': a.timestamp.isoformat()
        } for a in logs])

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}

        if not data.get('employee_number') or not data.get('password'):
            return jsonify({'error': 'Employee number and password required'}), 400

        user = User.query.filter_by(employee_number=data['employee_number']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Store user info in session
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['is_admin'] = user.is_admin
        session['department'] = user.department
        session.permanent = True

        # Create response object
        response = make_response(jsonify(user.to_dict()))

        # Handle remember me
        if data.get('remember_me'):
            # Generate remember token
            remember_token = user.generate_remember_token()
            db.session.commit()

            # Set cookies
            response.set_cookie('remember_token', remember_token, max_age=30*24*60*60, httponly=True)  # 30 days
            response.set_cookie('user_id', str(user.id), max_age=30*24*60*60, httponly=True)  # 30 days

        # Log the login
        activity = UserActivity(
            user_id=user.id,
            activity_type='login',
            description='User logged in' + (' with remember me' if data.get('remember_me') else ''),
            ip_address=request.remote_addr
        )
        db.session.add(activity)

        log = AuditLog(
            action_type='user_login',
            action_details=f'User {user.id} ({user.name}) logged in'
        )
        db.session.add(log)
        db.session.commit()

        return response

    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        user_id = session.get('user_id')
        if user_id:
            # Get user to clear remember token
            user = User.query.get(user_id)
            if user:
                user.clear_remember_token()
                db.session.commit()

                # Log the logout
                activity = UserActivity(
                    user_id=user.id,
                    activity_type='logout',
                    description='User logged out',
                    ip_address=request.remote_addr
                )
                db.session.add(activity)

                log = AuditLog(
                    action_type='user_logout',
                    action_details=f'User {user_id} ({session.get("user_name", "Unknown")}) logged out'
                )
                db.session.add(log)
                db.session.commit()

        # Clear session
        session.clear()

        # Create response and clear cookies
        response = make_response(jsonify({'message': 'Logged out successfully'}))
        response.delete_cookie('remember_token')
        response.delete_cookie('user_id')

        return response

    @app.route('/api/auth/status', methods=['GET'])
    def auth_status():
        if 'user_id' not in session:
            # Check for remember_me cookie
            remember_token = request.cookies.get('remember_token')
            if remember_token:
                user_id = request.cookies.get('user_id')
                if user_id:
                    user = User.query.get(int(user_id))
                    if user and user.check_remember_token(remember_token):
                        # Valid remember token, log the user in
                        session['user_id'] = user.id
                        session['user_name'] = user.name
                        session['is_admin'] = user.is_admin
                        session['department'] = user.department

                        # Log the auto-login
                        activity = UserActivity(
                            user_id=user.id,
                            activity_type='auto_login',
                            description='Auto-login via remember me token',
                            ip_address=request.remote_addr
                        )
                        db.session.add(activity)
                        db.session.commit()

                        return jsonify({
                            'authenticated': True,
                            'user': user.to_dict()
                        }), 200

            return jsonify({'authenticated': False}), 200

        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return jsonify({'authenticated': False}), 200

        return jsonify({
            'authenticated': True,
            'user': user.to_dict()
        }), 200

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['name', 'employee_number', 'department', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if employee number already exists
        if User.query.filter_by(employee_number=data['employee_number']).first():
            return jsonify({'error': 'Employee number already registered'}), 400

        # Create new user
        user = User(
            name=data['name'],
            employee_number=data['employee_number'],
            department=data['department']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Log the registration
        log = AuditLog(
            action_type='user_register',
            action_details=f'New user registered: {user.id} ({user.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201

    @app.route('/api/auth/reset-password/request', methods=['POST'])
    def request_password_reset():
        data = request.get_json() or {}

        if not data.get('employee_number'):
            return jsonify({'error': 'Employee number is required'}), 400

        user = User.query.filter_by(employee_number=data['employee_number']).first()
        if not user:
            # Don't reveal that the user doesn't exist
            return jsonify({'message': 'If your employee number is registered, a reset code will be sent'}), 200

        # Generate reset token
        reset_code = user.generate_reset_token()
        db.session.commit()

        # In a real application, you would send this code via email or SMS
        # For this demo, we'll just return it in the response (not secure for production)

        # Log the password reset request
        activity = UserActivity(
            user_id=user.id,
            activity_type='password_reset_request',
            description='Password reset requested',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        # In a real app, you would not return the code in the response
        # This is just for demonstration purposes
        return jsonify({
            'message': 'Reset code generated',
            'reset_code': reset_code  # In production, remove this line and send via email/SMS
        }), 200

    @app.route('/api/auth/reset-password/confirm', methods=['POST'])
    def confirm_password_reset():
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['employee_number', 'reset_code', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        user = User.query.filter_by(employee_number=data['employee_number']).first()
        if not user:
            return jsonify({'error': 'Invalid employee number'}), 400

        # Verify reset code
        if not user.check_reset_token(data['reset_code']):
            return jsonify({'error': 'Invalid or expired reset code'}), 400

        # Update password
        user.set_password(data['new_password'])
        user.clear_reset_token()
        db.session.commit()

        # Log the password reset
        activity = UserActivity(
            user_id=user.id,
            activity_type='password_reset',
            description='Password reset completed',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Password reset successful'}), 200

    @app.route('/api/auth/user', methods=['GET'])
    @login_required
    def get_profile():
        user = User.query.get(session['user_id'])
        return jsonify(user.to_dict()), 200

    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        user = User.query.get(session['user_id'])
        data = request.get_json() or {}

        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'department' in data:
            user.department = data['department']

        db.session.commit()

        # Log the profile update
        activity = UserActivity(
            user_id=user.id,
            activity_type='profile_update',
            description='Profile information updated',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify(user.to_dict()), 200

    @app.route('/api/user/password', methods=['PUT'])
    @login_required
    def change_password():
        user = User.query.get(session['user_id'])
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Update password
        user.set_password(data['new_password'])
        db.session.commit()

        # Log the password change
        activity = UserActivity(
            user_id=user.id,
            activity_type='password_change',
            description='Password changed',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Password updated successfully'}), 200

    @app.route('/api/user/activity', methods=['GET'])
    @login_required
    def get_user_activity():
        user_id = session['user_id']
        activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.timestamp.desc()).limit(50).all()
        return jsonify([activity.to_dict() for activity in activities]), 200

    @app.route('/api/tools/new', methods=['GET'])
    @tool_manager_required
    def get_new_tool_form():
        # This endpoint returns the form data needed to create a new tool
        # It can include any default values or validation rules
        return jsonify({
            'form_fields': [
                {'name': 'tool_number', 'type': 'text', 'required': True, 'label': 'Tool Number'},
                {'name': 'serial_number', 'type': 'text', 'required': True, 'label': 'Serial Number'},
                {'name': 'description', 'type': 'text', 'required': False, 'label': 'Description'},
                {'name': 'condition', 'type': 'select', 'required': False, 'label': 'Condition',
                 'options': ['New', 'Good', 'Fair', 'Poor']},
                {'name': 'location', 'type': 'text', 'required': False, 'label': 'Location'}
            ]
        }), 200

    @app.route('/api/tools/new/checkouts', methods=['GET'])
    @login_required
    def get_new_tool_checkouts():
        # This endpoint returns checkout history for a new tool (which should be empty)
        return jsonify([]), 200

    @app.route('/api/checkouts/user', methods=['GET'])
    @login_required
    def get_user_checkouts():
        # Get the current user's checkouts
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        user_id = session['user_id']
        checkouts = Checkout.query.filter_by(user_id=user_id, return_date=None).all()

        return jsonify([{
            'id': c.id,
            'tool_id': c.tool_id,
            'tool_number': c.tool.tool_number if c.tool else 'Unknown',
            'checkout_date': c.checkout_date.isoformat(),
            'expected_return_date': None  # Add this field if you have it in your model
        } for c in checkouts]), 200

    @app.route('/api/tools/<int:id>/checkouts', methods=['GET'])
    def get_tool_checkouts(id):
        # Get checkout history for a specific tool
        tool = Tool.query.get_or_404(id)
        checkouts = Checkout.query.filter_by(tool_id=id).order_by(Checkout.checkout_date.desc()).all()

        return jsonify([{
            'id': c.id,
            'user_id': c.user_id,
            'user_name': c.user.name if c.user else 'Unknown',
            'checkout_date': c.checkout_date.isoformat(),
            'return_date': c.return_date.isoformat() if c.return_date else None
        } for c in checkouts]), 200