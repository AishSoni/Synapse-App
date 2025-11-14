"""
Embedding Generation Service
Generates vector embeddings using gemini-embedding-001 via LiteLLM
"""

from typing import List
from .llm_client import get_llm_client

class EmbeddingService:
    """Generate embeddings for text content"""

    def __init__(self):
        self.llm_client = get_llm_client()
        self.model_name = "gemini-embedding-001"

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed (summary + key points + tags)

        Returns:
            List of floats (768 dimensions)
        """
        try:
            embedding = await self.llm_client.create_embedding(
                text=text,
                model=self.model_name
            )
            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback (will be filtered out)
            return [0.0] * 768

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query

        Args:
            query: Search query text

        Returns:
            List of floats (768 dimensions)
        """
        try:
            # Same embedding model for queries and documents
            embedding = await self.llm_client.create_embedding(
                text=query,
                model=self.model_name
            )
            return embedding

        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return [0.0] * 768

    def prepare_text_for_embedding(self, analysis: dict) -> str:
        """
        Prepare optimized text for embedding from analysis

        Combines:
        - Summary (high weight)
        - Key points (high weight)
        - Tags (medium weight)
        - Clean content excerpt (low weight)
        """
        parts = []

        # Add summary (most important)
        if analysis.get('summary'):
            parts.append(f"Summary: {analysis['summary']}")

        # Add key points
        if analysis.get('key_points'):
            parts.append("Key points: " + " | ".join(analysis['key_points']))

        # Add tags
        if analysis.get('tags'):
            parts.append("Tags: " + ", ".join(analysis['tags']))

        # Add content excerpt
        if analysis.get('clean_content'):
            # First 500 chars of clean content
            excerpt = analysis['clean_content'][:500]
            parts.append(f"Content: {excerpt}")

        # Add metadata context
        metadata = analysis.get('metadata', {})
        if metadata.get('price'):
            parts.append(f"Price: {metadata.get('currency', '')} {metadata['price']}")
        if metadata.get('author'):
            parts.append(f"Author: {metadata['author']}")

        return "\n\n".join(parts)

# Singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
