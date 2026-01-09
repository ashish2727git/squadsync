# Critical Fixes - Immediate Implementation

## 🔴 MUST FIX BEFORE PRODUCTION

### 1. Authentication Dependencies (CRITICAL)

**Problem:** All routers have placeholder authentication that raises `NotImplementedError`

**Create:** `backend/core/dependencies.py`
```python
"""
Centralized FastAPI dependencies for authentication and database.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

from backend.core.jwt_auth import get_user_from_token, InvalidToken, ExpiredToken
from backend.models.models import User

# Database setup (configure with your actual database URL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/squadsync")
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# HTTP Bearer token security
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    Get database session with proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        user = await get_user_from_token(db, token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        return user
    except (InvalidToken, ExpiredToken) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
```

**Update all routers:** Replace placeholder dependencies with imports:
```python
from backend.core.dependencies import get_db, get_current_user
```

---

### 2. JWT Secret Key Security (CRITICAL)

**File:** `backend/core/jwt_auth.py`

**Replace:**
```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
```

**With:**
```python
import sys

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    sys.exit("CRITICAL: JWT_SECRET_KEY environment variable must be set")
if len(JWT_SECRET_KEY) < 32:
    sys.exit("CRITICAL: JWT_SECRET_KEY must be at least 32 characters for security")
```

---

### 3. Password Hashing (CRITICAL)

**Create:** `backend/core/security.py`
```python
"""
Password hashing and security utilities.
"""

import bcrypt
from typing import Optional


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
```

---

### 4. Rate Limiting (CRITICAL)

**Create:** `backend/core/rate_limit.py`
```python
"""
Rate limiting middleware for API endpoints.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

# In-memory rate limit store (use Redis in production)
_rate_limit_store: dict[str, list[datetime]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get user identifier (from token or IP)
        user_id = request.headers.get("X-User-ID") or request.client.host
        key = f"{user_id}:{request.url.path}"
        
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Clean old entries
        _rate_limit_store[key] = [
            ts for ts in _rate_limit_store[key] if ts > hour_ago
        ]
        
        # Check minute limit
        recent_requests = [ts for ts in _rate_limit_store[key] if ts > minute_ago]
        if len(recent_requests) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )
        
        # Check hour limit
        if len(_rate_limit_store[key]) >= self.requests_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Hourly rate limit exceeded. Please try again later.",
            )
        
        # Record request
        _rate_limit_store[key].append(now)
        
        response = await call_next(request)
        return response
```

**Note:** Use Redis for distributed rate limiting in production.

---

### 5. Input Sanitization (CRITICAL)

**Create:** `backend/core/sanitization.py`
```python
"""
Input sanitization utilities.
"""

import html
import re
from typing import Any


def sanitize_string(value: str, max_length: int = 10000) -> str:
    """
    Sanitize string input to prevent XSS.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    # Escape HTML entities
    value = html.escape(value, quote=True)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    return value.strip()


def sanitize_dict(data: dict[str, Any], max_depth: int = 10) -> dict[str, Any]:
    """
    Recursively sanitize dictionary values.
    
    Args:
        data: Dictionary to sanitize
        max_depth: Maximum nesting depth
        
    Returns:
        Sanitized dictionary
    """
    if max_depth <= 0:
        return {}
    
    sanitized = {}
    for key, value in data.items():
        # Sanitize key
        safe_key = sanitize_string(str(key), max_length=100)
        
        if isinstance(value, str):
            sanitized[safe_key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[safe_key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[safe_key] = [
                sanitize_dict(item, max_depth - 1) if isinstance(item, dict)
                else sanitize_string(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[safe_key] = value
    
    return sanitized
```

---

### 6. Database Indexes (HIGH PRIORITY)

**Create:** `alembic/versions/001_add_indexes.py`
```python
"""Add missing database indexes

Revision ID: 001_add_indexes
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Squad membership lookup index
    op.create_index(
        'idx_squad_membership_lookup',
        'squad_membership',
        ['squad_id', 'user_id', 'is_active'],
        unique=False
    )
    
    # Summon response lookup index
    op.create_index(
        'idx_summon_response_lookup',
        'summon_response',
        ['summon_id', 'user_id'],
        unique=False
    )
    
    # Squad event date range index
    op.create_index(
        'idx_squad_event_date',
        'squad_event',
        ['squad_id', 'start_time'],
        unique=False
    )
    
    # Squad daily goal lookup
    op.create_index(
        'idx_squad_daily_goal_squad',
        'squad_daily_goal',
        ['squad_id', 'target_date'],
        unique=False
    )

def downgrade():
    op.drop_index('idx_squad_membership_lookup', table_name='squad_membership')
    op.drop_index('idx_summon_response_lookup', table_name='summon_response')
    op.drop_index('idx_squad_event_date', table_name='squad_event')
    op.drop_index('idx_squad_daily_goal_squad', table_name='squad_daily_goal')
```

---

### 7. Optimize Permission Checks (HIGH PRIORITY)

**File:** `backend/core/permissions.py`

**Current:** Makes 4 separate queries for `can_access_squad`

**Optimized version:**
```python
async def can_access_squad(
    db: AsyncSession,
    user: User,
    squad_id: UUID,
    load_relationships: bool = False,
) -> bool:
    """
    Optimized single-query permission check.
    """
    if not user or not user.is_active:
        return False
    
    # Single query with UNION to check all permission types
    from sqlalchemy import union_all, literal
    
    # Check all permission types in one query
    permission_checks = union_all(
        # Organization Admin
        select(literal(1)).select_from(
            OrganizationAdmin.join(Team).join(Squad)
        ).where(
            and_(
                Squad.id == squad_id,
                OrganizationAdmin.user_id == user.id,
            )
        ),
        # Team Manager
        select(literal(1)).select_from(
            TeamManager.join(Squad)
        ).where(
            and_(
                Squad.id == squad_id,
                TeamManager.user_id == user.id,
            )
        ),
        # Squad Leader
        select(literal(1)).select_from(
            SquadLeader
        ).where(
            and_(
                SquadLeader.squad_id == squad_id,
                SquadLeader.user_id == user.id,
            )
        ),
        # Squad Member
        select(literal(1)).select_from(
            squad_membership_table
        ).where(
            and_(
                squad_membership_table.c.squad_id == squad_id,
                squad_membership_table.c.user_id == user.id,
                squad_membership_table.c.is_active == True,
            )
        ),
    ).limit(1)
    
    result = await db.execute(permission_checks)
    return result.first() is not None
```

---

### 8. Fix Transaction Management (HIGH PRIORITY)

**Issue:** Services use `flush()` but routers commit. If error occurs between flush and commit, data inconsistency.

**Fix:** Use transaction context managers in services:
```python
# In services, use transactions properly
async def create_summon(...):
    async with self.db.begin():  # Start transaction
        # ... operations ...
        # Transaction auto-commits on success, rolls back on exception
        pass
```

---

### 9. Remove Duplicate Models File

**Action:** Delete `models.py` from root directory
```bash
rm models.py
```

**Reason:** Duplicate of `backend/models/models.py`, causes confusion

---

### 10. WebSocket Token Security

**File:** `backend/api/gateway/websocket_gateway.py`

**Current:** Token in query string
**Fix:** Use initial message for authentication

```python
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    manager: WebSocketManager = Depends(get_websocket_manager),
):
    await websocket.accept()
    
    # Receive token as first message
    try:
        auth_message = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
        auth_data = json.loads(auth_message)
        token = auth_data.get("token")
        
        if not token:
            await websocket.close(code=1008, reason="Missing authentication token")
            return
        
        user = await get_user_from_token(db, token)
        if not user or not user.is_active:
            await websocket.close(code=1008, reason="Invalid or expired token")
            return
    except Exception as e:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Continue with authenticated connection...
```

---

## ⚠️ ADDITIONAL CRITICAL FIXES

### 11. Add Request Size Limits

**In main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.limit import LimitUploadSize

app = FastAPI()
app.add_middleware(LimitUploadSize, max_upload_size=10485760)  # 10MB
```

### 12. Add Health Checks

**Create:** `backend/api/routers/health.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.core.redis_client import get_redis

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False
    
    # Check Redis
    try:
        redis = await get_redis()
        await redis._client.ping()
        redis_ready = True
    except Exception:
        redis_ready = False
    
    if db_ready and redis_ready:
        return {"status": "ready", "database": "ok", "redis": "ok"}
    else:
        return {
            "status": "not ready",
            "database": "ok" if db_ready else "error",
            "redis": "ok" if redis_ready else "error"
        }, 503
```

### 13. Fix N+1 Query in Summon Service

**File:** `backend/services/summon_service.py:105-131`

**Current:**
```python
squad_stmt = select(Squad).options(selectinload(Squad.members))...
# Then separately queries members
members_stmt = select(User).join(squad_membership_table)...
```

**Fix:**
```python
# Single query with proper join
members_stmt = (
    select(User)
    .join(squad_membership_table, User.id == squad_membership_table.c.user_id)
    .where(
        and_(
            squad_membership_table.c.squad_id == squad_id,
            squad_membership_table.c.is_active == True,
        )
    )
)
# Don't need to load squad.members if we're querying members separately anyway
```

---

## 📝 ENVIRONMENT VARIABLES REQUIRED

Create `.env.example`:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/squadsync

# JWT
JWT_SECRET_KEY=your-very-long-random-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
API_VERSION=v1

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## 🎯 PRIORITY ORDER

1. **Day 1:** Fix authentication dependencies (all endpoints broken without this)
2. **Day 1:** Fix JWT secret key (security risk)
3. **Day 2:** Add password hashing (if user registration exists)
4. **Day 2:** Add rate limiting (prevent abuse)
5. **Day 3:** Add input sanitization (prevent XSS)
6. **Day 3:** Add database indexes (performance)
7. **Week 1:** Optimize permission queries
8. **Week 1:** Fix transaction management
9. **Week 1:** Remove duplicate files
10. **Week 1:** Fix WebSocket token security

---

**These fixes address the most critical security and functionality issues. Implement in order of priority.**
