# SquadSync Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Git
- Domain name (for production)
- SSL certificate (for production HTTPS)

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd squadsync
```

### 2. Configure Environment Variables

Create/update `.env` file in the root directory:

```bash
# Required: Generate strong secrets (32+ characters)
JWT_SECRET_KEY=<generate-strong-secret>
JWT_REFRESH_SECRET_KEY=<generate-different-strong-secret>

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/squadsync

# Redis
REDIS_URL=redis://redis:6379/0

# Environment
ENVIRONMENT=production

# Optional: JWT token expiration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Optional: Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_REQUESTS_PER_DAY=10000

# Optional: Logging
LOG_LEVEL=INFO

# Optional: CORS (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 3. Generate Secrets

Generate strong JWT secrets:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run this command twice to generate both `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`.

## Development Deployment

### Using Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### Access Points

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

### Stop Services

```bash
docker-compose down

# Stop and remove volumes (database data)
docker-compose down -v
```

## Production Deployment

### 1. Production Environment Variables

Update `.env` with production values:

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:password@production-db:5432/squadsync
REDIS_URL=redis://production-redis:6379/0
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. SSL/TLS Setup

Update `frontend/nginx.conf` for HTTPS:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of configuration
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Update Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: squadsync
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    command: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    environment:
      VITE_API_URL: https://yourdomain.com
    restart: always

volumes:
  postgres_data:
```

### 4. Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Verify deployment
curl https://yourdomain.com/health
curl https://yourdomain.com/ready
```

## Database Migrations

### Create New Migration

```bash
# Access backend container
docker-compose exec backend bash

# Generate migration
alembic revision --autogenerate -m "Description of changes"

# Review migration file in alembic/versions/
# Edit if needed

# Apply migration
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# View migration history
alembic history
```

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres squadsync > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres squadsync < backup.sql
```

### Redis Monitoring

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check memory usage
INFO memory

# Monitor commands
MONITOR
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Readiness check (DB + Redis)
curl http://localhost:8000/ready

# Check all containers
docker-compose ps
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Behind a load balancer
# Update nginx configuration for load balancing
```

### Resource Limits

Update `docker-compose.yml` with resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Troubleshooting

### Backend Won't Start

1. Check logs: `docker-compose logs backend`
2. Verify environment variables: `docker-compose exec backend env`
3. Check database connection: `docker-compose exec backend python -c "from backend.core.dependencies import AsyncSessionLocal; print('DB OK')"`

### Database Connection Issues

1. Check postgres health: `docker-compose ps postgres`
2. Verify credentials in `.env`
3. Check network: `docker-compose exec backend ping postgres`

### Redis Connection Issues

1. Check redis health: `docker-compose ps redis`
2. Test connection: `docker-compose exec redis redis-cli ping`
3. Verify REDIS_URL in `.env`

### WebSocket Connection Fails

1. Check CORS settings in backend config
2. Verify JWT token is valid
3. Check nginx WebSocket proxy configuration
4. Review backend logs for WebSocket errors

## Security Checklist

- [ ] Strong JWT secrets (32+ characters)
- [ ] HTTPS enabled with valid SSL certificate
- [ ] CORS configured for production domains only
- [ ] Database credentials secured
- [ ] Redis secured (password, firewall)
- [ ] Rate limiting enabled
- [ ] Security headers configured in nginx
- [ ] Regular security updates applied

## Backup Strategy

1. **Database:** Daily automated backups using `pg_dump`
2. **Configuration:** Version controlled `.env` template
3. **Logs:** Retained for 30 days minimum
4. **Recovery:** Test restore procedure monthly

## Monitoring Recommendations

- **Uptime Monitoring:** Pingdom, UptimeRobot
- **Error Tracking:** Sentry
- **Performance Monitoring:** New Relic, DataDog
- **Log Aggregation:** ELK Stack, Splunk
- **Infrastructure Monitoring:** Prometheus + Grafana

## Update Procedure

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Stop services
docker-compose down

# Start services with new images
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify
curl http://localhost:8000/health
```

## Rollback Procedure

```bash
# Checkout previous version
git checkout <previous-commit>

# Rebuild and restart
docker-compose build
docker-compose up -d

# Rollback migrations if needed
docker-compose exec backend alembic downgrade -1
```
