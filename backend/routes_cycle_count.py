from flask import request, jsonify, session
from models import db, Tool, Checkout, AuditLog, Chemical, User
from models_cycle_count import (
    CycleCountSchedule, CycleCountBatch, CycleCountItem,
    CycleCountResult, CycleCountAdjustment, CycleCountNotification
)
from datetime import datetime, timedelta
from functools import wraps
import random
from sqlalchemy import func, extract

# Helper function to generate cycle count items for a batch
def generate_batch_items(batch_id, data):
    """
    Generate cycle count items for a batch based on the specified method
    """
    batch = CycleCountBatch.query.get(batch_id)
    if not batch:
        raise ValueError(f"Batch with ID {batch_id} not found")

    # Get method from schedule or data
    method = None
    if batch.schedule_id:
        schedule = CycleCountSchedule.query.get(batch.schedule_id)
        if schedule:
            method = schedule.method

    # Override method if provided in data
    if 'method' in data:
        method = data['method']

    if not method:
        raise ValueError("No method specified for generating items")

    # Get item types to include
    item_types = data.get('item_types', ['tool', 'chemical'])

    # Get filters
    location = data.get('location')
    category = data.get('category')

    # Get sample size or percentage
    sample_size = data.get('sample_size')
    sample_percentage = data.get('sample_percentage')

    # Generate items based on method
    items_to_add = []

    # Process tools
    if 'tool' in item_types:
        # Build query
        tool_query = Tool.query

        # Apply filters
        if location:
            tool_query = tool_query.filter(Tool.location == location)
        if category:
            tool_query = tool_query.filter(Tool.category == category)

        # Get all matching tools
        tools = tool_query.all()

        # Apply sampling if specified
        if method == 'ABC':
            # ABC analysis - prioritize high-value items
            # For tools, we'll use the most frequently checked out tools as "high value"
            tool_usage = {}
            for tool in tools:
                checkout_count = Checkout.query.filter_by(tool_id=tool.id).count()
                tool_usage[tool.id] = checkout_count

            # Sort tools by usage (descending)
            sorted_tools = sorted(tools, key=lambda t: tool_usage.get(t.id, 0), reverse=True)

            # Take top percentage as A, next as B, rest as C
            a_count = int(len(sorted_tools) * 0.2)  # Top 20% as A
            b_count = int(len(sorted_tools) * 0.3)  # Next 30% as B

            # A items - include all
            for tool in sorted_tools[:a_count]:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'tool',
                    'item_id': tool.id,
                    'expected_quantity': 1,
                    'expected_location': tool.location,
                    'status': 'pending'
                })

            # B items - include 50%
            b_tools = sorted_tools[a_count:a_count+b_count]
            if b_tools:
                sample_size = max(1, int(len(b_tools) * 0.5))
                b_sample = random.sample(b_tools, min(sample_size, len(b_tools)))
            else:
                b_sample = []
            for tool in b_sample:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'tool',
                    'item_id': tool.id,
                    'expected_quantity': 1,
                    'expected_location': tool.location,
                    'status': 'pending'
                })

            # C items - include 20%
            c_tools = sorted_tools[a_count+b_count:]
            if c_tools:
                sample_size = max(1, int(len(c_tools) * 0.2))
                c_sample = random.sample(c_tools, min(sample_size, len(c_tools)))
            else:
                c_sample = []
            for tool in c_sample:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'tool',
                    'item_id': tool.id,
                    'expected_quantity': 1,
                    'expected_location': tool.location,
                    'status': 'pending'
                })

        elif method == 'random':
            # Random sampling
            if len(tools) == 0:
                sampled_tools = []
            elif sample_size and sample_size < len(tools):
                # Take a random sample of specified size
                sampled_tools = random.sample(tools, sample_size)
            elif sample_percentage:
                # Take a random sample of specified percentage
                sample_count = max(1, int(len(tools) * sample_percentage / 100))
                sampled_tools = random.sample(tools, min(sample_count, len(tools)))
            else:
                # Include all tools
                sampled_tools = tools

            # Add sampled tools to items
            for tool in sampled_tools:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'tool',
                    'item_id': tool.id,
                    'expected_quantity': 1,
                    'expected_location': tool.location,
                    'status': 'pending'
                })

        elif method == 'location':
            # Group by location
            for tool in tools:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'tool',
                    'item_id': tool.id,
                    'expected_quantity': 1,
                    'expected_location': tool.location,
                    'status': 'pending'
                })

        elif method == 'category':
            # Group by category
            for tool in tools:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'tool',
                    'item_id': tool.id,
                    'expected_quantity': 1,
                    'expected_location': tool.location,
                    'status': 'pending'
                })

    # Process chemicals
    if 'chemical' in item_types:
        # Build query
        chemical_query = Chemical.query

        # Apply filters
        if location:
            chemical_query = chemical_query.filter(Chemical.location == location)
        if category:
            chemical_query = chemical_query.filter(Chemical.category == category)

        # Get all matching chemicals
        chemicals = chemical_query.all()

        # Apply sampling if specified
        if method == 'ABC':
            # ABC analysis - prioritize high-value items
            # For chemicals, we'll use quantity as a proxy for value
            sorted_chemicals = sorted(chemicals, key=lambda c: c.quantity, reverse=True)

            # Take top percentage as A, next as B, rest as C
            a_count = int(len(sorted_chemicals) * 0.2)  # Top 20% as A
            b_count = int(len(sorted_chemicals) * 0.3)  # Next 30% as B

            # A items - include all
            for chemical in sorted_chemicals[:a_count]:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'chemical',
                    'item_id': chemical.id,
                    'expected_quantity': chemical.quantity,
                    'expected_location': chemical.location,
                    'status': 'pending'
                })

            # B items - include 50%
            b_chemicals = sorted_chemicals[a_count:a_count+b_count]
            if b_chemicals:
                sample_size = max(1, int(len(b_chemicals) * 0.5))
                b_sample = random.sample(b_chemicals, min(sample_size, len(b_chemicals)))
            else:
                b_sample = []
            for chemical in b_sample:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'chemical',
                    'item_id': chemical.id,
                    'expected_quantity': chemical.quantity,
                    'expected_location': chemical.location,
                    'status': 'pending'
                })

            # C items - include 20%
            c_chemicals = sorted_chemicals[a_count+b_count:]
            if c_chemicals:
                sample_size = max(1, int(len(c_chemicals) * 0.2))
                c_sample = random.sample(c_chemicals, min(sample_size, len(c_chemicals)))
            else:
                c_sample = []
            for chemical in c_sample:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'chemical',
                    'item_id': chemical.id,
                    'expected_quantity': chemical.quantity,
                    'expected_location': chemical.location,
                    'status': 'pending'
                })

        elif method == 'random':
            # Random sampling
            if len(chemicals) == 0:
                sampled_chemicals = []
            elif sample_size and sample_size < len(chemicals):
                # Take a random sample of specified size
                sampled_chemicals = random.sample(chemicals, sample_size)
            elif sample_percentage:
                # Take a random sample of specified percentage
                sample_count = max(1, int(len(chemicals) * sample_percentage / 100))
                sampled_chemicals = random.sample(chemicals, min(sample_count, len(chemicals)))
            else:
                # Include all chemicals
                sampled_chemicals = chemicals

            # Add sampled chemicals to items
            for chemical in sampled_chemicals:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'chemical',
                    'item_id': chemical.id,
                    'expected_quantity': chemical.quantity,
                    'expected_location': chemical.location,
                    'status': 'pending'
                })

        elif method in ['location', 'category']:
            # Include all chemicals
            for chemical in chemicals:
                items_to_add.append({
                    'batch_id': batch_id,
                    'item_type': 'chemical',
                    'item_id': chemical.id,
                    'expected_quantity': chemical.quantity,
                    'expected_location': chemical.location,
                    'status': 'pending'
                })

    # Add all items to database
    for item_data in items_to_add:
        item = CycleCountItem(**item_data)
        db.session.add(item)

    db.session.commit()

    return len(items_to_add)

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

def register_cycle_count_routes(app):
    # Get all cycle count schedules
    @app.route('/api/cycle-counts/schedules', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_schedules():
        try:
            # Get query parameters
            active_only = request.args.get('active_only', 'false').lower() == 'true'

            # Build query
            query = CycleCountSchedule.query

            # Filter by active status if requested
            if active_only:
                query = query.filter_by(is_active=True)

            # Execute query
            schedules = query.order_by(CycleCountSchedule.created_at.desc()).all()

            # Return results
            return jsonify([schedule.to_dict() for schedule in schedules]), 200

        except Exception as e:
            print(f"Error getting cycle count schedules: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching cycle count schedules'}), 500

    # Get a specific cycle count schedule
    @app.route('/api/cycle-counts/schedules/<int:id>', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_schedule(id):
        try:
            # Get query parameters
            include_batches = request.args.get('include_batches', 'false').lower() == 'true'

            # Get schedule
            schedule = CycleCountSchedule.query.get_or_404(id)

            # Return result
            return jsonify(schedule.to_dict(include_batches=include_batches)), 200

        except Exception as e:
            print(f"Error getting cycle count schedule {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while fetching cycle count schedule {id}'}), 500

    # Create a new cycle count schedule
    @app.route('/api/cycle-counts/schedules', methods=['POST'])
    @tool_manager_required
    def create_cycle_count_schedule():
        try:
            # Get request data
            data = request.get_json()

            # Validate required fields
            if not all(key in data for key in ['name', 'frequency', 'method']):
                return jsonify({'error': 'Missing required fields: name, frequency, method'}), 400

            # Create new schedule
            schedule = CycleCountSchedule(
                name=data['name'],
                description=data.get('description', ''),
                frequency=data['frequency'],
                method=data['method'],
                created_by=session['user_id'],
                is_active=data.get('is_active', True)
            )

            # Save to database
            db.session.add(schedule)
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='cycle_count_schedule_created',
                action_details=f"Cycle count schedule '{data['name']}' created"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(schedule.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating cycle count schedule: {str(e)}")
            return jsonify({'error': 'An error occurred while creating cycle count schedule'}), 500

    # Update a cycle count schedule
    @app.route('/api/cycle-counts/schedules/<int:id>', methods=['PUT'])
    @tool_manager_required
    def update_cycle_count_schedule(id):
        try:
            # Get request data
            data = request.get_json()

            # Get schedule
            schedule = CycleCountSchedule.query.get_or_404(id)

            # Update fields
            if 'name' in data:
                schedule.name = data['name']
            if 'description' in data:
                schedule.description = data['description']
            if 'frequency' in data:
                schedule.frequency = data['frequency']
            if 'method' in data:
                schedule.method = data['method']
            if 'is_active' in data:
                schedule.is_active = data['is_active']

            # Save to database
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='cycle_count_schedule_updated',
                action_details=f"Cycle count schedule '{schedule.name}' updated"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(schedule.to_dict()), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating cycle count schedule {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while updating cycle count schedule {id}'}), 500

    # Delete a cycle count schedule
    @app.route('/api/cycle-counts/schedules/<int:id>', methods=['DELETE'])
    @tool_manager_required
    def delete_cycle_count_schedule(id):
        try:
            # Get schedule
            schedule = CycleCountSchedule.query.get_or_404(id)

            # Check if schedule has batches
            if schedule.batches:
                # Don't delete, just mark as inactive
                schedule.is_active = False
                db.session.commit()

                # Log the action
                log = AuditLog(
                    action_type='cycle_count_schedule_deactivated',
                    action_details=f"Cycle count schedule '{schedule.name}' deactivated"
                )
                db.session.add(log)
                db.session.commit()

                return jsonify({'message': f"Schedule '{schedule.name}' has batches and cannot be deleted. It has been deactivated instead."}), 200

            # Delete schedule
            db.session.delete(schedule)

            # Log the action
            log = AuditLog(
                action_type='cycle_count_schedule_deleted',
                action_details=f"Cycle count schedule '{schedule.name}' deleted"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify({'message': f"Schedule '{schedule.name}' deleted successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting cycle count schedule {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while deleting cycle count schedule {id}'}), 500

    # Get all cycle count batches
    @app.route('/api/cycle-counts/batches', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_batches():
        try:
            # Get query parameters
            status = request.args.get('status')
            schedule_id = request.args.get('schedule_id', type=int)

            # Build query
            query = CycleCountBatch.query

            # Apply filters
            if status:
                query = query.filter_by(status=status)
            if schedule_id:
                query = query.filter_by(schedule_id=schedule_id)

            # Execute query
            batches = query.order_by(CycleCountBatch.created_at.desc()).all()

            # Return results
            return jsonify([batch.to_dict() for batch in batches]), 200

        except Exception as e:
            print(f"Error getting cycle count batches: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching cycle count batches'}), 500

    # Get a specific cycle count batch
    @app.route('/api/cycle-counts/batches/<int:id>', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_batch(id):
        try:
            # Get query parameters
            include_items = request.args.get('include_items', 'false').lower() == 'true'

            # Get batch
            batch = CycleCountBatch.query.get_or_404(id)

            # Return result
            return jsonify(batch.to_dict(include_items=include_items)), 200

        except Exception as e:
            print(f"Error getting cycle count batch {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while fetching cycle count batch {id}'}), 500

    # Create a new cycle count batch
    @app.route('/api/cycle-counts/batches', methods=['POST'])
    @tool_manager_required
    def create_cycle_count_batch():
        try:
            # Get request data
            data = request.get_json()

            # Validate required fields
            if 'name' not in data:
                return jsonify({'error': 'Missing required field: name'}), 400

            # Validate dates
            if 'start_date' in data and 'end_date' in data and data['start_date'] and data['end_date']:
                start_date = datetime.fromisoformat(data['start_date'])
                end_date = datetime.fromisoformat(data['end_date'])
                if end_date < start_date:
                    return jsonify({'error': 'End date cannot be before start date'}), 400

            # Create new batch
            batch = CycleCountBatch(
                schedule_id=data.get('schedule_id'),
                name=data['name'],
                status='pending',
                start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
                end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
                created_by=session['user_id'],
                notes=data.get('notes', '')
            )

            # Save to database
            db.session.add(batch)
            db.session.commit()

            # Generate items for the batch if requested
            if data.get('generate_items', False):
                generate_batch_items(batch.id, data)

            # Log the action
            log = AuditLog(
                action_type='cycle_count_batch_created',
                action_details=f"Cycle count batch '{data['name']}' created"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(batch.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating cycle count batch: {str(e)}")
            return jsonify({'error': 'An error occurred while creating cycle count batch'}), 500

    # Update a cycle count batch
    @app.route('/api/cycle-counts/batches/<int:id>', methods=['PUT'])
    @tool_manager_required
    def update_cycle_count_batch(id):
        try:
            # Get request data
            data = request.get_json()

            # Get batch
            batch = CycleCountBatch.query.get_or_404(id)

            # Validate dates
            start_date = None
            end_date = None

            if 'start_date' in data and data['start_date']:
                start_date = datetime.fromisoformat(data['start_date'])
            else:
                start_date = batch.start_date

            if 'end_date' in data and data['end_date']:
                end_date = datetime.fromisoformat(data['end_date'])
            else:
                end_date = batch.end_date

            if start_date and end_date and end_date < start_date:
                return jsonify({'error': 'End date cannot be before start date'}), 400

            # Update fields
            if 'name' in data:
                batch.name = data['name']
            if 'status' in data:
                batch.status = data['status']
            if 'schedule_id' in data:
                batch.schedule_id = data['schedule_id']
            if 'start_date' in data:
                batch.start_date = start_date
            if 'end_date' in data:
                batch.end_date = end_date
            if 'notes' in data:
                batch.notes = data['notes']

            # Save to database
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='cycle_count_batch_updated',
                action_details=f"Cycle count batch '{batch.name}' updated"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(batch.to_dict()), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating cycle count batch {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while updating cycle count batch {id}'}), 500

    # Delete a cycle count batch
    @app.route('/api/cycle-counts/batches/<int:id>', methods=['DELETE'])
    @tool_manager_required
    def delete_cycle_count_batch(id):
        try:
            # Get batch
            batch = CycleCountBatch.query.get_or_404(id)

            # Check if batch has items with results
            has_results = False
            for item in batch.items:
                if item.results:
                    has_results = True
                    break

            if has_results:
                # Don't delete, just mark as cancelled
                batch.status = 'cancelled'
                db.session.commit()

                # Log the action
                log = AuditLog(
                    action_type='cycle_count_batch_cancelled',
                    action_details=f"Cycle count batch '{batch.name}' cancelled"
                )
                db.session.add(log)
                db.session.commit()

                return jsonify({'message': f"Batch '{batch.name}' has count results and cannot be deleted. It has been cancelled instead."}), 200

            # Delete batch items
            for item in batch.items:
                db.session.delete(item)

            # Delete batch
            db.session.delete(batch)

            # Log the action
            log = AuditLog(
                action_type='cycle_count_batch_deleted',
                action_details=f"Cycle count batch '{batch.name}' deleted"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify({'message': f"Batch '{batch.name}' deleted successfully"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting cycle count batch {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while deleting cycle count batch {id}'}), 500

    # Get all cycle count items for a batch
    @app.route('/api/cycle-counts/batches/<int:batch_id>/items', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_items(batch_id):
        try:
            # Get query parameters
            status = request.args.get('status')
            assigned_to = request.args.get('assigned_to')
            item_type = request.args.get('item_type')

            # Build query
            query = CycleCountItem.query.filter_by(batch_id=batch_id)

            # Apply filters
            if status:
                query = query.filter_by(status=status)
            if assigned_to:
                query = query.filter_by(assigned_to=assigned_to)
            if item_type:
                query = query.filter_by(item_type=item_type)

            # Execute query
            items = query.all()

            # Return results
            return jsonify([item.to_dict() for item in items]), 200

        except Exception as e:
            print(f"Error getting cycle count items for batch {batch_id}: {str(e)}")
            return jsonify({'error': f'An error occurred while fetching cycle count items for batch {batch_id}'}), 500

    # Assign items to users
    @app.route('/api/cycle-counts/batches/<int:id>/assign', methods=['POST'])
    @tool_manager_required
    def assign_cycle_count_items(id):
        try:
            # Get request data
            data = request.get_json()

            # Validate required fields
            if not data.get('assignments'):
                return jsonify({'error': 'Missing required field: assignments'}), 400

            # Get batch
            batch = CycleCountBatch.query.get_or_404(id)

            # Track assignments by user for notifications
            assignments_by_user = {}

            # Process assignments
            for assignment in data.get('assignments'):
                # Validate assignment data
                if not assignment.get('item_id') or not assignment.get('user_id'):
                    continue

                # Validate item
                item = CycleCountItem.query.get(assignment["item_id"])
                if not item or item.batch_id != batch.id:
                    continue

                # Validate user
                assignee = User.query.get(assignment["user_id"])
                if not assignee or getattr(assignee, 'is_disabled', False):
                    # Skip invalid users instead of committing bad data
                    continue

                # Assign user
                item.assigned_to = assignment.get('user_id')

                # Track for notification
                user_id = assignment.get('user_id')
                if user_id not in assignments_by_user:
                    assignments_by_user[user_id] = []
                assignments_by_user[user_id].append(item)

            # Create notifications for assigned users
            for user_id, items in assignments_by_user.items():
                # Create notification
                notification = CycleCountNotification(
                    user_id=user_id,
                    notification_type='batch_assigned',
                    reference_id=batch.id,
                    reference_type='batch',
                    message=f"You have been assigned {len(items)} items to count in batch '{batch.name}'."
                )
                db.session.add(notification)

            # Log the action
            log = AuditLog(
                action_type='cycle_count_items_assigned',
                action_details=f"Items assigned for batch {id}"
            )
            db.session.add(log)
            db.session.commit()   # <-- one and only commit

            # Return success
            return jsonify({'message': 'Items assigned successfully'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error assigning cycle count items: {str(e)}")
            return jsonify({'error': 'An error occurred while assigning cycle count items'}), 500

    # Get a specific cycle count item
    @app.route('/api/cycle-counts/items/<int:id>', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_item(id):
        try:
            # Get query parameters
            include_results = request.args.get('include_results', 'false').lower() == 'true'

            # Get item
            item = CycleCountItem.query.get_or_404(id)

            # Return result
            return jsonify(item.to_dict(include_results=include_results)), 200

        except Exception as e:
            print(f"Error getting cycle count item {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while fetching cycle count item {id}'}), 500

    # Update a cycle count item
    @app.route('/api/cycle-counts/items/<int:id>', methods=['PUT'])
    @tool_manager_required
    def update_cycle_count_item(id):
        try:
            # Get request data
            data = request.get_json()

            # Get item
            item = CycleCountItem.query.get_or_404(id)

            # Update fields
            if 'assigned_to' in data:
                item.assigned_to = data['assigned_to']
            if 'status' in data:
                item.status = data['status']

            # Save to database
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='cycle_count_item_updated',
                action_details=f"Cycle count item {id} updated"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(item.to_dict()), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating cycle count item {id}: {str(e)}")
            return jsonify({'error': f'An error occurred while updating cycle count item {id}'}), 500

    # Submit a count result for an item
    @app.route('/api/cycle-counts/items/<int:item_id>/count', methods=['POST'])
    @tool_manager_required
    def submit_count_result(item_id):
        try:
            # Get request data
            data = request.get_json()

            # Validate required fields
            if not all(key in data for key in ['actual_quantity']):
                return jsonify({'error': 'Missing required field: actual_quantity'}), 400

            # Get item
            item = CycleCountItem.query.get_or_404(item_id)

            # Get batch
            batch = CycleCountBatch.query.get_or_404(item.batch_id)

            # Check if item is already counted
            if item.status == 'counted':
                return jsonify({'error': f'Item {item_id} has already been counted'}), 400

            # Determine if there's a discrepancy
            has_discrepancy = False
            discrepancy_type = None
            discrepancy_notes = []

            # Check quantity discrepancy
            if item.expected_quantity != data['actual_quantity']:
                has_discrepancy = True
                discrepancy_type = 'quantity'
                discrepancy_notes.append(f"Expected quantity: {item.expected_quantity}, Actual: {data['actual_quantity']}")

            # Check location discrepancy
            if 'actual_location' in data and item.expected_location != data['actual_location']:
                has_discrepancy = True
                discrepancy_type = discrepancy_type or 'location'
                discrepancy_notes.append(f"Expected location: {item.expected_location}, Actual: {data['actual_location']}")

            # Create count result
            result = CycleCountResult(
                item_id=item_id,
                counted_by=session['user_id'],
                actual_quantity=data['actual_quantity'],
                actual_location=data.get('actual_location'),
                condition=data.get('condition'),
                notes=data.get('notes', ''),
                has_discrepancy=has_discrepancy,
                discrepancy_type=discrepancy_type,
                discrepancy_notes='\n'.join(discrepancy_notes) if discrepancy_notes else None
            )

            # Update item status
            item.status = 'counted'

            # Save to database
            db.session.add(result)
            db.session.commit()

            # Create notification for discrepancy if needed
            if has_discrepancy:
                # Get all admin users and materials department users
                admin_users = User.query.filter_by(is_admin=True).all()
                materials_users = User.query.filter_by(department='Materials').all()

                # Combine and deduplicate users
                notify_users = set()
                for user in admin_users + materials_users:
                    notify_users.add(user.id)

                # Create notifications
                item_type_name = "tool" if item.item_type == "tool" else "chemical"
                item_details = ""
                if item.item_type == "tool":
                    tool = Tool.query.get(item.item_id)
                    if tool:
                        item_details = f"{tool.tool_number} - {tool.description}"
                elif item.item_type == "chemical":
                    chemical = Chemical.query.get(item.item_id)
                    if chemical:
                        item_details = f"{chemical.part_number} - {chemical.description}"

                for user_id in notify_users:
                    notification = CycleCountNotification(
                        user_id=user_id,
                        notification_type='discrepancy_found',
                        reference_id=result.id,
                        reference_type='result',
                        message=f"Discrepancy found in batch '{batch.name}' for {item_type_name} {item_details}. Type: {discrepancy_type}."
                    )
                    db.session.add(notification)

            # Check if batch is complete
            pending_items = CycleCountItem.query.filter_by(batch_id=batch.id, status='pending').count()
            if pending_items == 0:
                # All items are counted, update batch status
                batch.status = 'completed'
                batch.end_date = datetime.utcnow()

                # Create notification for batch completion
                notification = CycleCountNotification(
                    user_id=batch.created_by,
                    notification_type='batch_completed',
                    reference_id=batch.id,
                    reference_type='batch',
                    message=f"Cycle count batch '{batch.name}' has been completed."
                )
                db.session.add(notification)

            # Log the action
            log = AuditLog(
                action_type='cycle_count_result_submitted',
                action_details=f"Count result submitted for item {item_id}"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(result.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error submitting count result for item {item_id}: {str(e)}")
            return jsonify({'error': f'An error occurred while submitting count result for item {item_id}'}), 500

    # Get all count results with discrepancies
    @app.route('/api/cycle-counts/discrepancies', methods=['GET'])
    @tool_manager_required
    def get_count_discrepancies():
        try:
            # Get query parameters
            batch_id = request.args.get('batch_id')

            # Build query
            query = CycleCountResult.query.filter_by(has_discrepancy=True)

            # Apply batch filter if provided
            if batch_id:
                query = query.join(CycleCountItem).filter(CycleCountItem.batch_id == batch_id)

            # Execute query
            results = query.all()

            # Return results
            return jsonify([result.to_dict(include_item=True) for result in results]), 200

        except Exception as e:
            print(f"Error getting count discrepancies: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching count discrepancies'}), 500

    # Get a specific count result
    @app.route('/api/cycle-counts/results/<int:result_id>', methods=['GET'])
    @tool_manager_required
    def get_count_result(result_id):
        try:
            # Get result
            result = CycleCountResult.query.get_or_404(result_id)

            # The item details are included via include_item=True

            # Return result with item details
            result_dict = result.to_dict(include_item=True, include_adjustments=True)

            return jsonify(result_dict), 200

        except Exception as e:
            print(f"Error getting count result {result_id}: {str(e)}")
            return jsonify({'error': f'An error occurred while fetching count result {result_id}'}), 500

    # Approve and process a count adjustment
    @app.route('/api/cycle-counts/results/<int:result_id>/adjust', methods=['POST'])
    @tool_manager_required
    def approve_count_adjustment(result_id):
        try:
            # Get request data
            data = request.get_json()

            # Validate required fields
            if not all(key in data for key in ['adjustment_type', 'new_value']):
                return jsonify({'error': 'Missing required fields: adjustment_type, new_value'}), 400

            # Get result
            result = CycleCountResult.query.get_or_404(result_id)

            # Get item
            item = CycleCountItem.query.get_or_404(result.item_id)

            # Get batch
            batch = CycleCountBatch.query.get_or_404(item.batch_id)

            # Get old value based on adjustment type
            old_value = None
            if data['adjustment_type'] == 'quantity':
                if item.item_type == 'tool':
                    old_value = '1'  # Tools always have quantity 1
                elif item.item_type == 'chemical':
                    chemical = Chemical.query.get(item.item_id)
                    if chemical:
                        old_value = str(chemical.quantity)
            elif data['adjustment_type'] == 'location':
                if item.item_type == 'tool':
                    tool = Tool.query.get(item.item_id)
                    if tool:
                        old_value = tool.location
                elif item.item_type == 'chemical':
                    chemical = Chemical.query.get(item.item_id)
                    if chemical:
                        old_value = chemical.location
            elif data['adjustment_type'] == 'condition':
                if item.item_type == 'tool':
                    tool = Tool.query.get(item.item_id)
                    if tool:
                        old_value = tool.condition
            elif data['adjustment_type'] == 'status':
                if item.item_type == 'tool':
                    tool = Tool.query.get(item.item_id)
                    if tool:
                        old_value = tool.status
                elif item.item_type == 'chemical':
                    chemical = Chemical.query.get(item.item_id)
                    if chemical:
                        old_value = chemical.status

            # Create adjustment record
            adjustment = CycleCountAdjustment(
                result_id=result_id,
                approved_by=session['user_id'],
                adjustment_type=data['adjustment_type'],
                old_value=old_value,
                new_value=data['new_value'],
                notes=data.get('notes', '')
            )

            # Apply the adjustment to the inventory
            if item.item_type == 'tool':
                tool = Tool.query.get(item.item_id)
                if tool:
                    if data['adjustment_type'] == 'location':
                        tool.location = data['new_value']
                    elif data['adjustment_type'] == 'condition':
                        tool.condition = data['new_value']
                    elif data['adjustment_type'] == 'status':
                        tool.status = data['new_value']
                        if data['new_value'] in ['maintenance', 'retired']:
                            tool.status_reason = data.get('notes', 'Updated from cycle count')
            elif item.item_type == 'chemical':
                chemical = Chemical.query.get(item.item_id)
                if chemical:
                    if data['adjustment_type'] == 'quantity':
                        chemical.quantity = float(data['new_value'])
                    elif data['adjustment_type'] == 'location':
                        chemical.location = data['new_value']
                    elif data['adjustment_type'] == 'status':
                        chemical.status = data['new_value']

            # Save to database
            db.session.add(adjustment)
            db.session.commit()

            # Create notification for the user who counted the item
            item_type_name = "tool" if item.item_type == "tool" else "chemical"
            item_details = ""
            if item.item_type == "tool":
                tool = Tool.query.get(item.item_id)
                if tool:
                    item_details = f"{tool.tool_number} - {tool.description}"
            elif item.item_type == "chemical":
                chemical = Chemical.query.get(item.item_id)
                if chemical:
                    item_details = f"{chemical.part_number} - {chemical.description}"

            # Notify the user who counted the item
            notification = CycleCountNotification(
                user_id=result.counted_by,
                notification_type='adjustment_approved',
                reference_id=adjustment.id,
                reference_type='adjustment',
                message=f"Your count discrepancy for {item_type_name} {item_details} in batch '{batch.name}' has been adjusted. {data['adjustment_type'].capitalize()} changed from {old_value} to {data['new_value']}."
            )
            db.session.add(notification)

            # Log the action
            log = AuditLog(
                action_type='cycle_count_adjustment_approved',
                action_details=f"Count adjustment approved for result {result_id}"
            )
            db.session.add(log)
            db.session.commit()

            # Return result
            return jsonify(adjustment.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error approving count adjustment for result {result_id}: {str(e)}")
            return jsonify({'error': f'An error occurred while approving count adjustment for result {result_id}'}), 500

    # Get cycle count statistics
    @app.route('/api/cycle-counts/stats', methods=['GET'])
    @tool_manager_required
    def get_cycle_count_stats():
        try:
            # Get overall statistics
            total_schedules = CycleCountSchedule.query.count()
            active_schedules = CycleCountSchedule.query.filter_by(is_active=True).count()

            total_batches = CycleCountBatch.query.count()
            pending_batches = CycleCountBatch.query.filter_by(status='pending').count()
            in_progress_batches = CycleCountBatch.query.filter_by(status='in_progress').count()
            completed_batches = CycleCountBatch.query.filter_by(status='completed').count()

            total_items = CycleCountItem.query.count()
            counted_items = CycleCountItem.query.filter_by(status='counted').count()
            pending_items = CycleCountItem.query.filter_by(status='pending').count()

            total_results = CycleCountResult.query.count()
            discrepancy_results = CycleCountResult.query.filter_by(has_discrepancy=True).count()

            # Calculate accuracy rate
            accuracy_rate = 0
            if total_results > 0:
                accuracy_rate = round(100 * (total_results - discrepancy_results) / total_results, 2)

            # Get recent batches
            recent_batches = CycleCountBatch.query.order_by(CycleCountBatch.created_at.desc()).limit(5).all()

            # Return results
            return jsonify({
                'schedules': {
                    'total': total_schedules,
                    'active': active_schedules
                },
                'batches': {
                    'total': total_batches,
                    'pending': pending_batches,
                    'in_progress': in_progress_batches,
                    'completed': completed_batches
                },
                'items': {
                    'total': total_items,
                    'counted': counted_items,
                    'pending': pending_items,
                    'completion_rate': round(100 * counted_items / total_items, 2) if total_items > 0 else 0
                },
                'results': {
                    'total': total_results,
                    'with_discrepancies': discrepancy_results,
                    'accuracy_rate': accuracy_rate
                },
                'recent_batches': [batch.to_dict() for batch in recent_batches]
            }), 200

        except Exception as e:
            print(f"Error getting cycle count statistics: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching cycle count statistics'}), 500

    # Cycle Count Reports
    # Inventory Accuracy Report
    @app.route('/api/reports/cycle-counts/accuracy', methods=['GET'])
    @tool_manager_required
    def cycle_count_accuracy_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get('timeframe', 'month')
            location = request.args.get('location')
            category = request.args.get('category')

            # Calculate date range based on timeframe
            end_date = datetime.now()
            if timeframe == 'week':
                start_date = end_date - timedelta(days=7)
            elif timeframe == 'month':
                start_date = end_date - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif timeframe == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)  # Default to month

            # Build base query for results
            query = db.session.query(
                CycleCountResult,
                CycleCountItem
            ).join(
                CycleCountItem,
                CycleCountResult.item_id == CycleCountItem.id
            ).join(
                CycleCountBatch,
                CycleCountItem.batch_id == CycleCountBatch.id
            ).filter(
                CycleCountBatch.created_at >= start_date
            )

            # Apply filters if provided
            if location:
                query = query.filter(CycleCountItem.expected_location == location)
            if category:
                # For category filtering, we need to join with the appropriate table
                query = query.outerjoin(
                    Tool,
                    (CycleCountItem.item_type == 'tool') & (CycleCountItem.item_id == Tool.id)
                ).outerjoin(
                    Chemical,
                    (CycleCountItem.item_type == 'chemical') & (CycleCountItem.item_id == Chemical.id)
                ).filter(
                    ((CycleCountItem.item_type == 'tool') & (Tool.category == category)) |
                    ((CycleCountItem.item_type == 'chemical') & (Chemical.category == category))
                )

            # Execute query
            results = query.all()

            # Calculate accuracy metrics
            total_counts = len(results)
            accurate_counts = sum(1 for r, i in results if not r.has_discrepancy)

            # Calculate accuracy by location
            accuracy_by_location = {}
            for r, i in results:
                location = i.expected_location or 'Unknown'
                if location not in accuracy_by_location:
                    accuracy_by_location[location] = {'total': 0, 'accurate': 0}
                accuracy_by_location[location]['total'] += 1
                if not r.has_discrepancy:
                    accuracy_by_location[location]['accurate'] += 1

            # Calculate accuracy by category
            accuracy_by_category = {}
            for r, i in results:
                category = 'Unknown'
                if i.item_type == 'tool':
                    tool = Tool.query.get(i.item_id)
                    if tool:
                        category = tool.category or 'General'
                elif i.item_type == 'chemical':
                    chemical = Chemical.query.get(i.item_id)
                    if chemical:
                        category = chemical.category or 'General'

                if category not in accuracy_by_category:
                    accuracy_by_category[category] = {'total': 0, 'accurate': 0}
                accuracy_by_category[category]['total'] += 1
                if not r.has_discrepancy:
                    accuracy_by_category[category]['accurate'] += 1

            # Calculate accuracy trend over time
            accuracy_trend = {}
            for r, i in results:
                date_key = r.counted_at.strftime('%Y-%m-%d')
                if date_key not in accuracy_trend:
                    accuracy_trend[date_key] = {'total': 0, 'accurate': 0}
                accuracy_trend[date_key]['total'] += 1
                if not r.has_discrepancy:
                    accuracy_trend[date_key]['accurate'] += 1

            # Format response
            response = {
                'overall_accuracy': round(100 * accurate_counts / total_counts, 2) if total_counts > 0 else 0,
                'total_counts': total_counts,
                'accurate_counts': accurate_counts,
                'accuracy_by_location': [
                    {
                        'location': loc,
                        'accuracy': round(100 * data['accurate'] / data['total'], 2) if data['total'] > 0 else 0,
                        'total': data['total'],
                        'accurate': data['accurate']
                    }
                    for loc, data in accuracy_by_location.items()
                ],
                'accuracy_by_category': [
                    {
                        'category': cat,
                        'accuracy': round(100 * data['accurate'] / data['total'], 2) if data['total'] > 0 else 0,
                        'total': data['total'],
                        'accurate': data['accurate']
                    }
                    for cat, data in accuracy_by_category.items()
                ],
                'accuracy_trend': [
                    {
                        'date': date,
                        'accuracy': round(100 * data['accurate'] / data['total'], 2) if data['total'] > 0 else 0,
                        'total': data['total'],
                        'accurate': data['accurate']
                    }
                    for date, data in sorted(accuracy_trend.items())
                ]
            }

            return jsonify(response), 200

        except Exception as e:
            print(f"Error generating cycle count accuracy report: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the cycle count accuracy report'}), 500

    # Discrepancy Report
    @app.route('/api/reports/cycle-counts/discrepancies', methods=['GET'])
    @tool_manager_required
    def cycle_count_discrepancy_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get('timeframe', 'month')
            discrepancy_type = request.args.get('type')
            location = request.args.get('location')
            category = request.args.get('category')

            # Calculate date range based on timeframe
            end_date = datetime.now()
            if timeframe == 'week':
                start_date = end_date - timedelta(days=7)
            elif timeframe == 'month':
                start_date = end_date - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif timeframe == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)  # Default to month

            # Build base query for results with discrepancies
            query = db.session.query(
                CycleCountResult,
                CycleCountItem
            ).join(
                CycleCountItem,
                CycleCountResult.item_id == CycleCountItem.id
            ).join(
                CycleCountBatch,
                CycleCountItem.batch_id == CycleCountBatch.id
            ).filter(
                CycleCountBatch.created_at >= start_date,
                CycleCountResult.has_discrepancy == True
            )

            # Apply filters if provided
            if discrepancy_type:
                query = query.filter(CycleCountResult.discrepancy_type == discrepancy_type)
            if location:
                query = query.filter(CycleCountItem.expected_location == location)
            if category:
                # For category filtering, we need to join with the appropriate table
                query = query.outerjoin(
                    Tool,
                    (CycleCountItem.item_type == 'tool') & (CycleCountItem.item_id == Tool.id)
                ).outerjoin(
                    Chemical,
                    (CycleCountItem.item_type == 'chemical') & (CycleCountItem.item_id == Chemical.id)
                ).filter(
                    ((CycleCountItem.item_type == 'tool') & (Tool.category == category)) |
                    ((CycleCountItem.item_type == 'chemical') & (Chemical.category == category))
                )

            # Execute query
            results = query.all()

            # Process results
            discrepancies = []
            discrepancy_by_type = {}
            discrepancy_by_location = {}
            discrepancy_by_category = {}
            discrepancy_trend = {}

            for r, i in results:
                # Get item details
                item_details = {}
                if i.item_type == 'tool':
                    tool = Tool.query.get(i.item_id)
                    if tool:
                        item_details = {
                            'tool_number': tool.tool_number,
                            'serial_number': tool.serial_number,
                            'description': tool.description,
                            'category': tool.category or 'General'
                        }
                elif i.item_type == 'chemical':
                    chemical = Chemical.query.get(i.item_id)
                    if chemical:
                        item_details = {
                            'part_number': chemical.part_number,
                            'description': chemical.description,
                            'category': chemical.category or 'General'
                        }

                # Add to discrepancies list
                discrepancies.append({
                    'id': r.id,
                    'item_type': i.item_type,
                    'item_id': i.item_id,
                    'item_details': item_details,
                    'expected_quantity': i.expected_quantity,
                    'expected_location': i.expected_location,
                    'actual_quantity': r.actual_quantity,
                    'actual_location': r.actual_location,
                    'discrepancy_type': r.discrepancy_type,
                    'discrepancy_notes': r.discrepancy_notes,
                    'counted_at': r.counted_at.isoformat(),
                    'batch_id': i.batch_id
                })

                # Count by type
                disc_type = r.discrepancy_type or 'Unknown'
                discrepancy_by_type[disc_type] = discrepancy_by_type.get(disc_type, 0) + 1

                # Count by location
                location = i.expected_location or 'Unknown'
                discrepancy_by_location[location] = discrepancy_by_location.get(location, 0) + 1

                # Count by category
                category = item_details.get('category', 'Unknown')
                discrepancy_by_category[category] = discrepancy_by_category.get(category, 0) + 1

                # Count by date
                date_key = r.counted_at.strftime('%Y-%m-%d')
                discrepancy_trend[date_key] = discrepancy_trend.get(date_key, 0) + 1

            # Format response
            response = {
                'total_discrepancies': len(discrepancies),
                'discrepancies': discrepancies,
                'discrepancy_by_type': [
                    {'type': t, 'count': c}
                    for t, c in discrepancy_by_type.items()
                ],
                'discrepancy_by_location': [
                    {'location': l, 'count': c}
                    for l, c in discrepancy_by_location.items()
                ],
                'discrepancy_by_category': [
                    {'category': c, 'count': count}
                    for c, count in discrepancy_by_category.items()
                ],
                'discrepancy_trend': [
                    {'date': d, 'count': c}
                    for d, c in sorted(discrepancy_trend.items())
                ]
            }

            return jsonify(response), 200

        except Exception as e:
            print(f"Error generating cycle count discrepancy report: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the cycle count discrepancy report'}), 500

    # Cycle Count Performance Report
    @app.route('/api/reports/cycle-counts/performance', methods=['GET'])
    @tool_manager_required
    def cycle_count_performance_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get('timeframe', 'month')

            # Calculate date range based on timeframe
            end_date = datetime.now()
            if timeframe == 'week':
                start_date = end_date - timedelta(days=7)
            elif timeframe == 'month':
                start_date = end_date - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif timeframe == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)  # Default to month

            # Get batches in the timeframe
            batches = CycleCountBatch.query.filter(
                CycleCountBatch.created_at >= start_date
            ).all()

            # Calculate completion rates
            total_batches = len(batches)
            completed_batches = sum(1 for b in batches if b.status == 'completed')
            in_progress_batches = sum(1 for b in batches if b.status == 'in_progress')
            pending_batches = sum(1 for b in batches if b.status == 'pending')

            # Calculate average time to complete
            completion_times = []
            for batch in batches:
                if batch.status == 'completed' and batch.start_date and batch.end_date:
                    duration = (batch.end_date - batch.start_date).total_seconds() / 3600  # hours
                    completion_times.append(duration)

            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

            # Get counts by user
            counts_by_user = db.session.query(
                CycleCountResult.counted_by,
                func.count().label('count')
            ).filter(
                CycleCountResult.counted_at >= start_date
            ).group_by(
                CycleCountResult.counted_by
            ).all()

            # Get user names
            user_counts = []
            for user_id, count in counts_by_user:
                from models import User
                user = User.query.get(user_id)
                user_name = user.name if user else f"User {user_id}"
                user_counts.append({
                    'user_id': user_id,
                    'user_name': user_name,
                    'count': count
                })

            # Get counts by day/week/month
            counts_by_day = db.session.query(
                func.date(CycleCountResult.counted_at).label('date'),
                func.count().label('count')
            ).filter(
                CycleCountResult.counted_at >= start_date
            ).group_by(
                func.date(CycleCountResult.counted_at)
            ).all()

            # Format response
            response = {
                'completion_rate': {
                    'total_batches': total_batches,
                    'completed_batches': completed_batches,
                    'in_progress_batches': in_progress_batches,
                    'pending_batches': pending_batches,
                    'completion_percentage': round(100 * completed_batches / total_batches, 2) if total_batches > 0 else 0
                },
                'average_completion_time': round(avg_completion_time, 2),  # in hours
                'counts_by_user': user_counts,
                'counts_by_day': [
                    {'date': date.strftime('%Y-%m-%d'), 'count': count}
                    for date, count in counts_by_day
                ]
            }

            return jsonify(response), 200

        except Exception as e:
            print(f"Error generating cycle count performance report: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the cycle count performance report'}), 500

    # Cycle Count Coverage Report
    @app.route('/api/reports/cycle-counts/coverage', methods=['GET'])
    @tool_manager_required
    def cycle_count_coverage_report():
        try:
            # Get parameters
            days = request.args.get('days', 90, type=int)
            location = request.args.get('location')
            category = request.args.get('category')

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)

            # Get all tools and chemicals
            tools_query = Tool.query
            chemicals_query = Chemical.query

            # Apply filters if provided
            if location:
                tools_query = tools_query.filter(Tool.location == location)
                chemicals_query = chemicals_query.filter(Chemical.location == location)
            if category:
                tools_query = tools_query.filter(Tool.category == category)
                chemicals_query = chemicals_query.filter(Chemical.category == category)

            # Get all tools and chemicals
            all_tools = tools_query.all()
            all_chemicals = chemicals_query.all()

            # Get tools and chemicals that have been counted
            counted_tool_ids = db.session.query(
                CycleCountItem.item_id
            ).filter(
                CycleCountItem.item_type == 'tool',
                CycleCountItem.status == 'counted',
                CycleCountItem.updated_at >= cutoff_date
            ).distinct().all()

            counted_chemical_ids = db.session.query(
                CycleCountItem.item_id
            ).filter(
                CycleCountItem.item_type == 'chemical',
                CycleCountItem.status == 'counted',
                CycleCountItem.updated_at >= cutoff_date
            ).distinct().all()

            # Convert to sets for faster lookup
            counted_tool_ids = {id[0] for id in counted_tool_ids}
            counted_chemical_ids = {id[0] for id in counted_chemical_ids}

            # Calculate coverage
            total_items = len(all_tools) + len(all_chemicals)
            counted_items = len(counted_tool_ids) + len(counted_chemical_ids)

            # Identify items not counted
            uncounted_tools = [t for t in all_tools if t.id not in counted_tool_ids]
            uncounted_chemicals = [c for c in all_chemicals if c.id not in counted_chemical_ids]

            # Calculate coverage by location
            coverage_by_location = {}

            # Process tools by location
            for tool in all_tools:
                location = tool.location or 'Unknown'
                if location not in coverage_by_location:
                    coverage_by_location[location] = {'total': 0, 'counted': 0}
                coverage_by_location[location]['total'] += 1
                if tool.id in counted_tool_ids:
                    coverage_by_location[location]['counted'] += 1

            # Process chemicals by location
            for chemical in all_chemicals:
                location = chemical.location or 'Unknown'
                if location not in coverage_by_location:
                    coverage_by_location[location] = {'total': 0, 'counted': 0}
                coverage_by_location[location]['total'] += 1
                if chemical.id in counted_chemical_ids:
                    coverage_by_location[location]['counted'] += 1

            # Calculate coverage by category
            coverage_by_category = {}

            # Process tools by category
            for tool in all_tools:
                category = tool.category or 'General'
                if category not in coverage_by_category:
                    coverage_by_category[category] = {'total': 0, 'counted': 0}
                coverage_by_category[category]['total'] += 1
                if tool.id in counted_tool_ids:
                    coverage_by_category[category]['counted'] += 1

            # Process chemicals by category
            for chemical in all_chemicals:
                category = chemical.category or 'General'
                if category not in coverage_by_category:
                    coverage_by_category[category] = {'total': 0, 'counted': 0}
                coverage_by_category[category]['total'] += 1
                if chemical.id in counted_chemical_ids:
                    coverage_by_category[category]['counted'] += 1

            # Format uncounted items for response
            uncounted_items = []

            for tool in uncounted_tools[:100]:  # Limit to 100 items
                uncounted_items.append({
                    'id': tool.id,
                    'type': 'tool',
                    'identifier': tool.tool_number,
                    'description': tool.description,
                    'location': tool.location,
                    'category': tool.category or 'General'
                })

            for chemical in uncounted_chemicals[:100]:  # Limit to 100 items
                uncounted_items.append({
                    'id': chemical.id,
                    'type': 'chemical',
                    'identifier': chemical.part_number,
                    'description': chemical.description,
                    'location': chemical.location,
                    'category': chemical.category or 'General'
                })

            # Format response
            response = {
                'overall_coverage': {
                    'total_items': total_items,
                    'counted_items': counted_items,
                    'coverage_percentage': round(100 * counted_items / total_items, 2) if total_items > 0 else 0
                },
                'coverage_by_location': [
                    {
                        'location': loc,
                        'total': data['total'],
                        'counted': data['counted'],
                        'coverage_percentage': round(100 * data['counted'] / data['total'], 2) if data['total'] > 0 else 0
                    }
                    for loc, data in coverage_by_location.items()
                ],
                'coverage_by_category': [
                    {
                        'category': cat,
                        'total': data['total'],
                        'counted': data['counted'],
                        'coverage_percentage': round(100 * data['counted'] / data['total'], 2) if data['total'] > 0 else 0
                    }
                    for cat, data in coverage_by_category.items()
                ],
                'uncounted_items': uncounted_items,
                'uncounted_items_count': len(uncounted_tools) + len(uncounted_chemicals),
                'days_threshold': days
            }

            return jsonify(response), 200

        except Exception as e:
            print(f"Error generating cycle count coverage report: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the cycle count coverage report'}), 500

    # Notification Endpoints
    # Get notifications for the current user
    @app.route('/api/cycle-counts/notifications', methods=['GET'])
    def get_cycle_count_notifications():
        try:
            # Get query parameters
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            limit = request.args.get('limit', 10, type=int)

            # Build query
            query = CycleCountNotification.query.filter_by(user_id=session['user_id'])

            # Filter by read status if requested
            if unread_only:
                query = query.filter_by(is_read=False)

            # Execute query with limit and order by created_at desc
            notifications = query.order_by(CycleCountNotification.created_at.desc()).limit(limit).all()

            # Get unread count
            unread_count = CycleCountNotification.query.filter_by(
                user_id=session['user_id'],
                is_read=False
            ).count()

            # Return results
            return jsonify({
                'notifications': [notification.to_dict() for notification in notifications],
                'unread_count': unread_count
            }), 200

        except Exception as e:
            print(f"Error getting cycle count notifications: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching cycle count notifications'}), 500

    # Mark notification as read
    @app.route('/api/cycle-counts/notifications/<int:id>/read', methods=['POST'])
    def mark_notification_read(id):
        try:
            # Get notification
            notification = CycleCountNotification.query.get_or_404(id)

            # Check if notification belongs to current user
            if notification.user_id != session['user_id']:
                return jsonify({'error': 'Unauthorized'}), 403

            # Mark as read
            notification.is_read = True

            # Save to database
            db.session.commit()

            # Return success
            return jsonify({'message': 'Notification marked as read'}), 200

        except Exception as e:
            print(f"Error marking notification as read: {str(e)}")
            return jsonify({'error': 'An error occurred while marking the notification as read'}), 500

    # Mark all notifications as read
    @app.route('/api/cycle-counts/notifications/read-all', methods=['POST'])
    def mark_all_notifications_read():
        try:
            # Update all unread notifications for the current user
            CycleCountNotification.query.filter_by(
                user_id=session['user_id'],
                is_read=False
            ).update({'is_read': True})

            # Save to database
            db.session.commit()

            # Return success
            return jsonify({'message': 'All notifications marked as read'}), 200

        except Exception as e:
            print(f"Error marking all notifications as read: {str(e)}")
            return jsonify({'error': 'An error occurred while marking all notifications as read'}), 500
