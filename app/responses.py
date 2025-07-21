import os, openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = "o4-mini-deep-research"

openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def start_research(query, webhook_url, model=None):
    """
    Start an OpenAI response in background mode.
    Note: webhook_url is not used in the new Responses API - webhooks are configured 
    in the OpenAI dashboard at the project level.
    """
    model_name = model or DEFAULT_MODEL
    print(f"🚀 Starting OpenAI response with background=True (model={model_name})")
    print(f"📝 Query: {query}")
    return openai_client.responses.create(
        model=model_name,
        input=query,
        background=True,      # This enables async processing
        store=True,           # Store the response for retrieval
        tools=[
            {"type": "web_search_preview"},
            {"type": "code_interpreter", "container": {"type": "auto"}},
        ],
    )