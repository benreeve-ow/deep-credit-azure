"""
WSGI Entry Point for Azure App Service

This is the main entry point that Azure App Service will use to start the Flask application.
"""

import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# Add some debugging
print(f"Flask app created. Environment: {os.environ.get('WEBSITE_SITE_NAME', 'Unknown')}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

@app.route("/")
def index():
    """Main page"""
    return """
    <h1>OpenAI Responses API Test App</h1>
    <p>✅ App is running successfully!</p>
    <p>This is a test to verify the deployment is working.</p>
    <p><a href="/api/status">Check API Status</a></p>
    <p><a href="/test">Test Endpoint</a></p>
    <p><a href="/debug">Debug Info</a></p>
    """

@app.route("/debug")
def debug():
    """Debug endpoint to see what's happening"""
    return {
        "message": "Debug endpoint working!",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "WEBSITE_SITE_NAME": os.environ.get('WEBSITE_SITE_NAME', 'Not set'),
            "WEBSITE_HOSTNAME": os.environ.get('WEBSITE_HOSTNAME', 'Not set'),
            "PORT": os.environ.get('PORT', 'Not set'),
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "files_in_directory": os.listdir(".")
        }
    }

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

@app.route("/<path:path>")
def catch_all(path):
    """Catch all other routes for debugging"""
    return {
        "message": f"Route /{path} not found",
        "available_routes": ["/", "/api/status", "/test", "/debug"],
        "timestamp": datetime.now().isoformat()
    }

# This is the variable that Azure App Service expects 