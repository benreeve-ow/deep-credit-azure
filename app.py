"""
WSGI Entry Point for Azure App Service

This is the main entry point that Azure App Service will use to start the Flask application.
Azure App Service looks for 'app:app' which means it expects this file to have an 'app' variable.
"""

import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime

# Create Flask app
app = Flask(__name__)

@app.route("/")
def index():
    """Main page"""
    return """
    <h1>OpenAI Responses API Test App</h1>
    <p>✅ App is running successfully!</p>
    <p>This is a test to verify the deployment is working.</p>
    <p><a href="/api/status">Check API Status</a></p>
    """

@app.route("/api/status")
def api_status():
    """API status endpoint"""
    return {
        "status": "running",
        "message": "OpenAI Responses API Test App - DEPLOYMENT TEST",
        "environment": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "files_in_directory": os.listdir(".")
        },
        "note": "This is a test deployment to verify Azure App Service is working"
    }

@app.route("/test")
def test():
    """Simple test endpoint"""
    return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

# This is the variable that Azure App Service expects
# When it runs 'gunicorn app:app', it looks for the 'app' variable in this file 