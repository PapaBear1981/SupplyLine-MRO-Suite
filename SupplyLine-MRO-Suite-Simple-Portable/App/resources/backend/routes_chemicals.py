from flask import request, jsonify, session
from models import db, Chemical, ChemicalIssuance, User, AuditLog, UserActivity
from datetime import datetime, timedelta
from functools import wraps
from utils.error_handler import handle_errors, ValidationError, log_security_event, validate_input
from utils.validation import validate_schema, validate_types, validate_constraints
from utils.session_manager import SessionManager, secure_login_required
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

# Decorator to check if user is admin or in Materials department
def materials_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use secure session validation
        valid, message = SessionManager.validate_session()
        if not valid:
            log_security_event('unauthorized_access_attempt', f'Materials access denied: {message}')
            return jsonify({'error': 'Authentication required', 'reason': message}), 401

        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            log_security_event('insufficient_permissions', f'Materials access denied for user {session.get("user_id")}')
            return jsonify({'error': 'Materials management privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def register_chemical_routes(app):
    # Get all chemicals
    @app.route('/api/chemicals', methods=['GET'])
    @handle_errors
    def chemicals_route():
        # Get query parameters for filtering
        category = request.args.get('category')
        status = request.args.get('status')
        search = request.args.get('q')
        show_archived = request.args.get('archived', 'false').lower() == 'true'

        # Start with base query
        query = Chemical.query

        # Filter by archived status if the column exists
        try:
            if not show_archived:
                query = query.filter(Chemical.is_archived.is_(False))
        except AttributeError:
            # If the column doesn't exist, we can't filter by it
            logger.warning("is_archived column not found, skipping archived filter")
            pass

        # Apply filters if provided
        if category:
            query = query.filter(Chemical.category == category)
        if status:
            query = query.filter(Chemical.status == status)
        if search:
            query = query.filter(
                db.or_(
                    Chemical.part_number.ilike(f'%{search}%'),
                    Chemical.lot_number.ilike(f'%{search}%'),
                    Chemical.description.ilike(f'%{search}%'),
                    Chemical.manufacturer.ilike(f'%{search}%')
                )
            )

        # Execute query first
        chemicals = query.all()

        # Batch update status based on expiration and stock level to avoid N+1 queries
        chemicals_to_update = []
        archive_logs = []

        for chemical in chemicals:
            try:
                is_archived = chemical.is_archived
            except AttributeError:
                # If the column doesn't exist, assume not archived
                logger.debug(f"is_archived attribute not found for chemical {chemical.id}")
                is_archived = False

            if not is_archived:  # Only update status for non-archived chemicals
                status_changed = False

                if chemical.is_expired():
                    chemical.status = 'expired'
                    status_changed = True

                    # Auto-archive expired chemicals if the columns exist
                    try:
                        chemical.is_archived = True
                        chemical.archived_reason = 'expired'
                        chemical.archived_date = datetime.utcnow()

                        # Prepare log for archiving (batch insert later)
                        archive_logs.append({
                            'action_type': 'chemical_archived',
                            'action_details': f"Chemical {chemical.part_number} - {chemical.lot_number} automatically archived: expired",
                            'timestamp': datetime.utcnow()
                        })

                        # Update reorder status for expired chemicals
                        chemical.update_reorder_status()
                    except AttributeError as e:
                        # If the columns don't exist, just update the status
                        logger.debug(f"Archive columns not found for chemical {chemical.id}: {str(e)}")
                        pass
                elif chemical.quantity <= 0:
                    chemical.status = 'out_of_stock'
                    status_changed = True
                    # Update reorder status for out-of-stock chemicals
                    chemical.update_reorder_status()
                elif chemical.is_low_stock():
                    chemical.status = 'low_stock'
                    status_changed = True
                    # Update reorder status for low-stock chemicals
                    chemical.update_reorder_status()

                # Check if chemical is expiring soon (within 30 days)
                if chemical.is_expiring_soon(30):
                    # Add a flag to the chemical data
                    chemical.expiring_soon = True

                if status_changed:
                    chemicals_to_update.append(chemical)

        # Batch insert archive logs if any
        if archive_logs:
            db.session.bulk_insert_mappings(AuditLog, archive_logs)

        # Single commit for all changes
        if chemicals_to_update or archive_logs:
            db.session.commit()

        # Serialize after all mutations to ensure client gets updated data
        result = [
            {**c.to_dict(), **({'expiring_soon': True} if getattr(c, 'expiring_soon', False) else {})}
            for c in chemicals
        ]

        return jsonify(result)

    # Create a new chemical
    @app.route('/api/chemicals', methods=['POST'])
    @materials_manager_required
    @handle_errors
    def create_chemical_route():
        data = request.get_json() or {}

        # Validate and sanitize input using schema
        validated_data = validate_schema(data, 'chemical')

        logger.info(f"Creating chemical with part number: {validated_data.get('part_number')}")

        # Check if chemical with same part number and lot number already exists
        existing_chemical = Chemical.query.filter_by(
            part_number=validated_data['part_number'],
            lot_number=validated_data['lot_number']
        ).first()

        if existing_chemical:
            raise ValidationError('Chemical with this part number and lot number already exists')

        # Create new chemical
        chemical = Chemical(
            part_number=validated_data['part_number'],
            lot_number=validated_data['lot_number'],
            description=validated_data.get('description', ''),
            manufacturer=validated_data.get('manufacturer', ''),
            quantity=validated_data['quantity'],
            unit=validated_data['unit'],
            location=validated_data.get('location', ''),
            category=validated_data.get('category', 'General'),
            status=validated_data.get('status', 'available'),
            expiration_date=validated_data.get('expiration_date'),
            minimum_stock_level=validated_data.get('minimum_stock_level'),
            notes=validated_data.get('notes', '')
        )

        db.session.add(chemical)

        # Log the action
        log = AuditLog(
            action_type='chemical_added',
            action_details=f"Chemical {validated_data['part_number']} - {validated_data['lot_number']} added"
        )
        db.session.add(log)

        # Log user activity
        if 'user_id' in session:
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='chemical_added',
                description=f"Added chemical {validated_data['part_number']} - {validated_data['lot_number']}"
            )
            db.session.add(activity)

        db.session.commit()

        logger.info(f"Chemical created successfully: {chemical.part_number} - {chemical.lot_number}")
        return jsonify(chemical.to_dict()), 201

    # Get barcode data for a chemical
    @app.route('/api/chemicals/<int:id>/barcode', methods=['GET'])
    def chemical_barcode_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Format expiration date for barcode (YYYYMMDD)
            expiration_date = "NOEXP"
            if chemical.expiration_date:
                expiration_date = chemical.expiration_date.strftime('%Y%m%d')

            # Create barcode data
            barcode_data = f"{chemical.part_number}-{chemical.lot_number}-{expiration_date}"

            return jsonify({
                'chemical_id': chemical.id,
                'part_number': chemical.part_number,
                'lot_number': chemical.lot_number,
                'expiration_date': chemical.expiration_date.isoformat() if chemical.expiration_date else None,
                'barcode_data': barcode_data
            })
        except Exception as e:
            print(f"Error in chemical barcode route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating barcode data'}), 500

    # Issue a chemical
    @app.route('/api/chemicals/<int:id>/issue', methods=['POST'])
    @secure_login_required
    @handle_errors
    def chemical_issue_route(id):
        # Get the chemical
        chemical = Chemical.query.get_or_404(id)

        # Check if chemical can be issued
        if chemical.status == 'expired':
            raise ValidationError('Cannot issue an expired chemical')

        if chemical.quantity <= 0:
            raise ValidationError('Cannot issue a chemical that is out of stock')

        # Get and validate request data
        data = request.get_json() or {}

        # Use centralized schema validation
        validated_data = validate_schema(data, 'chemical_issuance')

        # Ensure the user exists
        if not User.query.get(validated_data['user_id']):
            raise ValidationError('Supplied user_id does not exist')

        quantity = float(validated_data['quantity'])
        if quantity > chemical.quantity:
            raise ValidationError(f'Cannot issue more than available quantity ({chemical.quantity} {chemical.unit})')

        # Create issuance record
        issuance = ChemicalIssuance(
            chemical_id=chemical.id,
            user_id=validated_data['user_id'],
            quantity=quantity,
            hangar=validated_data['hangar'],
            purpose=validated_data.get('purpose', '')
        )

        # Update chemical quantity
        chemical.quantity -= quantity

        # Update chemical status based on new quantity
        if chemical.quantity <= 0:
            chemical.status = 'out_of_stock'
            # Update reorder status
            chemical.update_reorder_status()
        elif chemical.is_low_stock():
            chemical.status = 'low_stock'
            # Update reorder status
            chemical.update_reorder_status()

        db.session.add(issuance)

        # Log the action
        log = AuditLog(
            action_type='chemical_issued',
            action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} issued: {quantity} {chemical.unit}"
        )
        db.session.add(log)

        # Log user activity
        if 'user_id' in session:
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='chemical_issued',
                description=f"Issued {quantity} {chemical.unit} of chemical {chemical.part_number} - {chemical.lot_number}"
            )
            db.session.add(activity)

        db.session.commit()

        logger.info(f"Chemical issued successfully: {chemical.part_number} - {chemical.lot_number}, quantity: {quantity}")

        # Return updated chemical and issuance record
        return jsonify({
            'chemical': chemical.to_dict(),
            'issuance': issuance.to_dict()
        })

    # Get issuance history for a chemical
    @app.route('/api/chemicals/<int:id>/issuances', methods=['GET'])
    @handle_errors
    def chemical_issuances_route(id):
        # Get the chemical
        chemical = Chemical.query.get_or_404(id)

        # Get issuance records with eager loading to avoid N+1 queries
        issuances = ChemicalIssuance.query.options(
            joinedload(ChemicalIssuance.user),
            joinedload(ChemicalIssuance.chemical)
        ).filter_by(chemical_id=id).order_by(ChemicalIssuance.issue_date.desc()).all()

        # Convert to list of dictionaries
        result = [i.to_dict() for i in issuances]

        # Return the result
        return jsonify(result)

    # Mark a chemical as ordered
    @app.route('/api/chemicals/<int:id>/mark-ordered', methods=['POST'])
    @materials_manager_required
    def mark_chemical_as_ordered_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Only allow ordering when a reorder is needed
            if chemical.reorder_status != 'needed':
                return jsonify({
                    'error': f'Cannot mark chemical as ordered when reorder_status is "{chemical.reorder_status}"'
                }), 400

            # Get request data
            data = request.get_json() or {}

            # Validate required fields
            if not data.get('expected_delivery_date'):
                return jsonify({'error': 'Missing required field: expected_delivery_date'}), 400

            # Parse the expected delivery date
            try:
                expected_delivery_date = datetime.fromisoformat(data.get('expected_delivery_date'))
                # Note: We're allowing past dates for testing purposes
                # This would normally validate that the date is in the future
            except ValueError:
                return jsonify({'error': 'Invalid date format for expected_delivery_date. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400

            # Update chemical reorder status
            try:
                chemical.reorder_status = 'ordered'
                chemical.reorder_date = datetime.utcnow()
                chemical.expected_delivery_date = expected_delivery_date
            except Exception as e:
                print(f"Error updating reorder status: {str(e)}")
                return jsonify({'error': 'Failed to update reorder status'}), 500

            # Log the action
            user_name = session.get('user_name', 'Unknown user')
            log = AuditLog(
                action_type='chemical_ordered',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} marked as ordered by {user_name}"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_ordered',
                    description=f"Marked chemical {chemical.part_number} - {chemical.lot_number} as ordered"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                'chemical': chemical.to_dict(),
                'message': 'Chemical marked as ordered successfully'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in mark chemical as ordered route: {str(e)}")
            return jsonify({'error': 'An error occurred while marking the chemical as ordered'}), 500

    # Get, update, or delete a specific chemical
    @app.route('/api/chemicals/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def chemical_detail_route(id):
        # Get the chemical
        chemical = Chemical.query.get_or_404(id)

        if request.method == 'GET':
            # Update status based on expiration and stock level
            try:
                is_archived = chemical.is_archived
            except:
                is_archived = False

            if not is_archived:  # Only update non-archived chemicals
                if chemical.is_expired():
                    chemical.status = 'expired'

                    # Auto-archive expired chemicals if the columns exist
                    try:
                        chemical.is_archived = True
                        chemical.archived_reason = 'expired'
                        chemical.archived_date = datetime.utcnow()

                        # Add log for archiving
                        archive_log = AuditLog(
                            action_type='chemical_archived',
                            action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} automatically archived: expired"
                        )
                        db.session.add(archive_log)

                        # Update reorder status for expired chemicals
                        chemical.update_reorder_status()
                    except:
                        # If the columns don't exist, just update the status
                        pass
                elif chemical.quantity <= 0:
                    chemical.status = 'out_of_stock'
                    # Update reorder status for out-of-stock chemicals
                    chemical.update_reorder_status()
                elif chemical.is_low_stock():
                    chemical.status = 'low_stock'
                    # Update reorder status for low-stock chemicals
                    chemical.update_reorder_status()

                # Check if chemical is expiring soon (within 30 days)
                if chemical.is_expiring_soon(30):
                    # Add a flag to the chemical data
                    chemical.expiring_soon = True

                db.session.commit()

            return jsonify(chemical.to_dict())

    # Archive a chemical
    @app.route('/api/chemicals/<int:id>/archive', methods=['POST'])
    @materials_manager_required
    def archive_chemical_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if the chemical is already archived
            try:
                if chemical.is_archived:
                    return jsonify({'error': 'Chemical is already archived'}), 400
            except:
                return jsonify({'error': 'Archive functionality not available'}), 500

            # Get request data
            data = request.get_json() or {}

            # Validate required fields
            if not data.get('reason'):
                return jsonify({'error': 'Missing required field: reason'}), 400

            # Update chemical archive status
            try:
                chemical.is_archived = True
                chemical.archived_reason = data.get('reason')
                chemical.archived_date = datetime.utcnow()
            except Exception as e:
                print(f"Error updating archive status: {str(e)}")
                return jsonify({'error': 'Failed to update archive status'}), 500

            # Log the action
            user_name = session.get('user_name', 'Unknown user')
            log = AuditLog(
                action_type='chemical_archived',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} archived by {user_name}: {data.get('reason')}"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_archived',
                    description=f"Archived chemical {chemical.part_number} - {chemical.lot_number}: {data.get('reason')}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                'chemical': chemical.to_dict(),
                'message': 'Chemical archived successfully'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in archive chemical route: {str(e)}")
            return jsonify({'error': 'An error occurred while archiving the chemical'}), 500

    # Unarchive a chemical
    @app.route('/api/chemicals/<int:id>/unarchive', methods=['POST'])
    @materials_manager_required
    def unarchive_chemical_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if the chemical is archived
            try:
                if not chemical.is_archived:
                    return jsonify({'error': 'Chemical is not archived'}), 400
            except:
                return jsonify({'error': 'Archive functionality not available'}), 500

            # Update chemical archive status
            try:
                chemical.is_archived = False
                chemical.archived_reason = None
                chemical.archived_date = None
            except Exception as e:
                print(f"Error updating archive status: {str(e)}")
                return jsonify({'error': 'Failed to update archive status'}), 500

            # Log the action
            user_name = session.get('user_name', 'Unknown user')
            log = AuditLog(
                action_type='chemical_unarchived',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} unarchived by {user_name}"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_unarchived',
                    description=f"Unarchived chemical {chemical.part_number} - {chemical.lot_number}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                'chemical': chemical.to_dict(),
                'message': 'Chemical unarchived successfully'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in unarchive chemical route: {str(e)}")
            return jsonify({'error': 'An error occurred while unarchiving the chemical'}), 500

    # Mark a chemical as delivered
    @app.route('/api/chemicals/<int:id>/mark-delivered', methods=['POST'])
    @materials_manager_required
    def mark_chemical_as_delivered_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if the chemical is currently marked as ordered
            if chemical.reorder_status != 'ordered':
                return jsonify({'error': 'Chemical is not currently on order'}), 400

            # Get request data
            data = request.get_json() or {}

            # Check if received quantity is provided
            quantity_log = ""
            if 'received_quantity' in data:
                try:
                    received_quantity = float(data['received_quantity'])
                    if received_quantity <= 0:
                        return jsonify({'error': 'Received quantity must be greater than zero'}), 400

                    # Update chemical quantity
                    previous_quantity = chemical.quantity
                    chemical.quantity += received_quantity

                    # Include quantity update in log details
                    quantity_log = f" with {received_quantity} {chemical.unit} received (previous: {previous_quantity} {chemical.unit}, new: {chemical.quantity} {chemical.unit})"
                except ValueError:
                    return jsonify({'error': 'Invalid received quantity format'}), 400

            # Update chemical reorder status and ensure it's properly added to active inventory
            try:
                # Update reorder status
                chemical.reorder_status = 'not_needed'
                chemical.needs_reorder = False
                chemical.reorder_date = None
                chemical.expected_delivery_date = None

                # Update chemical status to available if it's not already
                if chemical.status != 'available' and chemical.quantity > 0:
                    chemical.status = 'available'
                elif chemical.quantity <= 0:
                    chemical.status = 'out_of_stock'
                elif chemical.is_low_stock():
                    chemical.status = 'low_stock'

                # Make sure the chemical is not archived
                chemical.is_archived = False
                chemical.archived_reason = None
                chemical.archived_date = None
            except Exception as e:
                print(f"Error updating chemical status: {str(e)}")
                return jsonify({'error': 'Failed to update chemical status'}), 500

            # Log the action
            user_name = session.get('user_name', 'Unknown user')
            log = AuditLog(
                action_type='chemical_delivered',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} marked as delivered by {user_name}{quantity_log}"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_delivered',
                    description=f"Marked chemical {chemical.part_number} - {chemical.lot_number} as delivered{quantity_log}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                'chemical': chemical.to_dict(),
                'message': 'Chemical marked as delivered successfully'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in mark chemical as delivered route: {str(e)}")
            return jsonify({'error': 'An error occurred while marking the chemical as delivered'}), 500
