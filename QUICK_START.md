# SquadSync - Quick Start

## ✅ Critical Fixes Applied

I've implemented the following critical fixes to get the application running:

1. ✅ **Created `backend/main.py`** - FastAPI application entry point
2. ✅ **Created `backend/core/dependencies.py`** - Authentication and database dependencies
3. ✅ **Created `backend/core/config.py`** - Environment configuration
4. ✅ **Updated all routers** - Now use centralized dependencies
5. ✅ **Fixed JWT configuration** - Uses config module
6. ✅ **Created `requirements.txt`** - All dependencies listed
7. ✅ **Created startup scripts** - Easy server launch

## 🚀 How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Environment (Optional)
The app will work with defaults, but you can customize:
```powershell
# Windows PowerShell
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:ENVIRONMENT = "development"
```

### Step 3: Run the Server

**Windows:**
```powershell
# Set PYTHONPATH and run
$env:PYTHONPATH = $PWD
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# OR use the batch file
.\start_server.bat
```

**Linux/Mac:**
```bash
export PYTHONPATH=$(pwd)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# OR use the shell script
chmod +x start_server.sh
./start_server.sh
```

### Step 4: Access the Application

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root:** http://localhost:8000/

## ⚠️ Important Notes

1. **Database Required:** PostgreSQL must be running. The app will start but endpoints will fail without DB.
2. **Redis Optional:** Redis is optional - app works without it, but real-time features won't function.
3. **Development Mode:** Currently allows unauthenticated requests (mock user). **NOT FOR PRODUCTION!**
4. **Default JWT Secret:** Using default secret. **CHANGE IN PRODUCTION!**

## 🔍 Troubleshooting

### "ModuleNotFoundError: No module named 'backend'"
**Solution:** Make sure you're in the project root directory and PYTHONPATH is set:
```powershell
$env:PYTHONPATH = $PWD
```

### Database Connection Errors
- Verify PostgreSQL is running
- Check connection string matches your setup
- Database `squadsync` should exist (or create it)

### Port Already in Use
Change the port:
```bash
python -m uvicorn backend.main:app --port 8001
```

## 📋 What's Working

✅ FastAPI application structure
✅ All routers registered
✅ Authentication dependencies (dev mode)
✅ Database session management
✅ WebSocket gateway setup
✅ Health check endpoints
✅ CORS configured
✅ Error handling

## 📋 What Still Needs Work

⚠️ Database migrations (Alembic setup)
⚠️ User registration/login endpoints
⚠️ Production authentication (remove dev mode)
⚠️ Rate limiting
⚠️ Input sanitization
⚠️ Proper error tracking
⚠️ Monitoring/logging setup

See `AUDIT_REPORT.md` for complete list of issues and fixes.

## 🎯 Next Steps

1. Set up database and run migrations
2. Create user registration/login
3. Test API endpoints via Swagger UI
4. Implement production security fixes
5. Set up monitoring and logging

---

**The application should now start successfully!** Check http://localhost:8000/docs to see the API documentation.
