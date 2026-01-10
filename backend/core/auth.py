"""
JWT Authentication Core
Production-grade JWT authentication with access and refresh tokens.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError

from backend.core.config import JWT_ALGORITHM, JWT_SECRET_KEY

# Refresh token configuration
JWT_REFRESH_SECRET_KEY = os.getenv(
    "JWT_REFRESH_SECRET_KEY",
    JWT_SECRET_KEY  # In production, use a different secret
)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # Short-lived
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # Long-lived


class JWTError(Exception):
    """Base exception for JWT authentication errors."""

    pass


class InvalidToken(JWTError):
    """Raised when JWT token is invalid."""

    pass


class ExpiredToken(JWTError):
    """Raised when JWT token has expired."""

    pass


def create_access_token(user_id: UUID, username: str, email: str, role: str) -> str:
    """
    Create JWT access token (short-lived).

    Args:
        user_id: User UUID
        username: Username
        email: User email
        role: User role

    Returns:
        Encoded JWT access token string
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "username": username,
        "email": email,
        "role": role,
        "type": "access",  # Token type
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """
    Create JWT refresh token (long-lived).

    Args:
        user_id: User UUID

    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",  # Token type
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT access token.

    Args:
        token: JWT access token string

    Returns:
        Decoded token payload

    Raises:
        InvalidToken: If token is invalid
        ExpiredToken: If token has expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            raise InvalidToken("Token is not an access token")
        
        return payload
    except ExpiredSignatureError:
        raise ExpiredToken("Access token has expired")
    except DecodeError:
        raise InvalidToken("Invalid token format")
    except InvalidTokenError as e:
        raise InvalidToken(f"Invalid token: {str(e)}")


def decode_refresh_token(token: str) -> dict:
    """
    Decode and validate JWT refresh token.

    Args:
        token: JWT refresh token string

    Returns:
        Decoded token payload

    Raises:
        InvalidToken: If token is invalid
        ExpiredToken: If token has expired
    """
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise InvalidToken("Token is not a refresh token")
        
        return payload
    except ExpiredSignatureError:
        raise ExpiredToken("Refresh token has expired")
    except DecodeError:
        raise InvalidToken("Invalid token format")
    except InvalidTokenError as e:
        raise InvalidToken(f"Invalid token: {str(e)}")


def get_user_id_from_token(token: str, token_type: str = "access") -> UUID:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string
        token_type: Token type ("access" or "refresh")

    Returns:
        User UUID

    Raises:
        InvalidToken: If token is invalid or expired
    """
    if token_type == "access":
        payload = decode_access_token(token)
    elif token_type == "refresh":
        payload = decode_refresh_token(token)
    else:
        raise InvalidToken(f"Invalid token type: {token_type}")
    
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
    token_type: str = "access",
) -> Optional["User"]:
    """
    Get User object from JWT token.

    Args:
        db: Database session
        token: JWT token string
        token_type: Token type ("access" or "refresh")

    Returns:
        User object if token is valid, None otherwise
    """
    from sqlalchemy import select
    from backend.models.models import User

    try:
        user_id = get_user_id_from_token(token, token_type)
        stmt = select(User).where(User.id == user_id, User.is_active == True)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except (InvalidToken, ExpiredToken):
        return None
