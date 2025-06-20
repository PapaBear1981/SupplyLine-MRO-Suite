"""
Security Middleware for SupplyLine MRO Suite

This module provides security middleware for request processing including:
- Rate limiting
- Request size limits
- Security headers
- CORS configuration
- Request logging and monitoring
"""

import time
import logging
import re
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import request, jsonify, g
from functools import wraps
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation using sliding window"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = {}
    
    def is_allowed(self, identifier: str, limit: int, window: int) -> bool:
        """
        Check if request is allowed based on rate limit
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        
        # Check if IP is temporarily blocked
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                return False
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests outside the window
        request_times = self.requests[identifier]
        while request_times and request_times[0] < now - window:
            request_times.popleft()
        
        # Check if limit is exceeded
        if len(request_times) >= limit:
            # Block IP for 5 minutes if limit exceeded
            self.blocked_ips[identifier] = now + 300
            logger.warning(f"Rate limit exceeded for {identifier}. Blocking for 5 minutes.")
            return False
        
        # Add current request
        request_times.append(now)
        return True
    
    def cleanup_old_entries(self):
        """Clean up old entries to prevent memory leaks"""
        now = time.time()
        cutoff = now - 3600  # Keep entries for 1 hour
        
        for identifier in list(self.requests.keys()):
            request_times = self.requests[identifier]
            while request_times and request_times[0] < cutoff:
                request_times.popleft()
            
            if not request_times:
                del self.requests[identifier]

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit: int = 100, window: int = 3600, per: str = 'ip'):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum number of requests
        window: Time window in seconds
        per: Rate limit per 'ip' or 'user'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine identifier
            if per == 'user':
                user_payload = getattr(request, 'current_user', None)
                identifier = f"user_{user_payload['user_id']}" if user_payload else f"ip_{request.remote_addr}"
            else:
                identifier = f"ip_{request.remote_addr}"
            
            # Check rate limit
            if not rate_limiter.is_allowed(identifier, limit, window):
                logger.warning(f"Rate limit exceeded for {identifier}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'retry_after': 300
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def setup_security_middleware(app):
    """Setup security middleware for the Flask app"""
    
    @app.before_request
    def security_before_request():
        """Security checks before processing request"""
        
        # Request size limit (10MB)
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            logger.warning(f"Request too large: {request.content_length} bytes from {request.remote_addr}")
            return jsonify({'error': 'Request too large'}), 413
        
        # Log security-relevant requests
        if request.method in ['POST', 'PUT', 'DELETE']:
            logger.info(f"Security log: {request.method} {request.path} from {request.remote_addr}")
        
        # Store request start time for performance monitoring
        g.start_time = time.time()
        
        # Basic request validation
        if request.is_json and request.content_type != 'application/json':
            return jsonify({'error': 'Invalid content type'}), 400
    
    @app.after_request
    def security_after_request(response):
        """Add security headers to response"""
        
        # Security headers
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Additional security headers
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        # Performance monitoring
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            
            # Log slow requests
            if duration > 2.0:
                logger.warning(f"Slow request: {request.method} {request.path} took {duration:.3f}s")
        
        # CORS headers for API endpoints
        if request.path.startswith('/api/'):
            allowed_origins = app.config.get('CORS_ORIGINS', [])
            origin = request.headers.get('Origin')
            
            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
            elif '*' in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = '*'
            
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle request too large errors"""
        logger.warning(f"Request entity too large from {request.remote_addr}")
        return jsonify({'error': 'Request too large'}), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit exceeded errors"""
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429

class SecurityMonitor:
    """Security monitoring and alerting"""
    
    def __init__(self):
        self.suspicious_activities = defaultdict(list)
        self.alert_thresholds = {
            'failed_logins': 5,
            'invalid_tokens': 10,
            'sql_injection_attempts': 1,
            'xss_attempts': 1,
        }
    
    def log_security_event(self, event_type: str, details: Dict, ip_address: str):
        """
        Log security event and check for suspicious patterns
        
        Args:
            event_type: Type of security event
            details: Event details
            ip_address: Source IP address
        """
        event = {
            'timestamp': datetime.utcnow(),
            'type': event_type,
            'details': details,
            'ip_address': ip_address
        }
        
        self.suspicious_activities[ip_address].append(event)
        
        # Clean old events (keep last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.suspicious_activities[ip_address] = [
            e for e in self.suspicious_activities[ip_address]
            if e['timestamp'] > cutoff
        ]
        
        # Check for suspicious patterns
        self._check_suspicious_patterns(ip_address)
        
        # Log the event
        logger.warning(f"Security event: {event_type} from {ip_address} - {details}")
    
    def _check_suspicious_patterns(self, ip_address: str):
        """Check for suspicious activity patterns"""
        events = self.suspicious_activities[ip_address]
        
        # Count events by type in the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_events = [e for e in events if e['timestamp'] > one_hour_ago]
        
        event_counts = defaultdict(int)
        for event in recent_events:
            event_counts[event['type']] += 1
        
        # Check thresholds
        for event_type, count in event_counts.items():
            threshold = self.alert_thresholds.get(event_type, float('inf'))
            if count >= threshold:
                self._trigger_security_alert(ip_address, event_type, count)
    
    def _trigger_security_alert(self, ip_address: str, event_type: str, count: int):
        """Trigger security alert"""
        alert_message = f"SECURITY ALERT: {count} {event_type} events from {ip_address} in the last hour"
        logger.critical(alert_message)
        
        # Here you could integrate with external alerting systems
        # like Slack, email, or security monitoring tools

# Global security monitor instance
security_monitor = SecurityMonitor()

def log_security_event(event_type: str, details: Dict):
    """
    Log a security event
    
    Args:
        event_type: Type of security event
        details: Event details
    """
    ip_address = request.remote_addr
    security_monitor.log_security_event(event_type, details, ip_address)

def detect_sql_injection(query_string: str) -> bool:
    """
    Detect potential SQL injection attempts
    
    Args:
        query_string: Query string to analyze
        
    Returns:
        True if potential SQL injection detected
    """
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"].*['\"])",
        r"(--|#|/\*|\*/)",
        r"(\bUNION\s+SELECT\b)",
        r"(\bINTO\s+OUTFILE\b)",
    ]
    
    query_upper = query_string.upper()
    for pattern in sql_patterns:
        if re.search(pattern, query_upper, re.IGNORECASE):
            return True
    
    return False

def detect_xss_attempt(input_string: str) -> bool:
    """
    Detect potential XSS attempts
    
    Args:
        input_string: Input string to analyze
        
    Returns:
        True if potential XSS detected
    """
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    
    return False

def security_scan_request():
    """Scan request for security threats"""
    threats_detected = []
    
    # Check query parameters
    for key, value in request.args.items():
        if detect_sql_injection(value):
            threats_detected.append(f"SQL injection in parameter: {key}")
        if detect_xss_attempt(value):
            threats_detected.append(f"XSS attempt in parameter: {key}")
    
    # Check JSON data
    if request.is_json:
        json_data = request.get_json() or {}
        for key, value in json_data.items():
            if isinstance(value, str):
                if detect_sql_injection(value):
                    threats_detected.append(f"SQL injection in JSON field: {key}")
                if detect_xss_attempt(value):
                    threats_detected.append(f"XSS attempt in JSON field: {key}")
    
    # Log threats
    for threat in threats_detected:
        log_security_event('security_threat', {'threat': threat})
    
    return threats_detected
