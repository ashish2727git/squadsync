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

from backend.core.auth import ExpiredToken, InvalidToken, get_user_from_token
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


def extract_token_from_query(query_string: str) -> Optional[str]:
    """
    Extract JWT token from WebSocket query string.

    Args:
        query_string: URL query string (e.g., "token=xyz&other=value")

    Returns:
        Token string if found, None otherwise
    """
    if not query_string:
        return None

    params = {}
    for param in query_string.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params[key] = value

    return params.get("token") or params.get("access_token")


async def authenticate_websocket(
    websocket: WebSocket,
    query_string: str,
    db: AsyncSession,
) -> Optional[User]:
    """
    Authenticate WebSocket connection via JWT access token.

    Production-grade authentication: requires valid JWT access token.
    Token can be provided via:
    1. Query parameter: ?token=<jwt_token>
    2. Initial WebSocket message (preferred for security)

    Args:
        websocket: WebSocket connection
        query_string: URL query string containing token (legacy support)
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    token = None
    
    # Try to get token from query string (legacy support)
    if query_string:
        token = extract_token_from_query(query_string)
    
    # If no token in query, try to get from initial message (more secure)
    if not token:
        try:
            # Accept connection first to receive message
            await websocket.accept()
            
            # Wait for auth message (timeout: 5 seconds)
            message = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            try:
                auth_data = json.loads(message)
                token = auth_data.get("token") or auth_data.get("access_token")
            except json.JSONDecodeError:
                pass
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass
    
    # If still no token, reject connection
    if not token:
        if websocket.client_state.name != "CONNECTED":
            await websocket.accept()
        await websocket.close(code=1008, reason="Missing authentication token")
        logger.warning("WebSocket connection rejected: no token provided")
        return None

    try:
        # Validate token and get user
        user = await get_user_from_token(db, token, token_type="access")
        if not user:
            if websocket.client_state.name != "CONNECTED":
                await websocket.accept()
            await websocket.close(code=1008, reason="Invalid or expired token")
            logger.warning(f"WebSocket connection rejected: invalid token")
            return None

        if not user.is_active:
            if websocket.client_state.name != "CONNECTED":
                await websocket.accept()
            await websocket.close(code=1008, reason="User account is inactive")
            logger.warning(f"WebSocket connection rejected: inactive user {user.id}")
            return None

        return user

    except (InvalidToken, ExpiredToken) as e:
        if websocket.client_state.name != "CONNECTED":
            await websocket.accept()
        await websocket.close(code=1008, reason=str(e))
        logger.warning(f"WebSocket connection rejected: {e}")
        return None
    except Exception as e:
        logger.error(f"Error authenticating WebSocket: {e}", exc_info=True)
        if websocket.client_state.name != "CONNECTED":
            await websocket.accept()
        await websocket.close(code=1011, reason="Internal server error")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    manager: WebSocketManager = Depends(get_websocket_manager),
):
    """
    Main WebSocket endpoint for realtime communication.

    Authentication:
    - Requires JWT access token
    - Token can be provided via:
      1. Query parameter: ?token=<jwt_token> (legacy, less secure)
      2. Initial message: {"token": "<jwt_token>"} (preferred)
    - Token must be valid and user must be active

    Message Protocol:
    - First message (if not using query param): {"token": "<jwt_token>"}
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

    # Authenticate user (handles connection acceptance internally)
    user = await authenticate_websocket(websocket, query_string, db)
    if not user:
        return  # Connection already closed in authenticate_websocket
    
    # Ensure connection is accepted
    if websocket.client_state.name != "CONNECTED":
        await websocket.accept()

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

                elif message_type == "subscribe_whiteboard":
                    squad_id_str = data.get("squad_id")
                    if not squad_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "subscribe_whiteboard requires 'squad_id'",
                        })
                        continue

                    try:
                        squad_id = UUID(squad_id_str)
                        # Verify access
                        from backend.core.permissions import can_access_squad
                        can_access = await can_access_squad(db, user, squad_id)
                        if not can_access:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Access denied to squad {squad_id}",
                            })
                            continue

                        # Subscribe to whiteboard channel via connection
                        whiteboard_channel = f"squad:{squad_id}:whiteboard"
                        success = await connection.subscribe_to_channel(whiteboard_channel)
                        if success:
                            await connection.send_json({
                                "type": "subscribed",
                                "channel": whiteboard_channel,
                                "squad_id": str(squad_id),
                            })
                        else:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Failed to subscribe to whiteboard for squad {squad_id}",
                            })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid squad_id format: {squad_id_str}",
                        })

                elif message_type == "subscribe_chat":
                    squad_id_str = data.get("squad_id")
                    if not squad_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "subscribe_chat requires 'squad_id'",
                        })
                        continue

                    try:
                        squad_id = UUID(squad_id_str)
                        # Verify access
                        from backend.core.permissions import can_access_squad
                        can_access = await can_access_squad(db, user, squad_id)
                        if not can_access:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Access denied to squad {squad_id}",
                            })
                            continue

                        # Subscribe to chat channel via connection
                        chat_channel = f"squad:{squad_id}:chat"
                        success = await connection.subscribe_to_channel(chat_channel)
                        if success:
                            await connection.send_json({
                                "type": "subscribed",
                                "channel": chat_channel,
                                "squad_id": str(squad_id),
                            })
                        else:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Failed to subscribe to chat for squad {squad_id}",
                            })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid squad_id format: {squad_id_str}",
                        })

                elif message_type == "subscribe_voice":
                    squad_id_str = data.get("squad_id")
                    if not squad_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": "subscribe_voice requires 'squad_id'",
                        })
                        continue

                    try:
                        squad_id = UUID(squad_id_str)
                        # Verify access
                        from backend.core.permissions import can_access_squad
                        can_access = await can_access_squad(db, user, squad_id)
                        if not can_access:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Access denied to squad {squad_id}",
                            })
                            continue

                        # Subscribe to voice channel via connection
                        voice_channel = f"squad:{squad_id}:voice"
                        success = await connection.subscribe_to_channel(voice_channel)
                        if success:
                            await connection.send_json({
                                "type": "subscribed",
                                "channel": voice_channel,
                                "squad_id": str(squad_id),
                            })
                        else:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Failed to subscribe to voice for squad {squad_id}",
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

                elif message_type in ["draw_start", "draw_move", "draw_end", "clear"]:
                    # Whiteboard drawing events - validate and broadcast
                    squad_id_str = data.get("squad_id") or data.get("room_id")
                    if not squad_id_str:
                        await connection.send_json({
                            "type": "error",
                            "message": f"{message_type} requires 'squad_id' or 'room_id'",
                        })
                        continue

                    try:
                        squad_id = UUID(squad_id_str)
                        # Verify user has access to squad
                        from backend.core.permissions import can_access_squad
                        can_access = await can_access_squad(db, user, squad_id)
                        if not can_access:
                            await connection.send_json({
                                "type": "error",
                                "message": f"Access denied to squad {squad_id}",
                            })
                            continue

                        # Broadcast to squad whiteboard channel
                        redis = await get_redis()
                        whiteboard_channel = f"squad:{squad_id}:whiteboard"
                        await redis.publish(whiteboard_channel, {
                            **data,
                            "user_id": str(user.id),
                            "username": user.username,
                        })
                    except ValueError:
                        await connection.send_json({
                            "type": "error",
                            "message": f"Invalid squad_id format: {squad_id_str}",
                        })

                elif message_type == "whiteboard_draw":
                    # Whiteboard draw events
                    action = data.get("action")
                    if not action:
                        continue
                    
                    squad_id_str = data.get("squad_id") or data.get("room_id")
                    if squad_id_str:
                        try:
                            squad_id = UUID(squad_id_str)
                            # Verify access
                            from backend.core.permissions import can_access_squad
                            can_access = await can_access_squad(db, user, squad_id)
                            if not can_access:
                                await connection.send_json({
                                    "type": "error",
                                    "message": f"Access denied to squad {squad_id}",
                                })
                                continue
                            
                            redis = await get_redis()
                            whiteboard_channel = f"squad:{squad_id}:whiteboard"
                            await redis.publish(whiteboard_channel, {
                                "type": "whiteboard_draw",
                                "action": action,
                                "user_id": str(user.id),
                                "username": user.username,
                            })
                        except ValueError:
                            pass

                elif message_type == "whiteboard_clear":
                    # Whiteboard clear events
                    squad_id_str = data.get("squad_id") or data.get("room_id")
                    if squad_id_str:
                        try:
                            squad_id = UUID(squad_id_str)
                            # Verify access
                            from backend.core.permissions import can_access_squad
                            can_access = await can_access_squad(db, user, squad_id)
                            if not can_access:
                                await connection.send_json({
                                    "type": "error",
                                    "message": f"Access denied to squad {squad_id}",
                                })
                                continue
                            
                            redis = await get_redis()
                            whiteboard_channel = f"squad:{squad_id}:whiteboard"
                            await redis.publish(whiteboard_channel, {
                                "type": "whiteboard_clear",
                                "user_id": str(user.id),
                                "username": user.username,
                            })
                        except ValueError:
                            pass

                elif message_type == "chat_message":
                    # Squad chat messages
                    room_id_str = data.get("roomId") or data.get("squad_id")
                    message_text = data.get("message")
                    if room_id_str and message_text:
                        try:
                            squad_id = UUID(room_id_str)
                            from backend.core.permissions import can_access_squad
                            can_access = await can_access_squad(db, user, squad_id)
                            if can_access:
                                redis = await get_redis()
                                chat_channel = f"squad:{squad_id}:chat"
                                await redis.publish(chat_channel, {
                                    "type": "chat_message",
                                    "id": data.get("id", str(user.id)),
                                    "userId": str(user.id),
                                    "username": user.username,
                                    "message": message_text,
                                    "timestamp": data.get("timestamp"),
                                })
                                
                                # Subscribe to chat if not already
                                await connection.subscribe_to_channel(chat_channel)
                        except ValueError:
                            pass

                elif message_type in ["join_voice_call", "leave_voice_call"]:
                    # Voice call join/leave events
                    room_id_str = data.get("roomId") or data.get("squad_id")
                    if room_id_str:
                        try:
                            squad_id = UUID(room_id_str)
                            redis = await get_redis()
                            voice_channel = f"squad:{squad_id}:voice"
                            await redis.publish(voice_channel, {
                                "type": message_type,
                                "userId": str(user.id),
                                "username": user.username,
                                "roomId": str(squad_id),
                            })
                            
                            # Subscribe to voice channel
                            if message_type == "join_voice_call":
                                await connection.subscribe_to_channel(voice_channel)
                        except ValueError:
                            pass

                elif message_type in ["webrtc_offer", "webrtc_answer", "webrtc_ice_candidate"]:
                    # WebRTC signaling events
                    target_user_id_str = data.get("targetUserId")
                    if target_user_id_str:
                        try:
                            target_user_id = UUID(target_user_id_str)
                            redis = await get_redis()
                            target_channel = f"user:{target_user_id}:notifications"
                            await redis.publish(target_channel, {
                                **data,
                                "fromUserId": str(user.id),
                                "fromUsername": user.username,
                            })
                        except ValueError:
                            pass

                elif message_type == "typing_start":
                    # Typing indicator start
                    channel_id = data.get("channel_id") or data.get("squad_id")
                    if channel_id:
                        redis = await get_redis()
                        chat_channel = f"squad:{channel_id}:chat"
                        await redis.publish(chat_channel, {
                            "type": "typing_start",
                            "user_id": str(user.id),
                            "username": user.username,
                            "channel_id": channel_id,
                        })

                elif message_type == "typing_stop":
                    # Typing indicator stop
                    channel_id = data.get("channel_id") or data.get("squad_id")
                    if channel_id:
                        redis = await get_redis()
                        chat_channel = f"squad:{channel_id}:chat"
                        await redis.publish(chat_channel, {
                            "type": "typing_stop",
                            "user_id": str(user.id),
                            "username": user.username,
                            "channel_id": channel_id,
                        })

                elif message_type == "presence_update":
                    # User presence update
                    presence = data.get("presence", "ONLINE")
                    status_text = data.get("status_text")
                    activity = data.get("activity")
                    
                    # Store in Redis for quick lookup
                    redis = await get_redis()
                    await redis._client.hset(
                        f"presence:{user.id}",
                        mapping={
                            "presence": presence,
                            "status_text": status_text or "",
                            "activity": activity or "",
                        }
                    )
                    await redis._client.expire(f"presence:{user.id}", 300)  # 5 min TTL
                    
                    # Broadcast to user's squads
                    await connection.send_json({
                        "type": "presence_updated",
                        "presence": presence,
                    })

                elif message_type == "message_reaction":
                    # Message reaction via WebSocket
                    msg_id = data.get("message_id")
                    emoji = data.get("emoji")
                    action = data.get("action", "add")
                    channel_id = data.get("channel_id")
                    
                    if msg_id and emoji and channel_id:
                        redis = await get_redis()
                        chat_channel = f"squad:{channel_id}:chat"
                        await redis.publish(chat_channel, {
                            "type": "message_reaction",
                            "message_id": msg_id,
                            "emoji": emoji,
                            "action": action,
                            "user_id": str(user.id),
                            "username": user.username,
                        })

                elif message_type == "subscribe_dm":
                    # Subscribe to DM conversation
                    dm_id = data.get("dm_id")
                    if dm_id:
                        dm_channel = f"dm:{dm_id}"
                        await connection.subscribe_to_channel(dm_channel)
                        await connection.send_json({
                            "type": "subscribed",
                            "channel": dm_channel,
                        })

                elif message_type == "dm_message":
                    # Send DM via WebSocket
                    dm_id = data.get("dm_id")
                    content = data.get("content")
                    if dm_id and content:
                        redis = await get_redis()
                        dm_channel = f"dm:{dm_id}"
                        await redis.publish(dm_channel, {
                            "type": "dm_message",
                            "dm_id": dm_id,
                            "content": content,
                            "sender_id": str(user.id),
                            "sender_username": user.username,
                        })

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
