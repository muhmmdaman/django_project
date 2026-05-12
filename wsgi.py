"""
Vercel WSGI application wrapper
This file allows Vercel to locate and run the Django application
"""

import os
import sys

# Add the Django project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Django-Project", "config"))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Configure Django
import django
from django.core.wsgi import get_wsgi_application

django.setup()
application = get_wsgi_application()
