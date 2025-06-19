"""
Rate Limiter Configuration for SupplyLine MRO Suite

This module configures Flask-Limiter to prevent brute force attacks
and API abuse as identified in the pre-deployment security testing.
"""

import logging
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)

def get_user_id():
    """Get user ID for rate limiting, fallback to IP address"""
    from flask import session
    user_id = session.get('user_id')
    if user_id:
        return f"user:{user_id}"
    return get_remote_address()

def create_limiter(app):
    """Create and configure Flask-Limiter instance"""
    
    # Configure rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_user_id,
        default_limits=["1000 per hour"],  # Default limit for all endpoints
        storage_uri="memory://",  # Use in-memory storage for simplicity
        strategy="fixed-window",
        headers_enabled=True,
        swallow_errors=True  # Don't crash app if rate limiter fails
    )
    
    # Custom error handler for rate limit exceeded
    @limiter.request_filter
    def exempt_health_checks():
        """Exempt health check endpoints from rate limiting"""
        return request.endpoint in ['health_check_early', 'index']
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Custom error response for rate limit exceeded"""
        logger.warning(f"Rate limit exceeded for {get_user_id()} on {request.endpoint}")
        
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': error.retry_after
        }), 429
    
    logger.info("Rate limiter configured successfully")
    return limiter

def apply_auth_rate_limits(limiter, app):
    """Apply specific rate limits to authentication endpoints"""
    
    # Get the route functions by name
    with app.app_context():
        # Find login endpoint
        for rule in app.url_map.iter_rules():
            if rule.endpoint and 'login' in rule.endpoint.lower():
                # Apply strict rate limiting to login endpoints
                limiter.limit("5 per minute")(app.view_functions[rule.endpoint])
                logger.info(f"Applied login rate limit to {rule.endpoint}")
            
            elif rule.endpoint and any(auth_term in rule.endpoint.lower() 
                                     for auth_term in ['register', 'password', 'reset']):
                # Apply moderate rate limiting to other auth endpoints
                limiter.limit("10 per minute")(app.view_functions[rule.endpoint])
                logger.info(f"Applied auth rate limit to {rule.endpoint}")

def apply_api_rate_limits(limiter, app):
    """Apply rate limits to API endpoints"""
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint and rule.rule.startswith('/api/'):
                # Skip already limited auth endpoints
                if any(auth_term in rule.endpoint.lower() 
                       for auth_term in ['login', 'register', 'password', 'reset']):
                    continue
                
                # Apply general API rate limiting
                if rule.endpoint in app.view_functions:
                    limiter.limit("100 per minute")(app.view_functions[rule.endpoint])
                    logger.debug(f"Applied API rate limit to {rule.endpoint}")

def setup_rate_limiting(app):
    """Main function to set up rate limiting for the application"""
    try:
        # Create limiter instance
        limiter = create_limiter(app)
        
        # Apply specific rate limits
        apply_auth_rate_limits(limiter, app)
        apply_api_rate_limits(limiter, app)
        
        logger.info("Rate limiting setup completed successfully")
        return limiter
        
    except Exception as e:
        logger.error(f"Failed to setup rate limiting: {str(e)}")
        # Return None if setup fails - app should continue without rate limiting
        return None
