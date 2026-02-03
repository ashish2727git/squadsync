"""
Firebase Cloud Messaging (FCM) Integration
Handles push notifications for mobile and web.
"""

import logging
from typing import List, Optional

import firebase_admin
from firebase_admin import credentials, messaging

from backend.core.config import FIREBASE_CREDENTIALS_PATH

logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase Cloud Messaging service."""

    def __init__(self):
        """Initialize Firebase."""
        self._initialized = False

    def initialize(self) -> None:
        """Initialize Firebase Admin SDK."""
        if self._initialized:
            return

        try:
            if not FIREBASE_CREDENTIALS_PATH:
                logger.warning("⚠️  FIREBASE_CREDENTIALS_PATH not configured")
                return

            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            self._initialized = True
            logger.info("✅ Firebase initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> bool:
        """
        Send push notification to a single device.

        Args:
            device_token: FCM device registration token
            title: Notification title
            body: Notification body
            data: Additional data payload

        Returns:
            True if sent successfully, False otherwise
        """
        if not self._initialized:
            logger.warning("Firebase not initialized, skipping notification")
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=device_token,
            )

            response = messaging.send(message)
            logger.info(f"✅ Push notification sent: {response}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send push notification: {e}")
            return False

    async def send_multicast_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> int:
        """
        Send push notification to multiple devices.

        Args:
            device_tokens: List of FCM device registration tokens
            title: Notification title
            body: Notification body
            data: Additional data payload

        Returns:
            Number of successfully sent notifications
        """
        if not self._initialized:
            logger.warning("Firebase not initialized, skipping notification")
            return 0

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=device_tokens,
            )

            response = messaging.send_multicast(message)
            logger.info(
                f"✅ Multicast notification sent: "
                f"{response.success_count}/{len(device_tokens)} successful"
            )
            return response.success_count

        except Exception as e:
            logger.error(f"❌ Failed to send multicast notification: {e}")
            return 0

    async def send_summon_notification(
        self,
        device_tokens: List[str],
        squad_name: str,
        summon_title: str,
        created_by: str,
    ) -> int:
        """
        Send summon notification to squad members.

        Args:
            device_tokens: List of device tokens
            squad_name: Name of the squad
            summon_title: Summon title
            created_by: Username of summon creator

        Returns:
            Number of successfully sent notifications
        """
        return await self.send_multicast_notification(
            device_tokens=device_tokens,
            title=f"🎮 Summon in {squad_name}",
            body=f"{created_by}: {summon_title}",
            data={
                "type": "summon",
                "squad_name": squad_name,
                "created_by": created_by,
            }
        )


# Global Firebase service instance
_firebase_service: Optional[FirebaseService] = None


def get_firebase_service() -> FirebaseService:
    """Get global Firebase service instance."""
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseService()
    return _firebase_service
