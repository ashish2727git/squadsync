# SquadSync Environment Variables Documentation

## Overview

SquadSync uses environment variables for configuration management. This document describes all available environment variables, their purpose, and valid values.

## Required Variables

### JWT_SECRET_KEY
**Type:** String  
**Required:** Yes (in production)  
**Default:** `dev-secret-key-change-in-production-minimum-32-chars` (development only)  
**Min Length:** 32 characters (production)

Secret key used to sign JWT access tokens. Must be unique and unpredictable.

**Generation:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Example:**
```bash
JWT_SECRET_KEY="jYAIgC6333qNmUQFDn6DsnmMBvVHN8oVehI6QV7ae7rmYax79VTuZ4fDasprU9Qj"
```

**Security:**
- Never commit to version control
- Use different secrets for each environment
- Rotate periodically (requires user re-authentication)

---

### JWT_REFRESH_SECRET_KEY
**Type:** String  
**Required:** Yes (in production)  
**Default:** Same as `JWT_SECRET_KEY` (development only)  
**Min Length:** 32 characters (production)

Secret key used to sign JWT refresh tokens. Must be different from `JWT_SECRET_KEY`.

**Generation:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Example:**
```bash
JWT_REFRESH_SECRET_KEY="Rn_273JzG3qPB-ssQerLyF2KDqc4dCfGfP8fRJWeVirlap65jNGMnAV6WlHlyOxs"
```

**Security:**
- Must be different from `JWT_SECRET_KEY`
- Longer lifetime than access tokens
- More critical to protect

---

### DATABASE_URL
**Type:** Connection String  
**Required:** Yes  
**Default:** `postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync`

PostgreSQL database connection URL with AsyncPG driver.

**Format:**
```
postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```

**Examples:**
```bash
# Local development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync

# Docker Compose
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/squadsync

# Production with authentication
DATABASE_URL=postgresql+asyncpg://dbuser:securepass@db.example.com:5432/squadsync

# Cloud provider (example)
DATABASE_URL=postgresql+asyncpg://user:pass@db-instance.us-east-1.rds.amazonaws.com:5432/squadsync
```

**Requirements:**
- PostgreSQL 12 or higher
- AsyncPG driver support
- Database must exist before first run

---

### REDIS_URL
**Type:** Connection String  
**Required:** Yes  
**Default:** None (must be set)

Redis connection URL for caching and real-time features.

**Format:**
```
redis://[host]:[port]/[database]
redis://:[password]@[host]:[port]/[database]
```

**Examples:**
```bash
# Local development
REDIS_URL=redis://localhost:6379/0

# Docker Compose
REDIS_URL=redis://redis:6379/0

# With password
REDIS_URL=redis://:mypassword@redis:6379/0

# Cloud provider (example)
REDIS_URL=redis://:password@redis-instance.cloud.com:6379/0
```

**Requirements:**
- Redis 6.0 or higher
- Persistent storage not required (used for ephemeral data)

---

### ENVIRONMENT
**Type:** String  
**Required:** Yes  
**Default:** `development`  
**Valid Values:** `development`, `staging`, `production`

Application environment mode. Affects security validation and error verbosity.

**Example:**
```bash
ENVIRONMENT=production
```

**Impact:**
- **development:**
  - Detailed error messages
  - Relaxed security validation
  - Development mode logging
  - Hot reload enabled

- **staging:**
  - Similar to production
  - May include additional logging
  - Used for pre-production testing

- **production:**
  - Minimal error details in responses
  - Strict security validation
  - Production logging
  - Hot reload disabled

---

## Optional Variables

### JWT_ALGORITHM
**Type:** String  
**Default:** `HS256`  
**Valid Values:** `HS256`, `HS384`, `HS512`

Algorithm used for JWT signing and verification.

**Example:**
```bash
JWT_ALGORITHM=HS256
```

**Note:** Changing this requires updating all tokens.

---

### JWT_ACCESS_TOKEN_EXPIRE_MINUTES
**Type:** Integer  
**Default:** `15`  
**Recommended:** 5-30 minutes

Access token lifetime in minutes. Shorter lifetime is more secure.

**Example:**
```bash
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
```

**Recommendations:**
- Development: 60-120 minutes
- Production: 5-15 minutes
- High security: 5 minutes

---

### JWT_REFRESH_TOKEN_EXPIRE_DAYS
**Type:** Integer  
**Default:** `30`  
**Recommended:** 7-90 days

Refresh token lifetime in days. Balance between convenience and security.

**Example:**
```bash
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
```

**Recommendations:**
- Mobile apps: 60-90 days
- Web apps: 7-30 days
- High security: 7 days

---

### ALLOWED_ORIGINS
**Type:** Comma-separated string  
**Default:** `http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000`

CORS allowed origins for frontend applications.

**Example:**
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Production
ALLOWED_ORIGINS=https://squadsync.com,https://www.squadsync.com

# Multiple environments
ALLOWED_ORIGINS=https://squadsync.com,https://staging.squadsync.com,https://app.squadsync.com
```

**Security:**
- Never use `*` in production
- Include only trusted domains
- Use HTTPS in production

---

### RATE_LIMIT_REQUESTS_PER_MINUTE
**Type:** Integer  
**Default:** `60`

Maximum requests per minute per IP address.

**Example:**
```bash
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

**Recommendations:**
- API-heavy apps: 120-200
- Standard web apps: 60-100
- High security: 30-60

---

### RATE_LIMIT_REQUESTS_PER_HOUR
**Type:** Integer  
**Default:** `1000`

Maximum requests per hour per IP address.

**Example:**
```bash
RATE_LIMIT_REQUESTS_PER_HOUR=1000
```

---

### RATE_LIMIT_REQUESTS_PER_DAY
**Type:** Integer  
**Default:** `10000`

Maximum requests per day per IP address.

**Example:**
```bash
RATE_LIMIT_REQUESTS_PER_DAY=10000
```

---

### LOG_LEVEL
**Type:** String  
**Default:** `INFO`  
**Valid Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

Application logging level.

**Example:**
```bash
LOG_LEVEL=INFO
```

**Recommendations:**
- Development: `DEBUG`
- Staging: `INFO`
- Production: `INFO` or `WARNING`

---

## Example .env Files

### Development
```bash
# .env.development
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/squadsync
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_REFRESH_SECRET_KEY=dev-refresh-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=90
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_REQUESTS_PER_MINUTE=120
LOG_LEVEL=DEBUG
```

### Production
```bash
# .env.production
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:secure_pass@prod-db:5432/squadsync
REDIS_URL=redis://:redis_pass@prod-redis:6379/0
JWT_SECRET_KEY=jYAIgC6333qNmUQFDn6DsnmMBvVHN8oVehI6QV7ae7rmYax79VTuZ4fDasprU9Qj
JWT_REFRESH_SECRET_KEY=Rn_273JzG3qPB-ssQerLyF2KDqc4dCfGfP8fRJWeVirlap65jNGMnAV6WlHlyOxs
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
ALLOWED_ORIGINS=https://squadsync.com,https://www.squadsync.com
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_REQUESTS_PER_DAY=10000
LOG_LEVEL=INFO
```

## Environment Variable Validation

The application validates environment variables on startup:

1. **Production Mode:**
   - `JWT_SECRET_KEY` must be set and ≥32 characters
   - `JWT_REFRESH_SECRET_KEY` must be set and ≥32 characters
   - `REDIS_URL` must be set
   - Application exits if validation fails

2. **Development Mode:**
   - Warnings for missing/weak secrets
   - Default values used
   - Application starts even with weak configuration

## Security Best Practices

1. **Never Commit Secrets**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for templates
   - Document required variables

2. **Generate Strong Secrets**
   - Use cryptographically secure generators
   - Minimum 32 characters for JWT secrets
   - Use different secrets per environment

3. **Rotate Secrets Regularly**
   - JWT secrets: Every 90 days
   - Database passwords: Every 180 days
   - Document rotation procedures

4. **Limit Access**
   - Use secret management services (AWS Secrets Manager, HashiCorp Vault)
   - Restrict who can view production secrets
   - Audit secret access

5. **Environment Separation**
   - Use different secrets for dev/staging/production
   - Never share production secrets
   - Test security in staging environment

## Troubleshooting

### "JWT_SECRET_KEY environment variable must be set in production"
- Set `JWT_SECRET_KEY` in `.env` file
- Ensure key is at least 32 characters
- Verify `.env` file is loaded by Docker/application

### "REDIS_URL environment variable is not set"
- Set `REDIS_URL` in `.env` file
- Verify Redis is running
- Check connection string format

### "Invalid ENVIRONMENT"
- Ensure `ENVIRONMENT` is one of: `development`, `staging`, `production`
- Check for typos or extra whitespace
- Verify quotes if using special characters

### Environment variables not loading
- Check `.env` file location (must be in project root)
- Verify Docker Compose `env_file` configuration
- Check file permissions
- Restart application after changes
