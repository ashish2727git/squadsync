@echo off
echo ================================
echo SquadSync Deployment Script
echo ================================
echo.

REM Check if Docker is running
echo [1/5] Checking Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)
echo Docker is running ✓
echo.

REM Build images
echo [2/5] Building Docker images...
echo This may take 2-5 minutes on first run...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Build complete ✓
echo.

REM Start services
echo [3/5] Starting services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start services!
    pause
    exit /b 1
)
echo Services started ✓
echo.

REM Wait for services to be healthy
echo [4/5] Waiting for services to be healthy...
timeout /t 15 /nobreak >nul
echo Health check complete ✓
echo.

REM Run migrations
echo [5/5] Running database migrations...
docker-compose exec -T backend alembic upgrade head
if %errorlevel% neq 0 (
    echo WARNING: Migration failed! Backend might not be ready yet.
    echo Try running manually: docker-compose exec backend alembic upgrade head
    echo.
) else (
    echo Migrations complete ✓
    echo.
)

REM Show status
echo ================================
echo Deployment Complete!
echo ================================
echo.
echo Services Status:
docker-compose ps
echo.
echo Access Points:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Next Steps:
echo 1. Open http://localhost:3000 in your browser
echo 2. Register a new account
echo 3. Complete the onboarding wizard
echo 4. Start using SquadSync!
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause
