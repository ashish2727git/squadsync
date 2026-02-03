"""
OAuth Authentication Router
Handles Google and Discord OAuth login flow.
"""

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import create_access_token, create_refresh_token
from backend.core.dependencies import get_db
from backend.core.oauth_service import get_oauth_service
from backend.models.models import User, UserRole

router = APIRouter(prefix="/api/v1/auth/oauth", tags=["oauth"])


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: str


class OAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.get("/google/url")
async def get_google_auth_url(
    redirect_uri: str = Query(..., description="Frontend redirect URI"),
) -> dict:
    """
    Get Google OAuth authorization URL.
    
    Frontend should redirect user to this URL.
    """
    try:
        oauth = get_oauth_service()
        state = str(uuid4())  # CSRF protection
        
        auth_url = await oauth.get_google_auth_url(redirect_uri, state)
        
        return {
            "auth_url": auth_url,
            "state": state,  # Frontend should store this to verify callback
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.post("/google/callback", response_model=OAuthResponse)
async def google_oauth_callback(
    request: OAuthCallbackRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OAuthResponse:
    """
    Handle Google OAuth callback.
    
    Exchange authorization code for user info and create/login user.
    """
    oauth = get_oauth_service()
    
    # Exchange code for user info
    user_info = await oauth.exchange_google_code(request.code, request.redirect_uri)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google"
        )
    
    # Find or create user
    email = user_info["email"]
    
    # Check if user exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        username = user_info["name"].replace(" ", "").lower()
        # Ensure unique username
        base_username = username
        counter = 1
        while True:
            stmt = select(User).where(User.username == username)
            result = await db.execute(stmt)
            if result.scalar_one_or_none() is None:
                break
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            username=username,
            email=email,
            hashed_password="",  # OAuth users don't have passwords
            role=UserRole.PLAYER,
            is_active=True,
            is_verified=True,  # OAuth users are pre-verified
            avatar_url=user_info.get("picture"),
            oauth_provider="google",
            oauth_provider_id=user_info["provider_id"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Track registration
        try:
            from backend.core.analytics_service import get_analytics_service
            analytics = get_analytics_service()
            await analytics.track_user_registration(user.id, user.username, user.email)
        except Exception:
            pass  # Don't fail login if analytics fails
    
    # Generate tokens
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(user_id=user.id)
    
    return OAuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
        }
    )


@router.get("/discord/url")
async def get_discord_auth_url(
    redirect_uri: str = Query(..., description="Frontend redirect URI"),
) -> dict:
    """
    Get Discord OAuth authorization URL.
    
    Frontend should redirect user to this URL.
    """
    try:
        oauth = get_oauth_service()
        state = str(uuid4())
        
        auth_url = await oauth.get_discord_auth_url(redirect_uri, state)
        
        return {
            "auth_url": auth_url,
            "state": state,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.post("/discord/callback", response_model=OAuthResponse)
async def discord_oauth_callback(
    request: OAuthCallbackRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OAuthResponse:
    """
    Handle Discord OAuth callback.
    
    Exchange authorization code for user info and create/login user.
    """
    oauth = get_oauth_service()
    
    # Exchange code for user info
    user_info = await oauth.exchange_discord_code(request.code, request.redirect_uri)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Discord"
        )
    
    # Find or create user
    email = user_info["email"]
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discord account must have verified email"
        )
    
    # Check if user exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        username = user_info["name"].replace(" ", "").lower()
        # Ensure unique username
        base_username = username
        counter = 1
        while True:
            stmt = select(User).where(User.username == username)
            result = await db.execute(stmt)
            if result.scalar_one_or_none() is None:
                break
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            username=username,
            email=email,
            hashed_password="",
            role=UserRole.PLAYER,
            is_active=True,
            is_verified=True,
            avatar_url=user_info.get("picture"),
            oauth_provider="discord",
            oauth_provider_id=user_info["provider_id"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Track registration
        try:
            from backend.core.analytics_service import get_analytics_service
            analytics = get_analytics_service()
            await analytics.track_user_registration(user.id, user.username, user.email)
        except Exception:
            pass
    
    # Generate tokens
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(user_id=user.id)
    
    return OAuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
        }
    )
