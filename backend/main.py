"""
SquadSync FastAPI Application
Main entry point for the SquadSync gaming platform.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import ALLOWED_ORIGINS, ENVIRONMENT, LOG_LEVEL
from backend.core.redis_client import get_redis
from backend.core.websocket_manager import WebSocketManager
from backend.api.routers import summon_router, squad_schedule_router
from backend.api.gateway import websocket_gateway

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global WebSocket manager instance
_websocket_manager: WebSocketManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown.
    """
    global _websocket_manager
    
    # Startup
    logger.info("🚀 Starting SquadSync application...")
    logger.info(f"Environment: {ENVIRONMENT}")
    
    # Initialize Redis connection
    try:
        redis = await get_redis()
        await redis.connect()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}")
        logger.warning("⚠️  Application will continue but real-time features may not work")
    
    # Initialize WebSocket manager
    try:
        redis_client = await get_redis()
        _websocket_manager = WebSocketManager(redis_client)
        # Store in app state for access in dependencies
        app.state.websocket_manager = _websocket_manager
        logger.info("✅ WebSocket manager initialized")
    except Exception as e:
        logger.warning(f"⚠️  WebSocket manager initialization failed: {e}")
    
    # Set WebSocket manager factory for gateway
    from backend.api.gateway.websocket_gateway import set_websocket_manager_factory
    set_websocket_manager_factory(lambda: _websocket_manager)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down SquadSync application...")
    
    # Cleanup WebSocket connections
    if _websocket_manager:
        try:
            # Disconnect all connections
            for user_id in list(_websocket_manager._connections.keys()):
                await _websocket_manager.disconnect(user_id)
            logger.info("✅ WebSocket connections closed")
        except Exception as e:
            logger.error(f"Error closing WebSocket connections: {e}")
    
    # Close Redis connection
    try:
        redis = await get_redis()
        await redis.disconnect()
        logger.info("✅ Redis disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Redis: {e}")


# Create FastAPI app
app = FastAPI(
    title="SquadSync API",
    description="Production-grade gaming platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if ENVIRONMENT == "production" else str(exc)
        }
    )

# Include routers
app.include_router(summon_router.router, prefix="/api/v1")
app.include_router(squad_schedule_router.router, prefix="/api/v1")
app.include_router(websocket_gateway.router)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "environment": ENVIRONMENT}


@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies database and Redis connectivity."""
    from backend.core.dependencies import AsyncSessionLocal
    from sqlalchemy import text
    
    checks = {
        "database": False,
        "redis": False,
    }
    
    # Check database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            checks["database"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    # Check Redis
    try:
        redis = await get_redis()
        await redis._client.ping()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
    
    if all(checks.values()):
        return {"status": "ready", **checks}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", **checks}
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SquadSync API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENVIRONMENT == "development",
        log_level=LOG_LEVEL.lower(),
    )
