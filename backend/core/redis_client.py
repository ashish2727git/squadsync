"""
Redis Client Configuration
Production-grade Redis client for Pub/Sub and caching.
"""

import json
from typing import Any, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis


class RedisClient:
    """Redis client wrapper for async operations."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis client.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self._client: Optional[Redis] = None
        self._pubsub: Optional[aioredis.client.PubSub] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        if self._client is None:
            self._client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
            # Ensure connection is established
            await self._client.ping()

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

        if self._client:
            await self._client.aclose()
            self._client = None

    async def publish(self, channel: str, message: dict[str, Any]) -> int:
        """
        Publish message to Redis channel.

        Args:
            channel: Redis channel name
            message: Message payload as dictionary

        Returns:
            Number of subscribers that received the message
        """
        if self._client is None:
            await self.connect()

        message_json = json.dumps(message, default=str)
        return await self._client.publish(channel, message_json)

    async def subscribe(self, channel: str) -> aioredis.client.PubSub:
        """
        Subscribe to Redis channel.

        Args:
            channel: Redis channel name

        Returns:
            PubSub object for receiving messages
        """
        if self._client is None:
            await self.connect()

        self._pubsub = self._client.pubsub()
        await self._pubsub.subscribe(channel)
        return self._pubsub

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.

        Args:
            key: Redis key

        Returns:
            Value as string or None if not found
        """
        if self._client is None:
            await self.connect()

        return await self._client.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        Set value in Redis.

        Args:
            key: Redis key
            value: Value to set
            ex: Optional expiration time in seconds

        Returns:
            True if successful
        """
        if self._client is None:
            await self.connect()

        return await self._client.set(key, value, ex=ex)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Get Redis client instance.

    Returns:
        RedisClient instance
    """
    if redis_client._client is None:
        await redis_client.connect()
    return redis_client
