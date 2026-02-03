"""
Application configuration from environment variables.
Production-grade configuration with strict validation.
"""

import os
import sys
import warnings

# Environment - must be one of: development, staging, production
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT not in ["development", "staging", "production"]:
    raise ValueError(f"Invalid ENVIRONMENT: {ENVIRONMENT}. Must be: development, staging, or production")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

# Validate JWT secret key
if not JWT_SECRET_KEY:
    if ENVIRONMENT == "production":
        sys.exit("CRITICAL: JWT_SECRET_KEY environment variable must be set in production!")
    else:
        JWT_SECRET_KEY = "dev-secret-key-change-in-production-minimum-32-chars"
        warnings.warn(
            "⚠️  Using default JWT secret key. Set JWT_SECRET_KEY environment variable!",
            UserWarning
        )

if not JWT_REFRESH_SECRET_KEY:
    if ENVIRONMENT == "production":
        sys.exit("CRITICAL: JWT_REFRESH_SECRET_KEY environment variable must be set in production!")
    else:
        JWT_REFRESH_SECRET_KEY = JWT_SECRET_KEY
        warnings.warn(
            "⚠️  Using same secret for refresh tokens. Set JWT_REFRESH_SECRET_KEY environment variable!",
            UserWarning
        )

if ENVIRONMENT == "production":
    if len(JWT_SECRET_KEY) < 32:
        sys.exit("CRITICAL: JWT_SECRET_KEY must be at least 32 characters in production!")
    if len(JWT_REFRESH_SECRET_KEY) < 32:
        sys.exit("CRITICAL: JWT_REFRESH_SECRET_KEY must be at least 32 characters in production!")

# Redis
REDIS_URL = os.environ.get("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is not set")


# CORS - Allow all local network access for development
ALLOWED_ORIGINS_STR = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://192.168.1.5:3000"
)
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")]

# In development, also allow any local network IP
if ENVIRONMENT == "development":
    ALLOWED_ORIGINS.append("*")  # Allow all origins in development

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Rate limiting configuration
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
RATE_LIMIT_REQUESTS_PER_HOUR = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"))
RATE_LIMIT_REQUESTS_PER_DAY = int(os.getenv("RATE_LIMIT_REQUESTS_PER_DAY", "10000"))

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

# SendGrid Email Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@squadsync.com")

# Sentry Error Monitoring
SENTRY_DSN = os.getenv("SENTRY_DSN")

# Firebase Cloud Messaging
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

# Stripe Payment Configuration
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Analytics Configuration
MIXPANEL_TOKEN = os.getenv("MIXPANEL_TOKEN")
GOOGLE_ANALYTICS_ID = os.getenv("GOOGLE_ANALYTICS_ID")

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

# Twilio TURN Server Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Cloudflare Configuration
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

# Frontend URL (for emails, OAuth redirects, etc.)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
