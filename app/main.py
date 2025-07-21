from flask import Flask, request, jsonify, abort
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from . import responses
from . import db

# Create Flask app with simpler configuration
app = Flask(__name__)

# Initialize database connection
db_manager = db.initialize_database()

# Fallback in-memory storage for development/testing
response_data = {}

def store_response_data(run_id: str, data: dict):
    """Store response data in database or fallback to memory."""
    if db_manager:
        # Try to store in Cosmos DB
        success = db_manager.store_response(run_id, data)
        if success:
            return True
    
    # Fallback to in-memory storage
    response_data[run_id] = data
    print(f"📝 Stored response data in memory for run_id: {run_id}")
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
    from flask import render_template
    return render_template('index.html')

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
            "dotenv_loaded": True,
            "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "webhook_token_configured": bool(os.environ.get("WEBHOOK_TOKEN")),
            "cosmos_db_configured": bool(db_manager)
        },
        "database": db_stats,
        "endpoints": [
            "POST /start - Start OpenAI response",
            "GET /status/<run_id> - Check status",
            "POST /webhook - Receive webhook (if configured)",
            "GET /debug - See all stored data",
            "GET /responses - List all responses"
        ]
    }

@app.route("/start", methods=["POST"])
def start():
    """Start an OpenAI response request using background mode"""
    try:
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return {"error": "Missing 'query' in request body"}, 400
        
        query = data["query"]
        
        # For background mode, webhook URL is configured in OpenAI dashboard
        webhook_url = f"{request.url_root}webhook"
        
        print(f"🚀 Starting OpenAI response for query: {query}")
        print(f"💡 Note: Using background mode - webhooks configured in OpenAI dashboard")
        print(f"📡 Expected webhook URL: {webhook_url}")
        
        # Start the OpenAI response in background mode
        response = responses.start_research(query, webhook_url)
        
        # Store initial status
        response_data_to_store = {
            "status": "running",
            "query": query,
            "started_at": datetime.now().isoformat(),
            "response": None,
            "openai_status": response.status if hasattr(response, 'status') else 'unknown'
        }
        
        store_response_data(response.id, response_data_to_store)
        
        print(f"✅ Started OpenAI response with run_id: {response.id}")
        print(f"📊 Initial status: {response.status if hasattr(response, 'status') else 'unknown'}")
        
        return {
            "run_id": response.id,
            "status": "started",
            "query": query,
            "webhook_url": webhook_url,
            "note": "Use /status/<run_id> to check progress",
            "polling_info": "OpenAI response running in background mode"
        }, 202
        
    except Exception as e:
        print(f"❌ Error starting response: {str(e)}")
        return {"error": str(e)}, 500

@app.route("/status/<run_id>", methods=["GET"])
def get_status(run_id):
    """Check the status of an OpenAI response by polling the API"""
    try:
        # First check our stored data
        local_data = get_response_data(run_id)
        
        if not local_data:
            return {"error": "Run ID not found"}, 404
        
        # Poll OpenAI for the latest status
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            openai_response = client.responses.retrieve(run_id)
            
            openai_status = openai_response.status
            output_text = getattr(openai_response, 'output_text', None)
            
            print(f"📊 Polled OpenAI status for {run_id}: {openai_status}")
            
            # Update our stored data with latest info
            updates = {
                    "openai_status": openai_status,
                    "last_checked": datetime.now().isoformat()
            }
                
                if openai_status == "completed" and output_text:
                updates.update({
                        "status": "completed",
                        "response": output_text,
                        "completed_at": datetime.now().isoformat()
                    })
                    print(f"✅ Response completed for {run_id}")
                    print(f"📝 Response preview: {output_text[:100]}...")
            
            update_response_data(run_id, updates)
            
            # Get updated data
            updated_data = get_response_data(run_id)
            
            return {
                "run_id": run_id,
                "local_status": updated_data.get("status", "unknown"),
                "openai_status": openai_status,
                "query": updated_data.get("query"),
                "response": updated_data.get("response"),
                "started_at": updated_data.get("started_at"),
                "completed_at": updated_data.get("completed_at"),
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as poll_error:
            print(f"⚠️ Error polling OpenAI: {str(poll_error)}")
            # Return what we have locally
            return {
                "run_id": run_id,
                "local_status": local_data.get("status", "unknown"),
                "error": f"Could not poll OpenAI: {str(poll_error)}",
                "local_data": local_data
            }
    
    except Exception as e:
        print(f"❌ Error checking status: {str(e)}")
        return {"error": str(e)}, 500

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Receive webhook from OpenAI when response is complete.
    Uses OpenAI's webhook signature verification for security.
    """
    try:
        # Get the webhook secret from environment
        webhook_secret = os.environ.get("WEBHOOK_TOKEN")
        
        if webhook_secret:
            # Verify webhook signature using OpenAI's webhook headers
            webhook_signature = request.headers.get("webhook-signature")
            webhook_id = request.headers.get("webhook-id")
            webhook_timestamp = request.headers.get("webhook-timestamp")
            
            if webhook_signature:
                print(f"🔐 Webhook signature received: {webhook_signature[:20]}...")
                print(f"📋 Webhook ID: {webhook_id}")
                print(f"⏰ Webhook timestamp: {webhook_timestamp}")
                
                # Verify the webhook signature using OpenAI SDK
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
                    
                    # Get the raw request data for verification
                    raw_data = request.get_data()
                    
                    # Verify the webhook signature
                    event = client.webhooks.unwrap(
                        payload=raw_data,
                        headers=dict(request.headers),
                        secret=webhook_secret
                    )
                    
                    print(f"✅ Webhook signature verified successfully!")
                    print(f"📨 Verified event type: {event.type}")
                    
                    # Use the verified event data instead of raw payload
                    # Convert the event object to a serializable dictionary
                    payload = {
                        "id": str(event.id),
                        "object": str(event.object),
                        "created_at": int(event.created_at),
                        "type": str(event.type),
                        "data": {
                            "id": str(event.data.id) if hasattr(event.data, 'id') else str(event.data)
                        }
                    }
                    
                except Exception as verify_error:
                    print(f"❌ Webhook signature verification failed: {str(verify_error)}")
                    print("⚠️ Continuing with unverified payload...")
                    # Fall back to using the raw payload
                    payload = request.get_json()
            else:
                print("⚠️ No webhook signature header found")
                print("💡 Make sure your webhook is properly configured in OpenAI dashboard")
                payload = request.get_json()
        else:
            print("⚠️ No webhook secret configured - accepting all webhooks")
            payload = request.get_json()
        print(f"📨 Received webhook payload: {json.dumps(payload, indent=2)}")
        
        # Try to extract response data (payload structure may vary)
        run_id = None
        response_text = None
        
        # Handle different possible webhook payload structures
        if isinstance(payload, dict):
            if "response" in payload:
                run_id = payload["response"].get("id")
                if "choices" in payload["response"] and len(payload["response"]["choices"]) > 0:
                    response_text = payload["response"]["choices"][0]["message"]["content"]
            elif "id" in payload:
                run_id = payload["id"]
                response_text = payload.get("output_text") or payload.get("content", "Webhook received")
        
        if not run_id:
            print("⚠️ Could not extract run_id from webhook payload")
            return {"error": "Invalid webhook payload"}, 400
        
        # Update stored data
        updates = {
                "status": "completed",
                "response": response_text or "Response completed via webhook",
                "completed_at": datetime.now().isoformat(),
                "webhook_payload": payload
            }
        
        update_response_data(run_id, updates)
        
        print(f"✅ Webhook processed successfully for run_id: {run_id}")
        if response_text:
            print(f"📝 Response preview: {response_text[:100]}...")
        
        return "", 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return {"error": str(e)}, 500

@app.route("/debug", methods=["GET"])
def debug():
    """Debug endpoint to see all stored response data"""
    all_responses = get_all_responses()
    
    return {
        "total_responses": len(all_responses),
        "database_configured": bool(db_manager),
        "stored_data": all_responses,
        "environment": {
            "webhook_token_set": bool(os.environ.get("WEBHOOK_TOKEN")),
            "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
            "cosmos_conn_set": bool(os.environ.get("COSMOS_CONN"))
        }
    }

@app.route("/responses", methods=["GET"])
def list_responses():
    """List all responses with optional pagination"""
    try:
        # Get query parameters for pagination
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if db_manager:
            # Use database pagination
            responses = db_manager.list_responses(limit=limit, offset=offset)
        else:
            # Use in-memory pagination
            all_responses = list(response_data.values())
            responses = all_responses[offset:offset + limit]
        
        return {
            "responses": responses,
            "total": len(responses),
            "limit": limit,
            "offset": offset,
            "database_configured": bool(db_manager)
        }
        
    except Exception as e:
        print(f"❌ Error listing responses: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)