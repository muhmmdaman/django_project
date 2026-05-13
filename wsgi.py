"""
WSGI application wrapper for production deployment
Supports Vercel, Render, Heroku, and other platforms
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
from django.core.management import call_command

django.setup()

# Collect static files if not already done
if not os.path.exists(os.path.join(os.path.dirname(__file__), "Django-Project", "config", "staticfiles")):
    try:
        call_command('collectstatic', '--noinput', '--clear')
    except Exception as e:
        print(f"Warning: Could not collect static files: {e}")

application = get_wsgi_application()
