from flask import request, jsonify, session
from models import db, Tool, Checkout, AuditLog, Chemical
from models_cycle_count import (
    CycleCountSchedule, CycleCountBatch, CycleCountItem,
    CycleCountResult, CycleCountAdjustment
)
from datetime import datetime
from functools import wraps
import random

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
                start_date=datetime.fromisoformat(data['start_date']) if 'start_date' in data else None,
                end_date=datetime.fromisoformat(data['end_date']) if 'end_date' in data else None,
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
            return jsonify([result.to_dict() for result in results]), 200

        except Exception as e:
            print(f"Error getting count discrepancies: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching count discrepancies'}), 500

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
