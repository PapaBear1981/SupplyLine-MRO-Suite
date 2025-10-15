"""
Tests for JWT authentication system
"""

import json
from auth import JWTManager
from models import User


class TestJWTAuthentication:
    """Test JWT authentication functionality"""

    def test_login_success(self, client, admin_user, db_session):
        """Test successful login with valid credentials"""
        response = client.post('/api/auth/login',
                             json={
                                 'employee_number': 'ADMTEST001',
                                 'password': 'admin123'
                             })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['employee_number'] == 'ADMTEST001'
        assert data['user']['is_admin'] is True
        assert data['token_type'] == 'Bearer'
        assert data['expires_in'] == 900  # 15 minutes expiry

    def test_login_invalid_credentials(self, client, admin_user):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login',
                             json={
                                 'employee_number': 'ADMTEST001',
                                 'password': 'wrongpassword'
                             })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid employee number or password'
        assert data['code'] == 'INVALID_CREDENTIALS'

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/api/auth/login',
                             json={
                                 'employee_number': 'NONEXISTENT',
                                 'password': 'password'
                             })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid employee number or password'

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/auth/login', json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing employee_number or password' in data['error']

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user"""
        user = User(
            name='Inactive User',
            employee_number='INACTIVE001',
            department='Test',
            is_admin=False,
            is_active=False
        )
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()

        response = client.post('/api/auth/login',
                             json={
                                 'employee_number': 'INACTIVE001',
                                 'password': 'password123'
                             })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Account is inactive'

    def test_token_refresh_success(self, client, admin_user):
        """Test successful token refresh"""
        # First login to get tokens
        login_response = client.post('/api/auth/login',
                                   json={
                                       'employee_number': 'ADMIN001',
                                       'password': 'admin123'
                                   })

        login_data = json.loads(login_response.data)
        refresh_token = login_data['refresh_token']

        # Refresh tokens
        response = client.post('/api/auth/refresh',
                             json={'refresh_token': refresh_token})

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['message'] == 'Tokens refreshed successfully'

    def test_token_refresh_invalid_token(self, client):
        """Test token refresh with invalid token"""
        response = client.post('/api/auth/refresh',
                             json={'refresh_token': 'invalid_token'})

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid or expired refresh token'

    def test_logout_success(self, client, auth_headers_admin):
        """Test successful logout"""
        response = client.post('/api/auth/logout', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logged out successfully'

    def test_logout_without_token(self, client):
        """Test logout without authentication token"""
        response = client.post('/api/auth/logout')

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Authentication required'

    def test_get_current_user_success(self, client, auth_headers_admin, admin_user):
        """Test getting current user info"""
        response = client.get('/api/auth/me', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'user' in data
        assert data['user']['employee_number'] == 'ADMIN001'
        assert data['user']['is_admin'] is True

    def test_get_current_user_without_token(self, client):
        """Test getting current user without token"""
        response = client.get('/api/auth/me')

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Authentication required'

    def test_auth_status_authenticated(self, client, auth_headers_admin):
        """Test auth status when authenticated"""
        response = client.get('/api/auth/status', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['authenticated'] is True
        assert 'user' in data
        assert data['user']['employee_number'] == 'ADMIN001'

    def test_auth_status_unauthenticated(self, client):
        """Test auth status when not authenticated"""
        response = client.get('/api/auth/status')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['authenticated'] is False
        assert data['message'] == 'Not authenticated'


class TestJWTManager:
    """Test JWTManager utility functions"""

    def test_generate_tokens(self, app, admin_user):
        """Test token generation"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            assert 'access_token' in tokens
            assert 'refresh_token' in tokens
            assert 'expires_in' in tokens
            assert 'token_type' in tokens
            assert tokens['token_type'] == 'Bearer'

    def test_verify_access_token(self, app, admin_user):
        """Test access token verification"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            access_token = tokens['access_token']

            payload = JWTManager.verify_token(access_token, 'access')

            assert payload is not None
            assert payload['user_id'] == admin_user.id
            assert payload['type'] == 'access'
            assert payload['is_admin'] is True

    def test_verify_refresh_token(self, app, admin_user):
        """Test refresh token verification"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            refresh_token = tokens['refresh_token']

            payload = JWTManager.verify_token(refresh_token, 'refresh')

            assert payload is not None
            assert payload['user_id'] == admin_user.id
            assert payload['type'] == 'refresh'

    def test_verify_invalid_token(self, app):
        """Test verification of invalid token"""
        with app.app_context():
            payload = JWTManager.verify_token('invalid_token', 'access')
            assert payload is None

    def test_refresh_access_token(self, app, admin_user):
        """Test refreshing access token"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            refresh_token = tokens['refresh_token']

            new_tokens = JWTManager.refresh_access_token(refresh_token)

            assert new_tokens is not None
            assert 'access_token' in new_tokens
            assert 'refresh_token' in new_tokens
