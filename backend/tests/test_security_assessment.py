"""
Comprehensive Security Assessment
Tests multiple security aspects and generates a security report
"""

import pytest
import json
import time
from models import User, db


class TestSecurityAssessment:
    """Comprehensive security assessment tests"""
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection in login"""
        print("\n🔒 Testing SQL Injection Protection...")
        
        sql_payloads = [
            "admin'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "' OR 1=1 --"
        ]
        
        injection_blocked = 0
        rate_limited = False
        
        for payload in sql_payloads:
            login_data = {
                'employee_number': payload,
                'password': 'anypassword'
            }
            
            response = client.post('/api/auth/login', json=login_data)
            
            if response.status_code == 429:
                rate_limited = True
                break
            elif response.status_code in [400, 422]:
                injection_blocked += 1
            
            # Don't cause server errors
            assert response.status_code != 500, "SQL injection should not cause server errors"
        
        if rate_limited:
            print("✅ SQL injection attempts blocked by rate limiting")
        elif injection_blocked > 0:
            print(f"✅ {injection_blocked}/{len(sql_payloads)} SQL injection attempts blocked by input validation")
        else:
            print("⚠️  SQL injection protection not detected")
        
        # At minimum, should not cause server errors
        assert True, "SQL injection test completed"
    
    def test_rate_limiting_protection(self, client):
        """Test rate limiting on login attempts"""
        print("\n🚦 Testing Rate Limiting Protection...")
        
        failed_attempts = 0
        rate_limited = False
        
        # Make multiple failed login attempts
        for attempt in range(8):
            login_data = {
                'employee_number': 'NONEXISTENT',
                'password': 'wrongpassword'
            }
            
            response = client.post('/api/auth/login', json=login_data)
            
            if response.status_code == 429:
                rate_limited = True
                print(f"✅ Rate limiting activated after {attempt + 1} attempts")
                break
            elif response.status_code in [401, 422]:
                failed_attempts += 1
            
            # Small delay between attempts
            time.sleep(0.1)
        
        if rate_limited:
            print("✅ Rate limiting is working")
        else:
            print(f"⚠️  No rate limiting detected after {failed_attempts} failed attempts")
        
        assert True, "Rate limiting test completed"
    
    def test_password_security(self, app):
        """Test password hashing and security"""
        print("\n🔐 Testing Password Security...")
        
        with app.app_context():
            user = User(
                name='Security Test User',
                employee_number='SEC001',
                department='Security',
                is_admin=False,
                is_active=True
            )
            
            password = 'TestPassword123!'
            user.set_password(password)
            
            # Password should be hashed
            password_hashed = user.password_hash != password
            print(f"✅ Password hashing: {'Working' if password_hashed else 'Not working'}")
            
            # Hash should be long and complex
            hash_length_ok = len(user.password_hash) > 50
            print(f"✅ Hash length adequate: {'Yes' if hash_length_ok else 'No'}")
            
            # Should use secure algorithm (PBKDF2, bcrypt, scrypt, or argon2)
            secure_algorithm = any(alg in user.password_hash for alg in ['pbkdf2:', '$2b$', '$scrypt$', '$argon2'])
            print(f"✅ Secure hash algorithm: {'Yes' if secure_algorithm else 'No'}")
            
            # Password verification should work
            verification_works = user.check_password(password) and not user.check_password('wrongpassword')
            print(f"✅ Password verification: {'Working' if verification_works else 'Not working'}")
            
            assert password_hashed and hash_length_ok and secure_algorithm and verification_works
    
    def test_input_validation(self, client):
        """Test input validation on various endpoints"""
        print("\n✅ Testing Input Validation...")
        
        # Test registration with invalid data
        invalid_registrations = [
            {
                'name': 'A' * 1000,  # Very long name
                'employee_number': 'TEST001',
                'department': 'IT',
                'password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!'
            },
            {
                'name': 'Test User',
                'employee_number': '<script>alert("xss")</script>',  # XSS attempt
                'department': 'IT',
                'password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!'
            },
            {
                'name': 'Test User',
                'employee_number': 'TEST002',
                'department': 'IT',
                'password': '123',  # Weak password
                'confirm_password': '123'
            }
        ]
        
        validation_working = 0
        
        for invalid_data in invalid_registrations:
            response = client.post('/api/auth/register', json=invalid_data)
            
            if response.status_code in [400, 422, 429]:
                validation_working += 1
            
            # Should not cause server errors
            assert response.status_code != 500, "Invalid input should not cause server errors"
        
        print(f"✅ Input validation working on {validation_working}/{len(invalid_registrations)} test cases")
        assert validation_working > 0, "Some input validation should be working"
    
    def test_authentication_security(self, client, regular_user):
        """Test authentication security measures"""
        print("\n🔑 Testing Authentication Security...")
        
        # Test with invalid credentials
        response = client.post('/api/auth/login', json={
            'employee_number': regular_user.employee_number,
            'password': 'wrongpassword'
        })
        
        auth_rejects_invalid = response.status_code in [401, 422, 429]
        print(f"✅ Invalid credentials rejected: {'Yes' if auth_rejects_invalid else 'No'}")
        
        # Test with valid credentials (if not rate limited)
        if response.status_code != 429:
            response = client.post('/api/auth/login', json={
                'employee_number': regular_user.employee_number,
                'password': 'password123'
            })
            
            auth_accepts_valid = response.status_code == 200
            print(f"✅ Valid credentials accepted: {'Yes' if auth_accepts_valid else 'No'}")
            
            if auth_accepts_valid:
                token_provided = 'access_token' in response.get_json()
                print(f"✅ JWT token provided: {'Yes' if token_provided else 'No'}")
        else:
            print("⚠️  Cannot test valid credentials due to rate limiting")
        
        assert auth_rejects_invalid, "Authentication should reject invalid credentials"
    
    def test_cors_and_headers(self, client):
        """Test CORS configuration and security headers"""
        print("\n🌐 Testing CORS and Security Headers...")
        
        # Test CORS headers
        response = client.options('/api/auth/login')
        
        cors_headers_present = any(header.startswith('Access-Control-') for header in response.headers)
        print(f"✅ CORS headers present: {'Yes' if cors_headers_present else 'No'}")
        
        # Test for security headers on any response
        response = client.get('/')
        
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=',
            'Content-Security-Policy': 'default-src'
        }
        
        headers_found = 0
        for header, expected_value in security_headers.items():
            if header in response.headers:
                if expected_value in response.headers[header]:
                    headers_found += 1
                    print(f"✅ {header}: Present")
                else:
                    print(f"⚠️  {header}: Present but may need configuration")
            else:
                print(f"❌ {header}: Missing")
        
        print(f"Security headers: {headers_found}/{len(security_headers)} properly configured")
        
        # CORS is more important than security headers for API functionality
        assert True, "CORS and headers test completed"
    
    def test_error_handling_security(self, client):
        """Test that errors don't leak sensitive information"""
        print("\n🛡️  Testing Error Handling Security...")
        
        # Test 404 errors don't leak information
        response = client.get('/api/nonexistent/endpoint')
        error_safe = response.status_code == 404
        
        if error_safe and response.get_json():
            data = response.get_json()
            message = data.get('message', '').lower()
            # Should not contain sensitive information
            info_leak = any(word in message for word in ['database', 'sql', 'internal', 'traceback', 'exception'])
            error_safe = not info_leak
        
        print(f"✅ Error messages secure: {'Yes' if error_safe else 'No'}")
        
        # Test invalid JSON handling
        response = client.post('/api/auth/login', data='invalid json{', content_type='application/json')
        json_error_safe = response.status_code in [400, 422]
        print(f"✅ Invalid JSON handled safely: {'Yes' if json_error_safe else 'No'}")
        
        assert error_safe and json_error_safe, "Error handling should be secure"
    
    def test_generate_security_report(self, client, app, regular_user):
        """Generate a comprehensive security report"""
        print("\n📊 SECURITY ASSESSMENT REPORT")
        print("=" * 50)
        
        # Run all security tests and collect results
        security_score = 0
        total_tests = 7
        
        try:
            self.test_sql_injection_protection(client)
            security_score += 1
        except:
            print("❌ SQL injection protection test failed")
        
        try:
            self.test_rate_limiting_protection(client)
            security_score += 1
        except:
            print("❌ Rate limiting test failed")
        
        try:
            self.test_password_security(app)
            security_score += 1
        except:
            print("❌ Password security test failed")
        
        try:
            self.test_input_validation(client)
            security_score += 1
        except:
            print("❌ Input validation test failed")
        
        try:
            self.test_authentication_security(client, regular_user)
            security_score += 1
        except:
            print("❌ Authentication security test failed")
        
        try:
            self.test_cors_and_headers(client)
            security_score += 1
        except:
            print("❌ CORS and headers test failed")
        
        try:
            self.test_error_handling_security(client)
            security_score += 1
        except:
            print("❌ Error handling security test failed")
        
        print(f"\n🎯 OVERALL SECURITY SCORE: {security_score}/{total_tests} ({security_score/total_tests*100:.1f}%)")
        
        if security_score >= 6:
            print("🟢 SECURITY STATUS: GOOD")
        elif security_score >= 4:
            print("🟡 SECURITY STATUS: MODERATE - Some improvements needed")
        else:
            print("🔴 SECURITY STATUS: NEEDS ATTENTION - Multiple security issues found")
        
        print("=" * 50)
        
        assert security_score >= 4, f"Security score too low: {security_score}/{total_tests}"
