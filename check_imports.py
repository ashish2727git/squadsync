"""Check if all imports work"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print("Checking imports...")
try:
    print("1. Importing config...")
    from backend.core.config import ENVIRONMENT
    print(f"   ✅ Config OK - Environment: {ENVIRONMENT}")
except Exception as e:
    print(f"   ❌ Config failed: {e}")
    sys.exit(1)

try:
    print("2. Importing dependencies...")
    from backend.core.dependencies import get_db
    print("   ✅ Dependencies OK")
except Exception as e:
    print(f"   ❌ Dependencies failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Importing main app...")
    from backend.main import app
    print("   ✅ Main app OK")
    print(f"   ✅ App title: {app.title}")
except Exception as e:
    print(f"   ❌ Main app failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful! Server should start.")
