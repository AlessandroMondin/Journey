import os
import uuid
from typing import Dict, Any, List, Optional
import numpy as np
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


class VectorStoreConnectionError(Exception):
    """Exception raised when there is an error connecting to the vector store"""

    pass


class VectorStore:
    """Wrapper for Qdrant vector database client"""

    def __init__(
        self,
        collection_name: str = "documents",
        vector_size: int = 768,
    ):
        """Initialize the vector store with connection to Qdrant"""
        self.collection_name = collection_name
        self.vector_size = vector_size

        # Connect to Qdrant
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

        # Use QDRANT_URL for cloud hosted instance, or host/port for local
        qdrant_url = os.getenv("QDRANT_URL")

        try:
            if qdrant_url:
                self.client = QdrantClient(url=qdrant_url)
                logger.info(f"Connected to Qdrant at {qdrant_url}")
            else:
                self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
                logger.info(f"Connected to Qdrant at {qdrant_host}:{qdrant_port}")
        except Exception as e:
            raise VectorStoreConnectionError(f"Could not connect to Qdrant: {str(e)}")

        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self) -> None:
        """Create the collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            logger.info(f"Creating collection {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def store_embedding(
        self,
        text: str,
        embedding: List[float],
        owner_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store an embedding in the vector database

        Args:
            text: The text that was embedded
            embedding: The embedding vector
            owner_id: The ID of the owner/user
            metadata: Additional metadata to store

        Returns:
            The ID of the stored point
        """
        if metadata is None:
            metadata = {}

        # Add owner_id to metadata to enable filtering by owner
        metadata["owner_id"] = owner_id
        metadata["text"] = text

        # Generate a unique ID for this point
        point_id = str(uuid.uuid4())

        # Convert embedding to numpy array and ensure correct type
        vector = np.array(embedding, dtype=np.float32)

        # Store the point
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector.tolist(),
                    payload=metadata,
                )
            ],
        )

        return point_id

    def query_similar(
        self,
        query_vector: List[float],
        owner_id: str,
        limit: int = 5,
        additional_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query for similar vectors, filtered by owner_id

        Args:
            query_vector: The vector to compare against
            owner_id: The ID of the owner/user to filter by
            limit: The maximum number of results to return
            additional_filter: Additional filter conditions

        Returns:
            List of similar documents with their metadata and scores
        """
        # Create filter for owner_id
        filter_conditions = [
            FieldCondition(
                key="owner_id",
                match=MatchValue(value=owner_id),
            )
        ]

        # Add any additional filter conditions
        # For simplicity, we're not implementing complex filtering here

        # Query the vector database
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=Filter(must=filter_conditions),
        )

        # Format the results
        results = []
        for point in search_result:
            results.append(
                {
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "score": point.score,
                    "metadata": {
                        k: v for k, v in point.payload.items() if k not in ["text"]
                    },
                }
            )

        return results

    def delete_by_ids(self, ids: List[str], owner_id: str) -> int:
        """
        Delete points by their IDs, but only if they belong to the owner

        Args:
            ids: The IDs of the points to delete
            owner_id: The ID of the owner/user

        Returns:
            The number of points deleted
        """
        # First, check that all points belong to the owner
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=ids,
        )

        # Filter out points that don't belong to the owner
        valid_ids = []
        for point in points:
            if point.payload.get("owner_id") == owner_id:
                valid_ids.append(point.id)

        # Delete the valid points
        if valid_ids:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids,
            )

        return len(valid_ids)

    def delete_by_owner(self, owner_id: str) -> int:
        """
        Delete all points for a specific owner

        Args:
            owner_id: The ID of the owner/user

        Returns:
            The number of points deleted
        """
        # Count before deletion
        count_before = self.client.count(
            collection_name=self.collection_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="owner_id",
                        match=MatchValue(value=owner_id),
                    )
                ]
            ),
        ).count

        # Delete by filter
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="owner_id",
                        match=MatchValue(value=owner_id),
                    )
                ]
            ),
        )

        return count_before

    def search(
        self,
        embedding: List[float],
        owner_id: str = None,
        limit: int = 10,
        threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the database

        Args:
            embedding: The query embedding
            owner_id: Optional owner ID to filter results
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of matching documents with similarity scores
        """
        try:
            # Create filter based on owner_id if provided
            search_filter = None
            if owner_id:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="metadata.owner_id",
                            match=MatchValue(value=owner_id),
                        )
                    ]
                )

            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=limit,
                score_threshold=threshold,
                filter=search_filter,
            )

            # Format results
            formatted_results = []
            for res in results:
                # Extract metadata
                metadata = res.payload.get("metadata", {})

                # Format the result
                formatted_result = {
                    "id": res.id,
                    "text": res.payload.get("text", ""),
                    "score": res.score,
                    "created_at": metadata.get("created_at"),
                    "owner_id": metadata.get("owner_id"),
                }

                # Add any other metadata
                for key, value in metadata.items():
                    if key not in ["created_at", "owner_id"]:
                        formatted_result[key] = value

                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching for vectors: {str(e)}")
            return []
