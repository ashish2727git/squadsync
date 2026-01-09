"""
Quick server startup script for SquadSync.
"""

import uvicorn
import os

# Set development environment
os.environ.setdefault("ENVIRONMENT", "development")

if __name__ == "__main__":
    print("🚀 Starting SquadSync server...")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("\n⚠️  Note: Make sure PostgreSQL and Redis are running!")
    print("   Database: postgresql://localhost:5432/squadsync")
    print("   Redis: redis://localhost:6379/0\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
