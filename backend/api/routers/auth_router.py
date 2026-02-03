"""
Authentication API Router
Production-grade authentication endpoints with strict validation.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.auth_schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from backend.core.auth import (
    InvalidToken,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_user_from_token,
)
from backend.core.dependencies import get_db, get_current_user
from backend.core.security import hash_password, verify_password
from backend.models.models import User, UserRole

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Username and email must be unique.",
)
async def register(
    request: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user.

    Validates:
    - Username uniqueness
    - Email uniqueness
    - Password strength
    - Email format

    Returns:
        User information (without password)
    """
    # Check if username already exists
    stmt = select(User).where(User.username == request.username)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(request.password)

    # Create user (default role is PLAYER, only admins can set other roles)
    user_role = UserRole.PLAYER
    if request.role and request.role != "PLAYER":
        # In production, only admins can set non-PLAYER roles
        # For now, we'll default to PLAYER for security
        user_role = UserRole.PLAYER

    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        role=user_role,
        is_active=True,
        is_verified=False,  # Email verification required
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role.value,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and receive access + refresh tokens.",
)
async def login(
    request: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    Accepts username or email for login.

    Returns:
        Access token (short-lived) and refresh token (long-lived)
    """
    # Find user by username or email
    stmt = select(User).where(
        (User.username == request.username) | (User.email == request.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if username/email exists (security best practice)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Update last login (optional, can be done in background)
    from datetime import datetime, timezone

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(user_id=user.id)

    # Calculate expiration time
    from backend.core.auth import JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Use refresh token to get a new access token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Validates refresh token and returns new access + refresh tokens.
    """
    try:
        # Decode refresh token
        payload = decode_refresh_token(request.refresh_token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidToken("Refresh token missing subject")

        user_id = UUID(user_id_str)

        # Get user from database
        user = await get_user_from_token(db, request.refresh_token, token_type="refresh")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Create new tokens
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(user_id=user.id)

        from backend.core.auth import JWT_ACCESS_TOKEN_EXPIRE_MINUTES

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get information about the currently authenticated user.",
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Get current authenticated user information.

    Requires valid access token.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )


from pydantic import BaseModel, Field
from typing import Optional

class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = None


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update the current user's profile information.",
)
async def update_profile(
    request: ProfileUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Update current user's profile.
    """
    if request.username and request.username != current_user.username:
        # Check if username is taken
        stmt = select(User).where(User.username == request.username)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        current_user.username = request.username

    # Note: bio and avatar_url would need to be added to User model
    # For now, just update username
    
    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )
