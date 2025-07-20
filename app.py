"""
WSGI Entry Point for Azure App Service

This is the main entry point that Azure App Service will use to start the Flask application.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from the app module
from app.main import app

# For Azure App Service, we need to expose the app variable
application = app

if __name__ == "__main__":
    # Set Flask environment for production
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # Get port from environment (Azure App Service sets WEBSITES_PORT)
    port = int(os.environ.get('WEBSITES_PORT', 8000))
    
    print(f"🚀 Starting Flask app on port {port}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False) 