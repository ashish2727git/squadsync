# SquadSync Implementation Plan
## Priority-based fixes for production readiness

---

## 🔴 PHASE 1: Critical Security Fixes (Week 1)

### 1.1 Authentication Implementation
**Files to create:**
- `backend/core/dependencies.py` - Centralized auth dependencies
- `backend/core/middleware.py` - Auth middleware

**Tasks:**
- [ ] Implement `get_current_user()` with JWT validation
- [ ] Implement `get_db()` with proper session management
- [ ] Add HTTP Bearer token authentication
- [ ] Remove placeholder dependencies from all routers

### 1.2 JWT Security Hardening
**Files to modify:**
- `backend/core/jwt_auth.py`

**Tasks:**
- [ ] Remove default JWT secret, require environment variable
- [ ] Add startup validation for JWT_SECRET_KEY
- [ ] Move WebSocket token from query string to subprotocol/handshake
- [ ] Add token refresh mechanism
- [ ] Implement token blacklisting for logout

### 1.3 Password Security
**Files to create:**
- `backend/core/security.py` - Password hashing utilities

**Tasks:**
- [ ] Implement bcrypt password hashing
- [ ] Add password strength validation
- [ ] Create password reset flow
- [ ] Add password change endpoint

### 1.4 Input Validation & Sanitization
**Files to create:**
- `backend/core/validation.py` - Input sanitization

**Tasks:**
- [ ] Add HTML/script tag sanitization
- [ ] Validate all user inputs
- [ ] Add request size limits
- [ ] Implement rate limiting middleware

---

## ⚠️ PHASE 2: High Priority Fixes (Week 2)

### 2.1 Database & Performance
**Files to create:**
- `backend/core/database.py` - Database configuration
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Migration environment

**Tasks:**
- [ ] Set up Alembic migrations
- [ ] Configure database connection pooling
- [ ] Add missing database indexes
- [ ] Fix N+1 query issues
- [ ] Optimize permission check queries

### 2.2 Application Setup
**Files to create:**
- `backend/main.py` - FastAPI application
- `backend/core/config.py` - Configuration management
- `backend/core/logging_config.py` - Logging setup

**Tasks:**
- [ ] Create main FastAPI app with all routers
- [ ] Set up environment-based configuration
- [ ] Configure structured logging (JSON format)
- [ ] Add health check endpoints
- [ ] Configure CORS middleware

### 2.3 Error Handling & Observability
**Files to create:**
- `backend/core/exceptions.py` - Custom exception hierarchy
- `backend/core/error_handlers.py` - Global error handlers
- `backend/core/middleware.py` - Request/response logging

**Tasks:**
- [ ] Standardize error handling
- [ ] Add request ID tracking
- [ ] Integrate error tracking (Sentry)
- [ ] Add metrics collection (Prometheus)
- [ ] Sanitize error messages for production

### 2.4 Audit Logging
**Files to create:**
- `backend/core/audit.py` - Audit logging utilities
- `backend/models/audit_log.py` - Audit log model

**Tasks:**
- [ ] Create audit log model
- [ ] Implement audit logging for sensitive operations
- [ ] Log all permission changes
- [ ] Log vault access
- [ ] Log admin actions

---

## 🐌 PHASE 3: Performance Optimization (Week 3)

### 3.1 Query Optimization
**Files to modify:**
- `backend/core/permissions.py`
- `backend/services/*.py`

**Tasks:**
- [ ] Combine permission check queries (use UNION/CTEs)
- [ ] Add Redis caching for permission checks
- [ ] Optimize dashboard queries
- [ ] Add query result caching

### 3.2 Connection Management
**Files to modify:**
- `backend/core/redis_client.py`
- `backend/core/websocket_manager.py`

**Tasks:**
- [ ] Implement Redis connection pooling
- [ ] Optimize WebSocket Redis connections
- [ ] Add connection pool monitoring
- [ ] Implement connection retry logic

### 3.3 Caching Strategy
**Files to create:**
- `backend/core/cache.py` - Caching utilities

**Tasks:**
- [ ] Cache user permissions
- [ ] Cache squad memberships
- [ ] Cache frequently accessed data
- [ ] Implement cache invalidation

---

## 🔄 PHASE 4: Code Quality & Refactoring (Week 4)

### 4.1 Remove Duplication
**Tasks:**
- [ ] Create shared dependencies module
- [ ] Create shared error handlers
- [ ] Create shared model converters
- [ ] Create notification service

### 4.2 Hierarchy Enforcement
**Tasks:**
- [ ] Add database constraints for hierarchy
- [ ] Verify all endpoints check permissions
- [ ] Add hierarchy validation to updates
- [ ] Add atomic permission checks

### 4.3 Code Cleanup
**Tasks:**
- [ ] Remove duplicate `models.py` file
- [ ] Standardize exception handling
- [ ] Add type hints where missing
- [ ] Improve documentation

---

## 🚀 PHASE 5: Production Features (Week 5)

### 5.1 Background Tasks
**Files to create:**
- `backend/core/tasks.py` - Background task definitions
- `backend/core/celery_app.py` - Celery configuration

**Tasks:**
- [ ] Set up Celery for background tasks
- [ ] Move notification sending to background
- [ ] Add task retry logic
- [ ] Monitor task queue

### 5.2 API Enhancements
**Tasks:**
- [ ] Implement API versioning strategy
- [ ] Add request/response logging (with PII filtering)
- [ ] Add API documentation (OpenAPI)
- [ ] Add API rate limiting per user/endpoint

### 5.3 Monitoring & Alerting
**Tasks:**
- [ ] Set up Prometheus metrics
- [ ] Configure alerting rules
- [ ] Add performance monitoring
- [ ] Set up log aggregation

### 5.4 Deployment Readiness
**Tasks:**
- [ ] Add graceful shutdown handlers
- [ ] Add database migration automation
- [ ] Create Docker configuration
- [ ] Add environment validation on startup
- [ ] Create deployment documentation

---

## 📋 IMMEDIATE QUICK FIXES (Do First)

### Quick Fix 1: Remove Duplicate Models
```bash
# Delete root models.py - it's a duplicate
rm models.py
```

### Quick Fix 2: Create Dependencies Module
Create `backend/core/dependencies.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.jwt_auth import get_user_from_token, InvalidToken, ExpiredToken
from backend.models.models import User

security = HTTPBearer()

async def get_db() -> AsyncSession:
    # Implement with your database session factory
    pass

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    user = await get_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user
```

### Quick Fix 3: Add Missing Indexes
Create Alembic migration for indexes:
```python
# Add to migration
op.create_index('idx_squad_membership_lookup', 'squad_membership', 
                ['squad_id', 'user_id', 'is_active'])
op.create_index('idx_summon_response_lookup', 'summon_response',
                ['summon_id', 'user_id'])
op.create_index('idx_squad_event_date', 'squad_event',
                ['squad_id', 'start_time'])
```

### Quick Fix 4: Fix JWT Secret
```python
# backend/core/jwt_auth.py
import os
import sys

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    sys.exit("ERROR: JWT_SECRET_KEY environment variable is required")
if len(JWT_SECRET_KEY) < 32:
    sys.exit("ERROR: JWT_SECRET_KEY must be at least 32 characters")
```

---

## 📊 ESTIMATED EFFORT

- **Phase 1 (Critical Security):** 40 hours
- **Phase 2 (High Priority):** 60 hours
- **Phase 3 (Performance):** 40 hours
- **Phase 4 (Refactoring):** 30 hours
- **Phase 5 (Production Features):** 50 hours

**Total Estimated Effort:** ~220 hours (5-6 weeks for 1 developer)

---

## 🎯 SUCCESS CRITERIA

- [ ] All P0 security issues resolved
- [ ] Authentication fully implemented
- [ ] No duplicate code
- [ ] All endpoints have permission checks
- [ ] Database queries optimized
- [ ] Monitoring and logging in place
- [ ] Health checks working
- [ ] Error tracking integrated
- [ ] Rate limiting active
- [ ] Audit logging operational

---

## ⚠️ RISKS IF NOT ADDRESSED

1. **Security Breach:** Weak authentication = unauthorized access
2. **Data Leakage:** Missing permission checks = data exposure
3. **Performance Degradation:** N+1 queries = slow responses under load
4. **Service Outage:** No health checks = undetected failures
5. **Compliance Issues:** No audit logs = regulatory violations
6. **Scalability Problems:** Connection issues = cannot scale

---

**Next Steps:** Start with Phase 1, complete quick fixes immediately, then proceed systematically through phases.
