from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from service.database import Base


class Auth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship: Auth creates API key
    api_keys = relationship(
        "ApiKey", back_populates="auth", cascade="all, delete-orphan"
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    auth_id = Column(Integer, ForeignKey("auth.id"))
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime, server_default=func.now())

    # Relationship: API key belongs to Auth
    auth = relationship("Auth", back_populates="api_keys")

    # Relationship: API key creates user_id
    users = relationship("User", back_populates="api_key", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship: User belongs to API key
    api_key = relationship("ApiKey", back_populates="users")

    # Relationship: User has one-to-many relationship with Agent
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String)
    description = Column(Text, nullable=True)
    elevenlabs_agent_id = Column(String, nullable=True, index=True)
    voice_id = Column(String, nullable=True)
    memory = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship: Agent belongs to User
    user = relationship("User", back_populates="agents")

    # Relationship: Agent has one-to-many relationship with Document
    documents = relationship(
        "Document", back_populates="agent", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    content = Column(Text)
    doc_metadata = Column(Text, nullable=True)  # JSON string for metadata
    created_at = Column(DateTime, server_default=func.now())

    # Relationship: Document belongs to Agent
    agent = relationship("Agent", back_populates="documents")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    text = Column(Text, nullable=True)
    mood = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship: Memory belongs to User
    user = relationship("User", backref="memories")

    # Relationship: Memory belongs to Agent (optional)
    agent = relationship("Agent", backref="memories")
