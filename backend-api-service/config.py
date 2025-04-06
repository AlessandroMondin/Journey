import os
import dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

# Service URLs - with public URL overrides
RAG_SERVICE_URL = os.getenv(
    "PUBLIC_RAG_URL", os.getenv("RAG_SERVICE_URL", "http://localhost:8001")
)
API_SERVICE_PORT = os.getenv("API_SERVICE_PORT", 8000)
API_SERVICE_URL = os.getenv(
    "PUBLIC_API_URL",
    os.getenv("API_SERVICE_URL", f"http://localhost:{API_SERVICE_PORT}"),
)

ELEVENLABS_WEBHOOK_SECRET = os.getenv("ELEVENLABS_WEBHOOK_SECRET")

elevenlabs_webhook_config = {
    "webhook_secret": ELEVENLABS_WEBHOOK_SECRET,
    "dev_mode": os.getenv("ENV") == "testing",
    "port": API_SERVICE_PORT,
}
if not ELEVENLABS_WEBHOOK_SECRET:
    raise ValueError("ELEVENLABS_WEBHOOK_SECRET is not set")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY is not set")

# Network exposure settings
EXPOSE_PUBLICLY = True
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

# Log service configuration
logger.info(f"API Service URL: {API_SERVICE_URL}")
logger.info(f"RAG Service URL: {RAG_SERVICE_URL}")
logger.info(f"Expose Publicly: {EXPOSE_PUBLICLY}")

DEFAULT_MEMORY = """
“You are the alter ego of **name**

Who am I (long term memory)

How's life been lately (short term memory)

What was the topic of our latest conversation (short term memory)

{{agent_id}} {{memory_id}}
"""


END_CALL_TOOL_PROMPT = """
At the end of the call, sends a summary of the conversation to the following endpoint.
The request body must be a JSON object with the following fields:
- agent_id: The ID of the agent, whose value is stored in the dynamic variable `agent_id`
- memory_id: The ID of the memory, whose value is stored in the dynamic variable `memory_id`
- text: The summary of the conversation, must be as detailed as possible.
i.e:
{
    "agent_id": "{{agent_id}}",
    "memory_id": "{{memory_id}}",
    "text": "{{text}}"
}
"""


RETRIEVE_MEMORY_TOOL_PROMPT = """
Use this tool to retrieve information from the user's memory. Use it as much as possible.
Every time the user says something, or ask you something that is not present in your knowledge base,
use this tool to retrieve information from the user's memory. If the retrieved information add value to
the conversation, use it to answer the user's question.
The request body must be a JSON object with the following fields:
- agent_id: The ID of the agent, whose value is stored in the dynamic variable `agent_id`
- text: The text to search the memory for.
i.e:
{
    "agent_id": "{{agent_id}}",
    "text": "{{text}}"
}
"""
