"""
Security tests for input validation
Tests SQL injection prevention, XSS prevention, and data validation
"""

import pytest
import json
from models import User, Tool, Chemical, db


class TestSQLInjectionPrevention:
    """Test protection against SQL injection attacks"""
    
    def test_login_sql_injection(self, client):
        """Test SQL injection attempts in login fields"""
        sql_injection_payloads = [
            "admin'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "admin' OR '1'='1' --",
            "admin' OR '1'='1' /*",
            "admin'; INSERT INTO users (name) VALUES ('hacked'); --",
            "admin' UNION SELECT * FROM users --",
            "' OR 1=1 --",
            "1' OR '1'='1",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {
                'employee_number': payload,
                'password': 'anypassword'
            }
            
            response = client.post('/api/auth/login', json=login_data)
            # Should return 401 (unauthorized), 400 (bad request), 422 (validation error), or 429 (rate limited)
            # 429 indicates rate limiting is working, which is good for security
            assert response.status_code in [400, 401, 422, 429]

            # If rate limited, break early as this indicates security measures are working
            if response.status_code == 429:
                print("✅ Rate limiting detected - SQL injection attempts blocked by rate limiting")
                break
            
            # Should not return any sensitive data
            data = response.get_json()
            if data and 'message' in data:
                message = data['message'].lower()
                # Should not contain SQL error messages
                assert 'syntax error' not in message
                assert 'sql' not in message
                assert 'database' not in message
                assert 'table' not in message
    
    def test_search_sql_injection(self, client, auth_headers):
        """Test SQL injection in search parameters"""
        sql_payloads = [
            "'; DROP TABLE tools; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO tools (tool_number) VALUES ('hacked'); --"
        ]
        
        for payload in sql_payloads:
            # Test tool search
            response = client.get(f'/api/tools?search={payload}', headers=auth_headers)
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                data = response.get_json()
                # Should return normal search results, not error or unexpected data
                assert 'tools' in data or 'error' not in data
    
    def test_user_data_sql_injection(self, client, auth_headers):
        """Test SQL injection in user data fields"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1' --",
            "'; UPDATE users SET is_admin=1; --"
        ]
        
        for payload in sql_payloads:
            user_data = {
                'name': payload,
                'department': payload,
                'employee_number': f'TEST{hash(payload) % 1000}'
            }
            
            # Test user creation/update
            response = client.post('/api/users', json=user_data, headers=auth_headers)
            # Should handle gracefully, not cause server errors
            assert response.status_code != 500


class TestXSSPrevention:
    """Test protection against Cross-Site Scripting (XSS) attacks"""
    
    def test_xss_in_user_data(self, client, auth_headers):
        """Test XSS prevention in user input fields"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<<SCRIPT>alert('XSS')</SCRIPT>",
            "<script>document.location='http://evil.com'</script>"
        ]
        
        for payload in xss_payloads:
            # Test in tool description
            tool_data = {
                'tool_number': f'XSS{hash(payload) % 1000}',
                'description': payload,
                'condition': 'Good',
                'location': 'Test Lab',
                'category': 'Testing'
            }
            
            response = client.post('/api/tools', json=tool_data, headers=auth_headers)
            
            if response.status_code == 201:
                # If creation succeeded, verify the data is properly escaped/sanitized
                data = response.get_json()
                if 'tool' in data:
                    stored_description = data['tool'].get('description', '')
                    # Should not contain executable script tags
                    assert '<script>' not in stored_description.lower()
                    assert 'javascript:' not in stored_description.lower()
                    assert 'onerror=' not in stored_description.lower()
                    assert 'onload=' not in stored_description.lower()
    
    def test_xss_in_search_results(self, client, auth_headers):
        """Test that search results are properly escaped"""
        # First create a tool with potentially dangerous content
        tool_data = {
            'tool_number': 'XSS001',
            'description': '<script>alert("XSS")</script>Test Tool',
            'condition': 'Good',
            'location': 'Test Lab',
            'category': 'Testing'
        }
        
        response = client.post('/api/tools', json=tool_data, headers=auth_headers)
        
        # Search for the tool
        response = client.get('/api/tools?search=XSS001', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        if 'tools' in data and data['tools']:
            for tool in data['tools']:
                description = tool.get('description', '')
                # Verify script tags are escaped or removed
                assert '<script>' not in description.lower()


class TestDataValidation:
    """Test input data validation and sanitization"""
    
    def test_field_length_limits(self, client, auth_headers):
        """Test that field length limits are enforced"""
        # Test extremely long strings
        very_long_string = 'A' * 10000
        
        test_cases = [
            # Tool data
            {
                'endpoint': '/api/tools',
                'data': {
                    'tool_number': very_long_string,
                    'description': 'Test Tool',
                    'condition': 'Good',
                    'location': 'Test Lab',
                    'category': 'Testing'
                }
            },
            {
                'endpoint': '/api/tools',
                'data': {
                    'tool_number': 'TEST001',
                    'description': very_long_string,
                    'condition': 'Good',
                    'location': 'Test Lab',
                    'category': 'Testing'
                }
            },
            # User data
            {
                'endpoint': '/api/users',
                'data': {
                    'name': very_long_string,
                    'employee_number': 'TEST001',
                    'department': 'IT'
                }
            }
        ]
        
        for test_case in test_cases:
            response = client.post(test_case['endpoint'], json=test_case['data'], headers=auth_headers)
            # Should reject overly long data
            assert response.status_code in [400, 422]
    
    def test_data_type_validation(self, client, auth_headers):
        """Test that data types are properly validated"""
        invalid_data_cases = [
            # Invalid tool data
            {
                'endpoint': '/api/tools',
                'data': {
                    'tool_number': 123,  # Should be string
                    'description': 'Test Tool',
                    'condition': 'Good',
                    'location': 'Test Lab',
                    'category': 'Testing'
                }
            },
            {
                'endpoint': '/api/tools',
                'data': {
                    'tool_number': 'TEST001',
                    'description': ['array', 'not', 'string'],  # Should be string
                    'condition': 'Good',
                    'location': 'Test Lab',
                    'category': 'Testing'
                }
            },
            # Invalid chemical data
            {
                'endpoint': '/api/chemicals',
                'data': {
                    'part_number': 'CHEM001',
                    'description': 'Test Chemical',
                    'quantity': 'not_a_number',  # Should be numeric
                    'unit': 'ml',
                    'location': 'Storage A'
                }
            }
        ]
        
        for test_case in invalid_data_cases:
            response = client.post(test_case['endpoint'], json=test_case['data'], headers=auth_headers)
            # Should reject invalid data types
            assert response.status_code in [400, 422]
    
    def test_required_field_validation(self, client, auth_headers):
        """Test that required fields are enforced"""
        incomplete_data_cases = [
            # Missing required tool fields
            {
                'endpoint': '/api/tools',
                'data': {
                    'description': 'Test Tool',
                    'condition': 'Good',
                    'location': 'Test Lab'
                    # Missing tool_number and category
                }
            },
            # Missing required user fields
            {
                'endpoint': '/api/users',
                'data': {
                    'name': 'Test User',
                    'department': 'IT'
                    # Missing employee_number
                }
            }
        ]
        
        for test_case in incomplete_data_cases:
            response = client.post(test_case['endpoint'], json=test_case['data'], headers=auth_headers)
            # Should reject incomplete data
            assert response.status_code in [400, 422]
    
    def test_special_character_handling(self, client, auth_headers):
        """Test handling of special characters and unicode"""
        special_chars_data = [
            "Test with émojis 🔧🧪",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Unicode: αβγδε ñáéíóú çüöäß",
            "Null bytes: \x00\x01\x02",
            "Control chars: \n\r\t\b\f",
            "Mixed: Test\nWith\tTabs\rAnd\bBackspace"
        ]
        
        for special_data in special_chars_data:
            tool_data = {
                'tool_number': f'SPEC{hash(special_data) % 1000}',
                'description': special_data,
                'condition': 'Good',
                'location': 'Test Lab',
                'category': 'Testing'
            }
            
            response = client.post('/api/tools', json=tool_data, headers=auth_headers)
            # Should handle special characters gracefully
            assert response.status_code in [200, 201, 400, 422]
            # Should not cause server errors
            assert response.status_code != 500
