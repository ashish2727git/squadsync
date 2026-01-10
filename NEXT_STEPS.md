# SquadSync - Next Steps Action Plan

## 🎯 Current Status: ~75% Complete

**Backend:** 85% complete - Functional but needs security fixes  
**Frontend:** 30% complete - Components exist, no main app  
**Production Ready:** No - Critical security issues

---

## 🔴 CRITICAL: Do These First (This Week)

### 1. Set Up Database Migrations ⏱️ 2-3 hours
**Why:** Cannot deploy schema changes safely without migrations

```bash
# Install Alembic (already in requirements.txt)
pip install alembic

# Initialize Alembic
alembic init alembic

# Configure alembic.ini and alembic/env.py
# Create initial migration
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Files to create:**
- `alembic.ini`
- `alembic/env.py` 
- `alembic/versions/001_initial_schema.py`

---

### 2. Create User Authentication ⏱️ 8-10 hours
**Why:** No way to register/login users currently

**Create:** `backend/core/security.py`
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

**Create:** `backend/api/routers/auth_router.py`
- POST `/api/v1/auth/register` - Create user account
- POST `/api/v1/auth/login` - Get JWT token
- POST `/api/v1/auth/refresh` - Refresh token
- POST `/api/v1/auth/logout` - Invalidate token

**Update:** `backend/main.py` - Add auth router

---

### 3. Remove Development Mode ⏱️ 1-2 hours
**Why:** Currently allows unauthenticated access (security risk)

**Modify:** `backend/core/dependencies.py`
- Remove mock user logic (lines 72-88)
- Require valid JWT token for all requests
- Return 401 if no token provided

---

### 4. Add Rate Limiting ⏱️ 4-6 hours
**Why:** Vulnerable to DDoS and brute force attacks

**Create:** `backend/core/rate_limit.py`
- Middleware using Redis
- Limit: 60 requests/minute per user
- Limit: 1000 requests/hour per user

**Update:** `backend/main.py` - Add rate limit middleware

---

### 5. Add Input Sanitization ⏱️ 3-4 hours
**Why:** Prevent XSS attacks

**Create:** `backend/core/sanitization.py`
- HTML entity escaping
- String length limits
- Remove null bytes

**Update:** All routers to sanitize user input

---

## 🟡 HIGH PRIORITY: Do Next (Week 2)

### 6. Create Frontend Application ⏱️ 8-10 hours
**Why:** No way to use the application without a frontend

**Create:** `frontend/package.json`
```json
{
  "name": "squadsync-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

**Create:**
- `frontend/src/App.tsx` - Main app component
- `frontend/src/main.tsx` - Entry point
- `frontend/src/router.tsx` - Routes
- `frontend/src/api/client.ts` - API client
- `frontend/src/contexts/AuthContext.tsx` - Auth state

---

### 7. Add Database Indexes ⏱️ 1-2 hours
**Why:** Slow queries without indexes

**Create migration:**
```python
# alembic/versions/002_add_indexes.py
def upgrade():
    op.create_index('idx_squad_membership', 'squad_membership', 
                    ['squad_id', 'user_id', 'is_active'])
    op.create_index('idx_summon_response', 'summon_response',
                    ['summon_id', 'user_id'])
    op.create_index('idx_squad_event_date', 'squad_event',
                    ['squad_id', 'start_time'])
```

---

### 8. Optimize Permission Queries ⏱️ 4-6 hours
**Why:** Currently makes 4 separate queries (slow)

**Modify:** `backend/core/permissions.py`
- Combine into single UNION query
- Add Redis caching (5 min TTL)

---

## 🟢 MEDIUM PRIORITY: Do Later (Week 3-4)

### 9. Create Core Frontend Pages ⏱️ 12-16 hours
- `/login` - Login page
- `/register` - Registration
- `/dashboard` - Main dashboard
- `/squads` - Squad list
- `/squads/:id` - Squad detail
- `/squads/:id/summons` - Summon management

### 10. Add Tests ⏱️ 12-16 hours
- Backend unit tests (pytest)
- Service tests
- Router tests
- Frontend component tests

### 11. Environment Configuration ⏱️ 1-2 hours
- Create `.env.example`
- Add startup validation
- Document all variables

---

## 📋 Quick Checklist

### This Week (Critical)
- [ ] Set up Alembic migrations
- [ ] Create initial migration
- [ ] Create `backend/core/security.py`
- [ ] Create `backend/api/routers/auth_router.py`
- [ ] Remove development mode
- [ ] Add rate limiting
- [ ] Add input sanitization

### Next Week (High Priority)
- [ ] Create frontend package.json
- [ ] Create React app structure
- [ ] Create API client
- [ ] Add database indexes
- [ ] Optimize permission queries

### Week 3-4 (Medium Priority)
- [ ] Create frontend pages
- [ ] Integrate existing components
- [ ] Add tests
- [ ] Create .env.example
- [ ] Add monitoring/logging

---

## 🚀 Getting Started Right Now

**Step 1:** Set up Alembic (30 minutes)
```bash
cd backend
alembic init alembic
# Edit alembic.ini and alembic/env.py
alembic revision --autogenerate -m "Initial schema"
```

**Step 2:** Create password hashing (15 minutes)
```bash
# Create backend/core/security.py
# Copy code from CRITICAL_FIXES.md section 3
```

**Step 3:** Create auth router (2-3 hours)
```bash
# Create backend/api/routers/auth_router.py
# Implement register/login endpoints
# Add to main.py
```

---

## 📊 Estimated Timeline

| Task | Hours | Priority |
|------|-------|----------|
| Database migrations | 2-3 | 🔴 Critical |
| User authentication | 8-10 | 🔴 Critical |
| Remove dev mode | 1-2 | 🔴 Critical |
| Rate limiting | 4-6 | 🔴 Critical |
| Input sanitization | 3-4 | 🔴 Critical |
| Frontend app structure | 8-10 | 🟡 High |
| Database indexes | 1-2 | 🟡 High |
| Frontend pages | 12-16 | 🟢 Medium |
| Tests | 12-16 | 🟢 Medium |

**Total Critical:** ~20-25 hours (1 week)  
**Total High Priority:** ~20-25 hours (1 week)  
**Total Medium:** ~25-35 hours (2 weeks)

---

## 💡 Pro Tips

1. **Start with Alembic** - Everything else depends on database
2. **Test authentication** - Use Postman/Swagger to test endpoints
3. **Build frontend incrementally** - Start with login, then dashboard
4. **Use existing components** - SummonModal and Whiteboard are ready to use
5. **Follow the audit reports** - They have detailed fix instructions

---

## 🆘 Need Help?

- See `PROJECT_ANALYSIS.md` for detailed analysis
- See `CRITICAL_FIXES.md` for code examples
- See `IMPLEMENTATION_PLAN.md` for full roadmap
- See `AUDIT_REPORT.md` for security details

---

**Focus on the Critical items first. Once security is fixed and authentication works, you can build the frontend and add features incrementally.**
