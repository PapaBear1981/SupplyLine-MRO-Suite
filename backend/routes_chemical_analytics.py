from flask import request, jsonify, session
from models import db, Chemical, ChemicalIssuance, User, AuditLog, UserActivity
from datetime import datetime, timedelta
from functools import wraps

# Decorator to check if user is admin or in Materials department
def materials_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authentication check
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Check if user is admin or Materials department
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Materials management privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def register_chemical_analytics_routes(app):
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

            # Return simplified analytics data for debugging
            return jsonify({
                'timeframe': timeframe,
                'part_number_filter': part_number,
                'total_archived': 5,
                'expired_count': 2,
                'depleted_count': 2,
                'other_count': 1,
                'waste_by_category': [
                    {'category': 'Adhesives', 'count': 2},
                    {'category': 'Lubricants', 'count': 3}
                ],
                'waste_by_location': [
                    {'location': 'Hangar A', 'count': 3},
                    {'location': 'Hangar B', 'count': 2}
                ],
                'waste_by_part_number': [
                    {'part_number': 'Aeroshell 22', 'count': 2},
                    {'part_number': 'PR1422B1/2', 'count': 3}
                ],
                'waste_over_time': [
                    {'month': '2023-01', 'count': 2},
                    {'month': '2023-02', 'count': 3}
                ],
                'shelf_life_analytics': {
                    'detailed_data': [],
                    'averages_by_part_number': []
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

            # Return simplified analytics data for debugging
            return jsonify({
                'part_number': part_number,
                'inventory_stats': {
                    'total_count': 5,
                    'active_count': 3,
                    'archived_count': 2,
                    'current_inventory': 100
                },
                'usage_stats': {
                    'total_issued': 50,
                    'by_location': [
                        {'location': 'Hangar A', 'quantity': 30},
                        {'location': 'Hangar B', 'quantity': 20}
                    ],
                    'by_user': [
                        {'user': 'Test User', 'quantity': 50}
                    ],
                    'over_time': [
                        {'month': '2023-01', 'quantity': 25},
                        {'month': '2023-02', 'quantity': 25}
                    ]
                },
                'waste_stats': {
                    'expired_count': 1,
                    'depleted_count': 1,
                    'other_archived_count': 0,
                    'waste_percentage': 40.0
                },
                'shelf_life_stats': {
                    'detailed_data': [],
                    'avg_shelf_life_days': 365,
                    'avg_used_life_days': 180,
                    'avg_usage_percentage': 50.0
                },
                'lot_numbers': ['LOT123', 'LOT456', 'LOT789']
            })
        except Exception as e:
            print(f"Error in part analytics route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating part analytics'}), 500

    # Get usage analytics
    @app.route('/api/chemicals/usage-analytics', methods=['GET'])
    @materials_manager_required
    def chemical_usage_analytics_route():
        try:
            # Get query parameters
            timeframe = request.args.get('timeframe', 'month')  # week, month, quarter, year, all
            part_number = request.args.get('part_number')  # Required part number filter

            print(f"Usage analytics request received: part_number={part_number}, timeframe={timeframe}")

            # Part number is required
            if not part_number:
                return jsonify({'error': 'Part number is required'}), 400

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

            # Get all chemicals with this part number (both active and archived)
            all_chemicals = Chemical.query.filter(Chemical.part_number == part_number).all()

            if not all_chemicals:
                return jsonify({'error': f'No chemicals found with part number {part_number}'}), 404

            # SIMPLIFIED VERSION - Just return basic data to diagnose the issue
            # Count active and archived chemicals
            active_count = 0
            archived_count = 0
            current_inventory = 0

            for c in all_chemicals:
                try:
                    is_archived = getattr(c, 'is_archived', False)
                    if is_archived:
                        archived_count += 1
                    else:
                        active_count += 1
                        current_inventory += getattr(c, 'quantity', 0)
                except Exception as e:
                    print(f"Error processing chemical {c.id}: {str(e)}")
                    active_count += 1  # Default to active
                    current_inventory += getattr(c, 'quantity', 0)

            total_count = active_count + archived_count

            # Get basic issuance data
            try:
                issuances = db.session.query(ChemicalIssuance).join(
                    Chemical, ChemicalIssuance.chemical_id == Chemical.id
                ).filter(
                    Chemical.part_number == part_number,
                    ChemicalIssuance.issue_date >= start_date,
                    ChemicalIssuance.issue_date <= end_date
                ).all()

                total_issued = sum(i.quantity for i in issuances)

                # Basic location data
                locations = {}
                for i in issuances:
                    loc = getattr(i, 'hangar', 'Unknown')
                    if loc not in locations:
                        locations[loc] = 0
                    locations[loc] += i.quantity

                location_list = [{'location': loc, 'quantity': qty} for loc, qty in locations.items()]

                # Basic user data with actual user names
                users = {}
                user_names = {}

                for i in issuances:
                    user_id = i.user_id
                    if user_id not in users:
                        users[user_id] = 0
                        # Get the user's name from the database
                        user = User.query.get(user_id)
                        if user:
                            user_names[user_id] = f"{user.first_name} {user.last_name}"
                        else:
                            user_names[user_id] = f"User {user_id}"
                    users[user_id] += i.quantity

                user_list = [{'user': user_names.get(user_id, f"User {user_id}"), 'quantity': qty} for user_id, qty in users.items()]

                # Basic time data
                time_data = {}
                for i in issuances:
                    month = i.issue_date.strftime('%Y-%m')
                    if month not in time_data:
                        time_data[month] = 0
                    time_data[month] += i.quantity

                time_list = [{'month': month, 'quantity': qty} for month, qty in time_data.items()]

                # Calculate average monthly usage
                avg_monthly_usage = 0
                projected_depletion_days = None

                if issuances:
                    # Get the date range of issuances
                    if len(issuances) > 0:
                        earliest_date = min(i.issue_date for i in issuances)
                        latest_date = max(i.issue_date for i in issuances)

                        # Calculate the number of months between earliest and latest issuance
                        months_diff = (latest_date.year - earliest_date.year) * 12 + (latest_date.month - earliest_date.month)
                        months_diff = max(1, months_diff)  # Ensure at least 1 month to avoid division by zero

                        # Calculate average monthly usage
                        avg_monthly_usage = total_issued / months_diff

                        # Calculate projected depletion time in days
                        if avg_monthly_usage > 0:
                            projected_depletion_days = int((current_inventory / avg_monthly_usage) * 30)
                        else:
                            projected_depletion_days = None

            except Exception as e:
                print(f"Error processing issuances: {str(e)}")
                issuances = []
                total_issued = 0
                location_list = []
                user_list = []
                time_list = []
                avg_monthly_usage = 0
                projected_depletion_days = None

            # Return analytics data with real calculations
            return jsonify({
                'timeframe': timeframe,
                'part_number': part_number,
                'inventory_stats': {
                    'total_count': total_count,
                    'active_count': active_count,
                    'archived_count': archived_count,
                    'current_inventory': current_inventory
                },
                'usage_stats': {
                    'total_issued': total_issued,
                    'by_location': location_list,
                    'by_user': user_list,
                    'over_time': time_list,
                    'avg_monthly_usage': round(avg_monthly_usage, 2),  # Rounded to 2 decimal places
                    'projected_depletion_days': projected_depletion_days
                },
                'efficiency_stats': {
                    'usage_efficiency_data': []  # Simplified
                }
            })
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error in usage analytics route: {str(e)}")
            print(f"Traceback: {error_traceback}")
            return jsonify({'error': 'An error occurred while generating usage analytics', 'details': str(e)}), 500
