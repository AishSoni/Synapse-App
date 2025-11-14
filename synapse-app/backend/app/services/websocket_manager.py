"""
WebSocket Manager for Real-time Updates
Broadcasts capture events to connected desktop clients
"""

from typing import List, Set
from fastapi import WebSocket
import json
import asyncio

class WebSocketManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[WS] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_capture_event(self, event_type: str, data: dict):
        """
        Broadcast capture event to all connected clients

        Events:
        - capture_started: { capture_id, url, title }
        - capture_progress: { capture_id, stage, progress }
        - capture_complete: { capture_id, capture_data }
        - capture_error: { capture_id, error }
        """
        if not self.active_connections:
            return

        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": data.get("created_at") or ""
        })

        print(f"[WS] Broadcasting {event_type} to {len(self.active_connections)} clients")

        # Send to all connections, remove dead ones
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[WS] Failed to send to client: {e}")
                dead_connections.add(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection)

    async def send_capture_progress(self, capture_id: str, stage: str, progress: int):
        """Send progress update for a capture"""
        await self.broadcast_capture_event("capture_progress", {
            "capture_id": capture_id,
            "stage": stage,
            "progress": progress
        })

# Singleton instance
_ws_manager = None

def get_ws_manager() -> WebSocketManager:
    """Get or create WebSocket manager singleton"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
