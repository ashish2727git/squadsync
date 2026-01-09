"""
Centralized FastAPI dependencies for authentication and database.
"""

import os
import warnings
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.core.jwt_auth import get_user_from_token, InvalidToken, ExpiredToken
from backend.models.models import User

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Set to True for SQL debugging
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    """
    Get database session with proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> User:
    """
    Get current authenticated user from JWT token.
    
    For development/testing: If no token provided, returns a mock user.
    WARNING: Remove mock user in production!
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Development mode: Allow requests without auth (REMOVE IN PRODUCTION!)
    if not credentials:
        if os.getenv("ENVIRONMENT") == "development":
            warnings.warn(
                "⚠️  DEVELOPMENT MODE: Allowing unauthenticated requests. "
                "This is INSECURE and must be removed in production!",
                UserWarning
            )
            # Create a mock user for development
            # In production, this should raise HTTPException
            from uuid import UUID
            mock_user = User(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                username="dev_user",
                email="dev@example.com",
                is_active=True,
            )
            return mock_user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    token = credentials.credentials
    
    try:
        user = await get_user_from_token(db, token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        return user
    except (InvalidToken, ExpiredToken) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
