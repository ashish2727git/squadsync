"""
Stripe Payment Integration
Handles subscriptions, payments, and billing.
"""

import logging
from typing import Optional

import stripe

from backend.core.config import STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET

logger = logging.getLogger(__name__)


class StripeService:
    """Stripe payment service."""

    def __init__(self):
        """Initialize Stripe."""
        if STRIPE_API_KEY:
            stripe.api_key = STRIPE_API_KEY
            logger.info("✅ Stripe initialized")
        else:
            logger.warning("⚠️  STRIPE_API_KEY not configured")

    async def create_customer(
        self,
        email: str,
        name: str,
        metadata: Optional[dict] = None,
    ) -> Optional[str]:
        """
        Create Stripe customer.

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Stripe customer ID, or None if failed
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            logger.info(f"✅ Stripe customer created: {customer.id}")
            return customer.id
        except Exception as e:
            logger.error(f"❌ Failed to create Stripe customer: {e}")
            return None

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0,
    ) -> Optional[dict]:
        """
        Create subscription for customer.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Trial period in days

        Returns:
            Subscription data, or None if failed
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days if trial_days > 0 else None,
            )
            logger.info(f"✅ Subscription created: {subscription.id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
            }
        except Exception as e:
            logger.error(f"❌ Failed to create subscription: {e}")
            return None

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel subscription.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"✅ Subscription cancelled: {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel subscription: {e}")
            return False

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[dict]:
        """
        Create payment intent for one-time payment.

        Args:
            amount: Amount in cents
            currency: Currency code
            customer_id: Stripe customer ID
            metadata: Additional metadata

        Returns:
            Payment intent data, or None if failed
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
            )
            logger.info(f"✅ Payment intent created: {intent.id}")
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
            }
        except Exception as e:
            logger.error(f"❌ Failed to create payment intent: {e}")
            return None

    async def verify_webhook(self, payload: bytes, signature: str) -> Optional[dict]:
        """
        Verify Stripe webhook signature.

        Args:
            payload: Webhook payload
            signature: Stripe signature header

        Returns:
            Event data if valid, None otherwise
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
            logger.info(f"✅ Webhook verified: {event['type']}")
            return event
        except Exception as e:
            logger.error(f"❌ Webhook verification failed: {e}")
            return None


# Global Stripe service instance
_stripe_service: Optional[StripeService] = None


def get_stripe_service() -> StripeService:
    """Get global Stripe service instance."""
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripeService()
    return _stripe_service
