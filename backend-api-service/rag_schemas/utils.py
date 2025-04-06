import os
import httpx
from typing import Dict, Any, Optional
from logging import getLogger

logger = getLogger(__name__)

# Service URLs from environment variables with defaults for development
API_SERVICE_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")
EMBEDDER_SERVICE_URL = os.getenv("EMBEDDER_SERVICE_URL", "http://localhost:8001")

# Default timeout for HTTP requests
DEFAULT_TIMEOUT = 10.0  # seconds


async def make_service_request(
    url: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Make an HTTP request to another service

    Args:
        url: The URL to make the request to
        method: The HTTP method to use
        data: The data to send in the request body
        headers: The headers to include in the request
        timeout: The timeout for the request in seconds

    Returns:
        The JSON response from the service
    """
    default_headers = {
        "Content-Type": "application/json",
        "X-API-Key": os.getenv("SERVICE_API_KEY", "internal-service-api-key"),
    }

    if headers:
        default_headers.update(headers)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during service request: {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error during service request: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during service request: {str(e)}")
        raise
