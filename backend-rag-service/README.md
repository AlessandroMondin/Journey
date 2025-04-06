# RAG Service API

> **IMPORTANT NOTE:** The `shared` directory has been removed as its functionality has been moved to the backend-api-service in the `rag_schemas` module. The code in this service needs to be updated to use internal implementations of these components instead of relying on the shared directory.

# Backend RAG Service

This service provides a scalable Retrieval-Augmented Generation (RAG) implementation with two distinct components:

1. **API Service**: Customer-facing API that handles authentication and access control
2. **Embedder Service**: Internal service for text embedding and vector search

## Architecture

The service is designed with a separation of concerns:

- **API Service**: Handles user authentication, permissions, and provides a public API for RAG operations
- **Embedder Service**: Resource-intensive embedding and vector search operations, isolated for independent scaling
- **Qdrant**: Vector database for storing and retrieving embeddings

## Security Model

Security is implemented across both services:

1. **API Service**:

   - JWT-based authentication for end users
   - Validates permissions before forwarding requests to the Embedder Service
   - Extracts owner_id from authenticated user's token

2. **Embedder Service**:
   - Internal-only service, not exposed directly to the internet
   - Requires API key for all requests (validation via X-API-Key header)
   - Only processes requests with valid owner_id

## Running the Service

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Using Docker Compose (recommended)

1. Copy the example environment file:

   ```
   cp .env.example .env
   ```

2. Modify the `.env` file with your settings (especially security keys for production)

3. Run the entire stack:

   ```
   python run.py
   ```

   This will start all services:

   - API Service on port 8000
   - Embedder Service on port 8001
   - Qdrant on port 6333

4. Alternatively, run specific services:
   ```
   python run.py --service api      # API Service only
   python run.py --service embedder # Embedder Service only
   ```

### Manual Execution (Development)

For development, you can run each service separately:

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run Qdrant (Docker required):

   ```
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

3. Run the Embedder Service:

   ```
   python -m embedder_service.run
   ```

4. Run the API Service:
   ```
   python -m api_service.run
   ```

## API Endpoints

### API Service (Customer-facing)

- `POST /rag/store`: Store text in the RAG system (requires authentication)
- `POST /rag/query`: Query for similar documents (requires authentication)
- `DELETE /rag/documents`: Delete documents (requires authentication)

### Embedder Service (Internal)

- `POST /embed`: Embed and store text (requires service API key)
- `POST /query`: Query for similar documents (requires service API key)
- `POST /delete`: Delete documents (requires service API key)

## Configuration

Configuration is managed through environment variables, which can be set in the `.env` file:

- `JWT_SECRET_KEY`: Secret key for JWT token generation/validation
- `SERVICE_API_KEY`: API key for internal service communication
- `EMBEDDING_MODEL`: The sentence-transformer model to use for embeddings
- `QDRANT_HOST`, `QDRANT_PORT`: Qdrant connection settings
- `QDRANT_URL`: For cloud-hosted Qdrant (alternative to host/port)

# RAG Embedder Service with Memory

This service provides text embedding and vector search capabilities for a Retrieval-Augmented Generation (RAG) system.
It includes a memory system that stores and retrieves past conversations.

## Features

- Text embedding with vector storage
- Semantic search for similar documents
- User memory management
- Document deletion and management

## Memory System

The memory system uses two storage components:

1. Redis for storing plain text memory documents (one per user)
2. Qdrant for storing conversation embeddings with vector similarity search

Each user has exactly one memory document stored in Redis with the following format:

```
You are the alter ego of **

Who is the person (long term memory)

Who is the person (short term memory)

What was the topic of your latest conversation
```

The memory is updated through OpenAI when new conversations are added.

## Memory API Endpoints

- `POST /memory/create` - Creates a new memory document for a user
- `POST /memory/update/{owner_id}` - Updates memory with latest conversation
- `GET /memory/{owner_id}` - Gets the full memory document for a user
- `POST /memory/query/{owner_id}` - Finds relevant memories based on a query

## Configuration

Environment variables:

- `REDIS_HOST` - Redis host (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` - Redis password (optional)
- `OPENAI_API_KEY` - OpenAI API key (optional, mock client used if not provided)
- `SERVICE_API_KEY` - API key for internal service communication
- `QDRANT_HOST` - Qdrant host (default: localhost)
- `QDRANT_PORT` - Qdrant port (default: 6333)
- `QDRANT_URL` - Qdrant URL for cloud-hosted instance (optional)

## Dependencies

- FastAPI for API framework
- Redis for storing plain text memory
- Qdrant for vector storage and search
- OpenAI for memory updates with AI

## Development and Testing

Set up a local development environment:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m embedder_service.run
```

Test the service with the provided test script:

```bash
./test_endpoints.sh
```
