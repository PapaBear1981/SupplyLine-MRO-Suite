from flask import Flask, jsonify
import datetime
import time
import os
import sys

# Add the current directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import time_utils
try:
    from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime
    print("Successfully imported time_utils in direct_time_server.py")
    USE_TIME_UTILS = True
except ImportError as e:
    print(f"Error importing time_utils in direct_time_server.py: {str(e)}")
    USE_TIME_UTILS = False

app = Flask(__name__)

@app.route('/api/time')
def time_endpoint():
    """Return the current time in both UTC and local time."""
    if USE_TIME_UTILS:
        return jsonify({
            'status': 'ok',
            'utc_time': format_datetime(get_utc_timestamp()),
            'local_time': format_datetime(get_local_timestamp()),
            'timezone': str(time.tzname),
            'using_time_utils': True
        })
    else:
        return jsonify({
            'status': 'ok',
            'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'local_time': datetime.datetime.now().isoformat(),
            'timezone': str(time.tzname),
            'using_time_utils': False
        })

@app.route('/api/health')
def health_check():
    """Return a simple health check response."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting direct time server on port 5001...")
    app.run(host="0.0.0.0", port=5001, debug=True)
