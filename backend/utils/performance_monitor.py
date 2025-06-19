"""
Performance Monitoring for SupplyLine MRO Suite

This module provides performance monitoring and logging capabilities
to track API response times and identify bottlenecks.
"""

import time
import logging
from functools import wraps
from flask import request, g, jsonify
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring class to track API response times"""
    
    def __init__(self, app=None):
        self.app = app
        self.slow_threshold = 1000  # Log warnings for requests > 1000ms
        self.critical_threshold = 2000  # Log errors for requests > 2000ms
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize performance monitoring for Flask app"""
        self.app = app
        
        # Add before_request handler to start timing
        @app.before_request
        def start_timer():
            g.start_time = time.time()
        
        # Add after_request handler to log performance
        @app.after_request
        def log_performance(response):
            if hasattr(g, 'start_time'):
                duration_ms = (time.time() - g.start_time) * 1000
                
                # Log performance metrics
                self._log_request_performance(
                    endpoint=request.endpoint,
                    method=request.method,
                    path=request.path,
                    duration_ms=duration_ms,
                    status_code=response.status_code
                )
                
                # Add performance headers
                response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"
                
            return response
    
    def _log_request_performance(self, endpoint, method, path, duration_ms, status_code):
        """Log request performance with appropriate log level"""
        
        # Skip health checks and static files from detailed logging
        if endpoint in ['health_check_early', 'index'] or path.startswith('/static'):
            return
        
        log_data = {
            'endpoint': endpoint,
            'method': method,
            'path': path,
            'duration_ms': round(duration_ms, 2),
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log based on performance thresholds
        if duration_ms > self.critical_threshold:
            logger.error(f"CRITICAL SLOW REQUEST: {method} {path} took {duration_ms:.2f}ms", 
                        extra=log_data)
        elif duration_ms > self.slow_threshold:
            logger.warning(f"SLOW REQUEST: {method} {path} took {duration_ms:.2f}ms", 
                          extra=log_data)
        else:
            logger.debug(f"REQUEST: {method} {path} took {duration_ms:.2f}ms", 
                        extra=log_data)

def performance_monitor(threshold_ms=1000):
    """Decorator to monitor specific function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > threshold_ms:
                    logger.warning(f"Function {func.__name__} took {duration_ms:.2f}ms (threshold: {threshold_ms}ms)")
                else:
                    logger.debug(f"Function {func.__name__} took {duration_ms:.2f}ms")
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"Function {func.__name__} failed after {duration_ms:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator

def database_query_monitor(query_name="Unknown"):
    """Decorator to monitor database query performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                log_data = {
                    'query_name': query_name,
                    'function': func.__name__,
                    'duration_ms': round(duration_ms, 2)
                }
                
                if duration_ms > 500:  # Database queries should be faster
                    logger.warning(f"SLOW DB QUERY: {query_name} took {duration_ms:.2f}ms", 
                                  extra=log_data)
                else:
                    logger.debug(f"DB QUERY: {query_name} took {duration_ms:.2f}ms", 
                                extra=log_data)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"DB QUERY FAILED: {query_name} failed after {duration_ms:.2f}ms: {str(e)}")
                raise
                
        return wrapper
    return decorator

def get_performance_stats():
    """Get current performance statistics"""
    # This could be expanded to track metrics in memory or database
    return {
        'monitoring_active': True,
        'slow_threshold_ms': 1000,
        'critical_threshold_ms': 2000,
        'timestamp': datetime.utcnow().isoformat()
    }

def setup_performance_monitoring(app):
    """Set up performance monitoring for the application"""
    try:
        monitor = PerformanceMonitor(app)
        
        # Add performance stats endpoint
        @app.route('/api/admin/performance/stats', methods=['GET'])
        def performance_stats():
            """Get performance monitoring statistics"""
            return jsonify(get_performance_stats())
        
        logger.info("Performance monitoring setup completed")
        return monitor
        
    except Exception as e:
        logger.error(f"Failed to setup performance monitoring: {str(e)}")
        return None
