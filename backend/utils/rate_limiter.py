"""
Rate limiting utilities for API endpoints
Provides simple in-memory rate limiting for security-sensitive endpoints
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, consider using Redis-based rate limiting
    """

    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_rate_limited(self, key, limit, window_seconds):
        """
        Check if a key has exceeded the rate limit

        Args:
            key: Unique identifier (e.g., IP address, user ID)
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            tuple: (is_limited, retry_after_seconds)
        """
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window_seconds)

            # Remove old requests outside the window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]

            # Check if limit exceeded
            if len(self.requests[key]) >= limit:
                # Calculate retry after time
                oldest_request = min(self.requests[key])
                retry_after = (oldest_request + timedelta(seconds=window_seconds) - now).total_seconds()
                return True, max(0, int(retry_after))

            # Add current request
            self.requests[key].append(now)
            return False, 0

    def cleanup_old_entries(self, max_age_seconds=3600):
        """
        Clean up old entries to prevent memory bloat
        Should be called periodically
        """
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=max_age_seconds)

            keys_to_delete = []
            for key, requests in self.requests.items():
                # Remove old requests
                self.requests[key] = [
                    req_time for req_time in requests
                    if req_time > cutoff
                ]
                # Mark empty keys for deletion
                if not self.requests[key]:
                    keys_to_delete.append(key)

            # Delete empty keys
            for key in keys_to_delete:
                del self.requests[key]

    def reset_all(self):
        """Clear all tracked requests (useful for tests)."""

        with self.lock:
            self.requests.clear()


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(limit=5, window=3600, key_func=None):
    """
    Decorator to rate limit endpoint access

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        key_func: Optional function to generate rate limit key (default: IP address)

    Example:
        @rate_limit(limit=3, window=3600)  # 3 requests per hour
        def my_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                # Default to IP address
                key = f"ip:{request.remote_addr}"

            # Check rate limit
            is_limited, retry_after = _rate_limiter.is_rate_limited(key, limit, window)

            if is_limited:
                return jsonify({
                    'error': 'Too many requests. Please try again later.',
                    'retry_after': retry_after
                }), 429

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def get_rate_limiter():
    """Get the global rate limiter instance"""
    return _rate_limiter
