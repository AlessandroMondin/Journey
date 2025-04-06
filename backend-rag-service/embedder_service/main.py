from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from embedder_service.embedder import Embedder
from embedder_service.vector_store import VectorStore
from embedder_service import schemas
from embedder_service.auth import validate_service_api_key
from embedder_service.memory_service import MemoryService
from loguru import logger

# Initialize the embedder and vector store
embedder = Embedder()
vector_store = VectorStore(vector_size=embedder.vector_size)
memory_service = MemoryService(vector_store, embedder)

app = FastAPI(
    title="RAG Embedder Service",
    description="Internal service for text embedding and vector search",
    version="1.0.0",
)

# Configure CORS - restrictive since this is an internal service
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # No external origins allowed
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["X-API-Key", "Authorization"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "RAG Embedder Service",
        "status": "healthy",
        "embedding_model": embedder.model_name,
        "vector_size": embedder.vector_size,
    }


# When Agent is created.
@app.post("/memory/create/{owner_id}", response_model=schemas.MemoryCreateResponse)
async def create_document_memory(
    owner_id: str,
    _: bool = Depends(validate_service_api_key),
):
    """
    Create initial memory for a user
    Requires service API key
    """
    try:
        memory = memory_service.create_base_memory(owner_id)

        logger.info(f"Created memory for owner {owner_id}")

        # Convert to response model
        return schemas.MemoryCreateResponse(
            id=memory["id"],
            owner_id=memory["owner_id"],
            created_at=memory["created_at"],
        )
    except Exception as e:
        logger.error(f"Error creating memory: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating memory: {str(e)}",
        )


# When Agent conversation is completed.
@app.post("/memory/update/{owner_id}")
async def update_memory(
    owner_id: str,
    request: schemas.MemoryUpdateRequest,
    _: bool = Depends(validate_service_api_key),
):
    """
    Update memory with latest conversation
    Requires service API key
    """
    try:
        success = memory_service.update_memory(
            owner_id=owner_id,
            conversation=request.conversation,
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Memory not found for owner {owner_id}",
            )

        logger.info(f"Updated memory for owner {owner_id}")

        return {"status": "success", "message": "Memory updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating memory: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating memory: {str(e)}",
        )


# Load memory
@app.get("/memory/{owner_id}", response_model=schemas.MemoryDocumentResponse)
async def get_memory(
    owner_id: str,
    _: bool = Depends(validate_service_api_key),
):
    """
    Get the full memory document for a user
    Requires service API key
    """
    try:
        memory_doc = memory_service.get_memory_document(owner_id)

        if not memory_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Memory not found for owner {owner_id}",
            )

        logger.info(f"Retrieved memory document for owner {owner_id}")

        return schemas.MemoryDocumentResponse(
            id=memory_doc["id"],
            owner_id=memory_doc["owner_id"],
            text=memory_doc["text"],
            created_at=memory_doc["created_at"],
            updated_at=memory_doc["updated_at"],
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting memory document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting memory document: {str(e)}",
        )


# Agent Tool
@app.post(
    "/memory/query-similar-memories/{owner_id}",
    response_model=schemas.MemoryQueryResponse,
)
async def query_memory(
    owner_id: str,
    request: schemas.MemoryQueryRequest,
    _: bool = Depends(validate_service_api_key),
):
    """
    Query user memory for relevant information
    Requires service API key
    """
    try:
        results = memory_service.get_more_similar_memories(
            owner_id=owner_id,
            query=request.query,
            limit=5,
        )

        if not results:
            logger.warning(f"No memory results for owner {owner_id}")
            return schemas.MemoryQueryResponse(matches=[])

        # Convert to response model
        matches = [
            schemas.MemoryMatch(
                id=result["id"],
                text=result["text"],
                score=result["score"],
                created_at=result.get("created_at"),
            )
            for result in results
        ]

        logger.info(f"Found {len(matches)} memory matches for owner {owner_id}")

        return schemas.MemoryQueryResponse(matches=matches)
    except Exception as e:
        logger.error(f"Error querying memory: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error querying memory: {str(e)}",
        )


@app.post("/delete/{owner_id}", response_model=schemas.DeleteResponse)
async def delete_documents(
    owner_id: str,
    request: schemas.DeleteRequest,
    _: bool = Depends(validate_service_api_key),
):
    """
    Delete documents by IDs or all for a user
    Requires service API key
    """
    try:
        deleted = vector_store.delete_by_owner(
            owner_id=owner_id,
        )

        logger.info(f"Deleted {deleted} documents for owner {owner_id}")

        return schemas.DeleteResponse(deleted_count=deleted)
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting documents: {str(e)}",
        )
