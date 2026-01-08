"""
WebSocket Connection Manager
Manages WebSocket connections, subscriptions, and message routing.
Performance-optimized with no global state.
"""

import asyncio
import json
import logging
from collections import defaultdict
from typing import Optional
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.core.redis_client import RedisClient
from backend.models.models import User

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Represents a single WebSocket connection with subscriptions."""

    def __init__(self, websocket: WebSocket, user: User, redis_client: RedisClient):
        """
        Initialize WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            user: Authenticated user
            redis_client: Redis client for Pub/Sub
        """
        self.websocket = websocket
        self.user = user
        self.user_id = user.id
        self.redis_client = redis_client
        self.active = True
        self._subscribed_channels: set[str] = set()
        self._pubsub: Optional[PubSub] = None
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Accept WebSocket connection."""
        await self.websocket.accept()

    async def disconnect(self) -> None:
        """Clean disconnect - unsubscribe from all channels and close connections."""
        self.active = False

        # Cancel listen task
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        # Unsubscribe from all channels
        if self._pubsub:
            try:
                if self._subscribed_channels:
                    await self._pubsub.unsubscribe(*self._subscribed_channels)
                await self._pubsub.close()
            except Exception as e:
                logger.warning(f"Error during pubsub cleanup for user {self.user_id}: {e}")
            finally:
                self._pubsub = None

        # Close WebSocket
        try:
            await self.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing websocket for user {self.user_id}: {e}")

        self._subscribed_channels.clear()

    async def subscribe_to_channel(self, channel: str) -> bool:
        """
        Subscribe to a Redis channel.

        Args:
            channel: Redis channel name

        Returns:
            True if subscription successful, False otherwise
        """
        if channel in self._subscribed_channels:
            return True  # Already subscribed

        try:
            # Initialize pubsub if needed
            if self._pubsub is None:
                await self.redis_client.connect()
                # Get the underlying Redis client to create pubsub
                # We need direct access to create PubSub for multiple channels
                redis_instance = self.redis_client._client
                if redis_instance is None:
                    raise RuntimeError("Redis client not initialized")
                
                self._pubsub = redis_instance.pubsub()
                await self._pubsub.subscribe(channel)
                self._subscribed_channels.add(channel)

                # Start listening task
                if self._listen_task is None or self._listen_task.done():
                    self._listen_task = asyncio.create_task(self._listen_for_messages())
            else:
                # Add to existing subscription
                await self._pubsub.subscribe(channel)
                self._subscribed_channels.add(channel)

            logger.info(f"User {self.user_id} subscribed to channel: {channel}")
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe user {self.user_id} to channel {channel}: {e}")
            return False

    async def unsubscribe_from_channel(self, channel: str) -> None:
        """
        Unsubscribe from a Redis channel.

        Args:
            channel: Redis channel name
        """
        if channel not in self._subscribed_channels:
            return

        try:
            if self._pubsub:
                await self._pubsub.unsubscribe(channel)
            self._subscribed_channels.discard(channel)
            logger.info(f"User {self.user_id} unsubscribed from channel: {channel}")
        except Exception as e:
            logger.warning(f"Error unsubscribing user {self.user_id} from channel {channel}: {e}")

    async def _listen_for_messages(self) -> None:
        """Listen for messages from Redis Pub/Sub and forward to WebSocket."""
        if not self._pubsub:
            return

        try:
            while self.active:
                try:
                    # Get message from Redis (with timeout to allow checking active flag)
                    message = await asyncio.wait_for(
                        self._pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0,
                    )

                    if message is None:
                        continue

                    if message["type"] == "message":
                        # Forward message to WebSocket client
                        try:
                            data = message["data"]
                            # Parse JSON if it's a string
                            if isinstance(data, str):
                                try:
                                    data = json.loads(data)
                                except json.JSONDecodeError:
                                    # If not JSON, send as-is
                                    pass

                            await self.send_json(data)
                        except Exception as e:
                            logger.error(
                                f"Error sending message to user {self.user_id}: {e}",
                                exc_info=True,
                            )

                except asyncio.TimeoutError:
                    # Timeout is expected, continue loop
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(
                        f"Error in message listener for user {self.user_id}: {e}",
                        exc_info=True,
                    )
                    # Small delay before retrying
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.debug(f"Message listener cancelled for user {self.user_id}")
        except Exception as e:
            logger.error(f"Fatal error in message listener for user {self.user_id}: {e}", exc_info=True)
        finally:
            logger.debug(f"Message listener stopped for user {self.user_id}")

    async def send_json(self, data: dict) -> None:
        """
        Send JSON data to WebSocket client.

        Args:
            data: Dictionary to send as JSON
        """
        if not self.active:
            return

        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.warning(f"Failed to send message to user {self.user_id}: {e}")
            # Mark as inactive if send fails
            self.active = False

    async def send_text(self, text: str) -> None:
        """
        Send text message to WebSocket client.

        Args:
            text: Text message to send
        """
        if not self.active:
            return

        try:
            await self.websocket.send_text(text)
        except Exception as e:
            logger.warning(f"Failed to send text to user {self.user_id}: {e}")
            self.active = False


class WebSocketManager:
    """Manages all WebSocket connections and subscriptions."""

    def __init__(self, redis_client: RedisClient):
        """
        Initialize WebSocket manager.

        Args:
            redis_client: Redis client instance
        """
        self.redis_client = redis_client
        # Map user_id -> WebSocketConnection
        self._connections: dict[UUID, WebSocketConnection] = {}
        # Map channel -> set of user_ids subscribed
        self._channel_subscribers: dict[str, set[UUID]] = defaultdict(set)
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        user: User,
    ) -> WebSocketConnection:
        """
        Register and connect a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            user: Authenticated user

        Returns:
            WebSocketConnection instance
        """
        async with self._lock:
            # Disconnect existing connection for this user if any
            if user.id in self._connections:
                old_conn = self._connections[user.id]
                await old_conn.disconnect()

            # Create new connection
            conn = WebSocketConnection(websocket, user, self.redis_client)
            await conn.connect()
            self._connections[user.id] = conn

            # Auto-subscribe to user's personal channel
            personal_channel = f"user:{user.id}:notifications"
            await conn.subscribe_to_channel(personal_channel)
            self._channel_subscribers[personal_channel].add(user.id)

            logger.info(f"User {user.id} connected via WebSocket")
            return conn

    async def disconnect(self, user_id: UUID) -> None:
        """
        Disconnect a user's WebSocket connection.

        Args:
            user_id: User UUID
        """
        async with self._lock:
            if user_id not in self._connections:
                return

            conn = self._connections[user_id]
            await conn.disconnect()

            # Remove from all channel subscribers
            for channel in list(conn._subscribed_channels):
                self._channel_subscribers[channel].discard(user_id)

            del self._connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")

    async def subscribe_to_squad(
        self,
        user_id: UUID,
        squad_id: UUID,
    ) -> bool:
        """
        Subscribe user to a squad channel.

        Args:
            user_id: User UUID
            squad_id: Squad UUID

        Returns:
            True if subscription successful, False otherwise
        """
        async with self._lock:
            if user_id not in self._connections:
                logger.warning(f"Cannot subscribe user {user_id} to squad {squad_id}: not connected")
                return False

            conn = self._connections[user_id]
            channel = f"squad:{squad_id}:summons"
            success = await conn.subscribe_to_channel(channel)
            if success:
                self._channel_subscribers[channel].add(user_id)
            return success

    async def subscribe_to_summon(
        self,
        user_id: UUID,
        summon_id: UUID,
    ) -> bool:
        """
        Subscribe user to a specific summon channel.

        Args:
            user_id: User UUID
            summon_id: Summon UUID

        Returns:
            True if subscription successful, False otherwise
        """
        async with self._lock:
            if user_id not in self._connections:
                logger.warning(f"Cannot subscribe user {user_id} to summon {summon_id}: not connected")
                return False

            conn = self._connections[user_id]
            channel = f"summon:{summon_id}:updates"
            success = await conn.subscribe_to_channel(channel)
            if success:
                self._channel_subscribers[channel].add(user_id)
            return success

    async def unsubscribe_from_squad(
        self,
        user_id: UUID,
        squad_id: UUID,
    ) -> None:
        """
        Unsubscribe user from a squad channel.

        Args:
            user_id: User UUID
            squad_id: Squad UUID
        """
        async with self._lock:
            if user_id not in self._connections:
                return

            conn = self._connections[user_id]
            channel = f"squad:{squad_id}:summons"
            await conn.unsubscribe_from_channel(channel)
            self._channel_subscribers[channel].discard(user_id)

    async def unsubscribe_from_summon(
        self,
        user_id: UUID,
        summon_id: UUID,
    ) -> None:
        """
        Unsubscribe user from a summon channel.

        Args:
            user_id: User UUID
            summon_id: Summon UUID
        """
        async with self._lock:
            if user_id not in self._connections:
                return

            conn = self._connections[user_id]
            channel = f"summon:{summon_id}:updates"
            await conn.unsubscribe_from_channel(channel)
            self._channel_subscribers[channel].discard(user_id)

    def get_connection(self, user_id: UUID) -> Optional[WebSocketConnection]:
        """
        Get connection for a user.

        Args:
            user_id: User UUID

        Returns:
            WebSocketConnection if exists, None otherwise
        """
        return self._connections.get(user_id)

    def get_active_connections_count(self) -> int:
        """
        Get count of active connections.

        Returns:
            Number of active WebSocket connections
        """
        return len([c for c in self._connections.values() if c.active])

    async def broadcast_to_channel(self, channel: str, message: dict) -> int:
        """
        Broadcast message to all subscribers of a channel via Redis.

        This method publishes to Redis, and Redis Pub/Sub will deliver to subscribers.

        Args:
            channel: Redis channel name
            message: Message payload

        Returns:
            Number of subscribers that received the message
        """
        await self.redis_client.connect()
        return await self.redis_client.publish(channel, message)
