"""
Test script to verify server can start
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from backend.main import app
    print("✅ Application imports successfully!")
    print("✅ Server is ready to start!")
    print("\nTo start the server, run:")
    print("  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\nOr use:")
    print("  .\\start_server.bat")
except Exception as e:
    print(f"❌ Error importing application: {e}")
    import traceback
    traceback.print_exc()
