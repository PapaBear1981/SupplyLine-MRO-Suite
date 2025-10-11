"""
Test for Issue #411: Password Reset Token Exposed in API Response
Ensures that reset codes are not exposed in API responses
"""

import pytest
import json
from models import User


def test_password_reset_request_does_not_expose_code(client, db_session, regular_user):
    """Test that password reset request does not return the reset code"""
    response = client.post(
        '/api/auth/reset-password/request',
        data=json.dumps({'employee_number': regular_user.employee_number}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify response does not contain reset_code
    assert 'reset_code' not in data
    assert 'message' in data
    
    # Verify generic message is returned
    assert 'registered' in data['message'].lower()


def test_password_reset_request_for_nonexistent_user(client, db_session):
    """Test that password reset request returns same message for non-existent users"""
    response = client.post(
        '/api/auth/reset-password/request',
        data=json.dumps({'employee_number': 'NONEXISTENT'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Should return same generic message (prevents user enumeration)
    assert 'reset_code' not in data
    assert 'message' in data
    assert 'registered' in data['message'].lower()


def test_password_reset_token_stored_in_database(client, db_session, regular_user):
    """Test that reset token is properly stored in database"""
    # Request password reset
    response = client.post(
        '/api/auth/reset-password/request',
        data=json.dumps({'employee_number': regular_user.employee_number}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Refresh user from database
    db_session.refresh(regular_user)
    
    # Verify reset token is set in database
    assert regular_user.reset_token is not None
    assert regular_user.reset_token_expiry is not None


def test_password_reset_rate_limiting(client, db_session, regular_user):
    """Test that password reset requests are rate limited"""
    # Make multiple requests
    for i in range(4):
        response = client.post(
            '/api/auth/reset-password/request',
            data=json.dumps({'employee_number': regular_user.employee_number}),
            content_type='application/json'
        )
        
        if i < 3:
            # First 3 requests should succeed
            assert response.status_code == 200
        else:
            # 4th request should be rate limited
            assert response.status_code == 429
            data = response.get_json()
            assert 'error' in data
            assert 'too many' in data['error'].lower()


def test_password_reset_confirm_rate_limiting(client, db_session, regular_user):
    """Test that password reset confirmation is rate limited"""
    # Generate a reset token first
    reset_code = regular_user.generate_reset_token()
    db_session.commit()
    
    # Make multiple failed confirmation attempts
    for i in range(6):
        response = client.post(
            '/api/auth/reset-password/confirm',
            data=json.dumps({
                'employee_number': regular_user.employee_number,
                'reset_code': 'wrong_code',
                'new_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )
        
        if i < 5:
            # First 5 requests should process (but fail validation)
            assert response.status_code in [400, 200]
        else:
            # 6th request should be rate limited
            assert response.status_code == 429
            data = response.get_json()
            assert 'error' in data
            assert 'too many' in data['error'].lower()


def test_password_reset_workflow_without_code_exposure(client, db_session, regular_user):
    """Test complete password reset workflow without code exposure"""
    # Step 1: Request password reset
    response = client.post(
        '/api/auth/reset-password/request',
        data=json.dumps({'employee_number': regular_user.employee_number}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'reset_code' not in data
    
    # Step 2: Get the reset code from database (simulating admin retrieval or email)
    db_session.refresh(regular_user)
    # In real scenario, this would be sent via email
    # For testing, we need to generate it again to get the plain text
    reset_code = regular_user.generate_reset_token()
    db_session.commit()
    
    # Step 3: Confirm password reset with the code
    new_password = 'NewSecurePassword123!'
    response = client.post(
        '/api/auth/reset-password/confirm',
        data=json.dumps({
            'employee_number': regular_user.employee_number,
            'reset_code': reset_code,
            'new_password': new_password
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Step 4: Verify new password works
    db_session.refresh(regular_user)
    assert regular_user.check_password(new_password)


def test_password_reset_activity_logged(client, db_session, regular_user):
    """Test that password reset requests are logged"""
    from models import UserActivity
    
    # Count activities before
    activities_before = UserActivity.query.filter_by(
        user_id=regular_user.id,
        activity_type='password_reset_request'
    ).count()
    
    # Request password reset
    response = client.post(
        '/api/auth/reset-password/request',
        data=json.dumps({'employee_number': regular_user.employee_number}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Count activities after
    activities_after = UserActivity.query.filter_by(
        user_id=regular_user.id,
        activity_type='password_reset_request'
    ).count()
    
    # Verify activity was logged
    assert activities_after == activities_before + 1

