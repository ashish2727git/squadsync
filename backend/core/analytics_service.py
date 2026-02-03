"""
Google Analytics & Mixpanel Integration
Tracks user events and analytics.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from mixpanel import Mixpanel

from backend.core.config import MIXPANEL_TOKEN

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Analytics service for tracking user events."""

    def __init__(self):
        """Initialize analytics."""
        self._mixpanel: Optional[Mixpanel] = None
        if MIXPANEL_TOKEN:
            self._mixpanel = Mixpanel(MIXPANEL_TOKEN)
            logger.info("✅ Mixpanel initialized")
        else:
            logger.warning("⚠️  MIXPANEL_TOKEN not configured")

    async def track_event(
        self,
        user_id: UUID,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track user event.

        Args:
            user_id: User UUID
            event_name: Event name
            properties: Additional event properties
        """
        if not self._mixpanel:
            return

        try:
            self._mixpanel.track(
                str(user_id),
                event_name,
                properties or {}
            )
            logger.debug(f"📊 Event tracked: {event_name}")
        except Exception as e:
            logger.error(f"❌ Failed to track event: {e}")

    async def track_user_registration(
        self,
        user_id: UUID,
        username: str,
        email: str,
    ) -> None:
        """Track user registration event."""
        await self.track_event(
            user_id,
            "User Registered",
            {
                "username": username,
                "email": email,
            }
        )

    async def track_squad_created(
        self,
        user_id: UUID,
        squad_id: UUID,
        squad_name: str,
    ) -> None:
        """Track squad creation event."""
        await self.track_event(
            user_id,
            "Squad Created",
            {
                "squad_id": str(squad_id),
                "squad_name": squad_name,
            }
        )

    async def track_squad_joined(
        self,
        user_id: UUID,
        squad_id: UUID,
        squad_name: str,
    ) -> None:
        """Track squad join event."""
        await self.track_event(
            user_id,
            "Squad Joined",
            {
                "squad_id": str(squad_id),
                "squad_name": squad_name,
            }
        )

    async def track_summon_created(
        self,
        user_id: UUID,
        squad_id: UUID,
        summon_id: UUID,
    ) -> None:
        """Track summon creation event."""
        await self.track_event(
            user_id,
            "Summon Created",
            {
                "squad_id": str(squad_id),
                "summon_id": str(summon_id),
            }
        )

    async def track_war_room_entered(
        self,
        user_id: UUID,
        squad_id: UUID,
    ) -> None:
        """Track War Room entry event."""
        await self.track_event(
            user_id,
            "War Room Entered",
            {
                "squad_id": str(squad_id),
            }
        )

    async def set_user_profile(
        self,
        user_id: UUID,
        properties: Dict[str, Any],
    ) -> None:
        """
        Set user profile properties.

        Args:
            user_id: User UUID
            properties: User properties
        """
        if not self._mixpanel:
            return

        try:
            self._mixpanel.people_set(str(user_id), properties)
            logger.debug(f"📊 User profile updated: {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to update user profile: {e}")


# Global analytics service instance
_analytics_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Get global analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
