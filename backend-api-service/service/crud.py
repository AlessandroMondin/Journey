from sqlalchemy.orm import Session
import uuid
from . import models
from typing import Optional, List
from config import DEFAULT_MEMORY


def create_auth(db: Session, username: str, hashed_password: str) -> models.Auth:
    """Create a new auth record"""
    db_auth = models.Auth(username=username, hashed_password=hashed_password)
    db.add(db_auth)
    # https://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
    db.flush()  # Flush to get the ID without committing
    # Don't refresh here - will be done after transaction commit
    return db_auth


def create_api_key(db: Session, auth_id: int) -> models.ApiKey:
    """Create a new API key for an auth record"""
    api_key = str(uuid.uuid4())
    db_api_key = models.ApiKey(key=api_key, auth_id=auth_id)
    db.add(db_api_key)
    db.flush()  # Flush to get the ID without committing
    # Don't refresh here - will be done after transaction commit
    return db_api_key


def create_user(
    db: Session,
    api_key_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> models.User:
    """Create a new user associated with an API key"""
    user_id = f"user_{uuid.uuid4()}"
    db_user = models.User(
        user_id=user_id, api_key_id=api_key_id, name=name, email=email
    )
    db.add(db_user)
    db.flush()  # Flush to get the ID without committing
    # Don't refresh here - will be done after transaction commit
    return db_user


def create_agent(
    db: Session,
    user_id: int,
    name: str,
    description: Optional[str] = None,
    elevenlabs_agent_id: Optional[str] = None,
    memory: str = None,
) -> models.Agent:
    """Create a new agent for a user"""
    agent_id = f"agent_{uuid.uuid4()}"
    db_agent = models.Agent(
        agent_id=agent_id,
        user_id=user_id,
        name=name,
        description=description,
        elevenlabs_agent_id=elevenlabs_agent_id,
        memory=memory,
    )
    db.add(db_agent)
    db.flush()  # Flush to get the ID without committing
    # Don't refresh here - will be done after transaction commit
    return db_agent


def create_document(
    db: Session, agent_id: int, title: str, content: str, metadata: Optional[str] = None
) -> models.Document:
    """Create a new document for an agent"""
    document_id = f"doc_{uuid.uuid4()}"
    db_document = models.Document(
        document_id=document_id,
        agent_id=agent_id,
        title=title,
        content=content,
        metadata=metadata,
    )
    db.add(db_document)
    db.flush()  # Flush to get the ID without committing
    # Don't commit here - will be done by the transaction decorator
    # Don't refresh here - will be done after transaction commit
    return db_document


def get_user_agent(db: Session, user_id: int) -> List[models.Agent]:
    """Get all agents for a user"""
    return db.query(models.Agent).filter(models.Agent.user_id == user_id).first()


def get_agent_documents(db: Session, agent_id: int) -> List[models.Document]:
    """Get all documents for an agent"""
    return db.query(models.Document).filter(models.Document.agent_id == agent_id).all()


def deactivate_api_key(db: Session, api_key: str) -> bool:
    """Deactivate an API key"""
    db_api_key = db.query(models.ApiKey).filter(models.ApiKey.key == api_key).first()

    if not db_api_key:
        return False

    db_api_key.is_active = 0
    # Don't commit here - will be done by the transaction decorator
    return True


def update_agent_elevenlabs_id(
    db: Session, agent_id: str, elevenlabs_agent_id: str
) -> models.Agent:
    """Update an agent with the ElevenLabs agent ID"""
    db_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if db_agent:
        db_agent.elevenlabs_agent_id = elevenlabs_agent_id
        # Don't commit here - will be done by the transaction decorator
        # Don't refresh here - will be done after transaction commit
    return db_agent


def update_agent_voice_id(db: Session, agent_id: str, voice_id: str) -> models.Agent:
    """Update an agent with the ElevenLabs voice ID"""
    db_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if db_agent:
        db_agent.voice_id = voice_id
        # Don't commit here - will be done by the transaction decorator
        # Don't refresh here - will be done after transaction commit
    return db_agent


def get_user_from_auth(db: Session, auth_id: int) -> models.User:
    """Get the user associated with an Auth record"""
    # First, get the API key associated with the Auth record
    api_key = db.query(models.ApiKey).filter(models.ApiKey.auth_id == auth_id).first()
    if not api_key:
        return None

    # Then, get the user associated with the API key
    user = db.query(models.User).filter(models.User.api_key_id == api_key.id).first()
    return user


def get_user_by_id(db: Session, user_id: int) -> models.User:
    """Get a user by their ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_agent_id(db: Session, auth_id: int) -> str:
    """Get the agent ID for a user associated with an Auth record"""
    user = get_user_from_auth(db, auth_id)
    if not user:
        return None

    # Get the agent for this user
    agent = db.query(models.Agent).filter(models.Agent.user_id == user.id).first()
    if not agent:
        return None

    return agent.elevenlabs_agent_id


def create_default_memory(
    db: Session, user_id: int, agent_id: Optional[int] = None
) -> models.Memory:
    """Create a new memory entry for a user and optionally an agent"""
    memory_id = f"memory_{uuid.uuid4()}"
    db_memory = models.Memory(
        memory_id=memory_id, user_id=user_id, agent_id=agent_id, text=DEFAULT_MEMORY
    )
    db.add(db_memory)
    db.flush()  # Flush to get the ID without committing
    # Don't refresh here - will be done after transaction commit
    return db_memory


def get_memory(db: Session, user_id: int) -> models.Memory:
    """Get the memory for a user"""
    return db.query(models.Memory).filter(models.Memory.user_id == user_id).first()


def get_agent_by_elevenlabs_agent_id(
    db: Session, elevenlabs_id: str
) -> models.Agent | None:
    """
    Get the memory text for an agent by elevenlabs_id
    Returns the memory text or an empty string if not found
    """
    # First, get the agent by elevenlabs_id
    db_agent = (
        db.query(models.Agent)
        .filter(models.Agent.elevenlabs_agent_id == elevenlabs_id)
        .first()
    )
    if not db_agent:
        return None

    return db_agent


def update_user_memory_by_agent_id(
    db: Session, agent_id: str, text: str
) -> models.Memory:
    """
    Update the memory text for a user by user_id
    Creates a new memory if one doesn't exist
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()

    if agent:
        agent.memory = text
    else:
        raise ValueError("Agent not found")

    return agent


def add_new_user_memory(
    db: Session,
    user_id: str,
    agent_id: str,
    text: str,
    mood: str,
) -> models.Memory:
    """Add a new memory entry for a user"""
    # Validate required parameters
    if user_id is None:
        raise ValueError("user_id cannot be None for memory creation")

    memory_id = f"memory_{uuid.uuid4()}"
    db_memory = models.Memory(
        memory_id=memory_id, user_id=user_id, agent_id=agent_id, text=text, mood=mood
    )
    db.add(db_memory)
    db.flush()  # Flush to get the ID without committing
    return db_memory


def update_memory(db: Session, memory_id: int, text: str) -> models.Memory:
    """Update the text of a memory entry"""
    db_memory = db.query(models.Memory).filter(models.Memory.id == memory_id).first()
    if db_memory:
        db_memory.text = text
        # Don't commit here - will be done by the transaction decorator
    return db_memory


def get_agent_from_id(db: Session, agent_id: str) -> models.Agent:
    """Get an agent by its agent_id"""
    return db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
