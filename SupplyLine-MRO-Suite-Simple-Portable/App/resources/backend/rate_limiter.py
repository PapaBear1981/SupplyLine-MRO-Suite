"""
Rate Limiter for Flask API

This module provides a rate limiter for the Flask API to prevent
the backend from being overwhelmed by too many requests.
"""

import time
from collections import defaultdict
from functools import wraps
from threading import Lock
from flask import request, jsonify

class RateLimiter:
    """
    A simple rate limiter for Flask API endpoints.

    This class implements a token bucket algorithm to limit the rate of requests
    to the API. Each client (identified by IP address) has a bucket of tokens
    that is refilled at a constant rate. Each request consumes a token, and if
    there are no tokens available, the request is rejected.
    """

    def __init__(self, rate=10, per=1, burst=20, cleanup_interval=3600):
        """
        Initialize the rate limiter.

        Args:
            rate (int): The number of tokens to add to the bucket per time period
            per (int): The time period in seconds
            burst (int): The maximum number of tokens that can be in the bucket
            cleanup_interval (int): Time in seconds between bucket cleanup (default: 1 hour)
        """
        self.rate = rate  # tokens per second
        self.per = per    # seconds
        self.burst = burst  # maximum bucket size
        self.cleanup_interval = cleanup_interval  # cleanup interval in seconds
        self.buckets = {}  # Use regular dict instead of defaultdict
        self.lock = Lock()  # Thread safety
        self.last_cleanup = time.time()

    def _get_client_id(self):
        """Get a unique identifier for the client."""
        return request.remote_addr

    def _refill_bucket(self, bucket):
        """Refill the bucket based on the time elapsed since the last refill."""
        now = time.time()
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * (self.rate / self.per)

        bucket["tokens"] = min(bucket["tokens"] + tokens_to_add, self.burst)
        bucket["last_refill"] = now

    def _cleanup_old_buckets(self):
        """Remove buckets that haven't been used recently"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = now - (self.cleanup_interval * 2)  # 2 hours old

        with self.lock:
            old_clients = [
                client_id for client_id, bucket in self.buckets.items()
                if bucket["last_refill"] < cutoff_time
            ]

            for client_id in old_clients:
                del self.buckets[client_id]

            self.last_cleanup = now

        if old_clients:
            print(f"Rate limiter: Cleaned up {len(old_clients)} old client buckets")

    def _consume_token(self, client_id):
        """
        Consume a token from the client's bucket.

        Returns:
            bool: True if a token was consumed, False otherwise
        """
        self._cleanup_old_buckets()  # Periodic cleanup

        with self.lock:
            if client_id not in self.buckets:
                self.buckets[client_id] = {
                    "tokens": self.burst,
                    "last_refill": time.time()
                }

            bucket = self.buckets[client_id]
            self._refill_bucket(bucket)

            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True

        return False

    def limit(self, f):
        """
        Decorator to apply rate limiting to a Flask route.

        Args:
            f: The Flask route function to decorate

        Returns:
            The decorated function
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            client_id = self._get_client_id()

            if not self._consume_token(client_id):
                response = jsonify({
                    "error": "Too many requests",
                    "message": "You have exceeded the rate limit. Please try again later."
                })
                response.status_code = 429  # Too Many Requests
                return response

            return f(*args, **kwargs)

        return decorated

    def get_stats(self):
        """Get statistics about rate limiter memory usage"""
        with self.lock:
            return {
                "active_clients": len(self.buckets),
                "memory_usage_estimate": len(self.buckets) * 64,  # rough estimate in bytes
                "last_cleanup": self.last_cleanup,
                "cleanup_interval": self.cleanup_interval
            }


# Create a global rate limiter instance
# Allow 100 requests per second with a burst of 200 requests
rate_limiter = RateLimiter(rate=100, per=1, burst=200)

# Decorator for rate-limited routes
def rate_limit(f):
    """Decorator to apply rate limiting to a Flask route."""
    return rate_limiter.limit(f)
