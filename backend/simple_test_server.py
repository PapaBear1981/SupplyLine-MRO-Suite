#!/usr/bin/env python3
"""
Simple test server to isolate performance issues
"""

from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/test/health')
def simple_health():
    return jsonify({
        'status': 'ok',
        'timestamp': time.time()
    })

@app.route('/test/slow')
def intentionally_slow():
    time.sleep(2)  # Intentional 2-second delay
    return jsonify({
        'status': 'slow',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("Starting simple test server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)
