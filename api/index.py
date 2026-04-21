import os
import sys
from urllib.parse import urlparse, parse_qs

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
import django
django.setup()

# Import Django's handler
from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpResponse

# Create WSGI application
application = WSGIHandler()

def handler(event, context):
    """Vercel serverless function handler"""
    # Parse the request
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {})
    
    # Create a mock WSGI environment
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join(f"{k}={v}" for k, v in query_params.items()) if query_params else '',
        'SERVER_NAME': headers.get('host', 'localhost'),
        'SERVER_PORT': headers.get('x-forwarded-port', '80'),
        'HTTP_HOST': headers.get('host', 'localhost'),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if headers.get('x-forwarded-proto') == 'https' else 'http',
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
    }
    
    # Add headers
    for key, value in headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Create response
    def start_response(status, response_headers):
        return lambda x: None
    
    # Get response
    response = application(environ, start_response)
    
    # Convert to Vercel response
    return {
        'statusCode': 200,
        'body': ''.join(response) if response else '',
        'headers': {'Content-Type': 'text/html'}
    }