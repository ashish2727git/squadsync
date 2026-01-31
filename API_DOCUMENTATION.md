# SquadSync API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except `/health`, `/ready`, and auth endpoints) require JWT authentication.

### Authentication Header
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Health & Status

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "environment": "production"
}
```

#### GET /ready
Readiness check - verifies database and Redis connectivity.

**Response:**
```json
{
  "status": "ready",
  "database": true,
  "redis": true
}
```

### Authentication (`/api/v1/auth`)

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string (min 8 chars, 1 uppercase, 1 lowercase, 1 number)"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  "role": "PLAYER",
  "is_active": true,
  "is_verified": false
}
```

#### POST /api/v1/auth/login
Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "username": "string or email",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "jwt_token"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### GET /api/v1/auth/me
Get current authenticated user information.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  "role": "PLAYER",
  "is_active": true,
  "is_verified": false
}
```

### Summons (`/api/v1/summons`)

#### POST /api/v1/summons
Create a new summon request.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "squad_id": "uuid",
  "message": "string (optional)",
  "urgency": "low|medium|high|critical"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "squad_id": "uuid",
  "summoner_id": "uuid",
  "message": "string",
  "urgency": "high",
  "status": "pending",
  "created_at": "2026-01-30T12:00:00Z"
}
```

#### GET /api/v1/summons/active
Get all active summons for the current user's squads.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "squad_id": "uuid",
    "summoner_id": "uuid",
    "summoner_username": "string",
    "message": "string",
    "urgency": "high",
    "status": "pending",
    "created_at": "2026-01-30T12:00:00Z",
    "responses": []
  }
]
```

#### POST /api/v1/summons/{summon_id}/respond
Respond to a summon request.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "response_type": "accepted|declined|busy",
  "message": "string (optional)",
  "eta_minutes": 15
}
```

**Response:**
```json
{
  "id": "uuid",
  "summon_id": "uuid",
  "responder_id": "uuid",
  "response_type": "accepted",
  "message": "string",
  "eta_minutes": 15,
  "responded_at": "2026-01-30T12:00:00Z"
}
```

### Player Vault (`/api/v1/vault`)

#### GET /api/v1/vault/items
Get all vault items for the current user.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "item_type": "string",
    "is_private": true,
    "created_at": "2026-01-30T12:00:00Z"
  }
]
```

#### POST /api/v1/vault/items
Create a new vault item.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "name": "string",
  "description": "string (optional)",
  "item_type": "loadout|clip|achievement|note",
  "is_private": true,
  "data": {}
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "item_type": "loadout",
  "is_private": true,
  "created_at": "2026-01-30T12:00:00Z"
}
```

#### POST /api/v1/vault/items/{item_id}/share
Share a vault item with a squad.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "squad_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Item shared successfully"
}
```

### Squad Schedule (`/api/v1/squads/{squad_id}/schedule`)

#### GET /api/v1/squads/{squad_id}/schedule
Get schedule for a specific squad.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "events": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "event_type": "practice|tournament|casual",
      "scheduled_at": "2026-01-30T20:00:00Z",
      "duration_minutes": 120,
      "created_by": "uuid"
    }
  ],
  "daily_goals": [
    {
      "id": "uuid",
      "description": "string",
      "target_date": "2026-01-30",
      "is_completed": false,
      "assigned_to": "uuid"
    }
  ]
}
```

#### POST /api/v1/squads/{squad_id}/schedule/events
Create a new scheduled event.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "title": "string",
  "description": "string (optional)",
  "event_type": "practice|tournament|casual",
  "scheduled_at": "2026-01-30T20:00:00Z",
  "duration_minutes": 120
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "event_type": "practice",
  "scheduled_at": "2026-01-30T20:00:00Z",
  "duration_minutes": 120,
  "created_by": "uuid",
  "created_at": "2026-01-30T12:00:00Z"
}
```

#### POST /api/v1/squads/{squad_id}/schedule/daily-goals
Create a daily goal for the squad.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "description": "string",
  "target_date": "2026-01-30",
  "assigned_to": "uuid (optional)"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "description": "string",
  "target_date": "2026-01-30",
  "is_completed": false,
  "assigned_to": "uuid",
  "created_at": "2026-01-30T12:00:00Z"
}
```

### WebSocket Gateway (`/ws`)

#### WebSocket /ws
Real-time communication gateway for summons, chat, whiteboard, and WebRTC signaling.

**Connection URL:**
```
ws://localhost:8000/ws?token=<access_token>
```

**Message Types:**

##### Outgoing (Client → Server)
```json
{
  "type": "summon_create",
  "data": {
    "squad_id": "uuid",
    "message": "string",
    "urgency": "high"
  }
}
```

```json
{
  "type": "summon_respond",
  "data": {
    "summon_id": "uuid",
    "response_type": "accepted",
    "message": "string"
  }
}
```

```json
{
  "type": "whiteboard_draw",
  "data": {
    "squad_id": "uuid",
    "action": "start|draw|end",
    "x": 100,
    "y": 200,
    "color": "#000000"
  }
}
```

```json
{
  "type": "webrtc_signal",
  "data": {
    "target_user_id": "uuid",
    "signal_type": "offer|answer|ice_candidate",
    "signal_data": {}
  }
}
```

##### Incoming (Server → Client)
```json
{
  "type": "summon_created",
  "data": {
    "summon": {...}
  }
}
```

```json
{
  "type": "summon_response_received",
  "data": {
    "response": {...}
  }
}
```

```json
{
  "type": "whiteboard_update",
  "data": {
    "user_id": "uuid",
    "action": "draw",
    "x": 100,
    "y": 200
  }
}
```

```json
{
  "type": "webrtc_signal",
  "data": {
    "from_user_id": "uuid",
    "signal_type": "offer",
    "signal_data": {}
  }
}
```

## Rate Limiting

All endpoints (except health checks) are rate-limited:
- **Per minute:** 60 requests
- **Per hour:** 1000 requests
- **Per day:** 10000 requests

Rate limit headers are included in responses:
```
X-RateLimit-Remaining-Minute: 59
X-RateLimit-Remaining-Hour: 999
X-RateLimit-Remaining-Day: 9999
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message describing validation failure"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
