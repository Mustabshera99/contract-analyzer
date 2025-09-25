#!/usr/bin/env python3
"""
Run script for the Streamlit frontend application.
This script sets up the proper Python path and runs the app.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Change to the project directory
os.chdir(project_root)

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import streamlit.runtime.state
    
    # Set up Streamlit configuration
    streamlit.runtime.state.SessionState = streamlit.runtime.state.SessionState
    
    # Run the app
    sys.argv = ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=localhost"]
    sys.exit(stcli.main())