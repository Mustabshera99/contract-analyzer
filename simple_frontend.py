"""
Simple working Streamlit frontend for Contract Analyzer
"""
import sys
from pathlib import Path
import streamlit as st
import requests
import json

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Contract Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.title("📄 Contract Analyzer")
    st.markdown("AI-powered contract analysis and risk assessment")
    
    # Check backend connection
    if check_backend_connection():
        st.success("✅ Connected to analysis service")
        
        # Sidebar
        with st.sidebar:
            st.header("📊 Dashboard")
            
            # Get dashboard data
            try:
                response = requests.get(f"{BACKEND_URL}/api/v1/analytics/dashboard")
                if response.status_code == 200:
                    data = response.json()
                    
                    st.metric("Total Contracts", data["total_contracts"])
                    st.metric("High Risk", data["high_risk_count"], delta=f"{data['high_risk_count']}")
                    st.metric("Medium Risk", data["medium_risk_count"])
                    st.metric("Low Risk", data["low_risk_count"])
                    
                    st.subheader("Recent Analyses")
                    for analysis in data["recent_analyses"]:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"📄 {analysis['name']}")
                                st.write(f"📅 {analysis['date']}")
                            with col2:
                                risk_color = "🔴" if analysis['risk_score'] > 70 else "🟡" if analysis['risk_score'] > 40 else "🟢"
                                st.write(f"{risk_color} {analysis['risk_score']}")
            except:
                st.error("Failed to load dashboard data")
        
        # Main content
        tab1, tab2, tab3 = st.tabs(["📤 Upload Contract", "📊 Analytics", "⚙️ Settings"])
        
        with tab1:
            st.header("Contract Analysis")
            
            uploaded_file = st.file_uploader(
                "Upload your contract for analysis",
                type=['pdf', 'doc', 'docx', 'txt'],
                help="Supported formats: PDF, DOC, DOCX, TXT"
            )
            
            if uploaded_file:
                st.write(f"📄 **File:** {uploaded_file.name}")
                st.write(f"📊 **Size:** {uploaded_file.size} bytes")
                
                if st.button("🔍 Analyze Contract", type="primary"):
                    with st.spinner("Analyzing contract..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            response = requests.post(f"{BACKEND_URL}/api/v1/contracts/analyze", files=files)
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                st.success("✅ Analysis Complete!")
                                
                                # Display results
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Risk Score", f"{result['risk_score']}/100")
                                with col2:
                                    st.metric("Risk Level", result['risk_level'])
                                with col3:
                                    st.metric("Confidence", f"{result['confidence']:.1%}")
                                
                                # Key findings
                                st.subheader("🔍 Key Findings")
                                for finding in result['key_findings']:
                                    st.write(f"• {finding}")
                                
                                # Recommendations
                                st.subheader("💡 Recommendations")
                                for rec in result['recommendations']:
                                    st.write(f"• {rec}")
                                
                            else:
                                st.error(f"Analysis failed: {response.text}")
                        except Exception as e:
                            st.error(f"Error analyzing contract: {str(e)}")
        
        with tab2:
            st.header("📊 Analytics Dashboard")
            st.info("Analytics features will be available once you've analyzed some contracts.")
            
            # Placeholder charts
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Risk Distribution")
                st.bar_chart({"High": 15, "Medium": 45, "Low": 67})
            
            with col2:
                st.subheader("Analysis Trends")
                st.line_chart({"Week 1": 10, "Week 2": 15, "Week 3": 20, "Week 4": 25})
        
        with tab3:
            st.header("⚙️ Settings")
            st.write("**Backend URL:**", BACKEND_URL)
            st.write("**Status:** ✅ Connected")
            
            if st.button("🔄 Test Connection"):
                if check_backend_connection():
                    st.success("✅ Backend is responding")
                else:
                    st.error("❌ Backend is not responding")
    
    else:
        st.error("❌ Unable to connect to the analysis service.")
        st.markdown("""
        **Troubleshooting:**
        1. Make sure the backend server is running on port 8000
        2. Run: `python simple_backend.py`
        3. Check that no firewall is blocking the connection
        """)
        
        if st.button("🔄 Retry Connection"):
            st.rerun()

if __name__ == "__main__":
    main()