"""
Sentry Error Monitoring Integration
Captures and reports errors to Sentry for production monitoring.
"""

import logging
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from backend.core.config import ENVIRONMENT, SENTRY_DSN

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """
    Initialize Sentry error monitoring.

    Call this at application startup.
    """
    if not SENTRY_DSN:
        logger.warning("⚠️  SENTRY_DSN not configured, error monitoring disabled")
        return

    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            traces_sample_rate=1.0 if ENVIRONMENT == "development" else 0.1,
            profiles_sample_rate=1.0 if ENVIRONMENT == "development" else 0.1,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
            ],
            # Send PII (Personally Identifiable Information) - disable in production if needed
            send_default_pii=ENVIRONMENT == "development",
            # Attach stack traces
            attach_stacktrace=True,
            # Max breadcrumbs
            max_breadcrumbs=50,
        )
        logger.info("✅ Sentry initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {e}")


def capture_exception(exception: Exception, context: Optional[dict] = None) -> None:
    """
    Capture exception and send to Sentry.

    Args:
        exception: Exception to capture
        context: Additional context data
    """
    try:
        if context:
            sentry_sdk.set_context("custom", context)
        sentry_sdk.capture_exception(exception)
    except Exception as e:
        logger.error(f"❌ Failed to capture exception in Sentry: {e}")


def capture_message(message: str, level: str = "info", context: Optional[dict] = None) -> None:
    """
    Capture custom message and send to Sentry.

    Args:
        message: Message to capture
        level: Log level (debug, info, warning, error, fatal)
        context: Additional context data
    """
    try:
        if context:
            sentry_sdk.set_context("custom", context)
        sentry_sdk.capture_message(message, level=level)
    except Exception as e:
        logger.error(f"❌ Failed to capture message in Sentry: {e}")


def set_user_context(user_id: str, email: str, username: str) -> None:
    """
    Set user context for Sentry error tracking.

    Args:
        user_id: User UUID
        email: User email
        username: Username
    """
    try:
        sentry_sdk.set_user({"id": user_id, "email": email, "username": username})
    except Exception as e:
        logger.error(f"❌ Failed to set user context in Sentry: {e}")
