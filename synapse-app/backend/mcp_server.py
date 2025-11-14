"""
Synapse MCP Server
Stores AI chat conversations from external apps into Synapse
"""

import os
import sys
import asyncio
import uuid
from datetime import datetime
from typing import Any

# Fix for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import Field

# Import Synapse services
from app.services.llm_client import get_llm_client
from app.services.qdrant_client import get_qdrant_client
from app.services.supabase_client import get_supabase_client

# Initialize MCP server
app = Server("synapse-chat-storage")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="store_chat",
            description="""Store AI chat conversation in Synapse for semantic search and records.

This tool stores chat conversations from AI apps (Claude, ChatGPT, etc.) into your Synapse second brain.
The text is embedded and stored in Qdrant for semantic search, while a summary is stored in Supabase for record keeping.

Use this to build a searchable archive of all your AI conversations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The full conversation text to embed and make searchable. Include the entire conversation for best results."
                    },
                    "summary": {
                        "type": "string",
                        "description": "A short 1-2 sentence summary of the conversation (provided by the client)"
                    },
                    "title": {
                        "type": "string",
                        "description": "A brief title for the conversation (e.g., 'Discussion about Python decorators')"
                    },
                    "source_app": {
                        "type": "string",
                        "description": "The app this conversation is from (e.g., 'Claude', 'ChatGPT', 'Gemini')",
                        "default": "Unknown"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags/categories for this conversation",
                        "default": []
                    }
                },
                "required": ["text", "summary", "title"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "store_chat":
        try:
            # Extract arguments
            text = arguments.get("text", "")
            summary = arguments.get("summary", "")
            title = arguments.get("title", "Untitled Chat")
            source_app = arguments.get("source_app", "Unknown")
            tags = arguments.get("tags", [])

            if not text or not summary:
                return [TextContent(
                    type="text",
                    text="Error: Both 'text' and 'summary' are required"
                )]

            # Generate unique ID
            chat_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            print(f"[MCP] Storing chat: {title} (from {source_app})")

            # Step 1: Generate embedding from full text
            llm_client = get_llm_client()

            # Create embedding using the Gemini embeddings endpoint
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{llm_client.base_url}/embeddings",
                    headers=llm_client.headers,
                    json={
                        "model": "gemini-embedding-001",
                        "input": text
                    }
                )
                response.raise_for_status()
                data = response.json()
                embedding = data["data"][0]["embedding"]

            print(f"  [OK] Generated embedding ({len(embedding)} dims)")

            # Step 2: Store in Qdrant
            qdrant = get_qdrant_client()

            metadata = {
                "title": title,
                "summary": summary,
                "source_app": source_app,
                "content_type": "chat",
                "tags": tags,
                "created_at": timestamp,
                "word_count": len(text.split())
            }

            await qdrant.upsert_capture(chat_id, embedding, metadata)
            print(f"  [OK] Stored in Qdrant")

            # Step 3: Store summary in Supabase
            supabase = get_supabase_client()

            chat_record = {
                "id": chat_id,
                "title": title,
                "summary": summary,
                "source_app": source_app,
                "content_type": "chat",
                "tags": tags,
                "word_count": len(text.split()),
                "created_at": timestamp,
                # Store first 2000 chars as preview
                "text_preview": text[:2000] if len(text) > 2000 else text
            }

            supabase.table("chat_records").insert(chat_record).execute()
            print(f"  [OK] Stored in Supabase")

            return [TextContent(
                type="text",
                text=f"""✅ Chat stored successfully!

ID: {chat_id}
Title: {title}
Summary: {summary}
Source: {source_app}
Words: {len(text.split())}
Tags: {', '.join(tags) if tags else 'None'}

Your conversation is now searchable in Synapse."""
            )]

        except Exception as e:
            print(f"[ERROR] Failed to store chat: {e}")
            import traceback
            traceback.print_exc()

            return [TextContent(
                type="text",
                text=f"Error storing chat: {str(e)}"
            )]

    return [TextContent(
        type="text",
        text=f"Unknown tool: {name}"
    )]

async def main():
    """Run the MCP server"""
    print("[MCP] Synapse Chat Storage Server starting...")
    print("[MCP] This server stores AI chat conversations in Synapse")
    print("[MCP] Waiting for client connections...")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
