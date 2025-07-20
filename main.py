"""
WSGI Entry Point for Azure App Service

This is the main entry point that Azure App Service will use to start the Flask application.
Integrates OpenAI Responses API with Azure Cosmos DB for persistent storage.
"""

import os
import sys
import json
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from app import responses, db

# Create Flask app
app = Flask(__name__, template_folder='app/templates')

# Add some debugging
print(f"Flask app created. Environment: {os.environ.get('WEBSITE_SITE_NAME', 'Unknown')}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Initialize database connection
db_manager = db.initialize_database()

# Fallback in-memory storage for development/testing
response_data = {}

def store_response_data(run_id: str, data: dict):
    """Store response data in database or fallback to memory."""
    print(f"💾 Attempting to store data for run_id: {run_id}")
    print(f"📦 Data to store: {data}")
    
    if db_manager:
        # Try to store in Cosmos DB
        success = db_manager.store_response(run_id, data)
        if success:
            print(f"✅ Stored in Cosmos DB for run_id: {run_id}")
            return True
    
    # Fallback to in-memory storage
    response_data[run_id] = data
    print(f"📝 Stored response data in memory for run_id: {run_id}")
    print(f"📊 Current memory storage keys: {list(response_data.keys())}")
    return True

def get_response_data(run_id: str):
    """Get response data from database or fallback to memory."""
    if db_manager:
        # Try to get from Cosmos DB
        data = db_manager.get_response(run_id)
        if data:
            return data
    
    # Fallback to in-memory storage
    return response_data.get(run_id)

def update_response_data(run_id: str, updates: dict):
    """Update response data in database or fallback to memory."""
    if db_manager:
        # Try to update in Cosmos DB
        success = db_manager.update_response(run_id, updates)
        if success:
            return True
    
    # Fallback to in-memory storage
    if run_id in response_data:
        response_data[run_id].update(updates)
        print(f"📝 Updated response data in memory for run_id: {run_id}")
        return True
    
    return False

def get_all_responses():
    """Get all responses from database or fallback to memory."""
    if db_manager:
        # Try to get from Cosmos DB
        try:
            return db_manager.list_responses(limit=100)
        except Exception as e:
            print(f"⚠️ Error getting responses from DB: {str(e)}")
    
    # Fallback to in-memory storage
    return list(response_data.values())

@app.route("/")
def index():
    """Main page with the web interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback if template is not available
        return f"""
        <h1>OpenAI Responses API Test App</h1>
        <p>✅ App is running successfully!</p>
        <p>This is the full application with OpenAI integration.</p>
        <p><a href="/api/status">Check API Status</a></p>
        <p><a href="/test">Test Endpoint</a></p>
        <p><a href="/debug">Debug Info</a></p>
        <p><a href="/responses">View All Responses</a></p>
        <p><strong>Template Error:</strong> {str(e)}</p>
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
        },
        "stored_responses": {
            "count": len(response_data),
            "keys": list(response_data.keys()) if response_data else []
        }
    }

@app.route("/api/status")
def api_status():
    """API status endpoint for programmatic access"""
    db_stats = None
    if db_manager:
        try:
            db_stats = db_manager.get_stats()
        except Exception as e:
            db_stats = {"error": str(e)}
    
    return {
        "status": "running",
        "message": "OpenAI Responses API Test App",
        "note": "Uses background mode + polling instead of webhooks for testing",
        "environment": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "files_in_directory": os.listdir("."),
            "dotenv_loaded": True,
            "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "webhook_token_configured": bool(os.environ.get("WEBHOOK_TOKEN")),
            "cosmos_db_configured": bool(db_manager)
        },
        "database": db_stats,
        "azure_app_service": {
            "site_name": os.environ.get('WEBSITE_SITE_NAME', 'Not set'),
            "hostname": os.environ.get('WEBSITE_HOSTNAME', 'Not set'),
            "port": os.environ.get('PORT', 'Not set')
        }
    }

@app.route("/test")
def test():
    """Simple test endpoint"""
    return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

@app.route("/test-openai")
def test_openai():
    """Test OpenAI integration"""
    try:
        # Test a simple OpenAI response
        result = responses.edit_snippet("Hello world", "Make this more formal")
        return {
            "message": "OpenAI integration working!",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "message": "OpenAI integration failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.route("/test-status/<run_id>")
def test_status(run_id):
    """Test status endpoint with a specific run_id"""
    try:
        # Get stored data
        data = get_response_data(run_id)
        if not data:
            return jsonify({
                "error": "Response not found",
                "run_id": run_id,
                "available_responses": list(response_data.keys()) if response_data else []
            }), 404
        
        return jsonify({
            "message": "Status endpoint working",
            "run_id": run_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "run_id": run_id,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/test-storage")
def test_storage():
    """Test storage and retrieval functionality"""
    try:
        # Test storing some data
        test_run_id = "test_123"
        test_data = {
            "run_id": test_run_id,
            "query": "Test query",
            "status": "test",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store the data
        store_response_data(test_run_id, test_data)
        
        # Retrieve the data
        retrieved_data = get_response_data(test_run_id)
        
        return jsonify({
            "message": "Storage test completed",
            "stored_data": test_data,
            "retrieved_data": retrieved_data,
            "storage_working": retrieved_data is not None,
            "all_stored_keys": list(response_data.keys()) if response_data else [],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/start", methods=["POST"])
def start():
    """Start an OpenAI response in background mode"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' in request body"}), 400
        
        query = data['query']
        webhook_url = data.get('webhook_url', '')  # Not used in new API but kept for compatibility
        
        print(f"🚀 Starting OpenAI response for query: {query}")
        
        # Start the response using background mode
        response = responses.start_research(query, webhook_url)
        
        # Store initial data
        run_id = response.id
        initial_data = {
            "run_id": run_id,
            "query": query,
            "status": "started",
            "created_at": datetime.utcnow().isoformat(),
            "response_object": {
                "id": response.id,
                "status": response.status,
                "model": response.model
            }
        }
        
        store_response_data(run_id, initial_data)
        
        return jsonify({
            "run_id": run_id,
            "status": "started",
            "message": "OpenAI response started in background mode",
            "poll_url": f"/status/{run_id}"
        })
        
    except Exception as e:
        print(f"❌ Error starting response: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/status/<run_id>", methods=["GET"])
def get_status(run_id):
    """Get the status of a specific response"""
    try:
        print(f"🔍 Looking for run_id: {run_id}")
        print(f"📊 Current response_data keys: {list(response_data.keys()) if response_data else 'None'}")
        
        # Get stored data
        data = get_response_data(run_id)
        print(f"📋 Retrieved data for {run_id}: {data}")
        
        if not data:
            print(f"❌ No data found for run_id: {run_id}")
            return jsonify({
                "error": "Response not found", 
                "run_id": run_id,
                "available_keys": list(response_data.keys()) if response_data else [],
                "debug_info": "No data found in storage"
            }), 404
        
        # Try to get updated status from OpenAI
        try:
            import openai
            openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            response = openai_client.responses.retrieve(run_id)
            
            # Update our stored data
            updates = {
                "status": response.status,
                "updated_at": datetime.utcnow().isoformat(),
                "response_object": {
                    "id": response.id,
                    "status": response.status,
                    "model": response.model,
                    "output_text": getattr(response, 'output_text', None),
                    "error": getattr(response, 'error', None)
                }
            }
            
            update_response_data(run_id, updates)
            
            # Return the updated data
            return jsonify({
                "run_id": run_id,
                "status": response.status,
                "query": data.get("query", ""),
                "created_at": data.get("created_at", ""),
                "updated_at": updates["updated_at"],
                "output_text": getattr(response, 'output_text', ""),
                "error": getattr(response, 'error', ""),
                "note": ""  # Ensure note field is always present
            })
            
        except Exception as e:
            print(f"⚠️ Error fetching from OpenAI: {str(e)}")
            # Return stored data if we can't fetch from OpenAI
            return jsonify({
                "run_id": run_id,
                "status": data.get("status", "unknown"),
                "query": data.get("query", ""),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "output_text": "",
                "error": "",
                "note": f"Using cached data. OpenAI fetch error: {str(e)}"
            })
        
    except Exception as e:
        print(f"❌ Error getting status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/responses", methods=["GET"])
def list_responses():
    """List all stored responses"""
    try:
        responses_list = get_all_responses()
        # Ensure we return an array, not an object
        if not isinstance(responses_list, list):
            responses_list = []
        
        return jsonify({
            "responses": responses_list,
            "count": len(responses_list),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"❌ Error listing responses: {str(e)}")
        return jsonify({
            "responses": [],
            "count": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle webhook notifications from OpenAI (if configured)"""
    try:
        # Verify webhook token if configured
        webhook_token = os.environ.get("WEBHOOK_TOKEN")
        if webhook_token:
            auth_header = request.headers.get("Authorization")
            if not auth_header or auth_header != f"Bearer {webhook_token}":
                return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        print(f"📨 Received webhook: {json.dumps(data, indent=2)}")
        
        # Extract run_id from webhook data
        run_id = data.get("id") or data.get("run_id")
        if not run_id:
            return jsonify({"error": "No run_id in webhook data"}), 400
        
        # Update stored data with webhook information
        updates = {
            "webhook_received_at": datetime.utcnow().isoformat(),
            "webhook_data": data,
            "status": data.get("status", "unknown")
        }
        
        update_response_data(run_id, updates)
        
        return jsonify({"status": "webhook processed", "run_id": run_id})
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/<path:path>")
def catch_all(path):
    """Catch all other routes for debugging"""
    return {
        "message": f"Route /{path} not found",
        "available_routes": ["/", "/api/status", "/test", "/debug", "/start", "/status/<run_id>", "/responses", "/webhook"],
        "timestamp": datetime.now().isoformat()
    }

# This is the variable that Azure App Service expects 