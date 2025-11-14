import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range, MatchValue
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class QdrantService:
    def __init__(self):
        """
        Initialize Qdrant client
        Supports:
        - Qdrant Cloud (with API key)
        - Local Qdrant (Docker or standalone)
        - Custom instance
        """
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if qdrant_api_key:
            # Cloud instance with API key
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            print(f"[OK] Connected to Qdrant Cloud: {qdrant_url}")
        else:
            # Local instance (Docker or standalone)
            self.client = QdrantClient(url=qdrant_url)
            print(f"[OK] Connected to Local Qdrant: {qdrant_url}")

        self.collection_name = "synapse_captures"
        self._ensure_collection()

    def _ensure_collection(self):
        """
        Create collection if it doesn't exist
        Using 3072 dimensions for Gemini embeddings (gemini-embedding-001)
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            print(f"  [OK] Using existing collection: {self.collection_name}")
        except Exception as e:
            # Collection doesn't exist, create it
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
                )
                print(f"  [OK] Created new collection: {self.collection_name} (3072 dims)")
            except Exception as create_error:
                # If collection exists with wrong config, we need to delete and recreate
                if "already exists" in str(create_error).lower():
                    print(f"  [WARN] Collection exists with wrong config, recreating...")
                    self.client.delete_collection(self.collection_name)
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
                    )
                    print(f"  [OK] Recreated collection: {self.collection_name} (3072 dims)")
                else:
                    raise

    async def upsert_capture(self, capture_id: str, embedding: List[float], metadata: Dict):
        """
        Store or update a capture's embedding with rich metadata

        Metadata includes:
        - url, title, content_type
        - tags, summary, key_points
        - extracted metadata (price, author, etc.)
        """
        # Convert UUID to string if needed
        point_id = str(capture_id)

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload=metadata
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 20,
        filter_dict: Optional[Dict] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Find similar captures using vector search

        Args:
            query_embedding: Query vector
            limit: Max results
            filter_dict: Optional filters (e.g., {"content_type": "product"})
            start_date: Optional start date for temporal filtering
            end_date: Optional end date for temporal filtering

        Returns:
            List of {id, score, metadata}
        """
        # Build Qdrant filter
        query_filter = None
        conditions = []

        # Add content type filter if provided
        if filter_dict and "content_type" in filter_dict:
            conditions.append(
                FieldCondition(
                    key="content_type",
                    match=MatchValue(value=filter_dict["content_type"])
                )
            )

        # Add date range filter if provided
        if start_date or end_date:
            # Convert to Unix timestamp (seconds since epoch)
            if start_date and end_date:
                conditions.append(
                    FieldCondition(
                        key="created_at_timestamp",
                        range=Range(
                            gte=start_date.timestamp(),
                            lte=end_date.timestamp()
                        )
                    )
                )
            elif start_date:
                conditions.append(
                    FieldCondition(
                        key="created_at_timestamp",
                        range=Range(gte=start_date.timestamp())
                    )
                )
            elif end_date:
                conditions.append(
                    FieldCondition(
                        key="created_at_timestamp",
                        range=Range(lte=end_date.timestamp())
                    )
                )

        # Build final filter
        if conditions:
            query_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "metadata": hit.payload
            }
            for hit in results
        ]

_qdrant_service: QdrantService = None

def get_qdrant_client() -> QdrantService:
    """
    Get or create Qdrant service singleton
    """
    global _qdrant_service

    if _qdrant_service is None:
        _qdrant_service = QdrantService()

    return _qdrant_service
