"""
WebSocket Manager - Real-time updates for generation progress.
"""

import asyncio
import json
import logging
from typing import Dict, Set
from uuid import UUID

import redis.asyncio as redis
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from app.config import settings
from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and Redis pub/sub."""

    def __init__(self):
        # user_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # generation_id -> set of WebSocket connections
        self.generation_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.redis_client: redis.Redis | None = None
        self._pubsub_task: asyncio.Task | None = None

    async def startup(self):
        """Initialize Redis connection and start listening."""
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            await self.redis_client.ping()
            logger.info("WebSocket manager connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def shutdown(self):
        """Clean up connections."""
        if self._pubsub_task:
            self._pubsub_task.cancel()
        if self.redis_client:
            await self.redis_client.close()

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        # Check connection limit
        if len(self.active_connections[user_id]) >= settings.ws_max_connections_per_user:
            await websocket.close(code=4000, reason="Too many connections")
            return False

        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user={user_id}")
        return True

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from all generation subscriptions
        for gen_id in list(self.generation_subscriptions.keys()):
            self.generation_subscriptions[gen_id].discard(websocket)
            if not self.generation_subscriptions[gen_id]:
                del self.generation_subscriptions[gen_id]

        logger.info(f"WebSocket disconnected: user={user_id}")

    async def subscribe_to_generation(self, websocket: WebSocket, generation_id: str):
        """Subscribe a connection to generation updates."""
        if generation_id not in self.generation_subscriptions:
            self.generation_subscriptions[generation_id] = set()
            # Start listening to Redis channel for this generation
            if self.redis_client:
                asyncio.create_task(self._listen_to_generation(generation_id))

        self.generation_subscriptions[generation_id].add(websocket)
        logger.debug(f"WebSocket subscribed to generation {generation_id}")

    async def _listen_to_generation(self, generation_id: str):
        """Listen to Redis pub/sub for generation updates."""
        if not self.redis_client:
            return

        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(f"generation:{generation_id}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await self._broadcast_to_generation(generation_id, data)

                    # Unsubscribe if generation is complete
                    if data.get("status") in ("completed", "failed"):
                        await pubsub.unsubscribe(f"generation:{generation_id}")
                        break

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error listening to generation {generation_id}: {e}")

    async def _broadcast_to_generation(self, generation_id: str, data: dict):
        """Broadcast message to all connections subscribed to a generation."""
        if generation_id not in self.generation_subscriptions:
            return

        disconnected = set()

        for websocket in self.generation_subscriptions[generation_id]:
            try:
                await websocket.send_json(data)
            except Exception:
                disconnected.add(websocket)

        # Clean up disconnected
        for ws in disconnected:
            self.generation_subscriptions[generation_id].discard(ws)

    async def send_personal_message(self, user_id: str, message: dict):
        """Send a message to all connections of a specific user."""
        if user_id not in self.active_connections:
            return

        disconnected = set()

        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        # Clean up disconnected
        for ws in disconnected:
            self.active_connections[user_id].discard(ws)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/generations")
async def websocket_generations(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """
    WebSocket endpoint for real-time generation updates.

    Connect with: ws://localhost:8000/api/v1/ws/generations?token=YOUR_JWT_TOKEN

    Send messages:
    - Subscribe to generation: {"action": "subscribe", "generation_id": "uuid"}
    - Unsubscribe: {"action": "unsubscribe", "generation_id": "uuid"}
    - Ping: {"action": "ping"}

    Receive messages:
    - Generation update: {"type": "generation_update", "generation_id": "...", "status": "...", ...}
    - Pong: {"type": "pong"}
    - Error: {"type": "error", "message": "..."}
    """
    # Validate token
    payload = decode_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload.sub

    # Connect
    connected = await manager.connect(websocket, user_id)
    if not connected:
        return

    try:
        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to generation updates",
                "user_id": user_id,
            }
        )

        # Handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=settings.ws_heartbeat_interval,
                )

                action = data.get("action")

                if action == "subscribe":
                    generation_id = data.get("generation_id")
                    if generation_id:
                        await manager.subscribe_to_generation(websocket, generation_id)
                        await websocket.send_json(
                            {
                                "type": "subscribed",
                                "generation_id": generation_id,
                            }
                        )

                elif action == "unsubscribe":
                    generation_id = data.get("generation_id")
                    if generation_id and generation_id in manager.generation_subscriptions:
                        manager.generation_subscriptions[generation_id].discard(websocket)
                        await websocket.send_json(
                            {
                                "type": "unsubscribed",
                                "generation_id": generation_id,
                            }
                        )

                elif action == "ping":
                    await websocket.send_json({"type": "pong"})

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unknown action: {action}",
                        }
                    )

            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        manager.disconnect(websocket, user_id)


async def startup_websocket_manager():
    """Called on app startup."""
    await manager.startup()


async def shutdown_websocket_manager():
    """Called on app shutdown."""
    await manager.shutdown()
