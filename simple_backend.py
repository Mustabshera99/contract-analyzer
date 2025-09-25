"""
Simple working FastAPI backend for Contract Analyzer
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Create FastAPI app
app = FastAPI(
    title="Contract Analyzer API",
    description="AI-powered contract analysis tool",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Contract Analyzer Backend is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "contract-analyzer-backend",
        "version": "1.0.0"
    }

@app.post("/api/v1/contracts/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """Basic contract analysis endpoint"""
    if not file.filename.endswith(('.pdf', '.doc', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Simulate contract analysis
    return {
        "analysis_id": "mock-analysis-123",
        "status": "completed",
        "risk_score": 65,
        "risk_level": "Medium",
        "key_findings": [
            "Standard liability clause detected",
            "Termination clause requires review", 
            "Payment terms are favorable"
        ],
        "recommendations": [
            "Consider adding force majeure clause",
            "Review liability limits",
            "Clarify intellectual property terms"
        ],
        "confidence": 0.85
    }

@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_data():
    """Mock analytics data for dashboard"""
    return {
        "total_contracts": 127,
        "high_risk_count": 15,
        "medium_risk_count": 45,
        "low_risk_count": 67,
        "recent_analyses": [
            {"id": "1", "name": "Service Agreement", "risk_score": 75, "date": "2025-09-23"},
            {"id": "2", "name": "NDA Template", "risk_score": 25, "date": "2025-09-22"},
            {"id": "3", "name": "Employment Contract", "risk_score": 55, "date": "2025-09-21"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Contract Analyzer Backend...")
    print("📍 Backend: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("🏥 Health: http://127.0.0.1:8000/health")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")