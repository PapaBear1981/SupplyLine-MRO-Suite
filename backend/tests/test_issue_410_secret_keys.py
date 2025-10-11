"""
Test for Issue #410: Hardcoded Default Secret Keys
Ensures that the application requires SECRET_KEY and JWT_SECRET_KEY to be set
"""

import pytest
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_secret_key_required_in_production():
    """Test that SECRET_KEY is required when not in testing mode"""
    # Save original environment
    original_secret = os.environ.get('SECRET_KEY')
    original_jwt_secret = os.environ.get('JWT_SECRET_KEY')
    original_flask_env = os.environ.get('FLASK_ENV')
    
    try:
        # Remove secrets and set production mode
        if 'SECRET_KEY' in os.environ:
            del os.environ['SECRET_KEY']
        if 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
        os.environ['FLASK_ENV'] = 'production'
        
        # Force reload of config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # Importing config should raise RuntimeError
        with pytest.raises(RuntimeError, match='SECRET_KEY environment variable must be set'):
            import config
            # Force class evaluation
            _ = config.Config.SECRET_KEY
            
    finally:
        # Restore original environment
        if original_secret:
            os.environ['SECRET_KEY'] = original_secret
        elif 'SECRET_KEY' in os.environ:
            del os.environ['SECRET_KEY']
            
        if original_jwt_secret:
            os.environ['JWT_SECRET_KEY'] = original_jwt_secret
        elif 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
            
        if original_flask_env:
            os.environ['FLASK_ENV'] = original_flask_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        
        # Reload config module to restore normal state
        if 'config' in sys.modules:
            del sys.modules['config']


def test_jwt_secret_key_required_in_production():
    """Test that JWT_SECRET_KEY is required when not in testing mode"""
    # Save original environment
    original_secret = os.environ.get('SECRET_KEY')
    original_jwt_secret = os.environ.get('JWT_SECRET_KEY')
    original_flask_env = os.environ.get('FLASK_ENV')
    
    try:
        # Set SECRET_KEY but remove JWT_SECRET_KEY
        os.environ['SECRET_KEY'] = 'test-secret-for-validation'
        if 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
        os.environ['FLASK_ENV'] = 'production'
        
        # Force reload of config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # Importing config should raise RuntimeError
        with pytest.raises(RuntimeError, match='JWT_SECRET_KEY environment variable must be set'):
            import config
            # Force class evaluation
            _ = config.Config.JWT_SECRET_KEY
            
    finally:
        # Restore original environment
        if original_secret:
            os.environ['SECRET_KEY'] = original_secret
        elif 'SECRET_KEY' in os.environ:
            del os.environ['SECRET_KEY']
            
        if original_jwt_secret:
            os.environ['JWT_SECRET_KEY'] = original_jwt_secret
        elif 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
            
        if original_flask_env:
            os.environ['FLASK_ENV'] = original_flask_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        
        # Reload config module to restore normal state
        if 'config' in sys.modules:
            del sys.modules['config']


def test_secrets_allowed_in_testing_mode():
    """Test that secrets can be set via config in testing mode"""
    # Save original environment
    original_flask_env = os.environ.get('FLASK_ENV')
    
    try:
        # Set testing mode
        os.environ['FLASK_ENV'] = 'testing'
        
        # Remove secrets from environment
        if 'SECRET_KEY' in os.environ:
            del os.environ['SECRET_KEY']
        if 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
        
        # Force reload of config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # This should NOT raise an error in testing mode
        import config
        
        # Config should load without error
        assert config.Config._is_testing == True
        
    finally:
        # Restore original environment
        if original_flask_env:
            os.environ['FLASK_ENV'] = original_flask_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        
        # Reload config module to restore normal state
        if 'config' in sys.modules:
            del sys.modules['config']


def test_secrets_work_when_provided():
    """Test that application works correctly when secrets are provided"""
    # Save original environment
    original_secret = os.environ.get('SECRET_KEY')
    original_jwt_secret = os.environ.get('JWT_SECRET_KEY')
    original_flask_env = os.environ.get('FLASK_ENV')
    
    try:
        # Set valid secrets
        os.environ['SECRET_KEY'] = 'test-secret-key-for-validation'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-validation'
        os.environ['FLASK_ENV'] = 'production'
        
        # Force reload of config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # This should work fine
        import config
        
        assert config.Config.SECRET_KEY == 'test-secret-key-for-validation'
        assert config.Config.JWT_SECRET_KEY == 'test-jwt-secret-key-for-validation'
        
    finally:
        # Restore original environment
        if original_secret:
            os.environ['SECRET_KEY'] = original_secret
        elif 'SECRET_KEY' in os.environ:
            del os.environ['SECRET_KEY']
            
        if original_jwt_secret:
            os.environ['JWT_SECRET_KEY'] = original_jwt_secret
        elif 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
            
        if original_flask_env:
            os.environ['FLASK_ENV'] = original_flask_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        
        # Reload config module to restore normal state
        if 'config' in sys.modules:
            del sys.modules['config']

