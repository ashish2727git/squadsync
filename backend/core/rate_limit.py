"""
Rate Limiting Middleware
Redis-based rate limiting for API endpoints and WebSocket messages.
"""

import time
from typing import Callable, Optional

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.core.redis_client import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.
    
    Uses sliding window algorithm with Redis for distributed rate limiting.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        exempt_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.exempt_paths = exempt_paths or ["/health", "/ready", "/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Get user identifier (from token or IP)
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                from backend.core.auth import get_user_id_from_token
                user_id = str(get_user_id_from_token(token, token_type="access"))
            except Exception:
                pass  # Use IP if token invalid

        # Fallback to IP address
        if not user_id:
            user_id = request.client.host if request.client else "unknown"

        # Create rate limit keys
        minute_key = f"rate_limit:minute:{user_id}:{request.url.path}"
        hour_key = f"rate_limit:hour:{user_id}:{request.url.path}"
        day_key = f"rate_limit:day:{user_id}:{request.url.path}"

        try:
            redis = await get_redis()
            current_time = int(time.time())

            # Check minute limit
            minute_count = await redis._client.incr(minute_key)
            if minute_count == 1:
                await redis._client.expire(minute_key, 60)
            if minute_count > self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Maximum 60 requests per minute.",
                    headers={"Retry-After": "60"},
                )

            # Check hour limit
            hour_count = await redis._client.incr(hour_key)
            if hour_count == 1:
                await redis._client.expire(hour_key, 3600)
            if hour_count > self.requests_per_hour:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Maximum 1000 requests per hour.",
                    headers={"Retry-After": "3600"},
                )

            # Check day limit
            day_count = await redis._client.incr(day_key)
            if day_count == 1:
                await redis._client.expire(day_key, 86400)
            if day_count > self.requests_per_day:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Maximum 10000 requests per day.",
                    headers={"Retry-After": "86400"},
                )

        except HTTPException:
            raise
        except Exception as e:
            # If Redis fails, log but don't block requests (fail open)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Rate limiting check failed: {e}. Allowing request.")

        return await call_next(request)


async def check_rate_limit(
    user_id: str,
    endpoint: str,
    limit: int,
    window_seconds: int,
) -> bool:
    """
    Check rate limit for a specific user and endpoint.
    
    Args:
        user_id: User identifier
        endpoint: Endpoint path
        limit: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Returns:
        True if within limit, False if exceeded
    """
    try:
        redis = await get_redis()
        key = f"rate_limit:{window_seconds}:{user_id}:{endpoint}"
        count = await redis._client.incr(key)
        if count == 1:
            await redis._client.expire(key, window_seconds)
        return count <= limit
    except Exception:
        # Fail open if Redis unavailable
        return True
