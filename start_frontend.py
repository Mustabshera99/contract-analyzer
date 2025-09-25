"""
Startup script for the Streamlit frontend application.
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
    import streamlit.web.cli as stcli
    
    print("🎨 Starting Contract Analyzer Frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("-" * 50)
    
    # Configure Streamlit to run the frontend app
    sys.argv = [
        "streamlit", 
        "run", 
        "frontend/app.py",
        "--server.port=8501",
        "--server.address=localhost",
        "--server.headless=false"
    ]
    
    # Start Streamlit
    sys.exit(stcli.main())