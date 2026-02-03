# SquadSync

Real-time gaming squad coordination platform with voice chat, whiteboard, and team management.

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis

### Development Setup

```bash
# Backend
pip install -r requirements.txt
python run_server.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### First Time Setup
1. Register at http://localhost:3000/register
2. Complete onboarding (create Organization → Team → Squad)
3. Start using features

## Features

- **Authentication** - JWT-based with refresh tokens
- **Squad Management** - Create, join, leave squads
- **Summon System** - Real-time urgent notifications
- **War Room** - Collaborative whiteboard + voice chat (WebRTC)
- **Player Vault** - Private storage for loadouts, clips, notes
- **Scheduling** - Squad events and daily goals
- **Real-time** - WebSocket updates via Redis

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy (async), PostgreSQL, Redis |
| Frontend | React, TypeScript, Vite, Zustand |
| Real-time | WebSocket, WebRTC |

## Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Architecture](ARCHITECTURE.md) - System design and patterns
- [Environment Variables](ENVIRONMENT_VARIABLES.md) - Configuration guide

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-minimum-32-characters
```

See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for all options.

## Project Structure

```
backend/
├── api/routers/     # API endpoints
├── api/gateway/     # WebSocket gateway
├── core/            # Auth, config, security
├── services/        # Business logic
├── models/          # Database models
└── main.py

frontend/
├── src/components/  # React components
├── src/pages/       # Page components
├── src/hooks/       # Custom hooks
└── src/stores/      # Zustand stores
```
