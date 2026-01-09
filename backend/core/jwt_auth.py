"""
JWT Authentication Utilities
JWT token validation for WebSocket and HTTP authentication.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError
from sqlalchemy import and_, select

from backend.models.models import User

# JWT Configuration - imported from config module
from backend.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)


class JWTError(Exception):
    """Base exception for JWT authentication errors."""

    pass


class InvalidToken(JWTError):
    """Raised when JWT token is invalid."""

    pass


class ExpiredToken(JWTError):
    """Raised when JWT token has expired."""

    pass


def create_access_token(user_id: UUID, username: str, email: str) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User UUID
        username: Username
        email: User email

    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "username": username,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        InvalidToken: If token is invalid
        ExpiredToken: If token has expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise ExpiredToken("Token has expired")
    except DecodeError:
        raise InvalidToken("Invalid token format")
    except InvalidTokenError as e:
        raise InvalidToken(f"Invalid token: {str(e)}")


def get_user_id_from_token(token: str) -> UUID:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User UUID

    Raises:
        InvalidToken: If token is invalid or expired
    """
    payload = decode_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidToken("Token missing subject (user_id)")
    try:
        return UUID(user_id_str)
    except ValueError:
        raise InvalidToken(f"Invalid user ID format in token: {user_id_str}")


async def get_user_from_token(
    db,
    token: str,
) -> Optional[User]:
    """
    Get User object from JWT token.

    Args:
        db: Database session
        token: JWT token string

    Returns:
        User object if token is valid, None otherwise
    """
    from sqlalchemy import select

    try:
        user_id = get_user_id_from_token(token)
        stmt = select(User).where(and_(User.id == user_id, User.is_active == True))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except (InvalidToken, ExpiredToken):
        return None


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
