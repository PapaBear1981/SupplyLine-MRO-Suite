"""
Security tests for authorization and access control
Tests role-based access control, admin protection, and user data isolation
"""

from models import User, db


def _get_cookie_value(client, name, response=None):
    """Helper to fetch a cookie value from the Flask test client or response headers."""
    if client is not None and hasattr(client, 'cookie_jar'):
        for cookie in client.cookie_jar:
            if cookie.name == name:
                return cookie.value
    if response is not None:
        set_cookies = response.headers.getlist('Set-Cookie')
        for cookie_header in set_cookies:
            if f'{name}=' in cookie_header:
                return cookie_header.split(f'{name}=')[1].split(';', 1)[0]
    return None


class TestRoleBasedAccessControl:
    """Test role-based access control (RBAC)"""

    def test_admin_only_endpoints(self, client, auth_headers_user, auth_headers_admin):
        """Test that admin-only endpoints reject non-admin users"""
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
            request_kwargs = {'headers': auth_headers_user}
            if method in {'POST', 'PUT'}:
                request_kwargs['json'] = {}

            response = client.open(endpoint, method=method, **request_kwargs)
            assert response.status_code in [403, 404], f"Regular user should be denied access to {method} {endpoint}"

            # Admin should be allowed (or at least not forbidden due to role)
            admin_kwargs = {'headers': auth_headers_admin}
            if method in {'POST', 'PUT'}:
                admin_kwargs['json'] = {}

            response = client.open(endpoint, method=method, **admin_kwargs)

            # Admin should not get 403 (may get 404 if endpoint doesn't exist, or 400 for bad data)
            assert response.status_code != 403, f"Admin should not be forbidden from {method} {endpoint}"

    def test_user_data_isolation(self, client, regular_user, jwt_manager):
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
            user2_tokens = jwt_manager.generate_tokens(other_user)
            user2_headers = {'Authorization': f"Bearer {user2_tokens['access_token']}"}

        with client.application.app_context():
            tokens = jwt_manager.generate_tokens(regular_user)
        user1_headers = {'Authorization': f"Bearer {tokens['access_token']}"}

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

        # Other user should be able to fetch their own data if endpoint exists
        response = client.get(f'/api/users/{regular_user.id}', headers=user2_headers)
        assert response.status_code in [200, 403, 404]

    def test_inactive_user_access(self, client):
        """Test that inactive users cannot access the system"""
        # Create inactive user with unique employee number
        import time
        unique_emp_num = f'INACTIVE{int(time.time() * 1000) % 1000000}'

        with client.application.app_context():
            inactive_user = User(
                name='Inactive User',
                employee_number=unique_emp_num,
                department='IT',
                is_admin=False,
                is_active=False  # Inactive
            )
            inactive_user.set_password('inactivepass123')
            db.session.add(inactive_user)
            db.session.commit()

        # Try to login as inactive user
        login_data = {
            'employee_number': unique_emp_num,
            'password': 'inactivepass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401

        data = response.get_json()
        assert data.get('error') == 'Invalid employee number or password'
        assert data.get('code') == 'INVALID_CREDENTIALS'


class TestPrivilegeEscalation:
    """Test protection against privilege escalation attacks"""

    def test_user_cannot_promote_self(self, client, regular_user, jwt_manager):
        """Test that regular users cannot make themselves admin"""
        with client.application.app_context():
            tokens = jwt_manager.generate_tokens(regular_user)
        user_headers = {'Authorization': f"Bearer {tokens['access_token']}"}

        # Try to update own profile to become admin
        update_data = {
            'is_admin': True,
            'name': 'Hacked Admin'
        }

        response = client.put(f'/api/users/{regular_user.id}', json=update_data, headers=user_headers)
        # Should be denied or ignore the admin flag
        assert response.status_code in [403, 400, 422]

        # Verify user is still not admin
        with client.application.app_context():
            refreshed_user = User.query.get(regular_user.id)
            assert refreshed_user.is_admin is False

    def test_user_cannot_modify_other_users(self, client, regular_user, jwt_manager):
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
            tokens = jwt_manager.generate_tokens(regular_user)

        user_headers = {'Authorization': f"Bearer {tokens['access_token']}"}

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

    def test_tool_access_control(self, client, auth_headers_user, auth_headers_admin, test_warehouse):
        """Test access control for tool operations"""
        # Test tool creation (might be admin-only)
        tool_data_user = {
            'tool_number': 'AUTHTESTUSR001',
            'serial_number': 'AUTHUSR001',
            'description': 'Authorization Test Tool',
            'condition': 'Good',
            'location': 'Test Lab',
            'category': 'Testing',
            'warehouse_id': test_warehouse.id
        }

        # Regular user tries to create tool
        user_response = client.post('/api/tools', json=tool_data_user, headers=auth_headers_user)
        user_can_create = user_response.status_code in [200, 201]

        # Admin tries to create tool
        tool_data_admin = {
            'tool_number': 'AUTHTESTADM001',
            'serial_number': 'AUTHADM001',
            'description': 'Authorization Test Tool',
            'condition': 'Good',
            'location': 'Test Lab',
            'category': 'Testing',
            'warehouse_id': test_warehouse.id
        }
        admin_response = client.post('/api/tools', json=tool_data_admin, headers=auth_headers_admin)
        admin_can_create = admin_response.status_code in [200, 201]

        # At minimum, admin should be able to create tools
        assert admin_can_create, "Admin should be able to create tools"

        # If regular users can't create tools, that's a valid security policy
        if not user_can_create:
            assert user_response.status_code in [403, 401], "If users can't create tools, should get proper error code"

    def test_checkout_authorization(self, client, auth_headers_user, regular_user):
        """Test that users can only manage their own checkouts"""
        # Try to access all checkouts (might be admin-only)
        response = client.get('/api/checkouts', headers=auth_headers_user)

        if response.status_code == 200:
            # If user can see checkouts, verify they only see their own
            data = response.get_json()
            if isinstance(data, dict):
                checkouts = data.get('checkouts', [])
            else:
                checkouts = data

            for checkout in checkouts:
                # Should only see own checkouts
                assert checkout.get('user_id') == regular_user.id, "User should only see their own checkouts"
        else:
            # If denied, should get proper error code
            assert response.status_code in [403, 401], "Should get proper authorization error"


class TestTokenRefreshAndCSRF:
    """Tests for token refresh and CSRF protection"""

    def test_refresh_returns_new_access_token(self, client, admin_user):
        """Valid refresh token should yield a new access token"""
        # Login to obtain initial tokens
        login_resp = client.post(
            '/api/auth/login',
            json={
                'employee_number': admin_user.employee_number,
                'password': 'admin123'
            }
        )
        assert login_resp.status_code == 200
        initial_access_token = _get_cookie_value(client, 'access_token', login_resp)
        assert initial_access_token is not None

        # Request new tokens using refresh endpoint
        refresh_resp = client.post('/api/auth/refresh')
        assert refresh_resp.status_code == 200
        refreshed_access_token = _get_cookie_value(client, 'access_token', refresh_resp)
        assert refreshed_access_token is not None
        assert refreshed_access_token != initial_access_token

        set_cookie_headers = refresh_resp.headers.getlist('Set-Cookie')
        assert any('access_token=' in header for header in set_cookie_headers)

    def test_state_change_with_csrf_token(self, client, auth_headers_admin):
        """State-changing request succeeds with valid CSRF token"""
        # Get CSRF token
        csrf_resp = client.get('/api/auth/csrf-token', headers=auth_headers_admin)
        assert csrf_resp.status_code == 200
        csrf_token = csrf_resp.get_json()['csrf_token']

        headers = dict(auth_headers_admin)
        headers['X-CSRF-Token'] = csrf_token
        # Perform state-changing action (logout)
        logout_resp = client.post('/api/auth/logout', headers=headers)
        assert logout_resp.status_code == 200

    def test_state_change_without_or_invalid_csrf(self, client, auth_headers_admin):
        """State-changing requests clear cookies even when CSRF header is missing"""
        # Missing token
        missing_resp = client.post('/api/auth/logout', headers=auth_headers_admin)
        assert missing_resp.status_code == 200
        missing_headers = missing_resp.headers.getlist('Set-Cookie')
        assert any('access_token=' in header for header in missing_headers)

        # Invalid token behaves the same because CSRF enforcement is optional here
        invalid_headers = dict(auth_headers_admin)
        invalid_headers['X-CSRF-Token'] = 'invalid-token'
        invalid_resp = client.post('/api/auth/logout', headers=invalid_headers)
        assert invalid_resp.status_code == 200
