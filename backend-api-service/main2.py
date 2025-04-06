import logging

from fastapi import (
    FastAPI,
    WebSocket,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Request,
)
from typing import Dict
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from service.database import get_db, transactional
from service.init_db import init_database
from service import crud, models
from service.memory_manager import MemoryManager
from schemas import (
    UserCreate,
    UserRegisterResponse,
    UserLoginResponse,
    AgentVoiceResponse,
    AgentSignedUrlResponse,
    MemoryCreate,
    MemoryResponse,
)
from auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from service.elevenlabs_api import (
    create_elevenlabs_agent,
    get_signed_url,
    create_elevenlabs_voice,
    load_memory_into_agent,
    load_tools_into_agent,
)
from pydantic import BaseModel


from fastapi import FastAPI, Request, HTTPException, Response, status
import hmac
import hashlib
import time
import json
import os
from typing import Optional
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="ElevenLabs Webhook Server")

# Configuration
config = {
    "port": int(os.environ.get("PORT", 8000)),
    "webhook_secret": os.environ.get("WEBHOOK_SECRET", "your_webhook_secret"),
    "dev_mode": os.environ.get("ENV") == "development",
}

# Initialize database on startup
init_database()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keep track of active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


# Define the MemoryUpdateRequest model
class MemoryUpdateRequest(BaseModel):
    agent_id: str
    memory_id: str
    text: str


app = FastAPI(
    title="ElevenLabs RAG API",
    description=(
        "API for handling conversations with ElevenLabs agents " "and RAG processing"
    ),
    version="1.0.0",
)

# Configure CORS - THIS IS CRITICAL FOR YOUR FRONTEND TO WORK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["Content-Type", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


@app.get("/")
async def root():
    return {
        "name": "ElevenLabs RAG API",
        "version": "1.0.0",
        "endpoints": {
            "/": "This information",
            "/auth/register": "Register a new user",
            "/auth/token": "Login and get access token",
            "/agents": "Create and list agents",
            "/agents/{agent_id}": "Get agent details",
            "/talk": "Handle conversations and RAG processing",
            "WebSocket /ws/conversation/{agent_id}": {
                "description": "Real-time conversation endpoint via WebSocket",
                "connection_url": ("ws://your-domain/ws/conversation/{agent_id}"),
                "parameters": {
                    "agent_id": (
                        "The unique identifier for the AI agent " "(path parameter)"
                    ),
                },
                "message_format": {
                    "api_key": "Your ElevenLabs API key",
                    "messages": [{"role": "user", "content": "Your message"}],
                },
            },
        },
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.post(
    "/auth/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
@transactional
async def register_user(
    user: UserCreate, db: Session = Depends(get_db)
) -> UserRegisterResponse:

    # Check if username already exists
    existing_user = (
        db.query(models.Auth).filter(models.Auth.username == user.username).first()
    )
    if existing_user:
        logger.error(f"Username already registered: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    logger.info(f"Registering user: {user.username}")

    # Create auth record
    hashed_password = get_password_hash(user.password)
    logger.info(f"Creating auth record for: {user.username}")
    auth = crud.create_auth(db, user.username, hashed_password)

    # Create API key
    logger.info(f"Creating API key for: {user.username}")
    api_key = crud.create_api_key(db, auth.id)

    # Create user
    logger.info(f"Creating user record for: {user.username}")
    db_user = crud.create_user(db, api_key.id, user.name, user.email)

    # Default agent name and description
    agent_name = f"{user.username}'s Agent"
    agent_description = "Personal assistant"

    elevenlabs_agent_id = None
    has_voice_set = False  # New users don't have a voice set yet

    elevenlabs_response = create_elevenlabs_agent()

    # Extract the agent ID from the response
    elevenlabs_agent_id = elevenlabs_response.get("agent_id")
    load_tools_into_agent(elevenlabs_agent_id)
    signed_url = get_signed_url(elevenlabs_agent_id)

    crud.create_agent(
        db,
        db_user.id,
        agent_name,
        agent_description,
        elevenlabs_agent_id,
    )

    crud.create_default_memory(db, db_user.id)

    # Return the response with user_id and signed_url (which may be None)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return UserRegisterResponse(
        message="User registered successfully",
        signed_url=signed_url,
        access_token=access_token,
        has_voice_set=has_voice_set,
        agent_id=elevenlabs_agent_id,
    )


@app.post("/auth/token", response_model=UserLoginResponse)
@transactional
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user_exists = (
        db.query(models.Auth).filter(models.Auth.username == form_data.username).first()
    )
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )

    # TODO: is it ok to have more than one valid token for a user?
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Initialize signed_url to None and has_voice_set to False
    signed_url = None
    has_voice_set = False

    # Get the user from the Auth record
    db_user = crud.get_user_from_auth(db, user.id)

    agent = crud.get_user_agent(db, db_user.id)
    if agent:
        # Check if voice is set
        if agent.voice_id:
            has_voice_set = True

        # Get the signed URL if we have an agent ID
        if agent.elevenlabs_agent_id:
            try:
                memory = crud.get_memory(db, db_user.id)
                load_memory_into_agent(agent.elevenlabs_agent_id, memory.text)
                signed_url = get_signed_url(agent.elevenlabs_agent_id)
            except Exception as e:
                # Log the error but don't fail the login
                logger.error(f"Error getting signed URL: {str(e)}")
                signed_url = None
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not load user data",
        )

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        signed_url=signed_url,
        has_voice_set=has_voice_set,
        agent_id=agent.elevenlabs_agent_id,
    )


@app.patch("/agent/voice", response_model=AgentVoiceResponse)
@transactional
async def set_agent_voice(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Auth = Depends(get_current_user),
):
    """Set the voice for the user's agent"""
    # Get the user from the Auth record
    user = crud.get_user_from_auth(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get the agent for this user
    agent = crud.get_user_agent(db, user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No agent found for this user",
        )

    try:
        # Read the audio file content
        audio_content = await audio_file.read()

        # Call ElevenLabs API to create a voice
        voice_name = f"{agent.name}'s Voice"
        elevenlabs_response = create_elevenlabs_voice(audio_content, voice_name)
        elevenlabs_voice_id = elevenlabs_response.get("voice_id")

        if not elevenlabs_voice_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get voice ID from ElevenLabs API",
            )

        # Update the agent with the voice ID
        crud.update_agent_voice_id(db, agent.agent_id, elevenlabs_voice_id)

        return AgentVoiceResponse(
            success=True,
            voice_id=elevenlabs_voice_id,
        )
    except Exception as e:
        logger.error(f"Error setting agent voice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting agent voice: {str(e)}",
        )


@app.get("/agent/signed_url", response_model=AgentSignedUrlResponse)
@transactional
async def get_agent_signed_url(
    db: Session = Depends(get_db),
    current_user: models.Auth = Depends(get_current_user),
):
    """Get the signed URL for the user's agent and check if voice is set"""
    # Get the user from the Auth record
    user = crud.get_user_from_auth(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get the agent for this user
    agent = crud.get_user_agent(db, user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No agent found for this user",
        )

    # Initialize signed_url to None
    signed_url = None
    has_voice_set = False

    # Check if voice is set
    if agent.voice_id:
        has_voice_set = True

    # Get the signed URL
    if agent.elevenlabs_agent_id:
        try:
            signed_url = get_signed_url(agent.elevenlabs_agent_id)
        except Exception as e:
            # Log the error but don't fail the request
            logger.error(f"Error getting signed URL: {str(e)}")
            signed_url = None

    return AgentSignedUrlResponse(
        signed_url=signed_url,
        has_voice_set=has_voice_set,
    )


# AGENT TOOL
@app.post("/memory/update", response_model=MemoryResponse)
@transactional
async def update_memory(
    request: dict,
    db: Session = Depends(get_db),
):
    # No user authentication required, just use the data from the request
    memory_manager = MemoryManager(
        db, None
    )  # Modify MemoryManager to not require user_id
    # or pass a specific service account ID or get user_id from request
    agent_id = request.get("agent_id")
    memory_id = request.get("memory_id")
    db_agent = crud.get_agent_from_id(db, agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    text = request.get("text")
    if not agent_id or not memory_id or not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields",
        )
    response = memory_manager.update_memory(
        agent_id=agent_id, memory_id=memory_id, text=text
    )

    return response


# AGENT TOOL
@app.post("/memory/get", response_model=MemoryResponse)
@transactional
async def get_memory(
    request: dict,
    db: Session = Depends(get_db),
):
    # No user authentication required, just use the data from the request
    memory_manager = MemoryManager(
        db, None
    )  # Modify MemoryManager to not require user_id
    agent_id = request.get("agent_id")
    text = request.get("text")
    db_agent = crud.get_agent_from_id(db, agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    if not agent_id or not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields",
        )
    response = memory_manager.retrieve_from_memories(agent_id, text)
    return response


@app.post("/webhook/elevenlabs")
async def elevenlabs_webhook(request: Request):
    print("Received webhook request from ElevenLabs")

    try:
        # Get the raw request body
        request_body = await request.body()

        # Development mode - skip validation
        if config["dev_mode"] or config["webhook_secret"] == "testing":
            print("DEVELOPMENT MODE: Processing without validation")

            # Parse the JSON data
            json_data = json.loads(request_body)
            print(f"Webhook data received: {json.dumps(json_data)[:200]}...")

            # Return 200 OK
            return Response(content="Webhook received", status_code=status.HTTP_200_OK)

        # Get signature header (check both cases)
        signature_header = request.headers.get(
            "ElevenLabs-Signature"
        ) or request.headers.get("elevenlabs-signature")

        if not signature_header:
            print("Missing ElevenLabs-Signature header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing signature header",
            )

        # Parse header components
        headers = signature_header.split(",")
        timestamp = None
        signature = None

        for header in headers:
            if header.startswith("t="):
                timestamp = header[2:]
            elif header.startswith("v0="):
                signature = header

        if not timestamp or not signature:
            print("Invalid signature format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature format",
            )

        # Validate timestamp
        req_timestamp = int(timestamp) * 1000
        tolerance = int(time.time() * 1000) - 30 * 60 * 1000  # 30 minutes
        if req_timestamp < tolerance:
            print("Request expired")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Request expired"
            )

        # Validate hash - exactly as in ElevenLabs example
        message = f"{timestamp}.{request_body.decode('utf-8')}"
        digest = (
            "v0="
            + hmac.new(
                config["webhook_secret"].encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        )

        if signature != digest:
            print("Invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Request unauthorized"
            )

        # Signature is valid - process the data
        print("Signature valid, processing data")

        # Parse the JSON data
        json_data = json.loads(request_body)
        print(f"Webhook data received: {json.dumps(json_data)[:200]}...")

        # Process webhook data here
        # Add your custom processing logic

        # Return 200 OK
        return Response(content="Webhook received", status_code=status.HTTP_200_OK)

    except json.JSONDecodeError:
        print("Invalid JSON payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload"
        )
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/health")
async def health_check():
    return {"status": "Server is running"}
