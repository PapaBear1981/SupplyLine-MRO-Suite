"""
Rate Limiter for Flask API

This module provides a rate limiter for the Flask API to prevent
the backend from being overwhelmed by too many requests and to
protect against brute force attacks.
"""

from flask import request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import time

# Create a limiter instance that will be initialized with the app
limiter = None

def init_limiter(app):
    """
    Initialize the Flask-Limiter with the Flask app.

    Args:
        app: The Flask application instance
    """
    global limiter

    # Configure the limiter with the app
    limiter = Limiter(
        app=app,
        key_func=get_client_identifier,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window-elastic-expiry",  # More efficient for high-traffic APIs
        headers_enabled=True,  # Add rate limit headers to responses
        swallow_errors=True,  # Don't fail if rate limiter has issues
    )

    # Register custom error handler
    @limiter.request_filter
    def health_check_filter():
        """Don't rate limit health check endpoints"""
        return request.path == "/api/health"

    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Custom error handler for rate limit exceeded"""
        return jsonify({
            "error": "Too many requests",
            "message": "Rate limit exceeded. Please try again later.",
            "retry_after": e.description
        }), 429

    return limiter

def get_client_identifier():
    """
    Get a unique identifier for the client.

    Uses X-Forwarded-For header if available (for when behind a proxy),
    falls back to remote_addr, and includes User-Agent to help prevent
    simple spoofing.

    Returns:
        str: A string identifying the client
    """
    # Get the client's IP address
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr or 'unknown'

    # Include a portion of the User-Agent to make the identifier more unique
    # but not the entire string to avoid creating too many buckets
    user_agent = request.headers.get('User-Agent', '')[:20]

    # For authenticated users, include their user ID for more accurate limiting
    user_id = request.cookies.get('user_id', '')

    return f"{ip}:{user_agent}:{user_id}"

# Decorator for applying custom rate limits to specific routes
def custom_rate_limit(limit_string):
    """
    Decorator to apply a custom rate limit to a Flask route.

    Args:
        limit_string: A string specifying the rate limit (e.g., "5 per minute")

    Returns:
        The decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if limiter:
                return limiter.limit(limit_string)(f)(*args, **kwargs)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specific rate limits for sensitive operations
def auth_rate_limit():
    """Rate limit for authentication endpoints to prevent brute force attacks"""
    return custom_rate_limit("5 per minute, 20 per hour")(lambda f: f)

def api_rate_limit():
    """Standard rate limit for API endpoints"""
    return custom_rate_limit("60 per minute")(lambda f: f)

def admin_api_rate_limit():
    """Rate limit for admin API endpoints"""
    return custom_rate_limit("30 per minute")(lambda f: f)
