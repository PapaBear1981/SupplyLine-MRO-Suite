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
                        except:
                            # If the columns don't exist, just update the status
                            pass
                    elif chemical.is_low_stock():
                        chemical.status = 'low_stock'
                    elif chemical.quantity <= 0:
                        chemical.status = 'out_of_stock'
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
                    except:
                        # If the columns don't exist, just update the status
                        pass
                elif chemical.is_low_stock():
                    chemical.status = 'low_stock'
                elif chemical.quantity <= 0:
                    chemical.status = 'out_of_stock'
                db.session.commit()

            return jsonify(chemical.to_dict())

        # For PUT and DELETE, check permissions
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Materials management privileges required'}), 403

        if request.method == 'PUT':
            try:
                data = request.get_json() or {}

                # Update fields
                if 'part_number' in data:
                    chemical.part_number = data['part_number']
                if 'lot_number' in data:
                    chemical.lot_number = data['lot_number']
                if 'description' in data:
                    chemical.description = data['description']
                if 'manufacturer' in data:
                    chemical.manufacturer = data['manufacturer']
                if 'quantity' in data:
                    chemical.quantity = data['quantity']
                if 'unit' in data:
                    chemical.unit = data['unit']
                if 'location' in data:
                    chemical.location = data['location']
                if 'category' in data:
                    chemical.category = data['category']
                if 'status' in data:
                    chemical.status = data['status']
                if 'expiration_date' in data and data['expiration_date']:
                    chemical.expiration_date = datetime.fromisoformat(data['expiration_date'])
                if 'minimum_stock_level' in data:
                    chemical.minimum_stock_level = data['minimum_stock_level']
                if 'notes' in data:
                    chemical.notes = data['notes']

                # Log the action
                log = AuditLog(
                    action_type='chemical_updated',
                    action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} updated"
                )
                db.session.add(log)

                # Log user activity
                if 'user_id' in session:
                    activity = UserActivity(
                        user_id=session['user_id'],
                        activity_type='chemical_updated',
                        description=f"Updated chemical {chemical.part_number} - {chemical.lot_number}"
                    )
                    db.session.add(activity)

                db.session.commit()

                return jsonify(chemical.to_dict())
            except Exception as e:
                db.session.rollback()
                print(f"Error in update chemical route: {str(e)}")
                return jsonify({'error': 'An error occurred while updating the chemical'}), 500

        if request.method == 'DELETE':
            try:
                # Log the action
                log = AuditLog(
                    action_type='chemical_deleted',
                    action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} deleted"
                )
                db.session.add(log)

                # Log user activity
                if 'user_id' in session:
                    activity = UserActivity(
                        user_id=session['user_id'],
                        activity_type='chemical_deleted',
                        description=f"Deleted chemical {chemical.part_number} - {chemical.lot_number}"
                    )
                    db.session.add(activity)

                db.session.delete(chemical)
                db.session.commit()

                return jsonify({'message': 'Chemical deleted successfully'})
            except Exception as e:
                db.session.rollback()
                print(f"Error in delete chemical route: {str(e)}")
                return jsonify({'error': 'An error occurred while deleting the chemical'}), 500

    # Issue a chemical to a hangar
    @app.route('/api/chemicals/<int:id>/issue', methods=['POST'])
    @materials_manager_required
    def issue_chemical_route(id):
        try:
            chemical = Chemical.query.get_or_404(id)
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['quantity', 'hangar', 'user_id']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Check if quantity is valid
            quantity = float(data['quantity'])
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400

            if quantity > chemical.quantity:
                return jsonify({'error': 'Not enough quantity available'}), 400

            # Check if user exists
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Create issuance record
            issuance = ChemicalIssuance(
                chemical_id=id,
                user_id=data['user_id'],
                quantity=quantity,
                hangar=data['hangar'],
                purpose=data.get('purpose')
            )

            # Update chemical quantity
            chemical.quantity -= quantity

            # Update status if needed
            if chemical.quantity <= 0:
                chemical.status = 'out_of_stock'
                # Auto-archive depleted chemicals if the columns exist
                try:
                    chemical.is_archived = True
                    chemical.archived_reason = 'depleted'
                    chemical.archived_date = datetime.utcnow()

                    # Add additional log for archiving
                    archive_log = AuditLog(
                        action_type='chemical_archived',
                        action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} automatically archived: depleted"
                    )
                    db.session.add(archive_log)
                except:
                    # If the columns don't exist, just update the status
                    pass
            elif chemical.is_low_stock():
                chemical.status = 'low_stock'

            db.session.add(issuance)

            # Log the action
            log = AuditLog(
                action_type='chemical_issued',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} issued to {data['hangar']}"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_issued',
                    description=f"Issued {quantity} {chemical.unit} of {chemical.part_number} to {data['hangar']}"
                )
                db.session.add(activity)

            db.session.commit()

            return jsonify({
                'message': 'Chemical issued successfully',
                'chemical': chemical.to_dict(),
                'issuance': issuance.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in issue chemical route: {str(e)}")
            return jsonify({'error': 'An error occurred while issuing the chemical'}), 500

    # Get issuance history for a chemical
    @app.route('/api/chemicals/<int:id>/issuances', methods=['GET'])
    def chemical_issuances_route(id):
        try:
            # Check if chemical exists
            chemical = Chemical.query.get_or_404(id)

            # Get issuances
            issuances = ChemicalIssuance.query.filter_by(chemical_id=id).order_by(ChemicalIssuance.issue_date.desc()).all()

            return jsonify([i.to_dict() for i in issuances])
        except Exception as e:
            print(f"Error in chemical issuances route: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching issuances'}), 500

    # Get all issuances
    @app.route('/api/issuances', methods=['GET'])
    @materials_manager_required
    def issuances_route():
        try:
            # Get query parameters
            chemical_id = request.args.get('chemical_id', type=int)
            user_id = request.args.get('user_id', type=int)
            hangar = request.args.get('hangar')

            # Start with base query
            query = ChemicalIssuance.query

            # Apply filters if provided
            if chemical_id:
                query = query.filter(ChemicalIssuance.chemical_id == chemical_id)
            if user_id:
                query = query.filter(ChemicalIssuance.user_id == user_id)
            if hangar:
                query = query.filter(ChemicalIssuance.hangar == hangar)

            # Execute query and convert to list of dictionaries
            issuances = query.order_by(ChemicalIssuance.issue_date.desc()).all()

            return jsonify([i.to_dict() for i in issuances])
        except Exception as e:
            print(f"Error in issuances route: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching issuances'}), 500

    # Archive a chemical
    @app.route('/api/chemicals/<int:id>/archive', methods=['POST'])
    @materials_manager_required
    def archive_chemical_route(id):
        try:
            chemical = Chemical.query.get_or_404(id)
            data = request.get_json() or {}

            # Validate required fields
            if 'reason' not in data:
                return jsonify({'error': 'Reason for archiving is required'}), 400

            # Check if already archived
            if chemical.is_archived:
                return jsonify({'error': 'Chemical is already archived'}), 400

            # Archive the chemical
            chemical.is_archived = True
            chemical.archived_reason = data['reason']
            chemical.archived_date = datetime.utcnow()

            # Log the action
            log = AuditLog(
                action_type='chemical_archived',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} archived: {data['reason']}"
            )
            db.session.add(log)

            # Log user activity
            if 'user_id' in session:
                activity = UserActivity(
                    user_id=session['user_id'],
                    activity_type='chemical_archived',
                    description=f"Archived chemical {chemical.part_number} - {chemical.lot_number}: {data['reason']}"
                )
                db.session.add(activity)

            db.session.commit()

            return jsonify({
                'message': 'Chemical archived successfully',
                'chemical': chemical.to_dict()
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
            chemical = Chemical.query.get_or_404(id)

            # Check if not archived
            if not chemical.is_archived:
                return jsonify({'error': 'Chemical is not archived'}), 400

            # Unarchive the chemical
            chemical.is_archived = False
            chemical.archived_reason = None
            chemical.archived_date = None

            # Log the action
            log = AuditLog(
                action_type='chemical_unarchived',
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} unarchived"
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

            return jsonify({
                'message': 'Chemical unarchived successfully',
                'chemical': chemical.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in unarchive chemical route: {str(e)}")
            return jsonify({'error': 'An error occurred while unarchiving the chemical'}), 500

    # Get archived chemicals
    @app.route('/api/chemicals/archived', methods=['GET'])
    @materials_manager_required
    def archived_chemicals_route():
        try:
            # Get query parameters for filtering
            category = request.args.get('category')
            reason = request.args.get('reason')
            search = request.args.get('q')

            # Start with base query for archived chemicals
            try:
                query = Chemical.query.filter(Chemical.is_archived == True)
            except:
                # If the column doesn't exist, return an empty list
                return jsonify([])

            # Apply filters if provided
            if category:
                query = query.filter(Chemical.category == category)
            if reason:
                query = query.filter(Chemical.archived_reason.ilike(f'%{reason}%'))
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
            chemicals = query.order_by(Chemical.archived_date.desc()).all()
            result = [c.to_dict() for c in chemicals]

            return jsonify(result)
        except Exception as e:
            print(f"Error in archived chemicals route: {str(e)}")
            return jsonify({'error': 'An error occurred while fetching archived chemicals'}), 500

    # Get waste analytics
    @app.route('/api/chemicals/waste-analytics', methods=['GET'])
    @materials_manager_required
    def waste_analytics_route():
        try:
            # Get query parameters
            timeframe = request.args.get('timeframe', 'month')  # week, month, quarter, year, all
            part_number = request.args.get('part_number')  # Optional part number filter

            # Determine date range based on timeframe
            end_date = datetime.utcnow()
            if timeframe == 'week':
                start_date = end_date - timedelta(days=7)
            elif timeframe == 'month':
                start_date = end_date - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif timeframe == 'year':
                start_date = end_date - timedelta(days=365)
            else:  # 'all'
                start_date = datetime(1970, 1, 1)  # Beginning of time

            # Query archived chemicals within the timeframe
            try:
                query = Chemical.query.filter(
                    Chemical.is_archived == True,
                    Chemical.archived_date >= start_date,
                    Chemical.archived_date <= end_date
                )

                # Apply part number filter if provided
                if part_number:
                    query = query.filter(Chemical.part_number == part_number)

                archived_chemicals = query.all()
            except:
                # If the columns don't exist, return empty data
                archived_chemicals = []

            # Calculate waste metrics
            total_archived = len(archived_chemicals)
            expired_count = sum(1 for c in archived_chemicals if c.archived_reason == 'expired')
            depleted_count = sum(1 for c in archived_chemicals if c.archived_reason == 'depleted')
            other_count = total_archived - expired_count - depleted_count

            # Calculate waste by category
            waste_by_category = {}
            for chemical in archived_chemicals:
                category = chemical.category or 'Uncategorized'
                if category not in waste_by_category:
                    waste_by_category[category] = {
                        'total': 0,
                        'expired': 0,
                        'depleted': 0,
                        'other': 0
                    }

                waste_by_category[category]['total'] += 1

                if chemical.archived_reason == 'expired':
                    waste_by_category[category]['expired'] += 1
                elif chemical.archived_reason == 'depleted':
                    waste_by_category[category]['depleted'] += 1
                else:
                    waste_by_category[category]['other'] += 1

            # Format waste by category for response
            waste_by_category_list = [
                {
                    'category': category,
                    'total': data['total'],
                    'expired': data['expired'],
                    'depleted': data['depleted'],
                    'other': data['other']
                }
                for category, data in waste_by_category.items()
            ]

            # Sort by total count descending
            waste_by_category_list.sort(key=lambda x: x['total'], reverse=True)

            # Calculate waste over time (by month)
            waste_over_time = {}
            for chemical in archived_chemicals:
                month_key = chemical.archived_date.strftime('%Y-%m')
                if month_key not in waste_over_time:
                    waste_over_time[month_key] = {
                        'month': month_key,
                        'total': 0,
                        'expired': 0,
                        'depleted': 0,
                        'other': 0
                    }

                waste_over_time[month_key]['total'] += 1

                if chemical.archived_reason == 'expired':
                    waste_over_time[month_key]['expired'] += 1
                elif chemical.archived_reason == 'depleted':
                    waste_over_time[month_key]['depleted'] += 1
                else:
                    waste_over_time[month_key]['other'] += 1

            # Format waste over time for response
            waste_over_time_list = list(waste_over_time.values())

            # Sort by month
            waste_over_time_list.sort(key=lambda x: x['month'])

            # Calculate waste by location
            waste_by_location = {}
            for chemical in archived_chemicals:
                location = chemical.location or 'Unknown'
                if location not in waste_by_location:
                    waste_by_location[location] = {
                        'total': 0,
                        'expired': 0,
                        'depleted': 0,
                        'other': 0
                    }

                waste_by_location[location]['total'] += 1

                if chemical.archived_reason == 'expired':
                    waste_by_location[location]['expired'] += 1
                elif chemical.archived_reason == 'depleted':
                    waste_by_location[location]['depleted'] += 1
                else:
                    waste_by_location[location]['other'] += 1

            # Format waste by location for response
            waste_by_location_list = [
                {
                    'location': location,
                    'total': data['total'],
                    'expired': data['expired'],
                    'depleted': data['depleted'],
                    'other': data['other']
                }
                for location, data in waste_by_location.items()
            ]

            # Sort by total count descending
            waste_by_location_list.sort(key=lambda x: x['total'], reverse=True)

            # Calculate waste by part number
            waste_by_part_number = {}
            for chemical in archived_chemicals:
                part_num = chemical.part_number
                if part_num not in waste_by_part_number:
                    waste_by_part_number[part_num] = {
                        'part_number': part_num,
                        'total': 0,
                        'expired': 0,
                        'depleted': 0,
                        'other': 0
                    }

                waste_by_part_number[part_num]['total'] += 1

                if chemical.archived_reason == 'expired':
                    waste_by_part_number[part_num]['expired'] += 1
                elif chemical.archived_reason == 'depleted':
                    waste_by_part_number[part_num]['depleted'] += 1
                else:
                    waste_by_part_number[part_num]['other'] += 1

            # Format waste by part number for response
            waste_by_part_number_list = list(waste_by_part_number.values())

            # Sort by total count descending
            waste_by_part_number_list.sort(key=lambda x: x['total'], reverse=True)

            # Calculate average shelf life for expired chemicals
            shelf_life_data = []
            for chemical in archived_chemicals:
                if chemical.archived_reason == 'expired' and chemical.date_added and chemical.expiration_date:
                    # Calculate shelf life in days
                    shelf_life = (chemical.expiration_date - chemical.date_added).days
                    # Calculate how much of shelf life was used
                    if chemical.archived_date:
                        used_life = (chemical.archived_date - chemical.date_added).days
                        usage_percentage = (used_life / shelf_life) * 100 if shelf_life > 0 else 0
                    else:
                        used_life = 0
                        usage_percentage = 0

                    shelf_life_data.append({
                        'part_number': chemical.part_number,
                        'lot_number': chemical.lot_number,
                        'shelf_life_days': shelf_life,
                        'used_life_days': used_life,
                        'usage_percentage': round(usage_percentage, 2)
                    })

            # Calculate average shelf life by part number
            avg_shelf_life_by_part = {}
            for item in shelf_life_data:
                part_num = item['part_number']
                if part_num not in avg_shelf_life_by_part:
                    avg_shelf_life_by_part[part_num] = {
                        'part_number': part_num,
                        'total_items': 0,
                        'total_shelf_life': 0,
                        'total_used_life': 0,
                        'avg_shelf_life': 0,
                        'avg_used_life': 0,
                        'avg_usage_percentage': 0
                    }

                avg_shelf_life_by_part[part_num]['total_items'] += 1
                avg_shelf_life_by_part[part_num]['total_shelf_life'] += item['shelf_life_days']
                avg_shelf_life_by_part[part_num]['total_used_life'] += item['used_life_days']

            # Calculate averages
            for part_num, data in avg_shelf_life_by_part.items():
                if data['total_items'] > 0:
                    data['avg_shelf_life'] = round(data['total_shelf_life'] / data['total_items'], 2)
                    data['avg_used_life'] = round(data['total_used_life'] / data['total_items'], 2)
                    data['avg_usage_percentage'] = round((data['avg_used_life'] / data['avg_shelf_life']) * 100 if data['avg_shelf_life'] > 0 else 0, 2)

            # Format for response
            avg_shelf_life_list = list(avg_shelf_life_by_part.values())

            # Sort by total items descending
            avg_shelf_life_list.sort(key=lambda x: x['total_items'], reverse=True)

            return jsonify({
                'timeframe': timeframe,
                'part_number_filter': part_number,
                'total_archived': total_archived,
                'expired_count': expired_count,
                'depleted_count': depleted_count,
                'other_count': other_count,
                'waste_by_category': waste_by_category_list,
                'waste_by_location': waste_by_location_list,
                'waste_by_part_number': waste_by_part_number_list,
                'waste_over_time': waste_over_time_list,
                'shelf_life_analytics': {
                    'detailed_data': shelf_life_data,
                    'averages_by_part_number': avg_shelf_life_list
                }
            })
        except Exception as e:
            print(f"Error in waste analytics route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating waste analytics'}), 500

    # Get part number analytics
    @app.route('/api/chemicals/part-analytics', methods=['GET'])
    @materials_manager_required
    def part_analytics_route():
        try:
            # Get query parameters
            part_number = request.args.get('part_number')

            # Part number is required
            if not part_number:
                return jsonify({'error': 'Part number is required'}), 400

            # Get all chemicals with this part number (both active and archived)
            all_chemicals = Chemical.query.filter(Chemical.part_number == part_number).all()

            if not all_chemicals:
                return jsonify({'error': f'No chemicals found with part number {part_number}'}), 404

            # Separate active and archived chemicals
            try:
                active_chemicals = [c for c in all_chemicals if not c.is_archived]
                archived_chemicals = [c for c in all_chemicals if c.is_archived]
            except:
                # If is_archived column doesn't exist
                active_chemicals = all_chemicals
                archived_chemicals = []

            # Basic statistics
            total_count = len(all_chemicals)
            active_count = len(active_chemicals)
            archived_count = len(archived_chemicals)

            # Calculate current inventory
            current_inventory = sum(c.quantity for c in active_chemicals)

            # Calculate usage statistics
            total_issued = 0
            usage_by_location = {}
            usage_by_user = {}
            usage_over_time = {}

            # Get all issuances for this part number
            issuances = db.session.query(ChemicalIssuance).join(
                Chemical, ChemicalIssuance.chemical_id == Chemical.id
            ).filter(
                Chemical.part_number == part_number
            ).all()

            for issuance in issuances:
                total_issued += issuance.quantity

                # Usage by location (hangar)
                location = issuance.hangar
                if location not in usage_by_location:
                    usage_by_location[location] = 0
                usage_by_location[location] += issuance.quantity

                # Usage by user
                user_id = issuance.user_id
                user_name = issuance.user.name if issuance.user else f"User {user_id}"
                if user_name not in usage_by_user:
                    usage_by_user[user_name] = 0
                usage_by_user[user_name] += issuance.quantity

                # Usage over time (by month)
                month_key = issuance.issue_date.strftime('%Y-%m')
                if month_key not in usage_over_time:
                    usage_over_time[month_key] = 0
                usage_over_time[month_key] += issuance.quantity

            # Format usage by location for response
            usage_by_location_list = [
                {'location': location, 'quantity': quantity}
                for location, quantity in usage_by_location.items()
            ]
            usage_by_location_list.sort(key=lambda x: x['quantity'], reverse=True)

            # Format usage by user for response
            usage_by_user_list = [
                {'user': user, 'quantity': quantity}
                for user, quantity in usage_by_user.items()
            ]
            usage_by_user_list.sort(key=lambda x: x['quantity'], reverse=True)

            # Format usage over time for response
            usage_over_time_list = [
                {'month': month, 'quantity': quantity}
                for month, quantity in usage_over_time.items()
            ]
            usage_over_time_list.sort(key=lambda x: x['month'])

            # Calculate waste statistics
            expired_count = sum(1 for c in archived_chemicals if c.archived_reason == 'expired')
            depleted_count = sum(1 for c in archived_chemicals if c.archived_reason == 'depleted')
            other_archived_count = archived_count - expired_count - depleted_count

            # Calculate waste percentage
            total_quantity = total_issued + current_inventory
            waste_percentage = (expired_count / total_count) * 100 if total_count > 0 else 0

            # Calculate average shelf life
            shelf_life_data = []
            for chemical in all_chemicals:
                if chemical.date_added and chemical.expiration_date:
                    # Calculate shelf life in days
                    shelf_life = (chemical.expiration_date - chemical.date_added).days

                    # For archived chemicals, calculate how much of shelf life was used
                    try:
                        if chemical.is_archived and chemical.archived_date:
                            used_life = (chemical.archived_date - chemical.date_added).days
                            usage_percentage = (used_life / shelf_life) * 100 if shelf_life > 0 else 0
                        else:
                            # For active chemicals, calculate current usage
                            now = datetime.utcnow()
                            used_life = (now - chemical.date_added).days
                            usage_percentage = (used_life / shelf_life) * 100 if shelf_life > 0 else 0
                    except:
                        # If archived columns don't exist
                        now = datetime.utcnow()
                        used_life = (now - chemical.date_added).days
                        usage_percentage = (used_life / shelf_life) * 100 if shelf_life > 0 else 0

                    shelf_life_data.append({
                        'lot_number': chemical.lot_number,
                        'shelf_life_days': shelf_life,
                        'used_life_days': used_life,
                        'usage_percentage': round(usage_percentage, 2),
                        'status': 'archived' if getattr(chemical, 'is_archived', False) else 'active',
                        'archived_reason': getattr(chemical, 'archived_reason', None)
                    })

            # Calculate averages
            avg_shelf_life = sum(item['shelf_life_days'] for item in shelf_life_data) / len(shelf_life_data) if shelf_life_data else 0
            avg_used_life = sum(item['used_life_days'] for item in shelf_life_data) / len(shelf_life_data) if shelf_life_data else 0
            avg_usage_percentage = sum(item['usage_percentage'] for item in shelf_life_data) / len(shelf_life_data) if shelf_life_data else 0

            # Get lot numbers for this part number
            lot_numbers = [c.lot_number for c in all_chemicals]

            # Return the analytics data
            return jsonify({
                'part_number': part_number,
                'inventory_stats': {
                    'total_count': total_count,
                    'active_count': active_count,
                    'archived_count': archived_count,
                    'current_inventory': current_inventory
                },
                'usage_stats': {
                    'total_issued': total_issued,
                    'by_location': usage_by_location_list,
                    'by_user': usage_by_user_list,
                    'over_time': usage_over_time_list
                },
                'waste_stats': {
                    'expired_count': expired_count,
                    'depleted_count': depleted_count,
                    'other_archived_count': other_archived_count,
                    'waste_percentage': round(waste_percentage, 2)
                },
                'shelf_life_stats': {
                    'detailed_data': shelf_life_data,
                    'avg_shelf_life_days': round(avg_shelf_life, 2),
                    'avg_used_life_days': round(avg_used_life, 2),
                    'avg_usage_percentage': round(avg_usage_percentage, 2)
                },
                'lot_numbers': lot_numbers
            })
        except Exception as e:
            print(f"Error in part analytics route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating part analytics'}), 500
