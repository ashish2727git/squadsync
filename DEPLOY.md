# SquadSync Deployment Instructions

## 🚀 Quick Deployment Guide

### Prerequisites Check ✅
- [x] Docker installed (v29.1.3)
- [x] Docker Compose installed (v2.40.3)
- [x] Strong JWT secrets configured in .env
- [x] All code complete and ready

---

## Step 1: Start Docker Desktop

**IMPORTANT:** Docker Desktop must be running before deployment.

### Windows:
1. Open **Docker Desktop** from Start Menu
2. Wait for Docker to start (icon in system tray will turn green)
3. Verify it's running: You should see "Docker Desktop is running"

### Alternative - Check if Docker is running:
```bash
docker ps
```
If you see a table of containers (even if empty), Docker is ready!

---

## Step 2: Deploy the Application

### Option A: One-Command Deployment (Recommended)
```bash
# Navigate to project directory
cd C:\Users\19255\Desktop\squadsync

# Build and start all services
docker-compose up -d --build

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Option B: Step-by-Step Deployment
```bash
# 1. Navigate to project
cd C:\Users\19255\Desktop\squadsync

# 2. Build images (takes 2-5 minutes first time)
docker-compose build

# 3. Start all services
docker-compose up -d

# 4. Check if services are running
docker-compose ps

# 5. Run database migrations
docker-compose exec backend alembic upgrade head
```

---

## Step 3: Verify Deployment

### Check Service Status
```bash
docker-compose ps
```
**Expected output:** All services should show "Up" status

### Check Backend Health
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","environment":"production"}`

### Check Backend Readiness
```bash
curl http://localhost:8000/ready
```
**Expected:** `{"status":"ready","database":true,"redis":true}`

### Access Application
Open your browser and go to:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Backend API:** http://localhost:8000

---

## Step 4: Create Your First User

1. Go to http://localhost:3000
2. Click **Register**
3. Fill in the form:
   - Username: `admin` (or your choice)
   - Email: `admin@example.com`
   - Password: `Admin123!@#` (must meet requirements)
4. Click **Register**
5. **Login** with your credentials
6. Complete the **3-step onboarding**:
   - Create Organization (e.g., "Elite Gamers")
   - Create Team (e.g., "Valorant Pro Team")
   - Create Squad (e.g., "Alpha Squad")
7. **Start using SquadSync!** 🎉

---

## 📊 What's Running?

After successful deployment, you'll have:

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **Frontend** | 3000 | http://localhost:3000 | React UI served by Nginx |
| **Backend** | 8000 | http://localhost:8000 | FastAPI REST API |
| **PostgreSQL** | 5432 | localhost:5432 | Database |
| **Redis** | 6379 | localhost:6379 | Cache & Real-time |

---

## 🛠️ Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v  # WARNING: Deletes database data!
```

### Rebuild After Code Changes
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Issue: Docker Desktop not running
**Error:** `error during connect: ... dockerDesktopLinuxEngine`

**Solution:**
1. Open Docker Desktop
2. Wait for it to start (green icon)
3. Try again

### Issue: Port already in use
**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Check what's using the port
netstat -ano | findstr :8000

# Stop the process or change port in docker-compose.yml
```

### Issue: Backend won't start
**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
- Database not ready (wait 10-20 seconds)
- Missing environment variables (check .env)
- Port conflicts

### Issue: Database migration fails
**Solution:**
```bash
# Check backend logs
docker-compose logs backend

# Try running migration again
docker-compose exec backend alembic upgrade head

# If still fails, check database connection
docker-compose exec backend python -c "from backend.core.dependencies import AsyncSessionLocal; print('DB OK')"
```

### Issue: Frontend shows "Can't connect to API"
**Check:**
1. Backend is running: `docker-compose ps backend`
2. Backend health: `curl http://localhost:8000/health`
3. CORS configuration in backend/core/config.py

### Issue: WebSocket connection fails
**Check:**
1. JWT token is valid
2. Backend logs: `docker-compose logs -f backend`
3. Browser console for errors

---

## 🎯 Post-Deployment Checklist

After successful deployment, verify:

- [ ] Frontend loads at http://localhost:3000
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Onboarding wizard works
- [ ] Dashboard shows squads
- [ ] Can create vault items
- [ ] Profile page loads
- [ ] API docs accessible at http://localhost:8000/docs

---

## 🔒 Security Notes

### Production Deployment Additions
When deploying to production (not localhost):

1. **Enable HTTPS**
   - Get SSL certificate (Let's Encrypt)
   - Configure nginx for SSL
   - Update ALLOWED_ORIGINS in .env

2. **Update Environment Variables**
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com
   DATABASE_URL=<production-database-url>
   REDIS_URL=<production-redis-url>
   ```

3. **Database Security**
   - Change default postgres password
   - Use managed database service
   - Enable SSL connections

4. **Monitoring**
   - Set up error tracking (Sentry)
   - Configure log aggregation
   - Set up uptime monitoring

---

## 📱 Access Points Summary

### Local Development
- **Main App:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### What You Can Do Now
✅ Register and create account
✅ Complete onboarding wizard
✅ Create and join squads
✅ Send/receive summons
✅ Use vault for items
✅ Schedule events
✅ Enter War Room
✅ Customize profile

---

## 🎉 Success!

Once deployed, SquadSync is ready for:
- Multiple concurrent users
- Real-time summons and notifications
- Voice chat and whiteboard collaboration
- Full squad management
- Secure authentication
- Production-grade performance

**Happy Gaming!** 🎮🚀

---

## 📞 Need Help?

Refer to these guides:
- **User Guide:** USER_GUIDE.md
- **API Documentation:** API_DOCUMENTATION.md
- **Architecture:** ARCHITECTURE.md
- **Features List:** FEATURES_COMPLETE.md

For deployment issues, check:
- Docker Desktop is running
- Ports 3000, 8000, 5432, 6379 are available
- .env file is correctly configured
- All services show "Up" in `docker-compose ps`
