import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger
from openai import OpenAI
import redis

from embedder_service.vector_store import VectorStore


class MemoryService:
    """Service for managing user memory"""

    MEMORY_TEMPLATE = """You are the alter ego of **

Who is the person (long term memory)

Who is the person (short term memory)

What was the topic of your latest conversation
"""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder=None,
    ):
        """
        Initialize the memory service

        Args:
            vector_store: The vector store instance for storing conversation embeddings
            embedder: The embedder service for text embedding
        """
        # Vector store for conversation embeddings
        self.embeddings_store = vector_store
        self.embedder = embedder  # Store the embedder instance

        # Redis connection for plain text memory documents
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_password = os.getenv("REDIS_PASSWORD", None)

        # Connect to Redis
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )

        logger.info(f"Connected to Redis at {redis_host}:{redis_port}")

        # Initialize OpenAI client for memory updates if API key available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
            logger.info("Using OpenAI client for memory updates")
        else:
            self.openai_client = MockOpenAIClient()
            logger.warning("OPENAI_API_KEY not set, using mock client")

    def create_base_memory(self, owner_id: str) -> Dict[str, Any]:
        """
        Create initial memory for a user

        Args:
            owner_id: The user's ID

        Returns:
            The created memory entry
        """
        # Generate timestamp
        created_at = datetime.now().isoformat()

        # Create Redis key for this user's memory
        memory_key = f"memory:{owner_id}"

        # Check if memory already exists
        if self.redis.exists(memory_key):
            raise ValueError(f"Memory already exists for owner {owner_id}")

        # Create initial memory document
        memory_text = self.MEMORY_TEMPLATE

        # Store in Redis
        self.redis.set(memory_key, memory_text)

        # Store metadata
        metadata_key = f"memory:{owner_id}:metadata"
        metadata = {"created_at": created_at, "updated_at": created_at}

        # Store metadata as hash
        self.redis.hset(metadata_key, mapping=metadata)

        logger.info(f"Created memory document for owner {owner_id}")

        return {"id": memory_key, "owner_id": owner_id, "created_at": created_at}

    def update_memory(self, owner_id: str, conversation: str) -> bool:
        """
        Update memory with latest conversation

        Args:
            owner_id: The user's ID
            conversation: The latest conversation

        Returns:
            Success flag
        """
        try:
            # 1. Store conversation embedding in vector store
            now = datetime.now().isoformat()
            metadata = {"owner_id": owner_id, "created_at": now, "type": "conversation"}

            # Use the embedder to create an embedding
            if self.embedder:
                embedding = self.embedder.embed_query(conversation)
            else:
                # Fallback to direct embedding (though this shouldn't happen)
                logger.warning("No embedder instance, using default embedding")
                embedding = [0.0] * self.embeddings_store.vector_size

            # Store the embedding
            self.embeddings_store.store_embedding(
                text=conversation,
                embedding=embedding,
                owner_id=owner_id,
                metadata=metadata,
            )

            # 2. Get current memory document from Redis
            memory_key = f"memory:{owner_id}"
            memory_text = self.redis.get(memory_key)

            if not memory_text:
                logger.error(f"Memory document not found for owner {owner_id}")
                return False

            # 3. Update memory with OpenAI
            updated_memory = self._update_memory_with_ai(memory_text, conversation)

            # 4. Store updated memory in Redis
            self.redis.set(memory_key, updated_memory)

            # 5. Update metadata
            metadata_key = f"memory:{owner_id}:metadata"
            self.redis.hset(metadata_key, "updated_at", now)

            logger.info(f"Updated memory document for owner {owner_id}")

            return True
        except Exception as e:
            logger.error(f"Error updating memory: {str(e)}")
            return False

    def get_more_similar_memories(
        self, owner_id: str, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query user memory for relevant information

        Args:
            owner_id: The user's ID
            query: The search query
            limit: Maximum results to return

        Returns:
            List of similar memory results
        """
        try:
            # Create an embedding for the query
            if self.embedder:
                query_embedding = self.embedder.embed_query(query)
            else:
                # Fallback to direct embedding
                logger.warning("No embedder instance, using default embedding")
                query_embedding = [0.0] * self.embeddings_store.vector_size

            # Search for similar memories
            results = self.embeddings_store.search(
                embedding=query_embedding,
                owner_id=owner_id,
                limit=limit,
            )

            # Format results
            formatted_results = []
            for match in results:
                formatted_results.append(
                    {
                        "id": match["id"],
                        "text": match["text"],
                        "score": match["score"],
                        "created_at": match["metadata"].get("created_at"),
                    }
                )

            return formatted_results
        except Exception as e:
            logger.error(f"Error querying memory: {str(e)}")
            return []

    def get_memory_document(self, owner_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the full memory document for a user

        Args:
            owner_id: The user's ID

        Returns:
            Memory document with metadata or None if not found
        """
        try:
            memory_key = f"memory:{owner_id}"
            memory_text = self.redis.get(memory_key)

            if not memory_text:
                return None

            # Get metadata
            metadata_key = f"memory:{owner_id}:metadata"
            metadata = self.redis.hgetall(metadata_key) or {}

            return {
                "id": memory_key,
                "owner_id": owner_id,
                "text": memory_text,
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
            }
        except Exception as e:
            logger.error(f"Error getting memory document: {str(e)}")
            return None

    def _update_memory_with_ai(self, memory_text: str, conversation: str) -> str:
        """
        Update memory with latest conversation using OpenAI

        Args:
            memory_text: Current memory text
            conversation: Latest conversation

        Returns:
            Updated memory text
        """
        try:
            system_prompt = """You are an assistant that updates a user's memory
            document based on the latest conversation. The memory document has
            this structure:

            You are the alter ego of **

            Who is the person (long term memory)

            Who is the person (short term memory)

            What was the topic of your latest conversation

            Review the current memory and the latest conversation, and update
            the memory document accordingly. Keep important personal information
            and preferences in long-term memory. Update short-term memory and
            latest conversation topic sections based on the new conversation.
            Return ONLY the updated memory document with the same structure.
            """

            user_prompt = f"""CURRENT MEMORY DOCUMENT:
            {memory_text}

            LATEST CONVERSATION:
            {conversation}

            Please update the memory document based on this conversation.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            updated_memory = response.choices[0].message.content
            return updated_memory
        except Exception as e:
            logger.error(f"Error updating memory with AI: {str(e)}")
            # Return original memory if there's an error
            return memory_text


class MockOpenAIClient:
    """Mock OpenAI client for development/testing"""

    class ChatCompletions:
        def create(self, model, messages, temperature, max_tokens):
            # Parse content
            conversation = (
                messages[1]["content"].split("LATEST CONVERSATION:")[1].strip()
            )

            # Simulate updating memory with conversation content
            updated_memory = f"""You are the alter ego of **

Who is the person (long term memory)
The person enjoys coding and is working on a voice-based AI system.

Who is the person (short term memory)
The person was recently working on a memory system for their voice application.

What was the topic of your latest conversation
{conversation[:50]}..."""

            return MockCompletionResponse(updated_memory)

    def __init__(self):
        self.chat = self.ChatCompletions()


class MockCompletionResponse:
    class Choice:
        def __init__(self, content):
            self.message = type("obj", (object,), {"content": content})

    def __init__(self, content):
        self.choices = [self.Choice(content)]
