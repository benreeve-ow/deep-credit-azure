import os, openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "o4-mini-deep-research"

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
    return openai_client.responses.create(
        model=MODEL_NAME,
        input=query,
        background=True,      # This enables async processing
        store=True,           # Store the response for retrieval
    )