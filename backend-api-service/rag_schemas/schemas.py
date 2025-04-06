from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class EmbeddingRequest(BaseModel):
    """Request to embed text"""

    text: str
    owner_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    """Response with embedding id"""

    id: str
    text: str
    metadata: Dict[str, Any]


class CreateMemoryResponse(BaseModel):
    """Response for memory creation"""

    success: bool
    memory_id: Optional[str] = None
    message: Optional[str] = None


class QueryRequest(BaseModel):
    """Request to query similar documents"""

    query: str
    limit: int = 5
    filter: Optional[Dict[str, Any]] = None


class QueryMatch(BaseModel):
    """Single match from a query result"""

    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    """Response with query results"""

    matches: List[QueryMatch]


class DeleteRequest(BaseModel):
    """Request to delete documents"""

    ids: Optional[List[str]] = None  # If none, delete all for owner_id


class DeleteResponse(BaseModel):
    """Response for delete operation"""

    deleted_count: int
