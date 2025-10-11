"""
Test for Issue #412: Weak Password Reset Token - Only 6 Digits
Ensures that reset tokens are cryptographically secure and not easily brute-forceable
"""

import pytest
import re
from datetime import timedelta
from models import User, get_current_time


def test_reset_token_is_strong(db_session):
    """Test that reset token is not a simple 6-digit code"""
    user = User(
        name='Test User',
        employee_number='TEST001',
        department='Testing',
        is_admin=False,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Generate reset token
    reset_code = user.generate_reset_token()
    
    # Verify token is NOT a 6-digit code
    assert not re.match(r'^\d{6}$', reset_code), "Token should not be a 6-digit code"
    
    # Verify token is long enough (at least 32 characters)
    assert len(reset_code) >= 32, f"Token should be at least 32 characters, got {len(reset_code)}"
    
    # Verify token contains alphanumeric characters (not just digits)
    assert re.search(r'[a-zA-Z]', reset_code), "Token should contain letters"
    assert re.search(r'[0-9]', reset_code) or re.search(r'[-_]', reset_code), "Token should contain numbers or special chars"


def test_reset_token_entropy(db_session):
    """Test that reset tokens have high entropy (are not predictable)"""
    user = User(
        name='Test User',
        employee_number='TEST002',
        department='Testing',
        is_admin=False,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Generate multiple tokens
    tokens = []
    for _ in range(10):
        token = user.generate_reset_token()
        tokens.append(token)
        db_session.commit()
    
    # Verify all tokens are unique
    assert len(set(tokens)) == len(tokens), "All tokens should be unique"
    
    # Verify tokens are sufficiently different (no common prefixes/suffixes)
    for i in range(len(tokens) - 1):
        for j in range(i + 1, len(tokens)):
            # Check that tokens don't share long common prefixes
            common_prefix_len = 0
            for k in range(min(len(tokens[i]), len(tokens[j]))):
                if tokens[i][k] == tokens[j][k]:
                    common_prefix_len += 1
                else:
                    break
            assert common_prefix_len < 10, "Tokens should not have long common prefixes"


def test_reset_token_expiry_reduced(db_session):
    """Test that reset token expiry is reduced from 1 hour to 15 minutes"""
    user = User(
        name='Test User',
        employee_number='TEST003',
        department='Testing',
        is_admin=False,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Record time before generating token
    time_before = get_current_time()
    
    # Generate reset token
    reset_code = user.generate_reset_token()
    db_session.commit()
    
    # Verify expiry is set
    assert user.reset_token_expiry is not None
    
    # Calculate expected expiry (15 minutes from now)
    expected_expiry = time_before + timedelta(minutes=15)
    
    # Verify expiry is approximately 15 minutes (allow 1 minute tolerance)
    time_diff = abs((user.reset_token_expiry - expected_expiry).total_seconds())
    assert time_diff < 60, f"Expiry should be ~15 minutes, but difference is {time_diff} seconds"
    
    # Verify expiry is NOT 1 hour
    one_hour_expiry = time_before + timedelta(hours=1)
    time_diff_hour = abs((user.reset_token_expiry - one_hour_expiry).total_seconds())
    assert time_diff_hour > 2600, "Expiry should not be 1 hour (should be 15 minutes)"


def test_reset_token_url_safe(db_session):
    """Test that reset token is URL-safe (can be used in URLs without encoding)"""
    user = User(
        name='Test User',
        employee_number='TEST004',
        department='Testing',
        is_admin=False,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Generate reset token
    reset_code = user.generate_reset_token()
    
    # Verify token only contains URL-safe characters
    # URL-safe characters: A-Z, a-z, 0-9, -, _
    assert re.match(r'^[A-Za-z0-9_-]+$', reset_code), "Token should only contain URL-safe characters"


def test_reset_token_verification_still_works(db_session):
    """Test that token verification still works with the new stronger tokens"""
    user = User(
        name='Test User',
        employee_number='TEST005',
        department='Testing',
        is_admin=False,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Generate reset token
    reset_code = user.generate_reset_token()
    db_session.commit()
    
    # Verify correct token is accepted
    assert user.check_reset_token(reset_code) == True
    
    # Verify incorrect token is rejected
    assert user.check_reset_token('wrong_token') == False
    assert user.check_reset_token('123456') == False


def test_reset_token_brute_force_resistance(db_session):
    """Test that the token space is large enough to resist brute force"""
    user = User(
        name='Test User',
        employee_number='TEST006',
        department='Testing',
        is_admin=False,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Generate reset token
    reset_code = user.generate_reset_token()
    
    # Calculate approximate token space
    # URL-safe base64 uses 64 characters (A-Z, a-z, 0-9, -, _)
    # For a 43-character token: 64^43 ≈ 2^258 combinations
    # This is astronomically large and infeasible to brute force
    
    # Verify token length provides sufficient entropy
    # Minimum 32 characters from token_urlsafe(32) generates ~43 chars
    assert len(reset_code) >= 40, "Token should be at least 40 characters for sufficient entropy"
    
    # Verify token is not in a small predictable space
    # Old 6-digit code had only 1,000,000 combinations
    # New token should have vastly more combinations
    # Even with just 32 characters of base64, we have 64^32 ≈ 2^192 combinations

