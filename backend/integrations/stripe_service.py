"""
Stripe Payment Integration
"""
import os
import stripe
from typing import Optional, List

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripeService:
    def __init__(self):
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    async def create_customer(
        self, 
        email: str, 
        username: str, 
        user_id: str
    ) -> dict:
        """Create Stripe customer"""
        customer = stripe.Customer.create(
            email=email,
            name=username,
            metadata={'user_id': user_id}
        )
        return {
            'customer_id': customer.id,
            'email': customer.email
        }

    async def create_subscription(
        self, 
        customer_id: str, 
        price_id: str
    ) -> dict:
        """Create subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )
        return {
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        }

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception:
            return False

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> str:
        """Create checkout session"""
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url
        )
        return session.url

    def verify_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Verify Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")

# Subscription plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'max_squads': 3,
        'max_members_per_squad': 5,
        'features': ['basic_chat', 'basic_voice', 'whiteboard']
    },
    'pro': {
        'name': 'Pro',
        'price_monthly': 999,  # $9.99
        'max_squads': 20,
        'max_members_per_squad': 20,
        'features': ['all_free', 'priority_voice', 'screen_share', 'recordings']
    },
    'team': {
        'name': 'Team',
        'price_monthly': 2999,  # $29.99
        'max_squads': -1,  # unlimited
        'max_members_per_squad': 100,
        'features': ['all_pro', 'dedicated_server', 'custom_branding', 'analytics']
    }
}

stripe_service = StripeService()
