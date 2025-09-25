"""
Stable backend service for Contract Analyzer.
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
    from fastapi.middleware.cors import CORSMiddleware
    
    # Create FastAPI app
    app = FastAPI(
        title="Contract Analyzer Backend API",
        description="AI-powered contract analysis and negotiation assistance",
        version="1.0.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Basic routes
    @app.get("/")
    async def root():
        return {
            "message": "Contract Analyzer Backend API is running!",
            "status": "healthy",
            "version": "1.0.0"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "contract-analyzer-backend",
            "version": "1.0.0"
        }
    
    # Mock analysis endpoint for testing
    @app.post("/api/v1/analyze")
    async def analyze_contract():
        return {
            "status": "success",
            "message": "Contract analysis completed (mock)",
            "risk_score": 0.65,
            "analysis": {
                "summary": "This is a mock analysis result for testing the connection.",
                "risks": ["Mock risk 1", "Mock risk 2"],
                "recommendations": ["Mock recommendation 1", "Mock recommendation 2"]
            }
        }
    
    print("🚀 Starting Contract Analyzer Backend API...")
    print("📍 Server URL: http://127.0.0.1:8002")
    print("📚 API Documentation: http://127.0.0.1:8002/docs")
    print("🏥 Health Check: http://127.0.0.1:8002/health")
    print("🔗 Frontend can connect at: http://localhost:8501")
    print("-" * 60)
    
    # Start the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
        reload=False,
        log_level="info"
    )