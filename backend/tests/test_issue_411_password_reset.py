"""
Test for Issue #411: Password Reset Token Exposed in API Response
Ensures that reset codes are not exposed in API responses
"""

import json
from models import User
from utils.password_reset_security import get_password_reset_tracker
from utils.rate_limiter import get_rate_limiter


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
    get_rate_limiter().reset_all()

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
    tracker = get_password_reset_tracker()
    tracker.reset_all()
    get_rate_limiter().reset_all()

    # Generate a reset token first
    reset_code = regular_user.generate_reset_token()
    db_session.commit()

    def attempt_confirmation():
        return client.post(
            '/api/auth/reset-password/confirm',
            data=json.dumps({
                'employee_number': regular_user.employee_number,
                'reset_code': 'wrong_code',
                'new_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )

    # First two attempts should return validation errors and trigger backoff
    response = attempt_confirmation()
    assert response.status_code == 400
    tracker.force_unlock(regular_user.employee_number)

    response = attempt_confirmation()
    assert response.status_code == 400
    tracker.force_unlock(regular_user.employee_number)

    # Third attempt invalidates the token
    response = attempt_confirmation()
    assert response.status_code == 400
    assert 'invalidated' in response.get_json()['error'].lower()

    # Generate a fresh token to continue testing rate limit counts
    reset_code = regular_user.generate_reset_token()
    db_session.commit()
    tracker.reset_all()

    # Fourth and fifth attempts count toward rate limit
    response = attempt_confirmation()
    assert response.status_code == 400
    tracker.force_unlock(regular_user.employee_number)

    response = attempt_confirmation()
    assert response.status_code == 400
    tracker.force_unlock(regular_user.employee_number)

    # Sixth attempt should now be rate limited at the IP level
    response = attempt_confirmation()
    assert response.status_code == 429
    data = response.get_json()
    assert 'error' in data
    assert 'too many' in data['error'].lower()


def test_password_reset_confirm_exponential_backoff(client, db_session, regular_user):
    """Ensure exponential backoff locks the account between failed attempts."""
    tracker = get_password_reset_tracker()
    tracker.reset_all()
    get_rate_limiter().reset_all()

    reset_code = regular_user.generate_reset_token()
    db_session.commit()

    # First failed attempt should return 400 but include retry metadata
    response = client.post(
        '/api/auth/reset-password/confirm',
        data=json.dumps({
            'employee_number': regular_user.employee_number,
            'reset_code': 'invalid_code',
            'new_password': 'NewPassword123!'
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Invalid or expired reset code'
    assert data['attempts_remaining'] == 2
    assert data['retry_after'] >= 5

    # Immediate retry should be blocked by backoff
    response = client.post(
        '/api/auth/reset-password/confirm',
        data=json.dumps({
            'employee_number': regular_user.employee_number,
            'reset_code': 'invalid_code',
            'new_password': 'NewPassword123!'
        }),
        content_type='application/json'
    )

    assert response.status_code == 429
    data = response.get_json()
    assert 'too many' in data['error'].lower()
    assert data['retry_after'] >= 1


def test_password_reset_confirm_token_invalidated_after_failures(client, db_session, regular_user):
    """Verify reset token is invalidated after repeated failures."""
    tracker = get_password_reset_tracker()
    tracker.reset_all()
    get_rate_limiter().reset_all()

    reset_code = regular_user.generate_reset_token()
    db_session.commit()

    payload = {
        'employee_number': regular_user.employee_number,
        'reset_code': 'invalid_code',
        'new_password': 'NewPassword123!'
    }

    # Trigger three failed attempts
    for attempt in range(3):
        response = client.post(
            '/api/auth/reset-password/confirm',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # After each failed attempt (except the last) force unlock to simulate waiting
        if attempt < 2:
            tracker.force_unlock(regular_user.employee_number)

    assert response.status_code == 400
    data = response.get_json()
    assert 'invalidated' in data['error'].lower()

    # Token should be cleared from the user record
    db_session.refresh(regular_user)
    assert regular_user.reset_token is None
    assert regular_user.reset_token_expiry is None

    # Even with original token, confirmation should fail
    response = client.post(
        '/api/auth/reset-password/confirm',
        data=json.dumps({
            'employee_number': regular_user.employee_number,
            'reset_code': reset_code,
            'new_password': 'AnotherPassword123!'
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = response.get_json()
    assert 'invalid or expired reset code' in data['error'].lower()

def test_password_reset_workflow_without_code_exposure(client, db_session, regular_user):
    """Test complete password reset workflow without code exposure"""
    tracker = get_password_reset_tracker()
    tracker.reset_all()
    get_rate_limiter().reset_all()

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
    get_rate_limiter().reset_all()

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

