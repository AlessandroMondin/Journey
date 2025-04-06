from sqlalchemy.orm import Session
from . import models


def get_user_id_by_api_key(db: Session, api_key: str) -> str:
    """
    Get user_id associated with an API key.

    Args:
        db: Database session
        api_key: The API key string

    Returns:
        user_id if found, None otherwise
    """
    api_key_obj = (
        db.query(models.ApiKey)
        .filter(models.ApiKey.key == api_key, models.ApiKey.is_active == 1)
        .first()
    )
    if not api_key_obj:
        return None

    user = (
        db.query(models.User).filter(models.User.api_key_id == api_key_obj.id).first()
    )
    return user.user_id if user else None


def get_user_id_by_agent_id(db: Session, agent_id: str) -> str:
    """
    Get user_id associated with an agent_id.

    Args:
        db: Database session
        agent_id: The agent ID string

    Returns:
        user_id if found, None otherwise
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not agent:
        return None

    user = db.query(models.User).filter(models.User.id == agent.user_id).first()
    return user.user_id if user else None


def verify_agent_belongs_to_user(db: Session, user_id: str, agent_id: str) -> bool:
    """
    Verify that an agent belongs to a specific user.

    Args:
        db: Database session
        user_id: The user ID string
        agent_id: The agent ID string

    Returns:
        True if the agent belongs to the user, False otherwise
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        return False

    agent = (
        db.query(models.Agent)
        .filter(models.Agent.agent_id == agent_id, models.Agent.user_id == user.id)
        .first()
    )

    return agent is not None
