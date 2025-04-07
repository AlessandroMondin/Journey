import requests
import logging
import sys
import os
from typing import Optional, TypedDict
from pydantic import BaseModel

# Add the parent directory to Python path to find the config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ELEVENLABS_API_KEY, SYSTEM_PROMPT
from service.el_api_schemas.create_agent import (
    create_agent_payload,
    load_memory_payload,
    load_tools_payload,
    PATCH_AGENT_PAYLOAD,
)

# Set up logger
logger = logging.getLogger(__name__)

# ElevenLabs API base URL
ELEVENLABS_API_BASE_URL = "https://api.elevenlabs.io"


# Schema definitions for ElevenLabs API
class InitialMessage(TypedDict):
    text: str


class RagConfig(TypedDict):
    enabled: bool
    embedding_model: str


class PromptConfig(TypedDict):
    model: str
    initial_message: InitialMessage
    system_prompt: str
    rag: RagConfig


class AgentConfig(TypedDict):
    prompt: PromptConfig


class ConversationConfig(TypedDict):
    agent: AgentConfig


class AuthSettings(TypedDict):
    enable_auth: bool


class PlatformSettings(TypedDict):
    auth: AuthSettings


class AgentCreatePayload(TypedDict):
    conversation_config: ConversationConfig
    platform_settings: PlatformSettings
    name: Optional[str]


class AgentResponse(TypedDict):
    agent_id: str
    signed_url: Optional[str]


def create_elevenlabs_agent() -> AgentResponse:
    """
    Create a new agent using the ElevenLabs API

    Args:
        name: The name of the agent
        description: Optional description of the agent

    Returns:
        dict: The created agent data including agent_id
    """
    # Return a dummy response if using a dummy key

    url = f"{ELEVENLABS_API_BASE_URL}/v1/convai/agents/create"

    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    try:
        # Make the API request
        response = requests.post(url, json=create_agent_payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse and return the response
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log the error and re-raise
        logger.error(f"Error creating ElevenLabs agent: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise


def get_signed_url(agent_id):
    """
    Get a signed URL for an ElevenLabs agent

    Args:
        agent_id: The ElevenLabs agent ID

    Returns:
        str: The signed URL for the agent
    """

    url = f"{ELEVENLABS_API_BASE_URL}/v1/convai/conversation/get_signed_url"

    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    # Set up query parameters
    params = {"agent_id": agent_id}

    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse and return the response
        result = response.json()
        return result.get("signed_url")
    except requests.exceptions.RequestException as e:
        # Log the error and re-raise
        logger.error(f"Error getting signed URL for agent {agent_id}: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise


def create_elevenlabs_voice(file_data: bytes, name: str) -> dict:
    """
    Create a new voice using the ElevenLabs API

    Args:
        file_data: The audio file data as bytes to use for voice creation
        name: Name for the new voice

    Returns:
        dict: The created voice data including voice_id
    """

    url = f"{ELEVENLABS_API_BASE_URL}/v1/voices/add"

    # Set up headers with API key
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    # Prepare the multipart form data
    # The ElevenLabs API expects 'files' to be an array of files
    # We need to provide a filename with .webm extension for proper processing
    files = {
        "files": ("voice_sample.webm", file_data, "audio/webm"),
    }

    data = {
        "name": name,
    }

    try:
        # Make the API request
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse and return the response
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log the error and re-raise
        logger.error(f"Error creating ElevenLabs voice: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise


def load_memory_into_agent(agent_id: str, memory: str):
    """
    Load a memory into an ElevenLabs agent
    """
    url = f"{ELEVENLABS_API_BASE_URL}/v1/convai/agents/{agent_id}"

    INSTRUCT = SYSTEM_PROMPT + "/n" + memory

    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    PATCH_AGENT_PAYLOAD["conversation_config"]["agent"]["prompt"]["prompt"] = INSTRUCT

    # Make the API request
    response = requests.patch(url, headers=headers, json=PATCH_AGENT_PAYLOAD)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse and return the response
    return response.json()


def load_tools_into_agent(agent_id: str):
    """
    Load tools into an ElevenLabs agent
    """
    url = f"{ELEVENLABS_API_BASE_URL}/v1/convai/agents/{agent_id}"

    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    # Make the API request
    response = requests.patch(url, headers=headers, json=PATCH_AGENT_PAYLOAD)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse and return the response
    return response.json()


class ConversationTurn(TypedDict):
    role: str
    message: str


def parse_conversation(conversation: list[ConversationTurn]) -> str:
    """
    Parse a conversation string into a list of messages
    """
    parsed_conversation = ""
    for turn in conversation:
        parsed_conversation += f"{turn['role']}: {turn['message']}\n"
    return parsed_conversation
