"""
SendGrid Email Service
Handles email sending for verification, notifications, and alerts.
"""

import logging
from typing import List, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, Personalization

from backend.core.config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL

logger = logging.getLogger(__name__)


class EmailService:
    """SendGrid email service."""

    def __init__(self):
        """Initialize SendGrid client."""
        self._client = None
        self._from_email = SENDGRID_FROM_EMAIL

    def _get_client(self) -> SendGridAPIClient:
        """Get or create SendGrid client."""
        if self._client is None:
            if not SENDGRID_API_KEY:
                raise ValueError("SENDGRID_API_KEY not configured")
            self._client = SendGridAPIClient(SENDGRID_API_KEY)
            logger.info("✅ SendGrid client initialized")
        return self._client

    async def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_token: str,
        frontend_url: str = "http://localhost:3000",
    ) -> bool:
        """
        Send email verification link.

        Args:
            to_email: Recipient email
            username: User's username
            verification_token: Verification token
            frontend_url: Frontend base URL

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            verification_link = f"{frontend_url}/verify-email?token={verification_token}"

            message = Mail(
                from_email=self._from_email,
                to_emails=to_email,
                subject="Verify Your SquadSync Account",
                html_content=f"""
                <html>
                  <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Welcome to SquadSync, {username}! 🎮</h2>
                    <p>Please verify your email address by clicking the link below:</p>
                    <a href="{verification_link}" 
                       style="display: inline-block; padding: 10px 20px; 
                              background-color: #7c3aed; color: white; 
                              text-decoration: none; border-radius: 5px;">
                      Verify Email
                    </a>
                    <p>Or copy and paste this link:</p>
                    <p>{verification_link}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                      SquadSync - Your Gaming Squad Platform
                    </p>
                  </body>
                </html>
                """
            )

            client = self._get_client()
            response = client.send(message)

            if response.status_code in [200, 202]:
                logger.info(f"✅ Verification email sent to {to_email}")
                return True
            else:
                logger.error(f"❌ Failed to send verification email: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending verification email: {e}")
            return False

    async def send_summon_notification(
        self,
        to_emails: List[str],
        squad_name: str,
        summon_title: str,
        summon_message: str,
        created_by: str,
    ) -> bool:
        """
        Send summon notification to squad members.

        Args:
            to_emails: List of recipient emails
            squad_name: Name of the squad
            summon_title: Summon title
            summon_message: Summon message
            created_by: Username of summon creator

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=self._from_email,
                subject=f"🎮 Summon Alert: {summon_title}",
                html_content=f"""
                <html>
                  <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>🎮 New Summon in {squad_name}!</h2>
                    <p><strong>{created_by}</strong> has summoned the squad!</p>
                    <div style="background-color: #f3f4f6; padding: 15px; 
                                border-radius: 5px; margin: 15px 0;">
                      <h3 style="margin-top: 0;">{summon_title}</h3>
                      <p>{summon_message}</p>
                    </div>
                    <p>Login to SquadSync to respond!</p>
                    <a href="http://localhost:3000/dashboard" 
                       style="display: inline-block; padding: 10px 20px; 
                              background-color: #7c3aed; color: white; 
                              text-decoration: none; border-radius: 5px;">
                      Open SquadSync
                    </a>
                  </body>
                </html>
                """
            )

            # Add all recipients
            personalization = Personalization()
            for email in to_emails:
                personalization.add_to(To(email))
            message.add_personalization(personalization)

            client = self._get_client()
            response = client.send(message)

            if response.status_code in [200, 202]:
                logger.info(f"✅ Summon notification sent to {len(to_emails)} recipients")
                return True
            else:
                logger.error(f"❌ Failed to send summon notification: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending summon notification: {e}")
            return False

    async def send_password_reset(
        self,
        to_email: str,
        username: str,
        reset_token: str,
        frontend_url: str = "http://localhost:3000",
    ) -> bool:
        """
        Send password reset email.

        Args:
            to_email: Recipient email
            username: User's username
            reset_token: Password reset token
            frontend_url: Frontend base URL

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            reset_link = f"{frontend_url}/reset-password?token={reset_token}"

            message = Mail(
                from_email=self._from_email,
                to_emails=to_email,
                subject="Reset Your SquadSync Password",
                html_content=f"""
                <html>
                  <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Password Reset Request</h2>
                    <p>Hi {username},</p>
                    <p>You requested to reset your SquadSync password.</p>
                    <p>Click the link below to reset your password:</p>
                    <a href="{reset_link}" 
                       style="display: inline-block; padding: 10px 20px; 
                              background-color: #7c3aed; color: white; 
                              text-decoration: none; border-radius: 5px;">
                      Reset Password
                    </a>
                    <p>Or copy and paste this link:</p>
                    <p>{reset_link}</p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                  </body>
                </html>
                """
            )

            client = self._get_client()
            response = client.send(message)

            if response.status_code in [200, 202]:
                logger.info(f"✅ Password reset email sent to {to_email}")
                return True
            else:
                logger.error(f"❌ Failed to send password reset email: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending password reset email: {e}")
            return False


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get global email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
