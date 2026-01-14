# SquadSync - Tactical Gaming Operations Platform

Production-grade platform for managing gaming squads, teams, and organizations with real-time collaboration features.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Set JWT secret
export JWT_SECRET_KEY="your-super-secret-key-minimum-32-characters-long"

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

## 📚 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Detailed setup instructions
- **[ALL_PHASES_COMPLETE.md](ALL_PHASES_COMPLETE.md)** - Complete implementation summary
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Production deployment checklist
- **[README_SETUP.md](README_SETUP.md)** - Setup and configuration guide

## ✨ Features

- **Authentication** - JWT-based auth with refresh tokens
- **Summon System** - Real-time urgent notifications
- **Squad Management** - Hierarchical organization structure
- **War Room** - Collaborative whiteboard + voice chat
- **Player Vault** - Private data storage
- **Scheduling** - Squad events and daily goals
- **WebSocket** - Real-time updates via Redis Pub/Sub

## 🏗️ Architecture

- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL, Redis
- **Frontend:** React, TypeScript, Vite
- **Real-time:** WebSocket, WebRTC
- **Deployment:** Docker, docker-compose

## 🔒 Security

- Production-grade JWT authentication
- Password hashing (bcrypt)
- Rate limiting (Redis-based)
- Input sanitization
- Permission enforcement
- No development bypasses

## 📋 Requirements

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis (optional, for real-time features)

## 🛠️ Development

```bash
# Backend
pip install -r requirements.txt
python run_server.py

# Frontend
cd frontend
npm install
npm run dev
```

## 📖 API Documentation

Interactive API documentation available at `/docs` when server is running.

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

---

**Status:** Production-ready ✅

For detailed information, see the documentation files listed above.
