import os
from fastapi import HTTPException, status, Header
from loguru import logger


async def validate_service_api_key(
    x_api_key: str = Header(..., description="Service API Key")
) -> bool:
    """
    Validates the service API key.
    This is a simple security mechanism for internal service communication.
    """
    expected_key = os.getenv("SERVICE_API_KEY", "internal-service-api-key")

    if x_api_key != expected_key:
        logger.warning(f"Invalid API key attempt: {x_api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return True
