"""
WebSocket Gateway
Main WebSocket endpoint for realtime communication via Redis Pub/Sub.
"""

import asyncio
import json
import logging
from uuid import UUID

from typing import Callable, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.jwt_auth import ExpiredToken, InvalidToken, extract_token_from_query, get_user_from_token
from backend.core.redis_client import RedisClient, get_redis
from backend.core.websocket_manager import WebSocketConnection, WebSocketManager
from backend.models.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


# Import dependencies from core module
from backend.core.dependencies import get_db


# Factory function for WebSocket manager
# To avoid globals, initialize this at app startup via lifespan event
_websocket_manager_factory: Optional[Callable[[], WebSocketManager]] = None


def set_websocket_manager_factory(factory: Callable[[], WebSocketManager]) -> None:
    """
    Set WebSocket manager factory function.
    
    Call this at app startup to inject the manager factory.
    """
    global _websocket_manager_factory
    _websocket_manager_factory = factory


def set_websocket_manager(manager: WebSocketManager) -> None:
    """
    Set WebSocket manager instance (convenience wrapper).
    
    Call this at app startup to inject the manager instance.
    This avoids global variables while maintaining singleton pattern.
    """
    set_websocket_manager_factory(lambda: manager)


async def get_websocket_manager() -> WebSocketManager:
    """
    Get WebSocket manager instance.

    Requires manager to be initialized via set_websocket_manager() at app startup.
    """
    if _websocket_manager_factory is None:
        # Fallback: create on demand (not ideal, but works)
        # In production, always initialize at startup
        redis_client = await get_redis()
        manager = WebSocketManager(redis_client)
        set_websocket_manager(manager)
        logger.warning("WebSocketManager created on-demand. Initialize at app startup for better performance.")
    
    return _websocket_manager_factory()


async def authenticate_websocket(
    websocket: WebSocket,
    query_string: str,
    db: AsyncSession,
) -> Optional[User]:
    """
    Authenticate WebSocket connection via JWT token.

    Args:
        websocket: WebSocket connection
        query_string: URL query string containing token
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    token = extract_token_from_query(query_string)
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        logger.warning("WebSocket connection rejected: no token provided")
        return None

    try:
        user = await get_user_from_token(db, token)
        if not user:
            await websocket.close(code=1008, reason="Invalid or expired token")
            logger.warning(f"WebSocket connection rejected: invalid token")
            return None

        if not user.is_active:
            await websocket.close(code=1008, reason="User account is inactive")
            logger.warning(f"WebSocket connection rejected: inactive user {user.id}")
            return None

        return user

    except (InvalidToken, ExpiredToken) as e:
        await websocket.close(code=1008, reason=str(e))
        logger.warning(f"WebSocket connection rejected: {e}")
        return None
    except Exception as e:
        logger.error(f"Error authenticating WebSocket: {e}", exc_info=True)
        await websocket.close(code=1011, reason="Internal server error")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    db: AsyncSession = Depends(get_db),
    manager: WebSocketManager = Depends(get_websocket_manager),
):
    """
    Main WebSocket endpoint for realtime communication.

    Authentication:
    - Requires JWT token in query parameter: ?token=<jwt_token>
    - Token must be valid and user must be active

    Message Protocol:
    - Client can send JSON messages with 'type' field:
        - 'subscribe_squad': {"type": "subscribe_squad", "squad_id": "uuid"}
        - 'unsubscribe_squad': {"type": "unsubscribe_squad", "squad_id": "uuid"}
        - 'subscribe_summon': {"type": "subscribe_summon", "summon_id": "uuid"}
        - 'unsubscribe_summon': {"type": "unsubscribe_summon", "summon_id": "uuid"}
        - 'ping': {"type": "ping"} - for keepalive

    - Server sends JSON messages:
        - Real-time updates from Redis Pub/Sub channels
        - 'pong': {"type": "pong"} - response to ping
        - 'error': {"type": "error", "message": "error message"}
        - 'subscribed': {"type": "subscribed", "channel": "channel_name"}
        - 'unsubscribed': {"type": "unsubscribed", "channel": "channel_name"}

    Channels:
    - Personal: user:{user_id}:notifications (auto-subscribed)
    - Squad: squad:{squad_id}:summons
    - Summon: summon:{summon_id}:updates
    """
    # Extract query string from websocket URL
    query_string = websocket.url.query

    # Authenticate user
    user = await authenticate_websocket(websocket, query_string, db)
    if not user:
        return  # Connection already closed in authenticate_websocket

    connection: Optional[WebSocketConnection] = None

    try:
        # Connect to WebSocket manager
        connection = await manager.connect(websocket, user)

        # Send welcome message
        await connection.send_json({
            "type": "connected",
            "user_id": str(user.id),
            "username": user.username,
            "message": "WebSocket connection established",
        })

        # Keep connection alive and process messages
        while connection.active:
            try:
                # Receive message from client (with timeout to allow checking connection status)
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    await connection.send_json({
                        "type": "error",
                        "message": "Invalid JSON format",
                    })
                    continue

                message_type = data.get("type")
                if not message_type:
                    await connection.send_json({
                        "type": "error",
                        "message": "Message missing 'type' field",
                    })
                    continue

                # Handle different message types
                if message_type == "subscribe_squad":
                    squad_id_str = data.get("squad_id")
                    if not squad_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "subscribe_squad requires 'squad_id'",
                        })
                        continue

                    try:
                        squad_id = UUID(squad_id_str)
                        success = await manager.subscribe_to_squad(user.id, squad_id)
                        if success:
                            await connection.send_json({
                                "type": "subscribed",
                                "channel": f"squad:{squad_id}:summons",
                                "squad_id": str(squad_id),
                            })
                        else:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Failed to subscribe to squad {squad_id}",
                            })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid squad_id format: {squad_id_str}",
                        })

                elif message_type == "unsubscribe_squad":
                    squad_id_str = data.get("squad_id")
                    if not squad_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "unsubscribe_squad requires 'squad_id'",
                        })
                        continue

                    try:
                        squad_id = UUID(squad_id_str)
                        await manager.unsubscribe_from_squad(user.id, squad_id)
                        await connection.send_json({
                            "type": "unsubscribed",
                            "channel": f"squad:{squad_id}:summons",
                            "squad_id": str(squad_id),
                        })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid squad_id format: {squad_id_str}",
                        })

                elif message_type == "subscribe_summon":
                    summon_id_str = data.get("summon_id")
                    if not summon_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "subscribe_summon requires 'summon_id'",
                        })
                        continue

                    try:
                        summon_id = UUID(summon_id_str)
                        success = await manager.subscribe_to_summon(user.id, summon_id)
                        if success:
                            await connection.send_json({
                                "type": "subscribed",
                                "channel": f"summon:{summon_id}:updates",
                                "summon_id": str(summon_id),
                            })
                        else:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Failed to subscribe to summon {summon_id}",
                            })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid summon_id format: {summon_id_str}",
                        })

                elif message_type == "unsubscribe_summon":
                    summon_id_str = data.get("summon_id")
                    if not summon_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "unsubscribe_summon requires 'summon_id'",
                        })
                        continue

                    try:
                        summon_id = UUID(summon_id_str)
                        await manager.unsubscribe_from_summon(user.id, summon_id)
                        await connection.send_json({
                            "type": "unsubscribed",
                            "channel": f"summon:{summon_id}:updates",
                            "summon_id": str(summon_id),
                        })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid summon_id format: {summon_id_str}",
                        })

                elif message_type == "ping":
                    # Respond to keepalive ping
                    await connection.send_json({"type": "pong"})

                else:
                    await connection.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    })

            except asyncio.TimeoutError:
                # Send ping to check if client is still alive
                await connection.send_json({"type": "ping"})
                continue
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user.id}")
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message for user {user.id}: {e}", exc_info=True)
                await connection.send_json({
                    "type": "error",
                    "message": "Internal server error processing message",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user.id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {e}", exc_info=True)
    finally:
        # Clean disconnect
        if connection:
            await manager.disconnect(user.id)
        logger.info(f"WebSocket connection closed for user {user.id}")
