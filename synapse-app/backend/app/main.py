from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import base64
from datetime import datetime
import uuid
import asyncio
import sys

# Fix for Playwright on Windows - set event loop policy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from .services.supabase_client import get_supabase_client
from .services.enhanced_capture_pipeline import get_capture_pipeline
from .services.websocket_manager import get_ws_manager
from .services.rag_service import get_rag_service
from .services.embedding_service import get_embedding_service
from .services.qdrant_client import get_qdrant_client
from .services.temporal_parser import get_temporal_parser

app = FastAPI(title="Synapse API")

# CORS middleware to allow requests from Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Synapse API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time capture updates
    Desktop app connects here to receive live events
    """
    ws_manager = get_ws_manager()
    await ws_manager.connect(websocket)

    try:
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back (can be used for ping/pong)
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        ws_manager.disconnect(websocket)

@app.post("/api/capture")
async def create_capture(
    url: str = Form(...),
    title: str = Form(...),
    html: str = Form(...),
    screenshot: UploadFile = File(...)
):
    """
    ENHANCED capture pipeline:
    1. Robust scraping with Playwright (JavaScript rendering)
    2. Platform-specific extraction (YouTube, Twitter, ArXiv, etc.)
    3. Content chunking for long pages
    4. Multiple embeddings (per chunk)
    5. Comprehensive storage for Q&A
    """
    try:
        # Read screenshot
        screenshot_data = await screenshot.read()

        # Generate unique ID
        capture_id = str(uuid.uuid4())

        # Broadcast capture started
        ws_manager = get_ws_manager()
        await ws_manager.broadcast_capture_event("capture_started", {
            "capture_id": capture_id,
            "url": url,
            "title": title,
            "created_at": datetime.utcnow().isoformat()
        })

        # Use enhanced pipeline
        pipeline = get_capture_pipeline()
        result = await pipeline.process_capture(
            url=url,
            title=title,
            html=html,
            screenshot_data=screenshot_data,
            capture_id=capture_id
        )

        # Broadcast capture complete
        await ws_manager.broadcast_capture_event("capture_complete", {
            "capture_id": capture_id,
            "capture": result,
            "created_at": datetime.utcnow().isoformat()
        })

        return JSONResponse(result)

    except Exception as e:
        print(f"[ERROR] Error processing capture: {e}")
        import traceback
        traceback.print_exc()

        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/captures")
async def get_captures(limit: int = 50):
    """
    Get all captures, most recent first
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("captures")\
            .select("id, url, title, screenshot, created_at")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        return result.data
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

@app.get("/api/search")
async def search_captures(q: str, content_type: Optional[str] = None, limit: int = 20):
    """
    Semantic search across captures with optional filtering and temporal awareness

    Args:
        q: Search query (supports temporal expressions like "last week", "yesterday")
        content_type: Optional filter (product, video, article, etc.)
        limit: Max results (default 20)

    Examples:
        - "python async last week" - Searches for Python async content from the last 7 days
        - "articles from yesterday" - Articles captured yesterday
        - "machine learning this month" - ML content from current month
    """
    try:
        # Parse temporal expressions from query
        temporal_parser = get_temporal_parser()
        parsed = temporal_parser.parse(q)

        cleaned_query = parsed["cleaned_query"]
        start_date = parsed["start_date"]
        end_date = parsed["end_date"]

        if start_date or end_date:
            print(f"[Search] Temporal filter: {start_date} to {end_date}")
            print(f"[Search] Cleaned query: {cleaned_query}")

        # Generate embedding for cleaned search query
        embedding_service = get_embedding_service()
        query_embedding = await embedding_service.generate_query_embedding(cleaned_query)

        # Build filter if content_type specified
        filter_dict = None
        if content_type:
            filter_dict = {"content_type": content_type}

        # Search in Qdrant with temporal filtering
        qdrant = get_qdrant_client()
        results = await qdrant.search_similar(
            query_embedding,
            limit=limit,
            filter_dict=filter_dict,
            start_date=start_date,
            end_date=end_date
        )

        # Extract IDs for Supabase lookup
        capture_ids = [r['id'] for r in results]

        if not capture_ids:
            return []

        # Fetch full data from Supabase
        supabase = get_supabase_client()
        db_result = supabase.table("captures")\
            .select("id, url, title, screenshot, content_type, tags, summary, metadata, created_at")\
            .in_("id", capture_ids)\
            .execute()

        # Merge with similarity scores
        captures_dict = {c['id']: c for c in db_result.data}

        # Return ordered by similarity
        ordered_results = []
        for idx, result in enumerate(results, 1):
            if result['id'] in captures_dict:
                capture = captures_dict[result['id']]
                capture['similarity_score'] = result['score']
                ordered_results.append(capture)
                # Log similarity scores to terminal
                print(f"[Search] Result {idx}: {capture.get('title', 'Untitled')} ({result['score']:.2%} match)")

        return ordered_results

    except Exception as e:
        print(f"[ERROR] Search error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

@app.post("/api/chat")
async def chat(request: dict):
    """
    RAG-powered Q&A endpoint
    Answer questions using captured content as context

    Args:
        request: {"question": "How do I use async in Python?"}

    Returns:
        {
            "answer": "Based on your captured sources...",
            "sources": [{"id": "...", "title": "...", "url": "...", "relevance": 0.95}],
            "confidence": "high" | "medium" | "low"
        }
    """
    try:
        question = request.get("question")
        if not question:
            return JSONResponse({
                "error": "Question is required"
            }, status_code=400)

        rag_service = get_rag_service()
        result = await rag_service.answer_question(question)

        return result

    except Exception as e:
        print(f"[ERROR] Chat error: {e}")
        import traceback
        traceback.print_exc()

        return JSONResponse({
            "error": str(e)
        }, status_code=500)

@app.get("/api/capture/{capture_id}")
async def get_capture(capture_id: str):
    """
    Get full details of a single capture
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("captures")\
            .select("*")\
            .eq("id", capture_id)\
            .single()\
            .execute()

        return result.data
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
