"""Test if the application can run"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Testing SquadSync Application")
print("=" * 60)
print()

errors = []

# Test 1: Import models
print("1. Testing model imports...")
try:
    from backend.models.models import SquadEvent, SquadDailyGoal, User, Squad
    print("   [OK] Models import successfully")
except Exception as e:
    print(f"   [ERROR] Models import failed: {e}")
    errors.append(f"Models: {e}")

# Test 2: Import core modules
print("2. Testing core module imports...")
try:
    from backend.core.config import ENVIRONMENT
    from backend.core.dependencies import get_db, get_current_user
    from backend.core.jwt_auth import create_access_token
    print("   [OK] Core modules import successfully")
except Exception as e:
    print(f"   [ERROR] Core modules import failed: {e}")
    errors.append(f"Core: {e}")

# Test 3: Import services
print("3. Testing service imports...")
try:
    from backend.services.summon_service import SummonService
    from backend.services.squad_schedule_service import SquadScheduleService
    print("   [OK] Services import successfully")
except Exception as e:
    print(f"   [ERROR] Services import failed: {e}")
    errors.append(f"Services: {e}")

# Test 4: Import routers
print("4. Testing router imports...")
try:
    from backend.api.routers import summon_router, squad_schedule_router
    print("   [OK] Routers import successfully")
except Exception as e:
    print(f"   [ERROR] Routers import failed: {e}")
    errors.append(f"Routers: {e}")

# Test 5: Import main app
print("5. Testing main application import...")
try:
    from backend.main import app
    print(f"   [OK] Main app imports successfully")
    print(f"   [OK] App title: {app.title}")
    print(f"   [OK] App version: {app.version}")
except Exception as e:
    print(f"   [ERROR] Main app import failed: {e}")
    errors.append(f"Main app: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
if errors:
    print("[ERROR] APPLICATION HAS ERRORS")
    print("=" * 60)
    for error in errors:
        print(f"  - {error}")
    print()
    print("Fix these errors before running the server.")
else:
    print("[SUCCESS] APPLICATION IS READY TO RUN!")
    print("=" * 60)
    print()
    print("To start the server, run:")
    print("  python run_app.py")
    print()
    print("Or:")
    print("  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("Then access:")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Health: http://localhost:8000/health")
