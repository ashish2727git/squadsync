#!/usr/bin/env python
"""
SquadSync Server Startup Script
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment
os.environ.setdefault("ENVIRONMENT", "development")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting SquadSync Server")
    print("=" * 60)
    print()
    print("📖 API Documentation will be at: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🌐 Root: http://localhost:8000/")
    print()
    print("⚠️  Note: Make sure PostgreSQL and Redis are running!")
    print("   (App will start but endpoints may fail without DB)")
    print()
    print("=" * 60)
    print()
    
    try:
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
