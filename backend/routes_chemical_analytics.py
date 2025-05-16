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

def register_chemical_analytics_routes(app):
    # Debug endpoint to test chemical analytics API
    @app.route('/api/debug/chemical-analytics-test', methods=['GET'])
    def chemical_analytics_debug_test_route():
        return jsonify({
            'status': 'success',
            'message': 'Chemical Analytics API is working',
            'timestamp': datetime.now().isoformat()
        })

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

            # Get active and archived chemicals
            active_chemicals = [c for c in all_chemicals if not c.is_archived]
            archived_chemicals = [c for c in all_chemicals if c.is_archived]

            # Calculate inventory stats
            total_count = len(all_chemicals)
            active_count = len(active_chemicals)
            archived_count = len(archived_chemicals)
            current_inventory = sum(c.quantity if hasattr(c, 'quantity') else 0 for c in active_chemicals)

            # Get all issuances for this part number within the timeframe
            issuances = db.session.query(ChemicalIssuance).join(
                Chemical, ChemicalIssuance.chemical_id == Chemical.id
            ).filter(
                Chemical.part_number == part_number,
                ChemicalIssuance.issue_date >= start_date,
                ChemicalIssuance.issue_date <= end_date
            ).all()

            # Calculate total issued quantity
            total_issued = sum(i.quantity for i in issuances)

            # Calculate usage by location
            usage_by_location = {}
            for issuance in issuances:
                location = issuance.location or 'Unknown'
                if location not in usage_by_location:
                    usage_by_location[location] = 0
                usage_by_location[location] += issuance.quantity

            usage_by_location_list = [
                {'location': loc, 'quantity': qty}
                for loc, qty in usage_by_location.items()
            ]
            usage_by_location_list.sort(key=lambda x: x['quantity'], reverse=True)

            # Calculate usage by user
            usage_by_user = {}
            for issuance in issuances:
                user = User.query.get(issuance.user_id)
                user_name = f"{user.first_name} {user.last_name}" if user else f"User {issuance.user_id}"
                if user_name not in usage_by_user:
                    usage_by_user[user_name] = 0
                usage_by_user[user_name] += issuance.quantity

            usage_by_user_list = [
                {'user': user, 'quantity': qty}
                for user, qty in usage_by_user.items()
            ]
            usage_by_user_list.sort(key=lambda x: x['quantity'], reverse=True)

            # Calculate usage over time (by month)
            usage_over_time = {}
            for issuance in issuances:
                month_key = issuance.issue_date.strftime('%Y-%m')
                if month_key not in usage_over_time:
                    usage_over_time[month_key] = 0
                usage_over_time[month_key] += issuance.quantity

            usage_over_time_list = [
                {'month': month, 'quantity': qty}
                for month, qty in usage_over_time.items()
            ]
            usage_over_time_list.sort(key=lambda x: x['month'])

            # Calculate average monthly usage
            if usage_over_time_list:
                avg_monthly_usage = total_issued / len(usage_over_time_list)
            else:
                avg_monthly_usage = 0

            # Calculate projected depletion days
            projected_depletion_days = None
            if avg_monthly_usage > 0:
                daily_usage = avg_monthly_usage / 30  # Approximate days in a month
                if daily_usage > 0:
                    projected_depletion_days = round(current_inventory / daily_usage)

            # Calculate efficiency stats
            efficiency_data = []
            for chemical in archived_chemicals:
                if chemical.archived_reason == 'depleted':
                    # Get all issuances for this specific chemical
                    chem_issuances = ChemicalIssuance.query.filter(
                        ChemicalIssuance.chemical_id == chemical.id
                    ).all()

                    total_issued = sum(i.quantity for i in chem_issuances)

                    # Calculate days to deplete
                    if chemical.date_added and chemical.archived_date:
                        days_to_deplete = (chemical.archived_date - chemical.date_added).days
                        daily_usage_rate = total_issued / days_to_deplete if days_to_deplete > 0 else 0
                    else:
                        days_to_deplete = None
                        daily_usage_rate = 0

                    efficiency_data.append({
                        'lot_number': chemical.lot_number,
                        'original_quantity': chemical.original_quantity,
                        'total_issued': total_issued,
                        'days_to_deplete': days_to_deplete,
                        'daily_usage_rate': daily_usage_rate
                    })

            # Return the analytics data
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
                    'by_location': usage_by_location_list,
                    'by_user': usage_by_user_list,
                    'over_time': usage_over_time_list,
                    'avg_monthly_usage': avg_monthly_usage,
                    'projected_depletion_days': projected_depletion_days
                },
                'efficiency_stats': {
                    'usage_efficiency_data': efficiency_data
                }
            })
        except Exception as e:
            print(f"Error in usage analytics route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating usage analytics'}), 500
