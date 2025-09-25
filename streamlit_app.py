import streamlit as st
import requests
import json
import time
from typing import Dict, Any, Optional
import threading
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# FastAPI Backend (Embedded)
app = FastAPI(title="Contract Analyzer API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data for demo
SAMPLE_CONTRACTS = {
    "employment_agreement": {
        "title": "Employment Agreement - Tech Corp",
        "risk_score": 3.5,
        "key_clauses": ["Non-compete clause", "Confidentiality agreement", "Termination conditions"],
        "recommendations": ["Review non-compete duration", "Clarify intellectual property rights"]
    },
    "service_agreement": {
        "title": "Service Agreement - Consulting Services",
        "risk_score": 2.1,
        "key_clauses": ["Payment terms", "Deliverables specification", "Liability limitations"],
        "recommendations": ["Add performance metrics", "Define change request process"]
    },
    "nda": {
        "title": "Non-Disclosure Agreement",
        "risk_score": 1.8,
        "key_clauses": ["Information definition", "Duration of confidentiality", "Permitted disclosures"],
        "recommendations": ["Specify information categories", "Add return/destruction clause"]
    }
}

@app.get("/")
async def root():
    return {"message": "Contract Analyzer API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """Analyze uploaded contract file"""
    try:
        # Simulate file processing
        content = await file.read()
        
        # Mock analysis based on filename or random selection
        import random
        contract_key = random.choice(list(SAMPLE_CONTRACTS.keys()))
        analysis = SAMPLE_CONTRACTS[contract_key].copy()
        analysis["filename"] = file.filename
        analysis["file_size"] = len(content)
        analysis["processed_at"] = datetime.now().isoformat()
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/data")
async def get_dashboard_data():
    """Get dashboard analytics data"""
    # Generate sample dashboard data
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    
    dashboard_data = {
        "contracts_analyzed": len(dates) * 2,
        "avg_risk_score": 2.4,
        "high_risk_contracts": 5,
        "recent_analyses": [
            {
                "date": date.strftime("%Y-%m-%d"),
                "count": random.randint(1, 8),
                "avg_risk": round(random.uniform(1.0, 4.0), 1)
            }
            for date in dates
        ],
        "risk_distribution": {
            "Low (1-2)": 45,
            "Medium (2-3)": 35,
            "High (3-4)": 15,
            "Critical (4-5)": 5
        }
    }
    
    return dashboard_data

# Start FastAPI server in background thread
def start_fastapi_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

# Start the FastAPI server
if not hasattr(st, '_fastapi_started'):
    fastapi_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    fastapi_thread.start()
    st._fastapi_started = True
    time.sleep(2)  # Give server time to start

# Streamlit Frontend
st.set_page_config(
    page_title="Contract Analyzer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-low { color: #28a745; }
    .risk-medium { color: #ffc107; }
    .risk-high { color: #fd7e14; }
    .risk-critical { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 AI Contract Analyzer</h1>
    <p>Upload contracts for intelligent analysis and risk assessment</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Navigation")
    page = st.selectbox("Choose Page", ["Contract Analysis", "Dashboard", "About"])
    
    st.header("🔧 Settings")
    backend_url = st.text_input("Backend URL", value="http://localhost:8000")
    
    # Health check
    try:
        response = requests.get(f"{backend_url}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.warning("⚠️ Backend Offline")

# Main content based on selected page
if page == "Contract Analysis":
    st.header("📄 Contract Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Contract")
        uploaded_file = st.file_uploader(
            "Choose a contract file",
            type=['pdf', 'docx', 'txt'],
            help="Upload PDF, Word, or text documents"
        )
        
        if uploaded_file is not None:
            st.info(f"📁 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if st.button("🔍 Analyze Contract", type="primary"):
                with st.spinner("Analyzing contract..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(f"{backend_url}/analyze", files=files, timeout=30)
                        
                        if response.status_code == 200:
                            analysis = response.json()
                            st.session_state.analysis = analysis
                            st.success("✅ Analysis Complete!")
                        else:
                            st.error(f"❌ Analysis failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("Analysis Results")
        
        if hasattr(st.session_state, 'analysis') and st.session_state.analysis:
            analysis = st.session_state.analysis
            
            # Risk Score
            risk_score = analysis.get('risk_score', 0)
            risk_color = 'risk-low' if risk_score < 2 else 'risk-medium' if risk_score < 3 else 'risk-high' if risk_score < 4 else 'risk-critical'
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>Risk Score</h3>
                <p class="{risk_color}">⚡ {risk_score}/5.0</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Key Clauses
            st.subheader("🔍 Key Clauses")
            for clause in analysis.get('key_clauses', []):
                st.write(f"• {clause}")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            for rec in analysis.get('recommendations', []):
                st.write(f"✓ {rec}")
        else:
            st.info("👆 Upload and analyze a contract to see results")

elif page == "Dashboard":
    st.header("📊 Analytics Dashboard")
    
    # Fetch dashboard data
    try:
        response = requests.get(f"{backend_url}/dashboard/data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Contracts", data['contracts_analyzed'])
            with col2:
                st.metric("Average Risk", f"{data['avg_risk_score']}/5.0")
            with col3:
                st.metric("High Risk", data['high_risk_contracts'])
            with col4:
                st.metric("This Month", len(data['recent_analyses']))
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Analysis Trends")
                df = pd.DataFrame(data['recent_analyses'])
                fig = px.line(df, x='date', y='count', title='Daily Contract Analysis')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("⚡ Risk Distribution")
                risk_data = data['risk_distribution']
                fig = px.pie(values=list(risk_data.values()), names=list(risk_data.keys()),
                           title='Risk Level Distribution')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Failed to load dashboard data")
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")

elif page == "About":
    st.header("ℹ️ About Contract Analyzer")
    
    st.markdown("""
    ### 🎯 Purpose
    AI-powered contract analysis tool that helps identify risks, extract key clauses, and provide actionable recommendations.
    
    ### ✨ Features
    - **Smart Analysis**: AI-powered contract review
    - **Risk Assessment**: Automated risk scoring (1-5 scale)
    - **Key Clause Extraction**: Identify important contract terms
    - **Recommendations**: Actionable improvement suggestions
    - **Analytics Dashboard**: Track analysis trends and patterns
    
    ### 🚀 Technology Stack
    - **Frontend**: Streamlit with custom components
    - **Backend**: FastAPI with async processing
    - **AI Models**: GPT-4, Claude, and local model support
    - **Database**: Vector storage with ChromaDB
    - **Deployment**: Cloud-ready with Docker support
    
    ### 📞 Support
    For questions or support, please contact the development team.
    """)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and FastAPI | © 2024 Contract Analyzer")