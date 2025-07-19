"""
OpenAI Helper Functions for Credit Analysis

This module handles:
- OpenAI API integration
- Prompt engineering for credit analysis
- Response processing and formatting
- Error handling for AI operations
"""

import os
import openai
from typing import Dict, Any, Optional
import json
import time

# Set up OpenAI API credentials
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuration constants
DEFAULT_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper responses
MAX_TOKENS = 1500        # Maximum tokens in response
TEMPERATURE = 0.3        # Lower = more focused, higher = more creative

def validate_openai_setup():
    """
    Check if OpenAI API is properly configured
    
    Returns:
        bool: True if setup is valid
        
    Raises:
        Exception: If API key is missing or invalid
    """
    if not openai.api_key:
        raise Exception("OpenAI API key not found in environment variables")
    
    try:
        # Test API connection with a minimal request
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        raise Exception(f"OpenAI API validation failed: {str(e)}")

def create_credit_analysis_prompt(credit_data: Dict[str, Any], analysis_type: str = "basic") -> str:
    """
    Create a tailored prompt for credit analysis based on the input data
    
    Args:
        credit_data (dict): User's credit information
        analysis_type (str): Type of analysis ("basic", "detailed", "custom")
        
    Returns:
        str: Formatted prompt for OpenAI
    """
    
    # Base prompt template
    base_prompt = """
You are a professional credit analyst. Analyze the following credit information and provide insights.

Credit Data:
{credit_data}

Analysis Type: {analysis_type}

Please provide:
1. Credit Score Assessment
2. Risk Factors
3. Improvement Recommendations
4. Financial Health Summary

Format your response as a structured JSON with the following keys:
- credit_score_assessment
- risk_factors (array)
- recommendations (array)
- financial_health_summary
- overall_rating (scale 1-10)

Keep recommendations practical and actionable.
"""
    
    # Customize prompt based on analysis type
    if analysis_type == "detailed":
        base_prompt += """
Additionally include:
- Debt-to-income ratio analysis
- Payment history evaluation
- Credit utilization assessment
- Future financial projections
"""
    elif analysis_type == "custom":
        base_prompt += """
Focus on specific areas mentioned in the credit data.
Provide industry-specific insights if applicable.
"""
    
    # Format the prompt with actual data
    formatted_prompt = base_prompt.format(
        credit_data=json.dumps(credit_data, indent=2),
        analysis_type=analysis_type
    )
    
    return formatted_prompt

def generate_openai_response(credit_data: Dict[str, Any], analysis_type: str = "basic") -> Dict[str, Any]:
    """
    Generate credit analysis using OpenAI
    
    Args:
        credit_data (dict): User's credit information
        analysis_type (str): Type of analysis to perform
        
    Returns:
        dict: Parsed analysis results from OpenAI
        
    Raises:
        Exception: If OpenAI request fails
    """
    try:
        # Validate setup before making request
        validate_openai_setup()
        
        # Create the analysis prompt
        prompt = create_credit_analysis_prompt(credit_data, analysis_type)
        
        # Make request to OpenAI
        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional financial advisor specializing in credit analysis. Always respond with valid JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            timeout=30  # 30 second timeout
        )
        
        # Extract the response content
        ai_response = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            parsed_response = json.loads(ai_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return structured response
            parsed_response = {
                "error": "Failed to parse AI response as JSON",
                "raw_response": ai_response,
                "credit_score_assessment": "Unable to process",
                "risk_factors": ["Response parsing error"],
                "recommendations": ["Please try again"],
                "financial_health_summary": "Analysis incomplete",
                "overall_rating": 0
            }
        
        # Add metadata to response
        parsed_response.update({
            "analysis_timestamp": time.time(),
            "model_used": DEFAULT_MODEL,
            "analysis_type": analysis_type,
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
        })
        
        return parsed_response
        
    except openai.error.RateLimitError:
        raise Exception("OpenAI rate limit exceeded. Please try again later.")
    except openai.error.AuthenticationError:
        raise Exception("OpenAI authentication failed. Check API key.")
    except openai.error.APIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate AI response: {str(e)}")

def summarize_multiple_analyses(analyses: list) -> Dict[str, Any]:
    """
    Create a summary of multiple credit analyses for trends
    
    Args:
        analyses (list): List of previous analysis results
        
    Returns:
        dict: Summary with trends and insights
    """
    if not analyses:
        return {"error": "No analyses to summarize"}
    
    try:
        # Extract key metrics from analyses
        ratings = [analysis.get('overall_rating', 0) for analysis in analyses if analysis.get('overall_rating')]
        
        summary = {
            "total_analyses": len(analyses),
            "average_rating": sum(ratings) / len(ratings) if ratings else 0,
            "rating_trend": "improving" if len(ratings) > 1 and ratings[-1] > ratings[0] else "stable",
            "common_risk_factors": [],  # TODO: Implement risk factor analysis
            "improvement_progress": "analysis_needed"  # TODO: Implement progress tracking
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"Failed to summarize analyses: {str(e)}"}

# TODO: Add more AI helper functions:
# - validate_credit_data()
# - generate_report_summary()
# - create_improvement_plan()
# - compare_with_benchmarks() 