"""
Security Configuration for SupplyLine MRO Suite

This module contains security-related configuration settings and policies.
"""

import os

# Security Headers Configuration
SECURITY_HEADERS = {
    # Prevent MIME type sniffing
    'X-Content-Type-Options': 'nosniff',
    
    # Prevent clickjacking
    'X-Frame-Options': 'DENY',
    
    # Enable XSS protection
    'X-XSS-Protection': '1; mode=block',
    
    # Strict Transport Security (HTTPS enforcement)
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    
    # Content Security Policy
    'Content-Security-Policy': (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
    
    # Referrer Policy
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    
    # Permissions Policy (formerly Feature Policy)
    'Permissions-Policy': (
        'geolocation=(), '
        'microphone=(), '
        'camera=(), '
        'payment=(), '
        'usb=(), '
        'magnetometer=(), '
        'gyroscope=(), '
        'speaker=()'
    ),
    
    # Cache Control for sensitive pages
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

# CORS Configuration
CORS_CONFIG = {
    'origins': os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(','),
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization'],
    'expose_headers': ['X-Request-ID', 'X-Response-Time'],
    'supports_credentials': False,  # JWT doesn't need credentials
    'max_age': 3600
}

# Rate Limiting Configuration
RATE_LIMITS = {
    'global': {
        'limit': 1000,
        'window': 3600,  # 1 hour
        'per': 'ip'
    },
    'auth': {
        'login': {
            'limit': 5,
            'window': 300,  # 5 minutes
            'per': 'ip'
        },
        'refresh': {
            'limit': 10,
            'window': 300,  # 5 minutes
            'per': 'user'
        },
        'password_reset': {
            'limit': 3,
            'window': 3600,  # 1 hour
            'per': 'ip'
        }
    },
    'api': {
        'create': {
            'limit': 50,
            'window': 3600,  # 1 hour
            'per': 'user'
        },
        'update': {
            'limit': 100,
            'window': 3600,  # 1 hour
            'per': 'user'
        },
        'delete': {
            'limit': 20,
            'window': 3600,  # 1 hour
            'per': 'user'
        }
    }
}

# Request Size Limits
REQUEST_LIMITS = {
    'max_content_length': 10 * 1024 * 1024,  # 10MB
    'max_form_memory_size': 2 * 1024 * 1024,  # 2MB
    'max_json_payload': 1 * 1024 * 1024,  # 1MB
}

# Password Policy
PASSWORD_POLICY = {
    'min_length': 8,
    'max_length': 128,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digits': True,
    'require_special_chars': True,
    'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
    'max_consecutive_chars': 3,
    'prevent_common_passwords': True,
    'prevent_personal_info': True,
    'password_history': 5,  # Remember last 5 passwords
    'max_age_days': 90,  # Force password change every 90 days
}

# Session Security
SESSION_CONFIG = {
    'cookie_secure': True,  # HTTPS only
    'cookie_httponly': True,  # No JavaScript access
    'cookie_samesite': 'Strict',  # CSRF protection
    'permanent_session_lifetime': 3600,  # 1 hour
    'regenerate_on_login': True,
    'invalidate_on_logout': True,
}

# JWT Configuration
JWT_CONFIG = {
    'access_token_expires': 900,  # 15 minutes
    'refresh_token_expires': 604800,  # 7 days
    'algorithm': 'HS256',
    'issuer': 'supplyline-mro-suite',
    'audience': 'supplyline-users',
    'leeway': 10,  # 10 seconds clock skew tolerance
}

# Account Lockout Policy
ACCOUNT_LOCKOUT = {
    'max_failed_attempts': 5,
    'lockout_duration': 900,  # 15 minutes
    'progressive_delay': True,  # Increase delay with each failure
    'notify_admin': True,
    'log_attempts': True,
}

# Audit Logging Configuration
AUDIT_CONFIG = {
    'log_all_requests': False,
    'log_sensitive_operations': True,
    'log_failed_auth': True,
    'log_admin_actions': True,
    'log_data_changes': True,
    'retention_days': 365,
    'sensitive_fields': [
        'password', 'password_hash', 'secret_key', 'token',
        'api_key', 'private_key', 'ssn', 'credit_card'
    ]
}

# File Upload Security
FILE_UPLOAD_CONFIG = {
    'max_file_size': 5 * 1024 * 1024,  # 5MB
    'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    'forbidden_extensions': ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js'],
    'scan_for_malware': True,
    'quarantine_suspicious': True,
    'upload_path': '/secure/uploads/',
    'temp_path': '/tmp/uploads/',
}

# Database Security
DATABASE_CONFIG = {
    'use_ssl': True,
    'verify_ssl_cert': True,
    'connection_timeout': 30,
    'query_timeout': 60,
    'max_connections': 20,
    'connection_retry_attempts': 3,
    'log_slow_queries': True,
    'slow_query_threshold': 2.0,  # seconds
}

# API Security
API_CONFIG = {
    'require_https': True,
    'validate_content_type': True,
    'max_request_size': '10MB',
    'timeout': 30,
    'versioning': True,
    'deprecation_warnings': True,
}

# Monitoring and Alerting
MONITORING_CONFIG = {
    'enable_metrics': True,
    'enable_health_checks': True,
    'alert_on_errors': True,
    'alert_on_security_events': True,
    'performance_monitoring': True,
    'error_tracking': True,
    'log_level': 'INFO',
}

# Security Scanning
SECURITY_SCAN_CONFIG = {
    'enable_sql_injection_detection': True,
    'enable_xss_detection': True,
    'enable_path_traversal_detection': True,
    'enable_command_injection_detection': True,
    'block_suspicious_requests': True,
    'log_security_events': True,
    'alert_threshold': 5,  # Alert after 5 security events
}

# Environment-specific overrides
if os.environ.get('FLASK_ENV') == 'development':
    # Relaxed settings for development
    SECURITY_HEADERS['Strict-Transport-Security'] = 'max-age=0'
    CORS_CONFIG['origins'] = ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000', 'http://127.0.0.1:5173']
    SESSION_CONFIG['cookie_secure'] = False
    API_CONFIG['require_https'] = False
    
elif os.environ.get('FLASK_ENV') == 'testing':
    # Minimal security for testing
    RATE_LIMITS = {}  # Disable rate limiting in tests
    SECURITY_HEADERS = {}  # Minimal headers for tests
    PASSWORD_POLICY['min_length'] = 4  # Shorter passwords for tests
    
elif os.environ.get('FLASK_ENV') == 'production':
    # Maximum security for production
    SECURITY_HEADERS['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    SESSION_CONFIG['cookie_secure'] = True
    API_CONFIG['require_https'] = True
    MONITORING_CONFIG['log_level'] = 'WARNING'
