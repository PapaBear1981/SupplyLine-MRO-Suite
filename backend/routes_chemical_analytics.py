from flask import request, jsonify
from models import db, Chemical, ChemicalIssuance, User, AuditLog, UserActivity
from datetime import datetime, timedelta
from auth import department_required
import traceback
from sqlalchemy import func


# Helper functions for part number analytics
def calculate_inventory_stats(chemicals):
    """Calculate inventory statistics for the given chemicals."""
    active_count = 0
    archived_count = 0
    current_inventory = 0
    lot_numbers = set()

    for c in chemicals:
        try:
            is_archived = getattr(c, 'is_archived', False)
            if is_archived:
                archived_count += 1
            else:
                active_count += 1
                current_inventory += getattr(c, 'quantity', 0)

            # Collect unique lot numbers
            if c.lot_number:
                lot_numbers.add(c.lot_number)
        except Exception as e:
            print(f"Error processing chemical {c.id}: {str(e)}")
            # Log the full error with traceback for better debugging
            print(traceback.format_exc())
            # Consider if continuing with default values is appropriate
            active_count += 1  # Default to active
            current_inventory += getattr(c, 'quantity', 0)

    # Convert set back to list before returning
    lot_numbers = list(lot_numbers)
    total_count = active_count + archived_count

    return {
        'total_count': total_count,
        'active_count': active_count,
        'archived_count': archived_count,
        'current_inventory': current_inventory,
        'lot_numbers': lot_numbers
    }


def calculate_usage_stats(part_number, max_results=1000):
    """Calculate usage statistics for the given part number."""
    # Get issuances for this part number with pagination
    # Consider adding time filtering for large datasets
    issuances = db.session.query(ChemicalIssuance).join(
        Chemical, ChemicalIssuance.chemical_id == Chemical.id
    ).filter(
        Chemical.part_number == part_number
    ).order_by(
        ChemicalIssuance.issue_date.desc()
    ).limit(max_results).all()

    # Calculate total issued
    total_issued = sum(i.quantity for i in issuances)

    # Usage by location
    locations = {}
    for i in issuances:
        loc = getattr(i, 'hangar', 'Unknown')
        if loc not in locations:
            locations[loc] = 0
        locations[loc] += i.quantity

    location_list = [{'location': loc, 'quantity': qty} for loc, qty in locations.items()]

    # Usage by user - optimize to avoid N+1 query problem
    users = {}
    user_names = {}

    # Get all relevant user IDs first
    user_ids = set(i.user_id for i in issuances)

    # Fetch all users in a single query
    all_users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {user.id: user.name for user in all_users}

    for i in issuances:
        user_id = i.user_id
        if user_id not in users:
            users[user_id] = 0
            # Use the preloaded user information
            user_names[user_id] = user_dict.get(user_id, f"User {user_id}")
        users[user_id] += i.quantity

    user_list = [
        {'user': user_names.get(user_id, f"User {user_id}"), 'quantity': qty}
        for user_id, qty in users.items()
    ]

    # Usage over time
    time_data = {}
    for i in issuances:
        month = i.issue_date.strftime('%Y-%m')
        if month not in time_data:
            time_data[month] = 0
        time_data[month] += i.quantity

    # Sort time data chronologically
    sorted_months = sorted(time_data.keys())
    time_list = [{'month': month, 'quantity': time_data[month]} for month in sorted_months]

    return {
        'total_issued': total_issued,
        'by_location': location_list,
        'by_user': user_list,
        'over_time': time_list
    }


def calculate_waste_stats(chemicals):
    """Calculate waste statistics for the given chemicals."""
    expired_count = 0
    depleted_count = 0
    other_archived_count = 0
    archived_count = 0

    for c in chemicals:
        try:
            is_archived = getattr(c, 'is_archived', False)
            if is_archived:
                archived_count += 1
                archived_reason = getattr(c, 'archived_reason', '').lower()
                # Use more defined categories with broader matching patterns
                if any(term in archived_reason for term in ['expir', 'outdated', 'past date']):
                    expired_count += 1
                elif any(term in archived_reason for term in ['deplet', 'empty', 'used up', 'consumed', 'exhausted']):
                    depleted_count += 1
                else:
                    other_archived_count += 1
        except Exception as e:
            print(f"Error processing waste stats for chemical {c.id}: {str(e)}")
            print(traceback.format_exc())

    # Calculate waste percentage (expired items as percentage of total archived)
    waste_percentage = 0
    if archived_count > 0:
        waste_percentage = (expired_count / archived_count) * 100

    return {
        'expired_count': expired_count,
        'depleted_count': depleted_count,
        'other_archived_count': other_archived_count,
        'waste_percentage': round(waste_percentage, 1)
    }


def calculate_shelf_life_stats(chemicals):
    """Calculate shelf life statistics for a list of chemicals."""
    shelf_life_days_list = []
    used_life_days_list = []
    usage_percentage_list = []

    for c in chemicals:
        try:
            # Skip chemicals without expiration date
            if not c.expiration_date:
                continue

            # Calculate shelf life in days
            shelf_life_days = (c.expiration_date - c.date_added).days
            if shelf_life_days <= 0:
                continue  # Skip invalid shelf life

            shelf_life_days_list.append(shelf_life_days)

            # For archived chemicals, calculate used life
            is_archived = getattr(c, 'is_archived', False)
            if is_archived:
                archived_date = getattr(c, 'archived_date', None)
                if archived_date:
                    used_life_days = (archived_date - c.date_added).days
                    used_life_days_list.append(used_life_days)

                    # Calculate usage percentage
                    usage_percentage = (used_life_days / shelf_life_days) * 100
                    usage_percentage_list.append(usage_percentage)
        except Exception as e:
            import traceback
            print(f"Error processing shelf life stats for chemical {c.id}: {str(e)}")
            print(traceback.format_exc())

    # Calculate averages
    results = {
        'avg_shelf_life_days': 0,
        'avg_used_life_days': 0,
        'avg_usage_percentage': 0,
    }

    if shelf_life_days_list:
        results['avg_shelf_life_days'] = sum(shelf_life_days_list) / len(shelf_life_days_list)

    if used_life_days_list:
        results['avg_used_life_days'] = sum(used_life_days_list) / len(used_life_days_list)

    if usage_percentage_list:
        results['avg_usage_percentage'] = sum(usage_percentage_list) / len(usage_percentage_list)

    return results

# Decorator to check if user is admin or in Materials department
materials_manager_required = department_required('Materials')

def register_chemical_analytics_routes(app):
    # Get waste analytics
    @app.route('/api/chemicals/waste-analytics', methods=['GET'])
    @materials_manager_required
    def waste_analytics_route():
        try:
            # Helper function to categorize waste based on archived reason
            def categorize_waste(archived_reason):
                """Categorize waste based on archived reason."""
                archived_reason = archived_reason.lower() if archived_reason else ""
                if any(term in archived_reason for term in ['expir', 'outdated', 'past date']):
                    return 'expired'
                elif any(term in archived_reason for term in ['deplet', 'empty', 'used up', 'consumed', 'exhausted']):
                    return 'depleted'
                else:
                    return 'other'

            # Helper function to group chemicals by a dimension
            def group_by_dimension(chemicals, dimension_getter, dimension_name_default='Unknown'):
                """
                Group chemicals by a dimension (category, location, part_number)

                Args:
                    chemicals: List of chemicals
                    dimension_getter: Function to extract dimension value from a chemical
                    dimension_name_default: Default value if dimension is None

                Returns:
                    Dictionary of dimension values to stats
                """
                result = {}
                for chemical in chemicals:
                    dimension_value = dimension_getter(chemical) or dimension_name_default
                    if dimension_value not in result:
                        result[dimension_value] = {'total': 0, 'expired': 0, 'depleted': 0, 'other': 0}

                    result[dimension_value]['total'] += 1

                    waste_category = categorize_waste(getattr(chemical, 'archived_reason', ''))
                    result[dimension_value][waste_category] += 1

                return result

            # Helper function to convert dictionary to list for response
            def dict_to_list(data_dict, key_name):
                """Convert a dictionary to a list of dictionaries with the key as a named field."""
                return [
                    {key_name: key, **stats}
                    for key, stats in data_dict.items()
                ]

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

            # Build query for archived chemicals
            query = Chemical.query.filter(Chemical.is_archived)

            # Apply date filter based on archived_date
            query = query.filter(Chemical.archived_date >= start_date, Chemical.archived_date <= end_date)

            # Apply part number filter if provided
            if part_number:
                query = query.filter(Chemical.part_number == part_number)

            # Execute query
            archived_chemicals = query.all()

            # Calculate summary statistics
            total_archived = len(archived_chemicals)
            expired_count = 0
            depleted_count = 0
            other_count = 0

            # Categorize archived chemicals by reason
            for chemical in archived_chemicals:
                category = categorize_waste(getattr(chemical, 'archived_reason', ''))
                if category == 'expired':
                    expired_count += 1
                elif category == 'depleted':
                    depleted_count += 1
                else:
                    other_count += 1

            # Group by different dimensions
            categories = group_by_dimension(archived_chemicals, lambda c: c.category, 'Uncategorized')
            locations = group_by_dimension(archived_chemicals, lambda c: c.location, 'Unknown')
            part_numbers = group_by_dimension(archived_chemicals, lambda c: c.part_number, 'Unknown')

            # Group by time (month)
            time_data = {}
            for chemical in archived_chemicals:
                month = chemical.archived_date.strftime('%Y-%m')
                if month not in time_data:
                    time_data[month] = {'expired': 0, 'depleted': 0, 'other': 0}

                waste_category = categorize_waste(getattr(chemical, 'archived_reason', ''))
                time_data[month][waste_category] += 1

            # Convert dictionaries to lists for the response
            waste_by_category = dict_to_list(categories, 'category')
            waste_by_location = dict_to_list(locations, 'location')
            waste_by_part_number = dict_to_list(part_numbers, 'part_number')

            # Sort time data chronologically
            sorted_months = sorted(time_data.keys())
            waste_over_time = [
                {'month': month, **time_data[month]}
                for month in sorted_months
            ]

            # Return the analytics data
            return jsonify({
                'timeframe': timeframe,
                'part_number_filter': part_number,
                'total_archived': total_archived,
                'expired_count': expired_count,
                'depleted_count': depleted_count,
                'other_count': other_count,
                'waste_by_category': waste_by_category,
                'waste_by_location': waste_by_location,
                'waste_by_part_number': waste_by_part_number,
                'waste_over_time': waste_over_time,
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

            # Get all chemicals with this part number (both active and archived)
            all_chemicals = Chemical.query.filter(Chemical.part_number == part_number).all()

            if not all_chemicals:
                return jsonify({'error': f'No chemicals found with part number {part_number}'}), 404

            # Calculate all statistics using helper functions
            inventory_stats = calculate_inventory_stats(all_chemicals)
            usage_stats = calculate_usage_stats(part_number)
            waste_stats = calculate_waste_stats(all_chemicals)
            shelf_life_stats = calculate_shelf_life_stats(all_chemicals)

            # Extract lot numbers from inventory stats
            lot_numbers = inventory_stats.pop('lot_numbers', [])

            # Return analytics data with real calculations
            return jsonify({
                'part_number': part_number,
                'inventory_stats': inventory_stats,
                'usage_stats': usage_stats,
                'waste_stats': waste_stats,
                'shelf_life_stats': {
                    'detailed_data': [],  # Simplified for now
                    # Use consistent rounding for all shelf life stats (1 decimal place)
                    'avg_shelf_life_days': round(shelf_life_stats['avg_shelf_life_days'], 1),
                    'avg_used_life_days': round(shelf_life_stats['avg_used_life_days'], 1),
                    'avg_usage_percentage': round(shelf_life_stats['avg_usage_percentage'], 1)
                },
                'lot_numbers': lot_numbers
            })
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in part analytics route: {str(e)}")
            print(f"Traceback: {error_traceback}")
            return jsonify({'error': 'An error occurred while generating part analytics', 'details': str(e)}), 500

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
