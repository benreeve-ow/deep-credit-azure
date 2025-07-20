#!/bin/bash

# Simplified OpenAI Responses API Test App Startup Script
echo "🚀 Starting OpenAI Responses API Test App..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if .env file exists and show helpful info
if [ -f ".env" ]; then
    echo "📄 Found .env file - Python will load it automatically"
else
    echo "📋 No .env file found. You can create one from the template:"
    echo "   cp env.template .env"
    echo "   # then edit .env with your actual secrets"
    echo ""
fi

# Set essential environment variables (with defaults)
echo "🔧 Setting up Flask environment..."
export FLASK_APP="${FLASK_APP:-app.main}"
export FLASK_ENV="${FLASK_ENV:-development}"

# Check for OpenAI API key (Flask app will also check via python-dotenv)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  No OPENAI_API_KEY found in current environment"
    echo "   Option 1: Set it directly:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "   Option 2: Create a .env file:"
    echo "   cp env.template .env"
    echo "   # then edit .env and add: OPENAI_API_KEY=your-api-key-here"
    echo ""
    echo "   You can get your API key from: https://platform.openai.com/api-keys"
    echo ""
    echo "💡 The Flask app will try to load from .env file using python-dotenv"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Environment configured"
echo ""
echo "🌐 Starting Flask server on http://localhost:8000"
echo "📋 Available endpoints:"
echo "   GET  / - Web interface (main app)"
echo "   GET  /api/status - API status endpoint"
echo "   POST /start - Start OpenAI response"
echo "   GET  /status/<run_id> - Check status"
echo "   POST /webhook - Receive webhook (if configured)"
echo "   GET  /debug - Debug information"
echo ""
echo "🔗 OPTIONAL: Start ngrok in another terminal for webhook testing:"
echo "   ngrok http 8000"
echo ""
echo "Press CTRL+C to stop the server"
echo "----------------------------------------"

# Start Flask application
flask run --port 8000 --host 0.0.0.0 --debug 