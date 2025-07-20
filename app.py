"""
WSGI Entry Point for Azure App Service

This is the main entry point that Azure App Service will use to start the Flask application.
Azure App Service looks for 'app:app' which means it expects this file to have an 'app' variable.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from the app module
from app.main import app

# This is the variable that Azure App Service expects
# When it runs 'gunicorn app:app', it looks for the 'app' variable in this file 