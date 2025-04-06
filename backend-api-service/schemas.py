from pydantic import BaseModel, EmailStr
from service.memory_manager import Mood
from typing import Optional, Union
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegisterResponse(BaseModel):
    signed_url: Optional[str] = None
    message: str
    access_token: str
    has_voice_set: bool = False
    agent_id: Optional[str] = None

    class Config:
        orm_mode = True


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    signed_url: Optional[str] = None
    has_voice_set: bool = False
    agent_id: Optional[str] = None

    class Config:
        orm_mode = True


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    agent_id: str
    elevenlabs_agent_id: Optional[str] = None
    signed_url: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class AgentItem(BaseModel):
    agent_id: str
    elevenlabs_agent_id: Optional[str] = None
    signed_url: Optional[str] = None
    description: Optional[str] = None


class AgentVoiceResponse(BaseModel):
    success: bool
    voice_id: Optional[str] = None


class AgentSignedUrlResponse(BaseModel):
    signed_url: Optional[str] = None
    has_voice_set: bool = False

    class Config:
        orm_mode = True


class MemoryCreate(BaseModel):
    text: Optional[str] = None

    class Config:
        orm_mode = True


class MemoryResponse(BaseModel):
    text: Union[str, list[str]]

    class Config:
        orm_mode = True


class DailyMemoryItem(BaseModel):
    day_timestamp: str
    memory_text: str
    mood: Mood | str

    class Config:
        orm_mode = True


class AllMemoriesResponse(BaseModel):
    memories: list[DailyMemoryItem]

    class Config:
        orm_mode = True
