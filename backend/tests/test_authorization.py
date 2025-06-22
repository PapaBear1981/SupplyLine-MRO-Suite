"""
Security tests for authorization and access control
Tests role-based access control, admin protection, and user data isolation
"""

import pytest
import json
from models import User, Tool, Chemical, db


class TestRoleBasedAccessControl:
    """Test role-based access control (RBAC)"""
    
    def test_admin_only_endpoints(self, client, test_user, admin_user):
        """Test that admin-only endpoints reject non-admin users"""
        # Login as regular user
        login_data = {
            'employee_number': test_user.employee_number,
            'password': 'testpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user_token = response.get_json()['access_token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # Login as admin
        login_data = {
            'employee_number': admin_user.employee_number,
            'password': 'adminpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        admin_token = response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Test admin-only endpoints
        admin_endpoints = [
            ('GET', '/api/admin/users'),
            ('POST', '/api/admin/users'),
            ('GET', '/api/admin/dashboard'),
            ('GET', '/api/admin/audit-logs'),
            ('POST', '/api/admin/system-settings'),
            ('DELETE', '/api/admin/users/1'),
            ('PUT', '/api/admin/users/1'),
        ]
        
        for method, endpoint in admin_endpoints:
            # Regular user should be denied
            if method == 'GET':
                response = client.get(endpoint, headers=user_headers)
            elif method == 'POST':
                response = client.post(endpoint, json={}, headers=user_headers)
            elif method == 'PUT':
                response = client.put(endpoint, json={}, headers=user_headers)
            elif method == 'DELETE':
                response = client.delete(endpoint, headers=user_headers)
            
            assert response.status_code in [403, 404], f"Regular user should be denied access to {method} {endpoint}"
            
            # Admin should be allowed (or at least not forbidden due to role)
            if method == 'GET':
                response = client.get(endpoint, headers=admin_headers)
            elif method == 'POST':
                response = client.post(endpoint, json={}, headers=admin_headers)
            elif method == 'PUT':
                response = client.put(endpoint, json={}, headers=admin_headers)
            elif method == 'DELETE':
                response = client.delete(endpoint, headers=admin_headers)
            
            # Admin should not get 403 (may get 404 if endpoint doesn't exist, or 400 for bad data)
            assert response.status_code != 403, f"Admin should not be forbidden from {method} {endpoint}"
    
    def test_user_data_isolation(self, client, test_user, admin_user):
        """Test that users can only access their own data"""
        # Create another test user
        with client.application.app_context():
            other_user = User(
                name='Other User',
                employee_number='OTHER001',
                department='Engineering',
                is_admin=False,
                is_active=True
            )
            other_user.set_password('otherpass123')
            db.session.add(other_user)
            db.session.commit()
            other_user_id = other_user.id
        
        # Login as first user
        login_data = {
            'employee_number': test_user.employee_number,
            'password': 'testpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user1_token = response.get_json()['access_token']
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        
        # Login as second user
        login_data = {
            'employee_number': 'OTHER001',
            'password': 'otherpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user2_token = response.get_json()['access_token']
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        
        # Test that user1 cannot access user2's data
        user_specific_endpoints = [
            f'/api/users/{other_user_id}',
            f'/api/users/{other_user_id}/checkouts',
            f'/api/users/{other_user_id}/activity',
        ]
        
        for endpoint in user_specific_endpoints:
            response = client.get(endpoint, headers=user1_headers)
            # Should be denied access to other user's data
            assert response.status_code in [403, 404], f"User should not access other user's data at {endpoint}"
    
    def test_inactive_user_access(self, client):
        """Test that inactive users cannot access the system"""
        # Create inactive user
        with client.application.app_context():
            inactive_user = User(
                name='Inactive User',
                employee_number='INACTIVE001',
                department='IT',
                is_admin=False,
                is_active=False  # Inactive
            )
            inactive_user.set_password('inactivepass123')
            db.session.add(inactive_user)
            db.session.commit()
        
        # Try to login as inactive user
        login_data = {
            'employee_number': 'INACTIVE001',
            'password': 'inactivepass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
        
        data = response.get_json()
        assert 'inactive' in data.get('message', '').lower() or 'disabled' in data.get('message', '').lower()


class TestPrivilegeEscalation:
    """Test protection against privilege escalation attacks"""
    
    def test_user_cannot_promote_self(self, client, test_user):
        """Test that regular users cannot make themselves admin"""
        # Login as regular user
        login_data = {
            'employee_number': test_user.employee_number,
            'password': 'testpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user_token = response.get_json()['access_token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to update own profile to become admin
        update_data = {
            'is_admin': True,
            'name': 'Hacked Admin'
        }
        
        response = client.put(f'/api/users/{test_user.id}', json=update_data, headers=user_headers)
        # Should be denied or ignore the admin flag
        assert response.status_code in [403, 400, 422]
        
        # Verify user is still not admin
        response = client.get('/api/user/profile', headers=user_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('user', {}).get('is_admin') is False
    
    def test_user_cannot_modify_other_users(self, client, test_user):
        """Test that users cannot modify other users' data"""
        # Create another user
        with client.application.app_context():
            target_user = User(
                name='Target User',
                employee_number='TARGET001',
                department='Engineering',
                is_admin=False,
                is_active=True
            )
            target_user.set_password('targetpass123')
            db.session.add(target_user)
            db.session.commit()
            target_user_id = target_user.id
        
        # Login as first user
        login_data = {
            'employee_number': test_user.employee_number,
            'password': 'testpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user_token = response.get_json()['access_token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to modify other user
        update_data = {
            'name': 'Hacked Name',
            'is_admin': True,
            'department': 'Hacked Department'
        }
        
        response = client.put(f'/api/users/{target_user_id}', json=update_data, headers=user_headers)
        # Should be denied
        assert response.status_code in [403, 404]


class TestResourceAccess:
    """Test access control for resources (tools, chemicals, etc.)"""
    
    def test_tool_access_control(self, client, test_user, admin_user):
        """Test access control for tool operations"""
        # Login as regular user
        login_data = {
            'employee_number': test_user.employee_number,
            'password': 'testpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user_token = response.get_json()['access_token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # Login as admin
        login_data = {
            'employee_number': admin_user.employee_number,
            'password': 'adminpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        admin_token = response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Test tool creation (might be admin-only)
        tool_data = {
            'tool_number': 'AUTHTEST001',
            'description': 'Authorization Test Tool',
            'condition': 'Good',
            'location': 'Test Lab',
            'category': 'Testing'
        }
        
        # Regular user tries to create tool
        response = client.post('/api/tools', json=tool_data, headers=user_headers)
        user_can_create = response.status_code in [200, 201]
        
        # Admin tries to create tool
        response = client.post('/api/tools', json=tool_data, headers=admin_headers)
        admin_can_create = response.status_code in [200, 201]
        
        # At minimum, admin should be able to create tools
        assert admin_can_create, "Admin should be able to create tools"
        
        # If regular users can't create tools, that's a valid security policy
        if not user_can_create:
            assert response.status_code in [403, 401], "If users can't create tools, should get proper error code"
    
    def test_checkout_authorization(self, client, test_user):
        """Test that users can only manage their own checkouts"""
        # Login
        login_data = {
            'employee_number': test_user.employee_number,
            'password': 'testpass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        user_token = response.get_json()['access_token']
        user_headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to access all checkouts (might be admin-only)
        response = client.get('/api/checkouts', headers=user_headers)
        
        if response.status_code == 200:
            # If user can see checkouts, verify they only see their own
            data = response.get_json()
            checkouts = data.get('checkouts', [])
            
            for checkout in checkouts:
                # Should only see own checkouts
                assert checkout.get('user_id') == test_user.id, "User should only see their own checkouts"
        else:
            # If denied, should get proper error code
            assert response.status_code in [403, 401], "Should get proper authorization error"
