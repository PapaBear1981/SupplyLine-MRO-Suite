#!/usr/bin/env python3
"""
Security Validation Script for SupplyLine MRO Suite

This script checks for security vulnerabilities and provides recommendations.
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from utils.admin_init import validate_admin_setup
from rate_limiter import rate_limiter

def check_cors_configuration(app):
    """Check CORS configuration security"""
    issues = []

    cors_origins = app.config.get('CORS_ORIGINS', [])

    if '*' in str(cors_origins):
        issues.append("CRITICAL: CORS allows all origins (*)")
    elif not cors_origins:
        issues.append("WARNING: No CORS origins configured")
    else:
        print(f"✓ CORS origins properly configured: {cors_origins}")

    return issues

def check_session_configuration(app):
    """Check session security configuration"""
    issues = []

    # Check session timeout
    session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')
    if session_lifetime:
        lifetime_seconds = (
            session_lifetime.total_seconds()
            if hasattr(session_lifetime, "total_seconds")
            else int(session_lifetime)
        )
        if lifetime_seconds > 8 * 3600:
            issues.append("WARNING: Session timeout is longer than 8 hours")
        else:
            print("✓ Session timeout is appropriately configured")
    else:
        print("✓ Session timeout is appropriately configured")

    # Check cookie security
    if not app.config.get('SESSION_COOKIE_SECURE'):
        issues.append("WARNING: SESSION_COOKIE_SECURE is not enabled")
    else:
        print("✓ Secure cookies enabled")

    if not app.config.get('SESSION_COOKIE_HTTPONLY'):
        issues.append("WARNING: SESSION_COOKIE_HTTPONLY is not enabled")
    else:
        print("✓ HTTP-only cookies enabled")

    samesite = app.config.get('SESSION_COOKIE_SAMESITE')
    if samesite not in ['Strict', 'Lax']:
        issues.append("WARNING: SESSION_COOKIE_SAMESITE should be 'Strict' or 'Lax'")
    else:
        print(f"✓ SameSite cookie policy: {samesite}")

    return issues

def check_security_headers(app):
    """Check security headers configuration"""
    issues = []

    security_headers = app.config.get('SECURITY_HEADERS', {})

    required_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Strict-Transport-Security'
    ]

    missing_headers = [header for header in required_headers if header not in security_headers]

    if missing_headers:
        issues.append(f"WARNING: Missing security headers: {', '.join(missing_headers)}")
    else:
        print("✓ All required security headers configured")

    return issues

def check_rate_limiter():
    """Check rate limiter configuration"""
    issues = []

    try:
        stats = rate_limiter.get_stats()
        print(f"✓ Rate limiter active with {stats['active_clients']} active clients")

        if stats['active_clients'] > 1000:
            issues.append("WARNING: Rate limiter has many active clients, memory usage may be high")

    except Exception as e:
        issues.append(f"ERROR: Rate limiter check failed: {str(e)}")

    return issues

def check_environment_variables():
    """Check important environment variables"""
    issues = []

    important_vars = [
        'SECRET_KEY',
        'CORS_ORIGINS',
        'INITIAL_ADMIN_PASSWORD'
    ]

    for var in important_vars:
        if not os.environ.get(var):
            if var == 'SECRET_KEY':
                issues.append(f"CRITICAL: {var} environment variable not set")
            else:
                issues.append(f"WARNING: {var} environment variable not set")
        else:
            print(f"✓ {var} environment variable is set")

    return issues

def check_file_permissions():
    """Check file permissions for sensitive files"""
    issues = []

    sensitive_files = [
        'config.py',
        'utils/admin_init.py',
        'utils/session_manager.py'
    ]

    for file_path in sensitive_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            # Check if file is readable by others (basic check)
            stat_info = os.stat(full_path)
            if stat_info.st_mode & 0o044:  # Check if readable by group or others
                issues.append(f"WARNING: {file_path} may be readable by others")
            else:
                print(f"✓ {file_path} has appropriate permissions")
        else:
            issues.append(f"WARNING: {file_path} not found")

    return issues

def main():
    """Main security check function"""
    print("=" * 60)
    print("SupplyLine MRO Suite - Security Validation Report")
    print("=" * 60)
    print(f"Report generated: {datetime.now().isoformat()}")
    print()

    all_issues = []

    # Create Flask app for configuration checks
    app = create_app()

    with app.app_context():
        print("1. Checking admin user security...")
        is_secure, admin_issues = validate_admin_setup()
        if admin_issues:
            all_issues.extend(admin_issues)
        if is_secure:
            print("✓ Admin user setup is secure")
        print()

        print("2. Checking CORS configuration...")
        cors_issues = check_cors_configuration(app)
        all_issues.extend(cors_issues)
        print()

        print("3. Checking session configuration...")
        session_issues = check_session_configuration(app)
        all_issues.extend(session_issues)
        print()

        print("4. Checking security headers...")
        header_issues = check_security_headers(app)
        all_issues.extend(header_issues)
        print()

        print("5. Checking rate limiter...")
        rate_limit_issues = check_rate_limiter()
        all_issues.extend(rate_limit_issues)
        print()

        print("6. Checking environment variables...")
        env_issues = check_environment_variables()
        all_issues.extend(env_issues)
        print()

        print("7. Checking file permissions...")
        file_issues = check_file_permissions()
        all_issues.extend(file_issues)
        print()

    # Summary
    print("=" * 60)
    print("SECURITY SUMMARY")
    print("=" * 60)

    if not all_issues:
        print("✅ No security issues found!")
    else:
        critical_issues = [issue for issue in all_issues if issue.startswith('CRITICAL')]
        warning_issues = [issue for issue in all_issues if issue.startswith('WARNING')]
        error_issues = [issue for issue in all_issues if issue.startswith('ERROR')]

        if critical_issues:
            print(f"🚨 {len(critical_issues)} CRITICAL issue(s) found:")
            for issue in critical_issues:
                print(f"   {issue}")
            print()

        if error_issues:
            print(f"❌ {len(error_issues)} ERROR(s) found:")
            for issue in error_issues:
                print(f"   {issue}")
            print()

        if warning_issues:
            print(f"⚠️  {len(warning_issues)} WARNING(s) found:")
            for issue in warning_issues:
                print(f"   {issue}")
            print()

        print("RECOMMENDATIONS:")
        print("- Address CRITICAL issues immediately")
        print("- Review and fix ERROR issues")
        print("- Consider addressing WARNING issues for enhanced security")
        print("- Set INITIAL_ADMIN_PASSWORD environment variable")
        print("- Ensure HTTPS is used in production")
        print("- Regularly review and update security configurations")

    print("=" * 60)

    # Return exit code based on critical issues
    return 1 if any(issue.startswith('CRITICAL') for issue in all_issues) else 0

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during security check
        format='%(levelname)s: %(message)s'
    )

    exit_code = main()
    sys.exit(exit_code)
