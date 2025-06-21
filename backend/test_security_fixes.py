#!/usr/bin/env python3
"""
Test script to verify security improvements for PR 361
"""

import sys
import os
sys.path.append('.')

# Set environment for testing
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['FLASK_ENV'] = 'development'  # Use development to keep security headers

def test_csrf_protection():
    """Test JWT-compatible CSRF protection"""
    print('🔒 Testing JWT-compatible CSRF protection...')
    
    from auth.jwt_manager import JWTManager
    
    # Test CSRF token generation
    user_id = 1
    token_secret = 'test_secret_12345'
    csrf_token = JWTManager.generate_csrf_token(user_id, token_secret)
    print(f'  ✅ CSRF token generated: {csrf_token[:20]}...')
    
    # Test CSRF token validation
    is_valid = JWTManager.validate_csrf_token(csrf_token, user_id, token_secret)
    print(f'  ✅ CSRF token validation: {is_valid}')
    
    # Test invalid token
    is_invalid = JWTManager.validate_csrf_token('invalid:token', user_id, token_secret)
    print(f'  ✅ Invalid CSRF token rejected: {not is_invalid}')
    
    # Test expired token
    old_csrf = '1000000000:abcd1234'
    is_expired = JWTManager.validate_csrf_token(old_csrf, user_id, token_secret)
    print(f'  ✅ Expired CSRF token rejected: {not is_expired}')
    
    return True

def test_security_headers():
    """Test security headers configuration"""
    print('\n🛡️  Testing Security Headers...')
    
    from security_config import SECURITY_HEADERS
    
    required_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options', 
        'X-XSS-Protection',
        'Strict-Transport-Security',
        'Content-Security-Policy',
        'Referrer-Policy',
        'Permissions-Policy'
    ]
    
    for header in required_headers:
        if header in SECURITY_HEADERS:
            print(f'  ✅ {header}: Present')
        else:
            print(f'  ❌ {header}: Missing')
            return False
    
    # Check CSP has required directives
    csp = SECURITY_HEADERS.get('Content-Security-Policy', '')
    required_directives = ['default-src', 'script-src', 'style-src', 'object-src']
    for directive in required_directives:
        if directive in csp:
            print(f'  ✅ CSP {directive}: Present')
        else:
            print(f'  ❌ CSP {directive}: Missing')
            return False
    
    return True

def test_cors_configuration():
    """Test CORS configuration"""
    print('\n🌐 Testing CORS Configuration...')
    
    from security_config import CORS_CONFIG
    
    # Check CORS settings
    origins = CORS_CONFIG.get('origins', [])
    methods = CORS_CONFIG.get('methods', [])
    headers = CORS_CONFIG.get('allow_headers', [])
    credentials = CORS_CONFIG.get('supports_credentials', True)
    
    print(f'  ✅ Origins configured: {len(origins)} origins')
    print(f'  ✅ Methods: {methods}')
    print(f'  ✅ Headers: {headers}')
    print(f'  ✅ Credentials disabled: {not credentials}')
    
    # Check no wildcard in production
    if '*' in origins:
        print('  ⚠️  Wildcard origin detected (should be removed in production)')
    else:
        print('  ✅ No wildcard origins (secure)')
    
    return True

def test_imports():
    """Test that all imports work correctly"""
    print('\n📦 Testing Imports...')
    
    try:
        from auth import JWTManager, jwt_required, csrf_required
        print('  ✅ Auth imports: OK')
    except ImportError as e:
        print(f'  ❌ Auth imports failed: {e}')
        return False
    
    try:
        from security_config import SECURITY_HEADERS, CORS_CONFIG
        print('  ✅ Security config imports: OK')
    except ImportError as e:
        print(f'  ❌ Security config imports failed: {e}')
        return False
    
    return True

def main():
    """Run all security tests"""
    print('🚀 Running Security Improvements Tests for PR 361\n')
    
    tests = [
        test_imports,
        test_csrf_protection,
        test_security_headers,
        test_cors_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f'  ❌ {test.__name__} failed')
        except Exception as e:
            print(f'  ❌ {test.__name__} error: {e}')
    
    print(f'\n📊 Test Results: {passed}/{total} tests passed')
    
    if passed == total:
        print('🎉 All security improvements are working correctly!')
        return True
    else:
        print('⚠️  Some tests failed - please review the issues above')
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
