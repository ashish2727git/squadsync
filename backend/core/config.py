"""
Application configuration from environment variables.
"""

import os
import warnings

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-minimum-32-chars")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# CORS
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
).split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Security warnings for development
if ENVIRONMENT == "development":
    if JWT_SECRET_KEY == "dev-secret-key-change-in-production-minimum-32-chars":
        warnings.warn(
            "⚠️  Using default JWT secret key. Set JWT_SECRET_KEY environment variable in production!",
            UserWarning
        )
else:
    # Production checks
    if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
        raise ValueError(
            "JWT_SECRET_KEY must be set and at least 32 characters in production!"
        )
