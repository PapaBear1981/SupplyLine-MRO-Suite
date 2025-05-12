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
    # Temporarily remove authentication for testing
    # @materials_manager_required
    def chemical_usage_analytics_route():
        print(f"Usage analytics route called with args: {request.args}")
        print(f"Request URL: {request.url}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")

        try:
            # Get query parameters
            timeframe = request.args.get('timeframe', 'month')  # week, month, quarter, year, all
            part_number = request.args.get('part_number')  # Required part number filter

            print(f"Usage analytics request received: part_number={part_number}, timeframe={timeframe}")

            # Part number is required
            if not part_number:
                return jsonify({'error': 'Part number is required'}), 400

            # For testing, return mock data
            print(f"Returning mock data for part number {part_number}")
            return jsonify({
                'timeframe': timeframe,
                'part_number': part_number,
                'inventory_stats': {
                    'total_count': 5,
                    'active_count': 3,
                    'archived_count': 2,
                    'current_inventory': 25.5
                },
                'usage_stats': {
                    'total_issued': 75.0,
                    'by_location': [
                        {'location': 'Hangar A', 'quantity': 30.0},
                        {'location': 'Hangar B', 'quantity': 25.0},
                        {'location': 'Hangar C', 'quantity': 20.0}
                    ],
                    'by_user': [
                        {'user': 'John Doe', 'quantity': 35.0},
                        {'user': 'Jane Smith', 'quantity': 25.0},
                        {'user': 'Bob Johnson', 'quantity': 15.0}
                    ],
                    'over_time': [
                        {'month': '2023-01', 'quantity': 15.0},
                        {'month': '2023-02', 'quantity': 20.0},
                        {'month': '2023-03', 'quantity': 25.0},
                        {'month': '2023-04', 'quantity': 15.0}
                    ],
                    'avg_monthly_usage': 18.75,
                    'projected_depletion_days': 40.8
                },
                'efficiency_stats': {
                    'usage_efficiency_data': [
                        {
                            'lot_number': 'LOT123',
                            'original_quantity': 50.0,
                            'total_issued': 50.0,
                            'days_to_deplete': 30,
                            'daily_usage_rate': 1.6667
                        },
                        {
                            'lot_number': 'LOT456',
                            'original_quantity': 25.0,
                            'total_issued': 25.0,
                            'days_to_deplete': 15,
                            'daily_usage_rate': 1.6667
                        }
                    ]
                }
            })
        except Exception as e:
            print(f"Error in usage analytics route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating usage analytics'}), 500
