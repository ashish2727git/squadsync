# SquadSync Architecture Documentation

## System Overview

SquadSync is a production-grade gaming platform built with modern web technologies, designed for high performance, security, and scalability. The system enables real-time squad coordination, voice communication, collaborative whiteboarding, and team management.

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL 15 with AsyncPG driver
- **Cache/Real-time:** Redis 7
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Authentication:** JWT (access + refresh tokens)
- **WebSocket:** FastAPI native WebSocket support
- **Security:** Bcrypt password hashing, rate limiting, input sanitization

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **State Management:** Zustand
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Real-time:** Native WebSocket API
- **WebRTC:** Native WebRTC API for voice/video

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Web Server:** Nginx (reverse proxy, static files)
- **Process Management:** Uvicorn (ASGI server)

## Architecture Patterns

### Clean Architecture
```
┌─────────────────────────────────────────┐
│           API Layer (Routers)           │
│  - auth_router.py                       │
│  - summon_router.py                     │
│  - vault_router.py                      │
│  - squad_schedule_router.py             │
│  - websocket_gateway.py                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       Business Logic (Services)         │
│  - summon_service.py                    │
│  - vault_service.py                     │
│  - squad_schedule_service.py            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Data Layer (Models/DB)           │
│  - models.py (SQLAlchemy)               │
│  - AsyncSession (database)              │
│  - Redis (cache/real-time)              │
└─────────────────────────────────────────┘
```

### Core Components

#### 1. Authentication & Authorization
- **JWT-based authentication** with separate access and refresh tokens
- **Access tokens:** Short-lived (15 minutes), contain user identity and role
- **Refresh tokens:** Long-lived (30 days), used to obtain new access tokens
- **Password security:** Bcrypt with 12 rounds
- **Role-based access control (RBAC):** ORG_ADMIN > TEAM_MANAGER > SQUAD_LEADER > PLAYER

#### 2. Rate Limiting
- **Redis-based distributed rate limiting**
- **Multi-tier limits:** per-minute, per-hour, per-day
- **IP-based tracking**
- **Exempt paths:** health checks, documentation
- **Headers:** X-RateLimit-Remaining-* returned in responses

#### 3. Real-time Communication
- **WebSocket Gateway:** Single WebSocket connection per user
- **Message Types:**
  - Summon notifications (create, respond, update)
  - Whiteboard sync (drawing events)
  - WebRTC signaling (offer, answer, ICE candidates)
  - Squad chat (future)
- **Authentication:** JWT token in query parameters
- **Connection Management:** Automatic reconnection, heartbeat

#### 4. Database Design
- **Async I/O:** All database operations are non-blocking
- **Connection pooling:** SQLAlchemy async engine
- **Indexes:** On foreign keys and frequently queried fields
- **Migrations:** Alembic for version-controlled schema changes

## Data Model

### Entity Hierarchy
```
Organization (top level)
    ├── Teams (multiple per org)
    │   └── Squads (multiple per team)
    │       └── Players (multiple per squad)
    └── Users (members at various levels)
```

### Core Entities

#### User (`app_user`)
- **Fields:** id, username, email, hashed_password, role, is_active, is_verified, last_login
- **Relationships:** squads (many-to-many), vault_items, summons, summon_responses

#### Organization
- **Fields:** id, name, description, is_active, created_at
- **Relationships:** teams, admins

#### Team
- **Fields:** id, organization_id, name, game_title, is_active, created_at
- **Relationships:** organization (parent), squads, managers

#### Squad
- **Fields:** id, team_id, name, description, max_members, is_active, created_at
- **Relationships:** team (parent), members (many-to-many), summons, events, daily_goals

#### Summon
- **Fields:** id, squad_id, summoner_id, message, urgency, status, created_at, expires_at
- **Relationships:** squad, summoner (user), responses
- **Purpose:** Real-time squad assembly notifications

#### VaultItem
- **Fields:** id, user_id, name, description, item_type, is_private, data (JSONB), created_at
- **Purpose:** Private player storage (loadouts, clips, notes)
- **Sharing:** Can be shared with squads

#### ScheduleEvent
- **Fields:** id, squad_id, title, description, event_type, scheduled_at, duration_minutes
- **Purpose:** Squad calendar and event planning

#### DailyGoal
- **Fields:** id, squad_id, description, target_date, is_completed, assigned_to
- **Purpose:** Daily objectives and task tracking

## Request Flow

### HTTP Request (Example: Create Summon)
```
1. Client → Nginx → FastAPI
   POST /api/v1/summons
   Headers: Authorization: Bearer <token>
   Body: { squad_id, message, urgency }

2. Rate Limiting Middleware
   - Check Redis for request count
   - Increment counter
   - Return 429 if limit exceeded

3. CORS Middleware
   - Verify origin
   - Set CORS headers

4. Router (summon_router.py)
   - Route to create_summon endpoint
   - Validate request schema

5. Authentication (get_current_user dependency)
   - Decode JWT token
   - Fetch user from database
   - Verify user is active

6. Authorization (permission check)
   - Verify user is squad member
   - Check role permissions

7. Service Layer (summon_service.py)
   - Business logic validation
   - Create summon in database
   - Publish to Redis for real-time

8. Response
   - Return created summon
   - Status code 201
```

### WebSocket Message Flow
```
1. Client establishes WebSocket connection
   ws://server/ws?token=<jwt_token>

2. Authentication
   - Extract token from query params
   - Verify JWT token
   - Register connection in manager

3. Client sends message
   { type: "summon_create", data: {...} }

4. WebSocket Gateway
   - Parse message
   - Validate schema
   - Route to appropriate handler

5. Business Logic
   - Process message
   - Update database
   - Broadcast to relevant users

6. Broadcast
   - Query squad members from Redis
   - Send notification to all online members
   - Store for offline delivery
```

## Security Architecture

### Defense in Depth

#### 1. Network Layer
- **CORS:** Strict origin validation
- **Rate Limiting:** DDoS protection
- **HTTPS:** TLS 1.2+ encryption (production)

#### 2. Application Layer
- **Input Validation:** Pydantic schemas for all inputs
- **Sanitization:** XSS prevention, HTML escaping
- **SQL Injection:** ORM prevents direct SQL
- **Authentication:** JWT tokens, no sessions
- **Authorization:** Role-based access control

#### 3. Data Layer
- **Password Hashing:** Bcrypt with salt
- **Database Credentials:** Environment variables only
- **Redis:** No sensitive data stored
- **Secrets Management:** Environment-based configuration

### Security Features

#### Request Size Limits
- **Body size:** 1MB maximum
- **Headers:** Standard limits
- **WebSocket messages:** Rate limited

#### Token Security
- **Access tokens:** Short-lived (15 min)
- **Refresh tokens:** Long-lived (30 days)
- **Separate secrets:** Different signing keys
- **Type verification:** Token type validated
- **Expiration:** Enforced on all tokens

#### Error Handling
- **Production:** Generic error messages
- **Development:** Detailed error traces
- **Logging:** All errors logged with context
- **No information leakage:** User enumeration prevented

## Performance Optimization

### Database
- **Async operations:** Non-blocking I/O
- **Connection pooling:** Reuse connections
- **Eager loading:** selectin strategy for relationships
- **Indexes:** On foreign keys and query fields
- **Query optimization:** N+1 query prevention

### Caching Strategy
- **Redis use cases:**
  - Rate limiting counters
  - WebSocket user routing
  - Real-time message queues
- **No database caching:** Direct DB queries (small dataset)
- **Future:** Redis cache for frequently accessed data

### Real-time Performance
- **Single WebSocket per user:** Reduces connections
- **Redis pub/sub:** Fast message routing
- **Message batching:** Group notifications
- **Heartbeat:** Keep connections alive

### Scalability Considerations
- **Stateless backend:** Horizontal scaling ready
- **Shared Redis:** Cross-instance communication
- **Database read replicas:** (future) Separate read/write
- **Load balancing:** Nginx upstream configuration
- **CDN:** (future) Static asset delivery

## Monitoring & Observability

### Health Checks
- **GET /health:** Basic liveness check
- **GET /ready:** Database + Redis connectivity
- **Docker healthchecks:** Container-level monitoring

### Logging
- **Structured logging:** JSON format
- **Log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context:** Request ID, user ID, timestamps
- **Rotation:** Daily log files (production)

### Metrics to Track
- **API Performance:**
  - Response times (p50, p95, p99)
  - Request rate
  - Error rate (by endpoint)

- **WebSocket:**
  - Active connections
  - Message throughput
  - Connection duration

- **Database:**
  - Query performance
  - Connection pool utilization
  - Slow queries

- **Redis:**
  - Memory usage
  - Hit/miss ratio
  - Key count

- **Authentication:**
  - Failed login attempts
  - Token refresh rate
  - Active sessions

## Deployment Architecture

### Docker Compose Stack
```
┌─────────────────────────────────────────┐
│           Nginx (Port 80/443)           │
│  - Reverse proxy                        │
│  - Static file serving                  │
│  - SSL termination                      │
│  - WebSocket proxy                      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Frontend Container               │
│  - React app (production build)         │
│  - Served by Nginx                      │
└─────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Backend Container (Port 8000)    │
│  - FastAPI app                          │
│  - Uvicorn ASGI server                  │
│  - 4 workers (production)               │
└────────┬────────────────┬───────────────┘
         │                │
         ▼                ▼
┌──────────────┐  ┌─────────────────┐
│  PostgreSQL  │  │     Redis       │
│ (Port 5432)  │  │  (Port 6379)    │
│              │  │                 │
│ - Persistent │  │ - Ephemeral     │
│ - Volume     │  │ - No volume     │
└──────────────┘  └─────────────────┘
```

### Environment Separation
- **Development:** Local Docker Compose, hot reload
- **Staging:** Cloud deployment, production-like config
- **Production:** Cloud deployment, scaled resources

## API Design Principles

### RESTful Conventions
- **Resources:** Nouns (e.g., `/summons`, `/squads`)
- **Methods:** GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- **Status Codes:**
  - 200 OK (success)
  - 201 Created (resource created)
  - 400 Bad Request (validation error)
  - 401 Unauthorized (auth required)
  - 403 Forbidden (insufficient permissions)
  - 404 Not Found (resource not found)
  - 429 Too Many Requests (rate limit)
  - 500 Internal Server Error (server error)

### Response Format
- **Success:** JSON object/array with data
- **Error:** `{ "detail": "error message" }`
- **Pagination:** (future) `{ "items": [], "total": 100, "page": 1 }`

### WebSocket Protocol
- **Message format:** `{ "type": "action_name", "data": {...} }`
- **Error format:** `{ "type": "error", "message": "..." }`
- **Broadcast format:** `{ "type": "event_name", "data": {...} }`

## Future Enhancements

### Short-term
- [ ] Database read replicas for scaling
- [ ] Redis persistence for critical data
- [ ] Prometheus metrics export
- [ ] Sentry error tracking
- [ ] WebSocket message compression

### Medium-term
- [ ] GraphQL API for complex queries
- [ ] Server-sent events for notifications
- [ ] File upload support (S3/CDN)
- [ ] Email notifications
- [ ] Push notifications (mobile)

### Long-term
- [ ] Microservices architecture
- [ ] Event-driven architecture (Kafka/RabbitMQ)
- [ ] Machine learning integration
- [ ] Multi-region deployment
- [ ] Mobile app (React Native)

## Development Guidelines

### Code Organization
```
backend/
├── api/              # API layer
│   ├── routers/      # FastAPI routers
│   ├── schemas/      # Pydantic schemas
│   └── gateway/      # WebSocket gateway
├── core/             # Core functionality
│   ├── auth.py       # Authentication
│   ├── config.py     # Configuration
│   ├── security.py   # Security utilities
│   └── rate_limit.py # Rate limiting
├── services/         # Business logic
├── models/           # Database models
└── main.py           # Application entry

frontend/
├── src/
│   ├── api/          # API client
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── contexts/     # React contexts
│   ├── hooks/        # Custom hooks
│   └── stores/       # Zustand stores
└── public/           # Static assets
```

### Best Practices
- **Type hints:** All Python code uses type hints
- **Async/await:** All I/O operations are async
- **Error handling:** Try/except with specific exceptions
- **Testing:** Unit tests for business logic
- **Documentation:** Docstrings for all functions
- **Code review:** Required before merge
- **Linting:** Black, isort, flake8
- **Version control:** Git with feature branches

## Troubleshooting Guide

### Common Issues

#### Database Connection Fails
- Check `DATABASE_URL` in `.env`
- Verify PostgreSQL is running
- Check network connectivity
- Review database logs

#### Redis Connection Fails
- Check `REDIS_URL` in `.env`
- Verify Redis is running
- Check network connectivity
- Review Redis logs

#### WebSocket Connection Fails
- Verify JWT token is valid
- Check CORS configuration
- Review nginx WebSocket proxy config
- Check backend WebSocket logs

#### Rate Limit Hit Frequently
- Adjust rate limit settings
- Check for API abuse
- Review client-side request patterns
- Consider implementing client-side caching

## Conclusion

SquadSync is designed as a production-grade platform with security, performance, and scalability as core priorities. The architecture supports real-time features while maintaining clean separation of concerns and following industry best practices.
