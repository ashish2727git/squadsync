# SquadSync - Quick Start Guide

## 🚀 Running the Application

### Prerequisites

1. **Python 3.10+** installed
2. **PostgreSQL** running (default: `localhost:5432`)
3. **Redis** running (default: `localhost:6379`)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables** (optional, defaults provided):
```bash
# Windows PowerShell
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:ENVIRONMENT = "development"

# Linux/Mac
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
export REDIS_URL="redis://localhost:6379/0"
export ENVIRONMENT="development"
```

### Running the Server

**Option 1: Using the run script**
```bash
python run_server.py
```

**Option 2: Using uvicorn directly**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: From backend directory**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Application

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Readiness Check:** http://localhost:8000/ready
- **Root:** http://localhost:8000/

### API Endpoints

- **Summons:** `/api/v1/summons`
- **Squad Schedule:** `/api/v1/squads/{squad_id}/events`
- **WebSocket:** `/ws?token=<jwt_token>`

## ⚠️ Development Mode

The application runs in **development mode** by default, which:
- Allows unauthenticated requests (mock user)
- Uses default JWT secret (not secure!)
- Shows detailed error messages

**⚠️ DO NOT use in production without proper configuration!**

## 🔧 Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'backend'`:
- Make sure you're running from the project root directory
- Check that `backend/` folder exists
- Try: `python -m backend.main` or use the run script

### Database Connection Errors
- Verify PostgreSQL is running: `pg_isready` or check service status
- Check connection string matches your PostgreSQL setup
- Ensure database `squadsync` exists (or create it)

### Redis Connection Errors
- Verify Redis is running: `redis-cli ping` should return `PONG`
- Check Redis URL matches your setup
- Application will continue without Redis, but real-time features won't work

### Port Already in Use
- Change port: `uvicorn backend.main:app --port 8001`
- Or kill process using port 8000

## 📝 Next Steps

1. **Create database schema:**
   - Set up Alembic migrations
   - Run initial migration

2. **Set up authentication:**
   - Create user registration/login endpoints
   - Generate JWT tokens properly

3. **Configure for production:**
   - Set strong JWT_SECRET_KEY
   - Remove development mode
   - Set up proper logging
   - Configure CORS properly

## 🎯 Testing the API

Once running, you can test endpoints using:

1. **Swagger UI:** http://localhost:8000/docs (interactive)
2. **curl:**
```bash
# Health check
curl http://localhost:8000/health

# Get summons (requires auth in production)
curl http://localhost:8000/api/v1/summons
```

3. **Python requests:**
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())
```

## 📚 Documentation

- See `AUDIT_REPORT.md` for security and performance issues
- See `CRITICAL_FIXES.md` for immediate fixes needed
- See `IMPLEMENTATION_PLAN.md` for full implementation roadmap
