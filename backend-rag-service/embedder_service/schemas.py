from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EmbeddingRequest(BaseModel):
    """Request for embedding text"""

    text: str
    owner_id: str
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingResponse(BaseModel):
    """Response with embedded document info"""

    id: str
    text: str
    metadata: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    """Request for querying similar documents"""

    query: str
    limit: int = 5
    filter: Optional[Dict[str, Any]] = None


class QueryMatch(BaseModel):
    """A matching document from a query"""

    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = {}


class QueryResponse(BaseModel):
    """Response with query results"""

    matches: List[QueryMatch]


class DeleteRequest(BaseModel):
    """Request for deleting documents"""

    ids: Optional[List[str]] = None


class DeleteResponse(BaseModel):
    """Response for deletion operation"""

    deleted_count: int


# Memory-specific schemas
class MemoryCreateResponse(BaseModel):
    """Response for memory creation"""

    id: str
    owner_id: str
    created_at: datetime


class MemoryUpdateRequest(BaseModel):
    """Request to update memory with latest conversation"""

    conversation: str = Field(..., description="Latest conversation text")


class MemoryQueryRequest(BaseModel):
    """Request to query user's memory"""

    query: str = Field(..., description="User's query")


class MemoryMatch(BaseModel):
    """A matching memory from a query"""

    id: str
    text: str
    score: float
    created_at: Optional[datetime] = None


class MemoryQueryResponse(BaseModel):
    """Response with memory query results"""

    matches: List[MemoryMatch]


class MemoryDocumentResponse(BaseModel):
    """Response with full memory document"""

    id: str
    owner_id: str
    text: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
