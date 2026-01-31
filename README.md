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

### For Users
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual
- **[FEATURES_COMPLETE.md](FEATURES_COMPLETE.md)** - Full feature list

### For Developers
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Configuration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture details
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-launch checklist
- **[COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)** - Final implementation summary

## ✨ Features

### Core Functionality
- **Authentication** - JWT-based auth with refresh tokens
- **Organization Management** - Create and manage gaming organizations
- **Team Management** - Game-specific teams with full CRUD
- **Squad Management** - Create, join, leave tactical squads
- **Summon System** - Real-time urgent notifications with urgency levels
- **Player Vault** - Private storage for loadouts, clips, achievements, notes
- **Scheduling** - Squad events and daily goals with full management
- **War Room** - Collaborative whiteboard + WebRTC voice chat
- **WebSocket** - Real-time updates via Redis Pub/Sub

### User Experience
- **Onboarding Flow** - 3-step wizard for new users
- **Dashboard** - Central hub with squad overview and active summons
- **Profile Management** - User settings and preferences
- **Responsive Design** - Mobile-friendly on all devices
- **Real-time Updates** - Instant notifications and WebSocket sync

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

**Status:** 100% Complete & Production-Ready ✅

### What's New
- ✅ Complete organization/team/squad hierarchy
- ✅ Full frontend with Dashboard, Vault, Profile, Onboarding
- ✅ Real-time WebSocket integration
- ✅ Mobile-responsive design
- ✅ Comprehensive user documentation
- ✅ Production-grade security and performance

### First-Time Setup
1. Register at http://localhost:3000/register
2. Complete 3-step onboarding wizard:
   - Create Organization (e.g., "Elite Gamers")
   - Create Team (e.g., "Valorant Pro Team")
   - Create Squad (e.g., "Alpha Squad")
3. Start using all features immediately!

For detailed information, see the documentation files listed above.
