from flask import request, jsonify, session, make_response
from models import db, Tool, User, Checkout, AuditLog, UserActivity, ToolServiceRecord
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

    # Health check endpoint for Docker
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/tools', methods=['GET', 'POST'])
    def tools_route():
        # GET - List all tools
        if request.method == 'GET':
            print("Received request for all tools")

            # Check if there's a search query
            print(f"Request method: {request.method}")
            print(f"Request URL: {request.url}")
            print(f"Request args: {request.args}")
            print(f"Request args type: {type(request.args)}")
            print(f"Request args keys: {list(request.args.keys())}")

            search_query = request.args.get('q')
            print(f"Search query: {search_query}")
            print(f"Search query type: {type(search_query)}")

            if search_query:
                print(f"Searching for tools with query: {search_query}")
                search_term = f'%{search_query.lower()}%'
                print(f"Search term: {search_term}")

                try:
                    tools = Tool.query.filter(
                        db.or_(
                            db.func.lower(Tool.tool_number).like(search_term),
                            db.func.lower(Tool.serial_number).like(search_term),
                            db.func.lower(Tool.description).like(search_term),
                            db.func.lower(Tool.location).like(search_term)
                        )
                    ).all()
                    print(f"Found {len(tools)} tools matching search query")
                except Exception as e:
                    print(f"Error during search: {str(e)}")
                    tools = Tool.query.all()
                    print(f"Falling back to all tools: {len(tools)}")
            else:
                tools = Tool.query.all()
                print(f"Found {len(tools)} tools")

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()
            print(f"Found {len(active_checkouts)} active checkouts")

            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = 'checked_out'
                print(f"Tool {checkout.tool_id} is checked out")

            result = [{
                'id': t.id,
                'tool_number': t.tool_number,
                'serial_number': t.serial_number,
                'description': t.description,
                'condition': t.condition,
                'location': t.location,
                'category': getattr(t, 'category', 'General'),  # Use 'General' if category attribute doesn't exist
                'status': tool_status.get(t.id, getattr(t, 'status', 'available')),  # Use 'available' if status attribute doesn't exist
                'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
                'created_at': t.created_at.isoformat()
            } for t in tools]

            print(f"Returning {len(result)} tools")
            return jsonify(result)

        # POST - Create new tool (requires tool manager privileges)
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403

        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['tool_number', 'serial_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if tool with same tool number AND serial number already exists
        if Tool.query.filter_by(tool_number=data['tool_number'], serial_number=data['serial_number']).first():
            return jsonify({'error': 'A tool with this tool number and serial number combination already exists'}), 400

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

    @app.route('/api/tools/<int:id>', methods=['GET', 'PUT'])
    def get_tool(id):
        tool = Tool.query.get_or_404(id)

        # GET - Get tool details
        if request.method == 'GET':
            # Check if tool is currently checked out
            active_checkout = Checkout.query.filter_by(tool_id=id, return_date=None).first()

            # Determine status - checkout status takes precedence over tool status
            status = 'checked_out' if active_checkout else getattr(tool, 'status', 'available')

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'condition': tool.condition,
                'location': tool.location,
                'category': getattr(tool, 'category', 'General'),  # Use 'General' if category attribute doesn't exist
                'status': status,
                'status_reason': getattr(tool, 'status_reason', None) if status in ['maintenance', 'retired'] else None,
                'created_at': tool.created_at.isoformat()
            })

        # PUT - Update tool (requires tool manager privileges)
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403

        data = request.get_json() or {}

        # Update fields
        if 'tool_number' in data or 'serial_number' in data:
            # If either tool_number or serial_number is being updated, we need to check for duplicates
            new_tool_number = data.get('tool_number', tool.tool_number)
            new_serial_number = data.get('serial_number', tool.serial_number)

            # Check if the combination of tool_number and serial_number already exists for another tool
            existing_tool = Tool.query.filter_by(tool_number=new_tool_number, serial_number=new_serial_number).first()
            if existing_tool and existing_tool.id != id:
                return jsonify({'error': 'A tool with this tool number and serial number combination already exists'}), 400

            # Update the fields if they were provided
            if 'tool_number' in data:
                tool.tool_number = data['tool_number']
            if 'serial_number' in data:
                tool.serial_number = data['serial_number']

        if 'description' in data:
            tool.description = data['description']

        if 'condition' in data:
            tool.condition = data['condition']

        if 'location' in data:
            tool.location = data['location']

        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='update_tool',
            action_details=f'Updated tool {tool.id} ({tool.tool_number})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'id': tool.id,
            'tool_number': tool.tool_number,
            'serial_number': tool.serial_number,
            'description': tool.description,
            'condition': tool.condition,
            'location': tool.location,
            'message': 'Tool updated successfully'
        })

    @app.route('/api/users', methods=['GET', 'POST'])
    def users_route():
        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'User management privileges required'}), 403

        if request.method == 'GET':
            # Get all users, including inactive ones
            users = User.query.all()
            return jsonify([u.to_dict() for u in users])

        # POST - Create a new user
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['name', 'employee_number', 'department', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if employee number already exists
        if User.query.filter_by(employee_number=data['employee_number']).first():
            return jsonify({'error': 'Employee number already exists'}), 400

        # Create new user
        u = User(
            name=data.get('name'),
            employee_number=data.get('employee_number'),
            department=data.get('department'),
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True)
        )
        u.set_password(data.get('password'))

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
        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'User management privileges required'}), 403

        # Get the user
        user = User.query.get_or_404(id)

        if request.method == 'GET':
            # Return user details
            return jsonify(user.to_dict())

        elif request.method == 'PUT':
            # Update user
            data = request.get_json() or {}

            # Update fields
            if 'name' in data:
                user.name = data['name']
            if 'department' in data:
                user.department = data['department']
            if 'is_admin' in data:
                user.is_admin = data['is_admin']
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'password' in data and data['password']:
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
            # Deactivate user instead of deleting
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

    @app.route('/api/checkouts', methods=['GET', 'POST'])
    def checkouts_route():
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
                    'checkout_date': c.checkout_date.isoformat(),
                    'return_date': c.return_date.isoformat() if c.return_date else None,
                    'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                    'status': 'Returned' if c.return_date else 'Checked Out'
                } for c in checkouts])

            # POST - Create new checkout
            data = request.get_json() or {}
            print(f"Received checkout request with data: {data}")
            print(f"Current session: {session}")

            # Validate required fields
            required_fields = ['tool_id']
            for field in required_fields:
                if field not in data or data.get(field) is None:
                    print(f"Missing required field: {field}")
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Validate tool exists
            try:
                tool_id = int(data.get('tool_id'))
                print(f"Tool ID: {tool_id}")
            except (ValueError, TypeError):
                print(f"Invalid tool_id format: {data.get('tool_id')}")
                return jsonify({'error': 'Invalid tool ID format'}), 400

            tool = Tool.query.get(tool_id)
            if not tool:
                print(f"Tool with ID {tool_id} does not exist")
                return jsonify({'error': f'Tool with ID {tool_id} does not exist'}), 404

            # Get user ID - either from request data or from session
            user_id = data.get('user_id')
            print(f"User ID from request: {user_id}")

            # Convert user_id to integer if it's a string
            if user_id is not None:
                try:
                    user_id = int(user_id)
                    print(f"Converted user_id to integer: {user_id}")
                except (ValueError, TypeError):
                    print(f"Could not convert user_id '{user_id}' to integer")
                    user_id = None

            if not user_id:
                print("No valid user_id in request, checking session")
                # If user_id not provided in request, use the logged-in user's ID
                if 'user_id' not in session:
                    print("No user_id in session either")
                    return jsonify({'error': 'Authentication required'}), 401
                user_id = session['user_id']
                print(f"Using user_id from session: {user_id}")

            # Validate user exists
            user = User.query.get(user_id)
            if not user:
                print(f"User with ID {user_id} does not exist")
                return jsonify({'error': f'User with ID {user_id} does not exist'}), 404

            print(f"Found user: {user.name} (ID: {user.id})")

            # Check if tool is already checked out
            active_checkout = Checkout.query.filter_by(tool_id=tool_id, return_date=None).first()
            if active_checkout:
                print(f"Tool {tool.tool_number} is already checked out")
                return jsonify({'error': f'Tool {tool.tool_number} is already checked out'}), 400

            # Create checkout
            expected_return_date = data.get('expected_return_date')
            print(f"Creating checkout for tool {tool_id} to user {user_id}")

            # Parse expected_return_date if it's a string
            parsed_date = None
            if expected_return_date:
                try:
                    if isinstance(expected_return_date, str):
                        # Handle different date formats
                        if 'Z' in expected_return_date:
                            parsed_date = datetime.fromisoformat(expected_return_date.replace('Z', '+00:00'))
                        elif 'T' in expected_return_date:
                            parsed_date = datetime.fromisoformat(expected_return_date)
                        else:
                            # Simple date format (YYYY-MM-DD)
                            parsed_date = datetime.strptime(expected_return_date, '%Y-%m-%d')
                    else:
                        parsed_date = expected_return_date
                    print(f"Parsed expected return date: {parsed_date}")
                except Exception as e:
                    print(f"Error parsing date: {e}")
                    # Use a default date (7 days from now) if parsing fails
                    parsed_date = datetime.now() + timedelta(days=7)
                    print(f"Using default date: {parsed_date}")
            else:
                # Default to 7 days from now if no date provided
                parsed_date = datetime.now() + timedelta(days=7)
                print(f"No date provided, using default: {parsed_date}")

            # Create and save the checkout
            try:
                c = Checkout(
                    tool_id=tool_id,
                    user_id=user_id,
                    expected_return_date=parsed_date
                )
                db.session.add(c)
                db.session.commit()
                print(f"Checkout created with ID: {c.id}")

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
            except Exception as e:
                db.session.rollback()
                print(f"Database error during checkout: {str(e)}")
                return jsonify({'error': 'Database error during checkout'}), 500

        except Exception as e:
            print(f"Unexpected error in checkouts route: {str(e)}")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

    @app.route('/api/checkouts/<int:id>/return', methods=['POST', 'PUT'])
    def return_route(id):
        try:
            print(f"Received tool return request for checkout ID: {id}, method: {request.method}")

            # Validate checkout exists
            c = Checkout.query.get(id)
            if not c:
                print(f"Checkout with ID {id} not found")
                return jsonify({'error': f'Checkout with ID {id} not found'}), 404

            print(f"Found checkout: {c.id} for tool_id: {c.tool_id}, user_id: {c.user_id}")

            # Check if already returned
            if c.return_date:
                print(f"Tool already returned on: {c.return_date}")
                return jsonify({'error': 'This tool has already been returned'}), 400

            # Get tool and user info for better logging
            tool = Tool.query.get(c.tool_id)
            user = User.query.get(c.user_id)

            if not tool:
                print(f"Tool with ID {c.tool_id} not found")
                return jsonify({'error': f'Tool with ID {c.tool_id} not found'}), 404

            if not user:
                print(f"User with ID {c.user_id} not found")
                # Continue anyway since we can still return the tool

            print(f"Tool: {tool.tool_number if tool else 'Unknown'}, User: {user.name if user else 'Unknown'}")

            # Get condition from request if provided
            data = request.get_json() or {}
            condition = data.get('condition')
            print(f"Return condition: {condition}")

            try:
                # Mark as returned
                c.return_date = datetime.now()

                # Update tool condition if provided
                if condition and tool:
                    old_condition = tool.condition
                    tool.condition = condition
                    print(f"Updated tool condition from {old_condition} to {condition}")

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

                # Return a more detailed response
                return jsonify({
                    'id': c.id,
                    'tool_id': c.tool_id,
                    'tool_number': tool.tool_number if tool else 'Unknown',
                    'serial_number': tool.serial_number if tool else 'Unknown',
                    'description': tool.description if tool else '',
                    'condition': tool.condition if tool else '',
                    'user_id': c.user_id,
                    'user_name': user.name if user else 'Unknown',
                    'checkout_date': c.checkout_date.isoformat(),
                    'return_date': c.return_date.isoformat() if c.return_date else None,
                    'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                    'status': 'Returned',
                    'message': f'Tool {tool.tool_number if tool else "Unknown"} returned successfully'
                }), 200
            except Exception as e:
                db.session.rollback()
                print(f"Database error during tool return: {str(e)}")
                return jsonify({'error': 'Database error during tool return'}), 500

        except Exception as e:
            print(f"Unexpected error in return route: {str(e)}")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

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

    @app.route('/api/audit/logs', methods=['GET'])
    def audit_logs_route():
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get logs with pagination
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

        return jsonify([{
            'id': a.id,
            'action_type': a.action_type,
            'action_details': a.action_details,
            'timestamp': a.timestamp.isoformat()
        } for a in logs])

    @app.route('/api/audit/metrics', methods=['GET'])
    def audit_metrics_route():
        # Get timeframe parameter (default to 'week')
        timeframe = request.args.get('timeframe', 'week')

        # Calculate date range based on timeframe
        now = datetime.utcnow()
        if timeframe == 'day':
            start_date = now - timedelta(days=1)
        elif timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(weeks=1)  # Default to week

        # Get counts for different action types
        checkout_count = AuditLog.query.filter(
            AuditLog.action_type == 'checkout_tool',
            AuditLog.timestamp >= start_date
        ).count()

        return_count = AuditLog.query.filter(
            AuditLog.action_type == 'return_tool',
            AuditLog.timestamp >= start_date
        ).count()

        login_count = AuditLog.query.filter(
            AuditLog.action_type == 'user_login',
            AuditLog.timestamp >= start_date
        ).count()

        # Get total activity count
        total_activity = AuditLog.query.filter(
            AuditLog.timestamp >= start_date
        ).count()

        # Get recent activity by day
        from sqlalchemy import func

        # This query gets counts by day
        daily_activity = db.session.query(
            func.date(AuditLog.timestamp).label('date'),
            func.count().label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            func.date(AuditLog.timestamp)
        ).all()

        # Format the results
        daily_data = [{
            'date': str(day.date),
            'count': day.count
        } for day in daily_activity]

        return jsonify({
            'timeframe': timeframe,
            'total_activity': total_activity,
            'checkouts': checkout_count,
            'returns': return_count,
            'logins': login_count,
            'daily_activity': daily_data
        })

    @app.route('/api/audit/users/<int:user_id>', methods=['GET'])
    def user_audit_logs_route(user_id):
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get user activities with pagination
        activities = UserActivity.query.filter_by(user_id=user_id).order_by(
            UserActivity.timestamp.desc()
        ).offset(offset).limit(limit).all()

        return jsonify([activity.to_dict() for activity in activities])

    @app.route('/api/audit/tools/<int:tool_id>', methods=['GET'])
    def tool_audit_logs_route(tool_id):
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get tool-related audit logs with pagination
        # This is a simplified approach - in a real app, you might want to
        # search for tool ID in action_details or have a more structured way
        # to track tool-specific actions
        logs = AuditLog.query.filter(
            AuditLog.action_details.like(f'%tool%{tool_id}%')
        ).order_by(
            AuditLog.timestamp.desc()
        ).offset(offset).limit(limit).all()

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

        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is inactive. Please contact an administrator.'}), 403

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
        try:
            print("Auth status check - Session:", session)

            if 'user_id' not in session:
                print("No user_id in session, checking cookies")
                # Check for remember_me cookie
                remember_token = request.cookies.get('remember_token')
                if remember_token:
                    print("Found remember_token cookie")
                    user_id = request.cookies.get('user_id')
                    if user_id:
                        print(f"Found user_id cookie: {user_id}")
                        try:
                            user_id_int = int(user_id)
                            user = User.query.get(user_id_int)
                            if user and user.check_remember_token(remember_token):
                                print(f"Valid remember token for user: {user.name}")
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
                            else:
                                print("Invalid or expired remember token")
                        except (ValueError, TypeError) as e:
                            print(f"Error converting user_id to int: {e}")

                print("No valid session or remember token, returning unauthenticated")
                return jsonify({'authenticated': False}), 200

            print(f"User ID in session: {session['user_id']}")
            user = User.query.get(session['user_id'])
            if not user:
                print(f"User with ID {session['user_id']} not found in database")
                session.clear()
                return jsonify({'authenticated': False}), 200

            print(f"User authenticated: {user.name}")
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            }), 200

        except Exception as e:
            print(f"Error in auth_status route: {str(e)}")
            # Clear session on error to prevent login loops
            session.clear()
            return jsonify({
                'authenticated': False,
                'error': 'An error occurred while checking authentication status'
            }), 200  # Return 200 instead of 500 to prevent login loops

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

    @app.route('/api/tools/search', methods=['GET'])
    def search_tools():
        # Get search query from request parameters
        query = request.args.get('q', '')
        print(f"Search endpoint called with query: {query}")

        if not query:
            return jsonify({'error': 'Search query is required'}), 400

        # Convert query to lowercase for case-insensitive search
        search_term = f'%{query.lower()}%'
        print(f"Search term: {search_term}")

        # Search in tool_number, serial_number, description, and location
        try:
            tools = Tool.query.filter(
                db.or_(
                    db.func.lower(Tool.tool_number).like(search_term),
                    db.func.lower(Tool.serial_number).like(search_term),
                    db.func.lower(Tool.description).like(search_term),
                    db.func.lower(Tool.location).like(search_term)
                )
            ).all()
            print(f"Found {len(tools)} tools matching search query")
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return jsonify({'error': f'Search error: {str(e)}'}), 500

        # Get checkout status for each tool
        tool_status = {}
        active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()

        for checkout in active_checkouts:
            tool_status[checkout.tool_id] = 'checked_out'

        # Format the results
        result = [{
            'id': t.id,
            'tool_number': t.tool_number,
            'serial_number': t.serial_number,
            'description': t.description,
            'condition': t.condition,
            'location': t.location,
            'category': getattr(t, 'category', 'General'),  # Use 'General' if category attribute doesn't exist
            'status': tool_status.get(t.id, getattr(t, 'status', 'available')),  # Use 'available' if status attribute doesn't exist
            'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
            'created_at': t.created_at.isoformat()
        } for t in tools]

        return jsonify(result)

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

    @app.route('/api/analytics/usage', methods=['GET'])
    @tool_manager_required
    def get_usage_analytics():
        try:
            # Get timeframe parameter (default to 'week')
            timeframe = request.args.get('timeframe', 'week')

            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=1)
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'month':
                start_date = now - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = now - timedelta(days=90)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(weeks=1)  # Default to week

            # Initialize response data structure
            response_data = {
                'timeframe': timeframe,
                'checkoutsByDepartment': [],
                'checkoutsByDay': [],
                'toolUsageByCategory': [],
                'mostFrequentlyCheckedOut': [],
                'overallStats': {}
            }

            # 1. Get checkouts by department
            try:
                from sqlalchemy import func

                # Query to get checkout counts by department
                dept_checkouts = db.session.query(
                    User.department.label('department'),
                    func.count(Checkout.id).label('count')
                ).join(
                    User, User.id == Checkout.user_id
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    User.department
                ).all()

                # Format the results for the frontend
                dept_data = [{
                    'name': dept.department or 'Unknown',
                    'value': dept.count
                } for dept in dept_checkouts]

                response_data['checkoutsByDepartment'] = dept_data
            except Exception as e:
                print(f"Error getting department data: {str(e)}")
                # Continue with other queries even if this one fails

            # 2. Get daily checkout and return data
            try:
                # Get checkouts by day
                daily_checkouts = db.session.query(
                    func.date(Checkout.checkout_date).label('date'),
                    func.count().label('count')
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    func.date(Checkout.checkout_date)
                ).all()

                # Get returns by day
                daily_returns = db.session.query(
                    func.date(Checkout.return_date).label('date'),
                    func.count().label('count')
                ).filter(
                    Checkout.return_date >= start_date
                ).group_by(
                    func.date(Checkout.return_date)
                ).all()

                # Create a dictionary to store daily data
                daily_data_dict = {}

                # Process checkout data
                for day in daily_checkouts:
                    date_str = str(day.date)
                    weekday = datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')

                    if date_str not in daily_data_dict:
                        daily_data_dict[date_str] = {
                            'name': weekday,
                            'date': date_str,
                            'checkouts': 0,
                            'returns': 0
                        }

                    daily_data_dict[date_str]['checkouts'] = day.count

                # Process return data
                for day in daily_returns:
                    if day.date:  # Ensure date is not None
                        date_str = str(day.date)
                        weekday = datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')

                        if date_str not in daily_data_dict:
                            daily_data_dict[date_str] = {
                                'name': weekday,
                                'date': date_str,
                                'checkouts': 0,
                                'returns': 0
                            }

                        daily_data_dict[date_str]['returns'] = day.count

                # Convert dictionary to sorted list
                daily_data = sorted(daily_data_dict.values(), key=lambda x: x['date'])

                response_data['checkoutsByDay'] = daily_data
            except Exception as e:
                print(f"Error getting daily data: {str(e)}")
                # Continue with other queries even if this one fails

            # 3. Get tool usage by category
            try:
                # First, get all tools with their checkout counts
                tool_usage = db.session.query(
                    Tool.id,
                    Tool.tool_number,
                    Tool.description,
                    func.count(Checkout.id).label('checkout_count')
                ).join(
                    Checkout, Tool.id == Checkout.tool_id
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    Tool.id
                ).all()

                # Categorize tools based on their tool number or description
                category_counts = {}

                for tool in tool_usage:
                    # Determine category from tool number prefix or description
                    category = get_category_name(tool.tool_number[:3] if tool.tool_number else '')

                    if category not in category_counts:
                        category_counts[category] = 0

                    category_counts[category] += tool.checkout_count

                # Convert to list format for the frontend
                category_data = [{'name': cat, 'checkouts': count} for cat, count in category_counts.items()]

                # Sort by checkout count (descending)
                category_data.sort(key=lambda x: x['checkouts'], reverse=True)

                response_data['toolUsageByCategory'] = category_data
            except Exception as e:
                print(f"Error getting category data: {str(e)}")
                # Continue with other queries even if this one fails

            # 4. Get most frequently checked out tools
            try:
                top_tools = db.session.query(
                    Tool.id,
                    Tool.tool_number,
                    Tool.description,
                    func.count(Checkout.id).label('checkout_count')
                ).join(
                    Checkout, Tool.id == Checkout.tool_id
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    Tool.id
                ).order_by(
                    func.count(Checkout.id).desc()
                ).limit(5).all()

                top_tools_data = [{
                    'id': tool.id,
                    'tool_number': tool.tool_number,
                    'description': tool.description or '',
                    'checkouts': tool.checkout_count
                } for tool in top_tools]

                response_data['mostFrequentlyCheckedOut'] = top_tools_data
            except Exception as e:
                print(f"Error getting top tools data: {str(e)}")
                # Continue with other queries even if this one fails

            # 5. Get overall statistics
            try:
                # Total checkouts in period
                total_checkouts = Checkout.query.filter(
                    Checkout.checkout_date >= start_date
                ).count()

                # Total returns in period
                total_returns = Checkout.query.filter(
                    Checkout.return_date >= start_date
                ).count()

                # Currently checked out
                currently_checked_out = Checkout.query.filter(
                    Checkout.return_date.is_(None)
                ).count()

                # Average checkout duration (for returned items)
                from sqlalchemy import func, extract

                avg_duration_query = db.session.query(
                    func.avg(
                        func.julianday(Checkout.return_date) - func.julianday(Checkout.checkout_date)
                    ).label('avg_days')
                ).filter(
                    Checkout.checkout_date >= start_date,
                    Checkout.return_date.isnot(None)
                ).scalar()

                avg_duration = round(float(avg_duration_query or 0), 1)

                # Overdue checkouts
                overdue_count = Checkout.query.filter(
                    Checkout.return_date.is_(None),
                    Checkout.expected_return_date < now
                ).count()

                response_data['overallStats'] = {
                    'totalCheckouts': total_checkouts,
                    'totalReturns': total_returns,
                    'currentlyCheckedOut': currently_checked_out,
                    'averageDuration': avg_duration,
                    'overdueCount': overdue_count
                }
            except Exception as e:
                print(f"Error getting overall stats: {str(e)}")
                # Continue even if this query fails

            return jsonify(response_data), 200

        except Exception as e:
            print(f"Error in analytics endpoint: {str(e)}")
            return jsonify({
                'error': 'An error occurred while generating analytics data',
                'message': str(e)
            }), 500

    # Helper function for analytics
    def get_category_name(code):
        """Convert category code to readable name"""
        categories = {
            'DRL': 'Power Tools',
            'SAW': 'Power Tools',
            'WRN': 'Hand Tools',
            'PLR': 'Hand Tools',
            'HAM': 'Hand Tools',
            'MSR': 'Measurement',
            'SFT': 'Safety Equipment',
            'ELC': 'Electrical',
            'PLM': 'Plumbing',
            'WLD': 'Welding'
        }
        return categories.get(code, 'Other')

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

    @app.route('/api/tools/<int:id>/service/remove', methods=['POST'])
    @tool_manager_required
    def remove_tool_from_service(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Check if tool is already out of service
            if tool.status in ['maintenance', 'retired']:
                return jsonify({'error': f'Tool is already out of service with status: {tool.status}'}), 400

            # Check if tool is currently checked out
            active_checkout = Checkout.query.filter_by(tool_id=id, return_date=None).first()
            if active_checkout:
                return jsonify({'error': 'Cannot remove a tool that is currently checked out'}), 400

            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['action_type', 'reason']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Validate action type
            action_type = data.get('action_type')
            if action_type not in ['remove_maintenance', 'remove_permanent']:
                return jsonify({'error': 'Invalid action type. Must be "remove_maintenance" or "remove_permanent"'}), 400

            # Update tool status
            if action_type == 'remove_maintenance':
                tool.status = 'maintenance'
            else:  # remove_permanent
                tool.status = 'retired'

            tool.status_reason = data.get('reason')

            # Create service record
            service_record = ToolServiceRecord(
                tool_id=id,
                user_id=session['user_id'],
                action_type=action_type,
                reason=data.get('reason'),
                comments=data.get('comments', '')
            )

            # Create audit log
            log = AuditLog(
                action_type=action_type,
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) removed tool {tool.tool_number} (ID: {id}) from service. Reason: {data.get("reason")}'
            )

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type=action_type,
                description=f'Removed tool {tool.tool_number} from service',
                ip_address=request.remote_addr
            )

            # Save changes
            db.session.add(service_record)
            db.session.add(log)
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'status': tool.status,
                'status_reason': tool.status_reason,
                'message': f'Tool successfully removed from service with status: {tool.status}'
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error removing tool from service: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    @app.route('/api/tools/<int:id>/service/return', methods=['POST'])
    @tool_manager_required
    def return_tool_to_service(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Check if tool is out of service
            if tool.status not in ['maintenance', 'retired']:
                return jsonify({'error': f'Tool is not out of service. Current status: {tool.status}'}), 400

            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            if not data.get('reason'):
                return jsonify({'error': 'Missing required field: reason'}), 400

            # Update tool status
            tool.status = 'available'
            tool.status_reason = None

            # Create service record
            service_record = ToolServiceRecord(
                tool_id=id,
                user_id=session['user_id'],
                action_type='return_service',
                reason=data.get('reason'),
                comments=data.get('comments', '')
            )

            # Create audit log
            log = AuditLog(
                action_type='return_service',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) returned tool {tool.tool_number} (ID: {id}) to service. Reason: {data.get("reason")}'
            )

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='return_service',
                description=f'Returned tool {tool.tool_number} to service',
                ip_address=request.remote_addr
            )

            # Save changes
            db.session.add(service_record)
            db.session.add(log)
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'status': tool.status,
                'message': 'Tool successfully returned to service'
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error returning tool to service: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    @app.route('/api/tools/<int:id>/service/history', methods=['GET'])
    def get_tool_service_history(id):
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get service history
            service_records = ToolServiceRecord.query.filter_by(tool_id=id).order_by(
                ToolServiceRecord.timestamp.desc()
            ).offset(offset).limit(limit).all()

            return jsonify([record.to_dict() for record in service_records]), 200

        except Exception as e:
            print(f"Error getting tool service history: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500