"""
RAG (Retrieval-Augmented Generation) Service
Answer questions using captured content as context
"""

from typing import List, Dict, Any
from .llm_client import get_llm_client
from .qdrant_client import get_qdrant_client
from .supabase_client import get_supabase_client
import httpx

class RAGService:
    """
    RAG pipeline for answering questions with sources

    Flow:
    1. User asks a question
    2. Generate embedding for question
    3. Search Qdrant for relevant captures
    4. Fetch full capture data from Supabase
    5. Build context from top captures
    6. Ask Claude to answer based on context
    7. Return answer + source citations
    """

    def __init__(self):
        self.llm_client = get_llm_client()
        self.qdrant = get_qdrant_client()
        self.supabase = get_supabase_client()

    async def answer_question(
        self,
        question: str,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Answer question using RAG pipeline

        Args:
            question: User's question
            max_sources: Maximum number of sources to use

        Returns:
            {
                "answer": "The answer text...",
                "sources": [
                    {"id": "...", "title": "...", "url": "...", "relevance": 0.95},
                    ...
                ],
                "confidence": "high" | "medium" | "low"
            }
        """

        print(f"[RAG] Answering question: {question}")

        # Step 1: Generate embedding for question
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.llm_client.base_url}/embeddings",
                headers=self.llm_client.headers,
                json={
                    "model": "gemini-embedding-001",
                    "input": question
                }
            )
            response.raise_for_status()
            data = response.json()
            query_embedding = data["data"][0]["embedding"]

        print(f"[RAG] Generated query embedding")

        # Step 2: Search Qdrant for relevant captures
        results = await self.qdrant.search_similar(
            query_embedding,
            limit=max_sources
        )

        print(f"[RAG] Found {len(results)} relevant captures")

        if not results:
            return {
                "answer": "I couldn't find any relevant information in your captured content to answer this question.",
                "sources": [],
                "confidence": "none"
            }

        # Step 3: Fetch full capture data
        capture_ids = [r['id'] for r in results]
        captures_data = []

        for result in results:
            try:
                capture = self.supabase.table("captures")\
                    .select("*")\
                    .eq("id", result['id'])\
                    .single()\
                    .execute()

                if capture.data:
                    captures_data.append({
                        "id": result['id'],
                        "title": capture.data.get('title'),
                        "url": capture.data.get('url'),
                        "summary": capture.data.get('summary'),
                        "main_content": capture.data.get('main_content', '')[:2000],  # Limit content
                        "tags": capture.data.get('tags', []),
                        "relevance": result['score']
                    })
            except Exception as e:
                print(f"[RAG] Failed to fetch capture {result['id']}: {e}")
                continue

        print(f"[RAG] Retrieved {len(captures_data)} full captures")

        # Step 4: Build context from captures
        context = self._build_context(captures_data)

        # Step 5: Ask Claude to answer
        answer_text = await self._generate_answer(question, context)

        # Step 6: Determine confidence
        avg_relevance = sum(c['relevance'] for c in captures_data) / len(captures_data)
        confidence = "high" if avg_relevance > 0.8 else "medium" if avg_relevance > 0.6 else "low"

        print(f"[RAG] Average relevance: {avg_relevance:.2%} -> Confidence: {confidence}")

        # Step 7: Return answer with sources
        sources = []
        for idx, c in enumerate(captures_data, 1):
            relevance_pct = c['relevance'] * 100
            print(f"[RAG] Source {idx}: {c['title']} ({relevance_pct:.1f}% relevant)")
            sources.append({
                "id": c['id'],
                "title": c['title'],
                "url": c['url'],
                "relevance": round(c['relevance'], 2)
            })

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": confidence
        }

    def _build_context(self, captures: List[Dict]) -> str:
        """Build context string from captures"""

        context_parts = []
        for i, capture in enumerate(captures, 1):
            context_parts.append(f"""
Source {i}: {capture['title']}
URL: {capture['url']}
Summary: {capture['summary']}
Content: {capture['main_content']}
Tags: {', '.join(capture['tags'])}
---
""")

        return "\n".join(context_parts)

    async def _generate_answer(self, question: str, context: str) -> str:
        """Use Claude to generate answer from context"""

        system_prompt = """You are a helpful assistant that answers questions based ONLY on the provided source content.

Rules:
1. Answer using ONLY information from the provided sources
2. If the answer isn't in the sources, say "I don't have enough information to answer that"
3. Be concise and direct
4. Reference which source(s) you used (Source 1, Source 2, etc.)
5. Don't make assumptions or add information not in the sources
"""

        user_prompt = f"""Based on the following sources from my personal knowledge base, please answer this question:

Question: {question}

Sources:
{context}

Answer:"""

        messages = [
            {"role": "user", "content": system_prompt + "\n\n" + user_prompt}
        ]

        response = await self.llm_client.chat_completion(
            messages=messages,
            model="claude-sonnet-4-5-20250929",
            temperature=0.3,  # Lower temperature for factual answers
            max_tokens=1000
        )

        return response

# Singleton
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
