"""
Azure App Service Startup Script

This script is used by Azure App Service to start the Flask application.
It handles environment setup and ensures the app runs correctly in production.
"""

import os
import sys
from app.main import app

if __name__ == "__main__":
    # Set Flask environment for production
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # Get port from environment (Azure App Service sets WEBSITES_PORT)
    port = int(os.environ.get('WEBSITES_PORT', 8000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False) 