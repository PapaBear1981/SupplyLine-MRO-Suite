from flask import request, jsonify, session
from models import db, Chemical, ChemicalIssuance, User, AuditLog, UserActivity
from datetime import datetime, timedelta
from functools import wraps

# Decorator to check if user is admin or in Materials department
def materials_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Materials management privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def register_chemical_routes(app):
    # Get all chemicals
    @app.route('/api/chemicals', methods=['GET'])
    def chemicals_route():
        try:
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
                    query = query.filter(Chemical.is_archived == False)
            except:
                # If the column doesn't exist, we can't filter by it
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

            # Execute query and convert to list of dictionaries
            chemicals = query.all()
            result = [c.to_dict() for c in chemicals]

            # Update status based on expiration and stock level
            for chemical in chemicals:
                try:
                    is_archived = chemical.is_archived
                except:
                    is_archived = False

                if not is_archived:  # Only update status for non-archived chemicals
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

            return jsonify(result)
        except Exception as e:
            print(f"Error in chemicals route: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching chemicals'}), 500

    # Create a new chemical
    @app.route('/api/chemicals', methods=['POST'])
    @materials_manager_required
    def create_chemical_route():
        try:
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['part_number', 'lot_number', 'quantity', 'unit']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Create new chemical
            chemical = Chemical(
                part_number=data.get('part_number'),
                lot_number=data.get('lot_number'),
                description=data.get('description'),
                manufacturer=data.get('manufacturer'),
                quantity=data.get('quantity'),
                unit=data.get('unit'),
                location=data.get('location'),
                category=data.get('category', 'General'),
                status=data.get('status', 'available'),
                expiration_date=datetime.fromisoformat(data.get('expiration_date')) if data.get('expiration_date') else None,
                minimum_stock_level=data.get('minimum_stock_level'),
                notes=data.get('notes')
            )

            db.session.add(chemical)

            # Log the action
            log = AuditLog(
                action_type='chemical_added',
                action_details=f"Chemical {data.get('part_number')} - {data.get('lot_number')} added"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_added',
                    description=f"Added chemical {data.get('part_number')} - {data.get('lot_number')}"
                )
                db.session.add(activity)

            db.session.commit()

            return jsonify(chemical.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error in create chemical route: {str(e)}")
            return jsonify({'error': 'An error occurred while creating the chemical'}), 500

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
    def chemical_issue_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if chemical can be issued
            if chemical.status == 'expired':
                return jsonify({'error': 'Cannot issue an expired chemical'}), 400

            if chemical.quantity <= 0:
                return jsonify({'error': 'Cannot issue a chemical that is out of stock'}), 400

            # Get request data
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['quantity', 'hangar', 'user_id']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Validate quantity
            quantity = float(data.get('quantity'))
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be greater than zero'}), 400

            if quantity > chemical.quantity:
                return jsonify({'error': f'Cannot issue more than available quantity ({chemical.quantity} {chemical.unit})'}), 400

            # Create issuance record
            issuance = ChemicalIssuance(
                chemical_id=chemical.id,
                user_id=data.get('user_id'),
                quantity=quantity,
                hangar=data.get('hangar'),
                purpose=data.get('purpose')
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

            # Return updated chemical and issuance record
            return jsonify({
                'chemical': chemical.to_dict(),
                'issuance': issuance.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in chemical issue route: {str(e)}")
            return jsonify({'error': 'An error occurred while issuing the chemical'}), 500

    # Get issuance history for a chemical
    @app.route('/api/chemicals/<int:id>/issuances', methods=['GET'])
    def chemical_issuances_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Get issuance records
            issuances = ChemicalIssuance.query.filter_by(chemical_id=id).order_by(ChemicalIssuance.issue_date.desc()).all()

            # Convert to list of dictionaries
            result = [i.to_dict() for i in issuances]

            return jsonify(result)
        except Exception as e:
            print(f"Error in chemical issuances route: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching chemical issuances'}), 500

    # Mark a chemical as ordered
    @app.route('/api/chemicals/<int:id>/mark-ordered', methods=['POST'])
    @materials_manager_required
    def mark_chemical_as_ordered_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Get request data
            data = request.get_json() or {}

            # Validate required fields
            if not data.get('expected_delivery_date'):
                return jsonify({'error': 'Missing required field: expected_delivery_date'}), 400

            # Update chemical reorder status
            try:
                chemical.reorder_status = 'ordered'
                chemical.reorder_date = datetime.utcnow()
                chemical.expected_delivery_date = datetime.fromisoformat(data.get('expected_delivery_date'))
            except Exception as e:
                print(f"Error updating reorder status: {str(e)}")
                return jsonify({'error': 'Failed to update reorder status'}), 500

            # Log the action
            log = AuditLog(
                action_type='chemical_ordered',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} marked as ordered"
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

    # Mark a chemical as delivered
    @app.route('/api/chemicals/<int:id>/mark-delivered', methods=['POST'])
    @materials_manager_required
    def mark_chemical_as_delivered_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Update chemical reorder status
            try:
                chemical.reorder_status = 'not_needed'
                chemical.needs_reorder = False
                chemical.reorder_date = None
                chemical.expected_delivery_date = None
            except Exception as e:
                print(f"Error updating reorder status: {str(e)}")
                return jsonify({'error': 'Failed to update reorder status'}), 500

            # Log the action
            log = AuditLog(
                action_type='chemical_delivered',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} marked as delivered"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_delivered',
                    description=f"Marked chemical {chemical.part_number} - {chemical.lot_number} as delivered"
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
