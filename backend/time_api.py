"""
Time API module for the SupplyLine MRO Suite application.

This module provides a Flask Blueprint for time-related API endpoints.
"""

from flask import Blueprint, jsonify
import datetime
import time
import os
import sys

# Add the current directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import time_utils at module level
try:
    from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime
    print("Successfully imported time_utils in time_api.py")
except ImportError as e:
    print(f"Error importing time_utils at module level in time_api.py: {str(e)}")

# Create a Blueprint for time-related endpoints
time_api = Blueprint('time_api', __name__)

@time_api.route('/api/time')
def time_endpoint():
    """
    Return the current time in both UTC and local time.

    Returns:
        JSON response with UTC time, local time, and timezone information.
    """
    try:
        # Try to import the time_utils module again if needed
        from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime

        # Use the time utility functions
        return jsonify({
            'status': 'ok',
            'utc_time': format_datetime(get_utc_timestamp()),
            'local_time': format_datetime(get_local_timestamp()),
            'timezone': str(time.tzname)
        })
    except ImportError as e:
        # Fall back to standard datetime if time_utils is not available
        print(f"Error importing time_utils in time_endpoint: {str(e)}")
        return jsonify({
            'status': 'ok',
            'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'local_time': datetime.datetime.now().isoformat(),
            'timezone': str(time.tzname)
        })

@time_api.route('/api/time-test')
def time_test():
    """
    Test endpoint for time functionality.

    Returns:
        JSON response with UTC time, local time, and timezone information.
    """
    return jsonify({
        'status': 'ok',
        'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'local_time': datetime.datetime.now().isoformat(),
        'timezone': str(time.tzname),
        'message': 'This is a test endpoint for time functionality'
    })
