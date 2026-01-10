# SquadSync - Quick Start Guide

## 🚀 How to Use the Application

### Prerequisites

Before starting, ensure you have:
- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **PostgreSQL** running (or use Docker)
- **Redis** running (or use Docker)

---

## Option 1: Quick Start with Docker (Recommended)

### Step 1: Set Environment Variables

Create a `.env` file in the project root:

```bash
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long-for-production
JWT_REFRESH_SECRET_KEY=another-super-secret-key-minimum-32-characters-long
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/squadsync
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=development
```

### Step 2: Start All Services

```bash
# Build and start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 3: Run Database Migrations

```bash
# Run migrations to create database schema
docker-compose exec backend alembic upgrade head
```

### Step 4: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## Option 2: Local Development Setup

### Backend Setup

#### Step 1: Install Python Dependencies

```bash
# Install all Python packages
pip install -r requirements.txt
```

#### Step 2: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:JWT_SECRET_KEY = "your-super-secret-key-minimum-32-characters-long"
$env:JWT_REFRESH_SECRET_KEY = "another-super-secret-key-minimum-32-characters"
$env:ENVIRONMENT = "development"
```

**Linux/Mac:**
```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your-super-secret-key-minimum-32-characters-long"
export JWT_REFRESH_SECRET_KEY="another-super-secret-key-minimum-32-characters"
export ENVIRONMENT="development"
```

#### Step 3: Set Up Database

```bash
# Create database (if not exists)
createdb squadsync

# Or using PostgreSQL client:
psql -U postgres -c "CREATE DATABASE squadsync;"
```

#### Step 4: Run Migrations

```bash
# Generate initial migration (if needed)
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head
```

#### Step 5: Start Backend Server

```bash
# Option 1: Using the run script
python run_server.py

# Option 2: Using uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: **http://localhost:8000**

---

### Frontend Setup

#### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

#### Step 2: Start Development Server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## 📱 Using the Application

### 1. Register a New Account

1. Open http://localhost:3000
2. Click "Register" or go to `/register`
3. Fill in:
   - Username (min 3 chars, alphanumeric + underscore/hyphen)
   - Email (valid email format)
   - Password (min 8 chars, uppercase, lowercase, digit, special char)
4. Click "Register"
5. You'll be automatically logged in

### 2. Login

1. Go to http://localhost:3000/login
2. Enter username/email and password
3. Click "Login"
4. You'll be redirected to the dashboard

### 3. Dashboard

- View your squads (when you're added to one)
- Navigate to squad details
- Access War Room

### 4. Squad Details

- View active summons
- See upcoming events
- Check daily goals
- Enter War Room

### 5. War Room

- **Whiteboard:** Draw on tactical maps
- **Voice Chat:** WebRTC-based voice communication
- Real-time collaboration with squad members

### 6. Summons

- **Receive:** Instant popup when summoned
- **Respond:** ACCEPT or DECLINE (required, cannot ignore)
- **View:** See all responses in real-time

---

## 🔧 API Usage

### Using Swagger UI (Interactive)

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter your JWT token (from login response)
4. Test endpoints interactively

### Using curl

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }'

# Response will include:
# {
#   "access_token": "...",
#   "refresh_token": "...",
#   "token_type": "bearer",
#   "expires_in": 900
# }

# 3. Access Protected Endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🧪 Testing the Application

### Test Authentication Flow

1. **Register** → Get tokens
2. **Login** → Get new tokens
3. **Access protected endpoint** → Should work with token
4. **Access without token** → Should get 401 error
5. **Refresh token** → Get new access token

### Test Summon System

1. Create a squad (via API or database)
2. Add users to squad
3. As Squad Leader, create a summon
4. Members receive real-time notification
5. Members respond (ACCEPT/DECLINE)
6. Leader sees responses in real-time

### Test WebSocket

1. Open browser console
2. Connect to WebSocket:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_TOKEN');
   ws.onmessage = (e) => console.log(JSON.parse(e.data));
   ```
3. Subscribe to squad:
   ```javascript
   ws.send(JSON.stringify({
     type: 'subscribe_squad',
     squad_id: 'YOUR_SQUAD_ID'
   }));
   ```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'backend'`
- **Solution:** Make sure you're in project root and PYTHONPATH is set:
  ```bash
  export PYTHONPATH=$(pwd)  # Linux/Mac
  $env:PYTHONPATH = $PWD     # Windows PowerShell
  ```

**Problem:** Database connection error
- **Solution:** 
  - Verify PostgreSQL is running: `pg_isready`
  - Check DATABASE_URL matches your setup
  - Ensure database `squadsync` exists

**Problem:** Redis connection error
- **Solution:**
  - Verify Redis is running: `redis-cli ping`
  - App will continue without Redis, but real-time features won't work

**Problem:** Port 8000 already in use
- **Solution:** Change port in `run_server.py` or use:
  ```bash
  uvicorn backend.main:app --port 8001
  ```

### Frontend Issues

**Problem:** `npm install` fails
- **Solution:** 
  - Use Node.js 18+
  - Clear cache: `npm cache clean --force`
  - Delete `node_modules` and `package-lock.json`, then reinstall

**Problem:** API calls return 401
- **Solution:**
  - Check if token is in localStorage
  - Verify token hasn't expired
  - Try logging in again

**Problem:** WebSocket connection fails
- **Solution:**
  - Verify backend is running
  - Check token is valid
  - Ensure Redis is running for WebSocket features

---

## 📋 Environment Variables Reference

### Required (Production)
- `JWT_SECRET_KEY` - Minimum 32 characters
- `JWT_REFRESH_SECRET_KEY` - Minimum 32 characters (optional, defaults to JWT_SECRET_KEY)

### Optional (with defaults)
- `DATABASE_URL` - Default: `postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync`
- `REDIS_URL` - Default: `redis://localhost:6379/0`
- `ENVIRONMENT` - Default: `development` (options: development, staging, production)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Default: `15`
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` - Default: `30`
- `RATE_LIMIT_REQUESTS_PER_MINUTE` - Default: `60`
- `RATE_LIMIT_REQUESTS_PER_HOUR` - Default: `1000`
- `RATE_LIMIT_REQUESTS_PER_DAY` - Default: `10000`
- `LOG_LEVEL` - Default: `INFO`

---

## 🎯 Quick Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can register a new user
- [ ] Can login with credentials
- [ ] Can access `/api/v1/auth/me` with token
- [ ] WebSocket connects successfully
- [ ] Can view API docs at `/docs`
- [ ] Health check returns 200: `/health`

---

## 📚 Next Steps

1. **Create Test Data:**
   - Create organizations, teams, squads via API
   - Add users to squads
   - Test summon system

2. **Explore Features:**
   - Create summons
   - Test whiteboard in War Room
   - Try WebRTC voice chat
   - Use Player Vault

3. **Production Deployment:**
   - Set strong JWT secrets
   - Configure production database
   - Set up monitoring
   - Enable HTTPS

---

## 🆘 Need Help?

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Health Check:** http://localhost:8000/health
- **Readiness Check:** http://localhost:8000/ready

For detailed information, see:
- `ALL_PHASES_COMPLETE.md` - Complete implementation summary
- `PRODUCTION_CHECKLIST.md` - Production readiness checklist
- `PHASE1_COMPLETE.md` - Security implementation details

---

**The application is ready to use!** 🚀

Start with Docker for the easiest setup, or follow the local development guide for more control.
