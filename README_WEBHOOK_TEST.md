# OpenAI Responses API Background Mode Test

This is a simplified Flask app to test the OpenAI Responses API using background mode with polling. This approach is simpler than webhooks for testing and development.

## What's Changed

**✅ Now using:** OpenAI Responses API with background mode + polling  
**❌ Previous:** Webhook-based approach (still supported but requires dashboard config)

## Quick Start

### 1. Set up your environment

```bash
# Create virtual environment if you don't have one
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (REQUIRED)
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Start the Flask app

```bash
./start_app.sh
```

The app will start on `http://localhost:8000` and show available endpoints.

### 3. Test the pattern

Run the test script:
```bash
python test_webhook.py
```

Or test manually with curl:
```bash
# Start a response (background mode)
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key principles of good software architecture?"}'

# Check status (replace RUN_ID with the actual run_id from above)
curl http://localhost:8000/status/RUN_ID

# See debug info
curl http://localhost:8000/debug
```

## How it works

1. **POST /start** - Creates an OpenAI response request with `background=True`
2. **GET /status/<run_id>** - Polls OpenAI API to check progress and retrieve results
3. **POST /webhook** - Optionally receives webhooks (requires dashboard configuration)
4. **GET /debug** - See all stored response data

## Alternative: Test with ngrok + webhooks

If you want to test actual webhooks:

### 1. Start ngrok (optional)

```bash
ngrok http 8000
```

### 2. Configure OpenAI webhooks

1. Go to [OpenAI Webhooks Dashboard](https://platform.openai.com/settings/proj_oqYdgKHUff6eZWl8zZM01qBK/webhooks)
2. Set the webhook URL to: `https://your-ngrok-url.ngrok.io/webhook?token=test-webhook-token-12345`
3. Enable the events: `response.completed` and `response.failed`

## Troubleshooting

### "OPENAI_API_KEY not set"
Set your API key: `export OPENAI_API_KEY="your-key-here"`
You can get your API key from: https://platform.openai.com/api-keys

### "Cannot connect to Flask app"
Make sure the Flask app is running on port 8000: `./start_app.sh`

### "Error starting OpenAI response"
Check that:
- Your OpenAI API key is valid
- You have access to the `gpt-4o-mini` model
- You have sufficient credits in your OpenAI account

### "Response times out"
- Background responses can take time for complex queries
- Simple queries should complete within 30 seconds
- Complex queries may take 2-3 minutes

### Testing different approaches
```bash
# Test simple synchronous responses
python test_webhook.py --simple

# Test full background mode
python test_webhook.py

# See debug information
python test_webhook.py --debug
```

## What's simplified

This test version removes:
- Database integration (uses in-memory storage)
- Frontend templates and static files  
- SSE streaming, editing, and rollback functionality
- Azure dependencies
- Complex webhook verification

## Key improvements

✅ **Simpler setup** - No ngrok required for basic testing  
✅ **Better error handling** - Clear status updates and error messages  
✅ **Polling support** - Works without webhook configuration  
✅ **Debug endpoints** - Easy to see what's happening  
✅ **Multiple test modes** - Simple and complex response testing  

## Current API structure

The app now uses the modern OpenAI Responses API:
- `background=True` for async processing
- `client.responses.retrieve()` for status polling  
- Simplified input/output structure
- Better error handling and status reporting

Once this pattern works reliably, you can gradually add back the features you need like databases, frontends, and advanced functionality. 