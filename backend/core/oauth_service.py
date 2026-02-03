"""
OAuth Integration
Handles Google and Discord OAuth authentication.
"""

import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx

from backend.core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
)

logger = logging.getLogger(__name__)


class OAuthService:
    """OAuth service for social login."""

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
    DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
    DISCORD_USER_INFO_URL = "https://discord.com/api/users/@me"

    def __init__(self):
        """Initialize OAuth service."""
        self._http_client = httpx.AsyncClient()

    async def get_google_auth_url(
        self,
        redirect_uri: str,
        state: str,
    ) -> str:
        """
        Get Google OAuth authorization URL.

        Args:
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection

        Returns:
            Authorization URL
        """
        if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == "your-google-client-id":
            raise ValueError("Google OAuth not configured. Set GOOGLE_CLIENT_ID in .env")
        
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        return f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def get_discord_auth_url(
        self,
        redirect_uri: str,
        state: str,
    ) -> str:
        """
        Get Discord OAuth authorization URL.

        Args:
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection

        Returns:
            Authorization URL
        """
        if not DISCORD_CLIENT_ID or DISCORD_CLIENT_ID == "your-discord-client-id":
            raise ValueError("Discord OAuth not configured. Set DISCORD_CLIENT_ID in .env")
        
        params = {
            "client_id": DISCORD_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "identify email",
            "state": state,
        }
        return f"{self.DISCORD_AUTH_URL}?{urlencode(params)}"

    async def exchange_google_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange Google authorization code for user info.

        Args:
            code: Authorization code
            redirect_uri: Redirect URI (must match authorization request)

        Returns:
            User info dict, or None if failed
        """
        try:
            # Exchange code for tokens
            token_response = await self._http_client.post(
                self.GOOGLE_TOKEN_URL,
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            token_response.raise_for_status()
            tokens = token_response.json()

            # Get user info
            user_response = await self._http_client.get(
                self.GOOGLE_USER_INFO_URL,
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            user_response.raise_for_status()
            user_info = user_response.json()

            logger.info(f"✅ Google OAuth successful: {user_info.get('email')}")
            return {
                "provider": "google",
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "provider_id": user_info.get("id"),
            }

        except Exception as e:
            logger.error(f"❌ Google OAuth failed: {e}")
            return None

    async def exchange_discord_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange Discord authorization code for user info.

        Args:
            code: Authorization code
            redirect_uri: Redirect URI (must match authorization request)

        Returns:
            User info dict, or None if failed
        """
        try:
            # Exchange code for tokens
            token_response = await self._http_client.post(
                self.DISCORD_TOKEN_URL,
                data={
                    "client_id": DISCORD_CLIENT_ID,
                    "client_secret": DISCORD_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            token_response.raise_for_status()
            tokens = token_response.json()

            # Get user info
            user_response = await self._http_client.get(
                self.DISCORD_USER_INFO_URL,
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            user_response.raise_for_status()
            user_info = user_response.json()

            logger.info(f"✅ Discord OAuth successful: {user_info.get('email')}")
            return {
                "provider": "discord",
                "email": user_info.get("email"),
                "name": user_info.get("username"),
                "picture": f"https://cdn.discordapp.com/avatars/{user_info.get('id')}/{user_info.get('avatar')}.png",
                "provider_id": user_info.get("id"),
            }

        except Exception as e:
            logger.error(f"❌ Discord OAuth failed: {e}")
            return None

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http_client.aclose()


# Global OAuth service instance
_oauth_service: Optional[OAuthService] = None


def get_oauth_service() -> OAuthService:
    """Get global OAuth service instance."""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = OAuthService()
    return _oauth_service
