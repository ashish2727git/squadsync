# Getting Started with SquadSync

## 🎮 What is SquadSync?

SquadSync is a tactical gaming operations platform for managing:
- **Organizations** → **Teams** → **Squads** → **Players**
- Real-time summons (urgent notifications)
- Squad scheduling and daily goals
- War Room (whiteboard + voice chat)
- Private player vaults

---

## ⚡ Fastest Way to Start (5 Minutes)

### Using Docker (Easiest)

```bash
# 1. Set your JWT secret (required)
export JWT_SECRET_KEY="your-super-secret-key-minimum-32-characters-long"

# 2. Start everything
docker-compose up -d

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Open in browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

That's it! The application is running.

---

## 🖥️ Manual Setup (Step by Step)

### 1. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your-super-secret-key-minimum-32-characters-long"
export ENVIRONMENT="development"

# Create database
createdb squadsync

# Run migrations
alembic upgrade head

# Start server
python run_server.py
```

Backend runs on: **http://localhost:8000**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 👤 First Steps

### 1. Create Your Account

1. Go to http://localhost:3000
2. Click "Register"
3. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test123!@#` (meets requirements)
4. Click "Register"

You'll be automatically logged in!

### 2. Explore the Dashboard

- View your profile
- See your squads (when added)
- Navigate to different sections

### 3. Test the API

1. Go to http://localhost:8000/docs
2. Click "Authorize"
3. Enter your access token (from login)
4. Try endpoints:
   - `GET /api/v1/auth/me` - Get your user info
   - `GET /api/v1/summons/squad/{squad_id}` - Get squad summons

---

## 🎯 Common Tasks

### Create a Summon (via API)

```bash
# Get your access token from login
TOKEN="your-access-token-here"
SQUAD_ID="your-squad-id-here"

curl -X POST http://localhost:8000/api/v1/summons/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "squad_id": "'$SQUAD_ID'",
    "title": "Raid in 10 minutes!",
    "description": "Emergency raid, need everyone!"
  }'
```

### Connect to WebSocket

```javascript
// In browser console
const token = 'your-access-token';
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

ws.onopen = () => {
  console.log('Connected!');
  // Subscribe to squad
  ws.send(JSON.stringify({
    type: 'subscribe_squad',
    squad_id: 'your-squad-id'
  }));
};

ws.onmessage = (e) => {
  console.log('Message:', JSON.parse(e.data));
};
```

### Access Your Vault

```bash
curl -X GET http://localhost:8000/api/v1/vault/YOUR_USER_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Verify Everything Works

### Check Backend Health

```bash
# Health check
curl http://localhost:8000/health

# Readiness check (verifies DB + Redis)
curl http://localhost:8000/ready
```

### Check Frontend

1. Open http://localhost:3000
2. Should see login page
3. Register/Login should work
4. Dashboard should load

### Check WebSocket

1. Open browser console
2. Connect to WebSocket (see example above)
3. Should receive "connected" message

---

## 📖 Key Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get tokens
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Summons
- `POST /api/v1/summons/` - Create summon
- `GET /api/v1/summons/{id}` - Get summon
- `POST /api/v1/summons/{id}/respond` - Respond to summon
- `GET /api/v1/summons/squad/{squad_id}` - Get squad summons

### Vault
- `GET /api/v1/vault/{user_id}` - Get vault
- `PUT /api/v1/vault/{user_id}` - Update vault
- `PATCH /api/v1/vault/{user_id}` - Merge vault data
- `POST /api/v1/vault/{user_id}/share` - Share vault

### WebSocket
- `ws://localhost:8000/ws?token=TOKEN` - Connect
- Send messages: `subscribe_squad`, `subscribe_summon`, `draw_start`, etc.

---

## 🎨 Frontend Routes

- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main dashboard
- `/squads/:squadId` - Squad details
- `/squads/:squadId/war-room` - War Room (whiteboard + voice)

---

## 💡 Tips

1. **Use Swagger UI** (`/docs`) to explore and test the API
2. **Check browser console** for frontend errors
3. **Check backend logs** for API errors
4. **WebSocket messages** appear in browser console
5. **Tokens expire** in 15 minutes - use refresh token

---

## 🚨 Important Notes

- **JWT Secret:** Must be at least 32 characters in production
- **Password:** Must meet strength requirements (8+ chars, uppercase, lowercase, digit, special)
- **Database:** Must be running for API to work
- **Redis:** Optional, but needed for real-time features
- **Tokens:** Access tokens expire in 15 minutes, refresh tokens last 30 days

---

## 📞 Quick Reference

| Service | URL | Status Check |
|---------|-----|--------------|
| Frontend | http://localhost:3000 | Open in browser |
| Backend API | http://localhost:8000 | `/health` |
| API Docs | http://localhost:8000/docs | Swagger UI |
| WebSocket | ws://localhost:8000/ws | Connect with token |

---

**You're all set!** Start with registration, then explore the features. 🎉

For detailed information, see `QUICK_START_GUIDE.md` or `ALL_PHASES_COMPLETE.md`.
