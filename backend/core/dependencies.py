"""
Centralized FastAPI dependencies for authentication and database.
Production-grade authentication with no development bypasses.
"""

import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.core.auth import InvalidToken, ExpiredToken, get_user_from_token
from backend.core.config import ENVIRONMENT
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

# OAuth2 Password Bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)

# HTTP Bearer token security
security = HTTPBearer(auto_error=True)  # Require auth by default


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
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current authenticated user from JWT access token.
    
    Production-grade authentication with no development bypasses.
    All endpoints using this dependency require valid authentication.
    
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    token = credentials.credentials
    
    try:
        user = await get_user_from_token(db, token, token_type="access")
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
    except Exception as e:
        # Log unexpected errors but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )