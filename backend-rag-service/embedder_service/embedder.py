from typing import List
import numpy as np
from loguru import logger


class Embedder:
    """Mock text embedding service that uses random embeddings"""

    def __init__(self, vector_size: int = 768):
        """
        Initialize the embedder with a specified vector size

        Args:
            vector_size: Size of the embedding vectors to generate
        """
        logger.info(
            f"Initializing simple random embedder with dimension: {vector_size}"
        )
        self.vector_size = vector_size
        self.model_name = "random-embedding-model"

    def embed_text(self, text: str) -> List[float]:
        """
        Generate random embeddings for a text string - for testing only

        Args:
            text: The text to embed

        Returns:
            The embedding vector as a list of floats
        """
        # Use deterministic embedding based on text hash
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.randn(self.vector_size).astype(np.float32)
        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return [self.embed_text(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query

        Args:
            query: The search query to embed

        Returns:
            The query embedding vector
        """
        return self.embed_text(query)
