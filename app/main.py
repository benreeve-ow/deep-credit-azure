"""
Main Flask Application with OpenAI Integration

This file contains:
- Flask web application setup
- Route definitions for web endpoints
- OpenAI API integration logic
- Request/response handling
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for API keys, etc.)
load_dotenv()

# Create Flask application instance
app = Flask(__name__)

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# Import our helper modules
# from app.db import get_cosmos_client, save_to_cosmos
# from app.responses import generate_openai_response

@app.route('/')
def index():
    """
    Main page route - serves the web interface
    
    Returns:
        Rendered HTML template for the main page
    """
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_credit():
    """
    API endpoint for credit analysis using OpenAI
    
    Expected JSON payload:
    {
        "credit_data": "user's credit information",
        "analysis_type": "basic|detailed|custom"
    }
    
    Returns:
        JSON response with analysis results
    """
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        if not data or 'credit_data' not in data:
            return jsonify({'error': 'Missing credit_data in request'}), 400
        
        credit_data = data['credit_data']
        analysis_type = data.get('analysis_type', 'basic')
        
        # TODO: Implement OpenAI analysis logic
        # response = generate_openai_response(credit_data, analysis_type)
        
        # TODO: Save results to Cosmos DB
        # save_to_cosmos(credit_data, response)
        
        # Placeholder response
        response = {
            'status': 'success',
            'analysis': 'Credit analysis would go here',
            'credit_data_received': credit_data,
            'analysis_type': analysis_type
        }
        
        return jsonify(response)
        
    except Exception as e:
        # Log the error and return user-friendly message
        app.logger.error(f"Error in credit analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the service is running
    
    Returns:
        JSON status response
    """
    return jsonify({
        'status': 'healthy',
        'service': 'deep-credit-azure',
        'version': '0.1.0'
    })

if __name__ == '__main__':
    # Run the Flask development server
    # In production, use a proper WSGI server like Gunicorn
    app.run(
        debug=True,           # Enable debug mode for development
        host='0.0.0.0',       # Allow external connections
        port=5000             # Port to run the server on
    ) 