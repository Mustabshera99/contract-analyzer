"""
Startup script for the FastAPI backend server.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Change working directory
os.chdir(project_root)

if __name__ == "__main__":
    import uvicorn
    
    # Import the FastAPI app
    from backend.app.main import app
    
    print("🚀 Starting Contract Analyzer Backend Server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    print("📖 Alternative Docs: http://127.0.0.1:8000/redoc")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )