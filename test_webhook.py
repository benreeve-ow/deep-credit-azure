#!/usr/bin/env python3
"""
Simple test script for the OpenAI Responses API background mode pattern.

Usage:
1. Start the Flask app: ./start_app.sh
2. Set your OpenAI API key: export OPENAI_API_KEY="your-key"
3. Run this script: python test_webhook.py

Note: This uses background mode + polling instead of webhooks for simplicity.
"""

import requests
import json
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
FLASK_URL = "http://localhost:8000"
TEST_QUERY = "What are the key principles of good software architecture?"

def check_environment():
    """Check if required environment variables are set"""
    api_key = os.environ.get("OPENAI_API_KEY")
    webhook_token = os.environ.get("WEBHOOK_TOKEN")
    
    print("🔍 Environment Check:")
    print(f"   OPENAI_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"   WEBHOOK_TOKEN: {'✅ Set' if webhook_token else '⚠️ Using default'}")
    
    if not api_key:
        print("\n❌ OPENAI_API_KEY is required!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Or create a .env file with: OPENAI_API_KEY=your-key-here")
        return False
    
    return True

def test_responses_api_pattern():
    """Test the complete OpenAI Responses API background mode pattern"""
    print("🧪 Testing OpenAI Responses API Background Mode")
    print("=" * 60)
    
    # Step 1: Check if Flask app is running
    print("1. Checking if Flask app is running...")
    try:
        response = requests.get(f"{FLASK_URL}/")
        if response.status_code == 200:
            print("✅ Flask app is running")
            data = response.json()
            print(f"   Response: {data.get('message')}")
            print(f"   Note: {data.get('note', '')}")
        else:
            print(f"❌ Flask app returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on port 8000")
        return False
    
    print("\n" + "-" * 60)
    
    # Step 2: Start an OpenAI response
    print("2. Starting OpenAI response in background mode...")
    try:
        payload = {"query": TEST_QUERY}
        response = requests.post(f"{FLASK_URL}/start", json=payload)
        
        if response.status_code == 202:
            data = response.json()
            run_id = data["run_id"]
            print("✅ OpenAI response started successfully")
            print(f"   Run ID: {run_id}")
            print(f"   Query: {data['query']}")
            print(f"   Note: {data.get('note', '')}")
        else:
            print(f"❌ Failed to start OpenAI response: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting OpenAI response: {str(e)}")
        return False
    
    print("\n" + "-" * 60)
    
    # Step 3: Poll for completion
    print("3. Polling for response completion...")
    print("   (This will check every 5 seconds for up to 3 minutes)")
    
    max_attempts = 36  # 3 minutes total at 5-second intervals
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{FLASK_URL}/status/{run_id}")
            if response.status_code == 200:
                data = response.json()
                local_status = data.get("local_status", "unknown")
                openai_status = data.get("openai_status", "unknown")
                response_text = data.get("response")
                
                print(f"   Attempt {attempt + 1}/{max_attempts}: Local={local_status}, OpenAI={openai_status}")
                
                if local_status == "completed" and response_text:
                    print(f"✅ Response completed after {attempt * 5} seconds!")
                    print(f"   Response length: {len(response_text)}")
                    print(f"   Response preview: {response_text[:200]}...")
                    return True
                elif openai_status == "completed" and response_text:
                    print(f"✅ Response completed after {attempt * 5} seconds!")
                    print(f"   Response length: {len(response_text)}")
                    print(f"   Response preview: {response_text[:200]}...")
                    return True
                elif openai_status in ["failed", "cancelled"]:
                    print(f"❌ Response failed with status: {openai_status}")
                    return False
                elif "error" in data:
                    print(f"⚠️ Polling error: {data['error']}")
            else:
                print(f"❌ Error checking status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking status: {str(e)}")
        
        if attempt < max_attempts - 1:
            time.sleep(5)
    
    print("⏰ Timeout: Response did not complete within 3 minutes")
    print("   This might be normal for complex queries or if there are API issues")
    return False

def check_debug_info():
    """Check debug information"""
    print("\n" + "=" * 60)
    print("🔍 Debug Information")
    print("=" * 60)
    
    try:
        response = requests.get(f"{FLASK_URL}/debug")
        if response.status_code == 200:
            data = response.json()
            print(f"Total responses: {data.get('total_responses', 0)}")
            print(f"Stored run IDs: {data.get('stored_run_ids', [])}")
            
            env = data.get('environment', {})
            print(f"Environment:")
            print(f"  - Webhook token set: {env.get('webhook_token_set', False)}")
            print(f"  - OpenAI API key set: {env.get('openai_key_set', False)}")
            
            print(f"\nDetailed data:")
            for run_id, run_data in data.get('data', {}).items():
                print(f"\nRun {run_id}:")
                print(f"  Local Status: {run_data.get('status')}")
                print(f"  OpenAI Status: {run_data.get('openai_status')}")
                print(f"  Query: {run_data.get('query')}")
                print(f"  Started: {run_data.get('started_at')}")
                if run_data.get('completed_at'):
                    print(f"  Completed: {run_data.get('completed_at')}")
                if run_data.get('response'):
                    preview = run_data.get('response', '')[:100]
                    print(f"  Response: {preview}...")
        else:
            print(f"❌ Error getting debug info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting debug info: {str(e)}")

def test_simple_sync_response():
    """Test a simple synchronous response (without background mode)"""
    print("\n" + "=" * 60)
    print("🔄 Testing Simple Synchronous Response")
    print("=" * 60)
    
    try:
        # Test with a simple query that should work synchronously
        payload = {"query": "Say hello in exactly 5 words"}
        response = requests.post(f"{FLASK_URL}/start", json=payload)
        
        if response.status_code == 202:
            data = response.json()
            run_id = data["run_id"]
            print(f"✅ Started response: {run_id}")
            
            # Check immediately (might be done quickly)
            time.sleep(2)
            status_response = requests.get(f"{FLASK_URL}/status/{run_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Quick check result: {status_data.get('openai_status')}")
                if status_data.get('response'):
                    print(f"Response: {status_data.get('response')}")
                    return True
        
        return False
    except Exception as e:
        print(f"❌ Error in sync test: {str(e)}")
        return False

if __name__ == "__main__":
    print("OpenAI Responses API Background Mode Tester")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        print("\n💡 Tip: Create a .env file from the template:")
        print("   cp env.template .env")
        print("   # then edit .env with your API key")
        sys.exit(1)
    
    print("\nMake sure you have:")
    print("1. ✅ OPENAI_API_KEY is set")
    print("2. Started Flask app (./start_app.sh)")
    print("3. Optionally set up ngrok if testing webhooks")
    print("")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            check_debug_info()
        elif sys.argv[1] == "--simple":
            test_simple_sync_response()
        else:
            print("Usage: python test_webhook.py [--debug|--simple]")
    else:
        input("Press Enter to start test...")
        
        print("Testing simple response first...")
        simple_success = test_simple_sync_response()
        
        print("\nTesting background mode...")
        success = test_responses_api_pattern()
        
        print("\n" + "=" * 60)
        if success or simple_success:
            print("🎉 Test completed successfully!")
        else:
            print("❌ Test failed or timed out")
        
        print("\nFor debug info, run: python test_webhook.py --debug")
        print("For simple test only, run: python test_webhook.py --simple") 