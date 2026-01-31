"""
Sentry Error Monitoring Integration
"""
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    """Initialize Sentry for error tracking"""
    sentry_dsn = os.getenv('SENTRY_DSN')
    if not sentry_dsn:
        print("Warning: SENTRY_DSN not set, skipping Sentry initialization")
        return
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
        # We recommend adjusting this value in production
        send_default_pii=False,  # Don't send personally identifiable information
    )

def capture_exception(error: Exception, context: dict = None):
    """Capture exception to Sentry with context"""
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)

def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture message to Sentry"""
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)
