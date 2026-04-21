import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')

application = get_wsgi_application()

def handler(request, context):
    return application(request, context)