"""
Rate Limiter for Flask API

This module provides a rate limiter for the Flask API to prevent
the backend from being overwhelmed by too many requests.
"""

import time
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

class RateLimiter:
    """
    A simple rate limiter for Flask API endpoints.

    This class implements a token bucket algorithm to limit the rate of requests
    to the API. Each client (identified by IP address) has a bucket of tokens
    that is refilled at a constant rate. Each request consumes a token, and if
    there are no tokens available, the request is rejected.
    """

    def __init__(self, rate=10, per=1, burst=20):
        """
        Initialize the rate limiter.

        Args:
            rate (int): The number of tokens to add to the bucket per time period
            per (int): The time period in seconds
            burst (int): The maximum number of tokens that can be in the bucket
        """
        self.rate = rate  # tokens per second
        self.per = per    # seconds
        self.burst = burst  # maximum bucket size

        # Store the token buckets for each client
        self.buckets = defaultdict(lambda: {"tokens": burst, "last_refill": time.time()})

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

    def _consume_token(self, client_id):
        """
        Consume a token from the client's bucket.

        Returns:
            bool: True if a token was consumed, False otherwise
        """
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


# Create a global rate limiter instance
# Allow 100 requests per second with a burst of 200 requests
rate_limiter = RateLimiter(rate=100, per=1, burst=200)

# Decorator for rate-limited routes
def rate_limit(f):
    """Decorator to apply rate limiting to a Flask route."""
    return rate_limiter.limit(f)
