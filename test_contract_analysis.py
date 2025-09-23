#!/usr/bin/env python3
"""
Test script for contract analysis functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_contract_analysis():
	"""Test the contract analysis functionality."""
	print("🧪 Testing Contract Analysis Functionality")
	print("=" * 50)

	try:
		# Test backend imports
		print("1. Testing backend imports...")
		from backend.app.core.config import get_settings
		from backend.app.main import app

		print("   ✅ Backend imports successful")

		# Test settings
		print("2. Testing configuration...")
		settings = get_settings()
		print(f"   ✅ API Host: {settings.api_host}")
		print(f"   ✅ API Port: {settings.api_port}")
		print(f"   ✅ OpenAI API Key: {'configured' if settings.openai_api_key else 'not configured'}")
		print(f"   ✅ ChromaDB Directory: {settings.chroma_persist_directory}")

		# Test API client
		print("3. Testing API client...")
		from fastapi.testclient import TestClient

		client = TestClient(app)

		# Test health endpoint
		print("4. Testing health endpoint...")
		response = client.get("/api/v1/health")
		assert response.status_code == 200
		health_data = response.json()
		print(f"   ✅ Health check: {health_data['status']}")
		print(f"   ✅ Dependencies: {health_data['dependencies']}")

		# Test monitoring endpoints
		print("5. Testing monitoring endpoints...")
		response = client.get("/monitoring/health")
		assert response.status_code == 200
		print("   ✅ Monitoring health check passed")

		# Test file upload endpoint (without actual file)
		print("6. Testing contract analysis endpoint...")
		response = client.post("/api/v1/analyze-contract")
		# This should return 422 (validation error) since no file is provided
		assert response.status_code == 422
		print("   ✅ Contract analysis endpoint accessible")

		print("\n🎉 All tests passed! The application is ready to use.")
		print("\nTo start the application:")
		print("   python run_app.py")
		print("\nOr start servers separately:")
		print("   Backend: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload")
		print("   Frontend: streamlit run frontend/app.py --server.port 8501")

	except Exception as e:
		print(f"❌ Test failed: {e}")
		import traceback

		traceback.print_exc()
		return False

	return True


if __name__ == "__main__":
	success = test_contract_analysis()
	sys.exit(0 if success else 1)
