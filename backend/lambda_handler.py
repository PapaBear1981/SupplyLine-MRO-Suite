"""
AWS Lambda handler for SupplyLine MRO Suite backend

This module provides a Lambda-compatible handler for running the Flask application
on AWS Lambda with API Gateway.
"""

import json
import base64
from app import create_app
from werkzeug.serving import WSGIRequestHandler

# Create Flask app instance
app = create_app('production')

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response format
    """
    try:
        # Handle different event formats (API Gateway v1.0 vs v2.0)
        if 'version' in event and event['version'] == '2.0':
            return handle_api_gateway_v2(event, context)
        else:
            return handle_api_gateway_v1(event, context)
            
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def handle_api_gateway_v1(event, context):
    """Handle API Gateway v1.0 format"""
    
    # Extract request information
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_string = event.get('queryStringParameters') or {}
    headers = event.get('headers') or {}
    body = event.get('body', '')
    
    # Handle base64 encoded body
    if event.get('isBase64Encoded', False) and body:
        body = base64.b64decode(body).decode('utf-8')
    
    # Create WSGI environ
    environ = create_wsgi_environ(
        method=http_method,
        path=path,
        query_string=query_string,
        headers=headers,
        body=body
    )
    
    # Process request through Flask app
    response_data = []
    status_code = 200
    response_headers = {}
    
    def start_response(status, headers):
        nonlocal status_code, response_headers
        status_code = int(status.split()[0])
        response_headers = dict(headers)
    
    # Get response from Flask app
    app_response = app(environ, start_response)
    
    # Collect response data
    for data in app_response:
        if isinstance(data, bytes):
            response_data.append(data.decode('utf-8'))
        else:
            response_data.append(data)
    
    # Add CORS headers
    response_headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    })
    
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': ''.join(response_data)
    }


def handle_api_gateway_v2(event, context):
    """Handle API Gateway v2.0 format"""
    
    # Extract request information from v2.0 format
    request_context = event.get('requestContext', {})
    http = request_context.get('http', {})
    
    http_method = http.get('method', 'GET')
    path = http.get('path', '/')
    query_string = event.get('queryStringParameters') or {}
    headers = event.get('headers') or {}
    body = event.get('body', '')
    
    # Handle base64 encoded body
    if event.get('isBase64Encoded', False) and body:
        body = base64.b64decode(body).decode('utf-8')
    
    # Create WSGI environ
    environ = create_wsgi_environ(
        method=http_method,
        path=path,
        query_string=query_string,
        headers=headers,
        body=body
    )
    
    # Process request through Flask app
    response_data = []
    status_code = 200
    response_headers = {}
    
    def start_response(status, headers):
        nonlocal status_code, response_headers
        status_code = int(status.split()[0])
        response_headers = dict(headers)
    
    # Get response from Flask app
    app_response = app(environ, start_response)
    
    # Collect response data
    for data in app_response:
        if isinstance(data, bytes):
            response_data.append(data.decode('utf-8'))
        else:
            response_data.append(data)
    
    # Add CORS headers
    response_headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    })
    
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': ''.join(response_data)
    }


def create_wsgi_environ(method, path, query_string, headers, body):
    """Create WSGI environ dict from API Gateway event"""
    
    # Build query string
    query_string_parts = []
    for key, value in query_string.items():
        if value is not None:
            query_string_parts.append(f"{key}={value}")
    query_string_str = '&'.join(query_string_parts)
    
    # Create environ
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string_str,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_NAME': 'lambda',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': None,
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False
    }
    
    # Add headers to environ
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    # Add body as input stream
    if body:
        from io import StringIO
        environ['wsgi.input'] = StringIO(body)
    
    return environ


# For local testing
if __name__ == '__main__':
    # Test event for local development
    test_event = {
        'httpMethod': 'GET',
        'path': '/health',
        'queryStringParameters': {},
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': ''
    }
    
    test_context = {}
    
    response = lambda_handler(test_event, test_context)
    print(json.dumps(response, indent=2))
