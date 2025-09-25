"""
Minimal backend starter to isolate import issues.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))
os.chdir(project_root)

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    # Create a minimal FastAPI app for testing
    app = FastAPI(title="Contract Analyzer API - Minimal", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"message": "Contract Analyzer Backend is running!"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "contract-analyzer-backend"}
    
    print("🚀 Starting Minimal Contract Analyzer Backend...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    print("🏥 Health Check: http://127.0.0.1:8000/health")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )