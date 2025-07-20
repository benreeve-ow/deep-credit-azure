import os, openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def start_research(query, webhook_url):
    """
    Start an OpenAI response in background mode.
    Note: webhook_url is not used in the new Responses API - webhooks are configured 
    in the OpenAI dashboard at the project level.
    """
    print(f"🚀 Starting OpenAI response with background=True")
    print(f"📝 Query: {query}")
    
    # Use the new Responses API with background mode
    # Webhooks are configured in the OpenAI dashboard, not passed as parameter
    return openai_client.responses.create(
        model="gpt-4o-mini",  # Using a simpler model for testing
        input=query,
        background=True,      # This enables async processing
        store=True,          # Store the response for retrieval
    )

def edit_snippet(original, instruction):
    """Simple text editing using the responses API"""
    res = openai_client.responses.create(
        model="gpt-4o-mini",
        input=f"Rewrite this text: '{original}'\n\nInstruction: {instruction}",
    )
    return res.output_text.strip()