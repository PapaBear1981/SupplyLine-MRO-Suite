import os
import sys
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
# Ensure backend directory is importable as top-level modules (app, routes, config)
sys.path.insert(0, BACKEND_DIR)

from app import create_app

@pytest.fixture(scope='module')
def app_client():
    # Ensure sqlite database directory exists for create_app()
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
    os.makedirs(db_dir, exist_ok=True)
    app = create_app()
    app.config['TESTING'] = True
    # Flask-Session on Flask>=2.3 expects ``session_cookie_name`` which was removed.
    # Re-add attribute so the extension can access it without error.
    if not hasattr(app, 'session_cookie_name'):
        app.session_cookie_name = app.config.get('SESSION_COOKIE_NAME', 'session')
    return app.test_client()

def assert_cors_headers(response, origin):
    assert response.headers.get('Access-Control-Allow-Origin') == origin
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'

def test_cors_success(app_client):
    origin = 'http://localhost:5173'
    response = app_client.options(
        '/api/health',
        headers={'Origin': origin, 'Access-Control-Request-Method': 'GET'}
    )
    assert response.status_code == 200
    assert_cors_headers(response, origin)

def test_cors_failure(app_client):
    origin = 'http://localhost:5173'
    response = app_client.options(
        '/nonexistent',
        headers={'Origin': origin, 'Access-Control-Request-Method': 'GET'}
    )
    assert response.status_code == 404
    assert_cors_headers(response, origin)
