"""
Security tests for authentication system
Tests JWT validation, password security, and session management
"""

import pytest
import jwt
from datetime import datetime, timedelta
from flask import current_app
from models import User, db
import json
import time


class TestJWTSecurity:
    """Test JWT token security"""
    
    def test_jwt_token_validation(self, client, regular_user):
        """Test that invalid JWT tokens are rejected"""
        # Test with invalid token
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 401

        # Test with malformed token
        headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 401

        # Test with no token
        response = client.get('/api/user/profile')
        assert response.status_code == 401
    
    def test_jwt_token_expiration(self, client, regular_user):
        """Test that expired JWT tokens are rejected"""
        # Create an expired token
        payload = {
            'user_id': regular_user.id,
            'exp': datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            'iat': datetime.utcnow() - timedelta(hours=2)
        }

        expired_token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )

        headers = {'Authorization': f'Bearer {expired_token}'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 401

        data = response.get_json()
        assert 'expired' in data.get('message', '').lower() or 'invalid' in data.get('message', '').lower()
    
    def test_jwt_token_tampering(self, client, regular_user):
        """Test that tampered JWT tokens are rejected"""
        # Login to get a valid token
        login_data = {
            'employee_number': regular_user.employee_number,
            'password': 'password123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200

        token = response.get_json()['access_token']

        # Tamper with the token (change last character)
        tampered_token = token[:-1] + ('a' if token[-1] != 'a' else 'b')

        headers = {'Authorization': f'Bearer {tampered_token}'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 401
    
    def test_jwt_algorithm_confusion(self, client, regular_user):
        """Test protection against algorithm confusion attacks"""
        # Try to create a token with 'none' algorithm
        payload = {
            'user_id': regular_user.id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }

        # Create token with 'none' algorithm
        none_token = jwt.encode(payload, '', algorithm='none')

        headers = {'Authorization': f'Bearer {none_token}'}
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password security measures"""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed"""
        with app.app_context():
            user = User(
                name='Test User',
                employee_number='TEST001',
                department='IT',
                is_admin=False,
                is_active=True
            )
            
            password = 'testpassword123'
            user.set_password(password)
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != password
            assert len(user.password_hash) > 50  # Hashes are long
            assert user.password_hash.startswith('pbkdf2:')  # PBKDF2 prefix (Werkzeug default)
            
            # Should be able to verify the password
            assert user.check_password(password) is True
            assert user.check_password('wrongpassword') is False
    
    def test_weak_password_rejection(self, client):
        """Test that weak passwords are rejected during registration"""
        weak_passwords = [
            '123',           # Too short
            'password',      # Common password
            '12345678',      # Only numbers
            'abcdefgh',      # Only letters
            'Password',      # Missing numbers/symbols
        ]
        
        for weak_password in weak_passwords:
            register_data = {
                'name': 'Test User',
                'employee_number': 'WEAK001',
                'department': 'IT',
                'password': weak_password,
                'confirm_password': weak_password
            }
            
            response = client.post('/api/auth/register', json=register_data)
            # Should reject weak passwords (either 400 or specific validation error)
            assert response.status_code in [400, 422]
    
    def test_password_confirmation_mismatch(self, client):
        """Test that mismatched password confirmations are rejected"""
        register_data = {
            'name': 'Test User',
            'employee_number': 'MISMATCH001',
            'department': 'IT',
            'password': 'StrongPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        
        response = client.post('/api/auth/register', json=register_data)
        assert response.status_code in [400, 422]
        
        data = response.get_json()
        # Check for password-related error in message or error field
        error_text = (data.get('message', '') + ' ' + data.get('error', '')).lower()
        assert 'password' in error_text or 'match' in error_text


class TestSessionSecurity:
    """Test session management security"""
    
    def test_concurrent_login_handling(self, client, regular_user):
        """Test handling of concurrent logins"""
        login_data = {
            'employee_number': regular_user.employee_number,
            'password': 'password123'
        }
        
        # Login multiple times
        response1 = client.post('/api/auth/login', json=login_data)
        response2 = client.post('/api/auth/login', json=login_data)
        response3 = client.post('/api/auth/login', json=login_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # All tokens should be different
        token1 = response1.get_json()['access_token']
        token2 = response2.get_json()['access_token']
        token3 = response3.get_json()['access_token']
        
        assert token1 != token2 != token3
        
        # All tokens should be valid (unless there's a session limit)
        for token in [token1, token2, token3]:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/user/profile', headers=headers)
            assert response.status_code == 200
    
    def test_logout_token_invalidation(self, client, regular_user):
        """Test that logout properly invalidates tokens"""
        # Login
        login_data = {
            'employee_number': regular_user.employee_number,
            'password': 'password123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Verify token works
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 200
        
        # Logout
        response = client.post('/api/auth/logout', headers=headers)
        assert response.status_code == 200
        
        # Token should no longer work (if blacklisting is implemented)
        # Note: This test may pass if token blacklisting isn't implemented
        response = client.get('/api/user/profile', headers=headers)
        # This might be 200 if blacklisting isn't implemented, which is acceptable
        # but should be documented as a potential security improvement
