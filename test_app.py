"""
Minimal test version of the Streamlit app to identify import issues.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

import streamlit as st

st.title("Contract Analyzer - Test Version")
st.write("This is a test version to verify the application setup.")

try:
    from frontend.utils.api_client import APIClient
    st.success("✅ API Client imported successfully")
except ImportError as e:
    st.error(f"❌ API Client import failed: {e}")

try:
    from frontend.components.file_upload import file_upload_component
    st.success("✅ File Upload Component imported successfully")
except ImportError as e:
    st.error(f"❌ File Upload Component import failed: {e}")

try:
    from frontend.components.results_display import results_display
    st.success("✅ Results Display Component imported successfully")
except ImportError as e:
    st.error(f"❌ Results Display Component import failed: {e}")

try:
    from frontend.components.progress_indicator import progress_indicator
    st.success("✅ Progress Indicator Component imported successfully")
except ImportError as e:
    st.error(f"❌ Progress Indicator Component import failed: {e}")

try:
    from frontend.components.analytics_dashboard import render_analytics_dashboard
    st.success("✅ Analytics Dashboard Component imported successfully")
except ImportError as e:
    st.error(f"❌ Analytics Dashboard Component import failed: {e}")

try:
    from frontend.components.observability_dashboard import render_observability_dashboard
    st.success("✅ Observability Dashboard Component imported successfully")
except ImportError as e:
    st.error(f"❌ Observability Dashboard Component import failed: {e}")

try:
    from frontend.components.error_display import error_display
    st.success("✅ Error Display Component imported successfully")
except ImportError as e:
    st.error(f"❌ Error Display Component import failed: {e}")

st.write("---")
st.write("If all components are imported successfully, the main app should work.")