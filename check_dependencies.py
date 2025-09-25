"""
Check for missing dependencies in the backend.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print("🔍 Checking backend dependencies...")

# Test basic imports first
try:
    import fastapi
    print("✅ FastAPI available")
except ImportError as e:
    print(f"❌ FastAPI missing: {e}")

try:
    import uvicorn
    print("✅ Uvicorn available")
except ImportError as e:
    print(f"❌ Uvicorn missing: {e}")

try:
    import openai
    print("✅ OpenAI available")
except ImportError as e:
    print(f"❌ OpenAI missing: {e}")

try:
    import magic
    print("✅ Python-magic available")
except ImportError as e:
    print(f"❌ Python-magic missing: {e}")

try:
    import pyotp
    print("✅ PyOTP available")
except ImportError as e:
    print(f"❌ PyOTP missing: {e}")

# Test more specific imports
print("\n🔍 Testing backend module imports...")

try:
    from backend.app.core.config import get_settings
    print("✅ Config module available")
except ImportError as e:
    print(f"❌ Config module issue: {e}")

try:
    from backend.app.core.logging import get_logger
    print("✅ Logging module available")
except ImportError as e:
    print(f"❌ Logging module issue: {e}")

try:
    from backend.app.models.api_models import ErrorResponse
    print("✅ API models available")
except ImportError as e:
    print(f"❌ API models issue: {e}")

print("\n🔍 Testing main app import...")
try:
    from backend.app.main import create_app
    print("✅ Main app factory available")
    
    # Try creating the app
    print("🚀 Testing app creation...")
    app = create_app()
    print("✅ App created successfully!")
    
except ImportError as e:
    print(f"❌ Main app import issue: {e}")
except Exception as e:
    print(f"❌ App creation issue: {e}")

print("\n🎯 Dependency check complete!")