"""
Pytest configuration and fixtures for contract analyzer tests.
"""

import asyncio
import os

# Add the app directory to the Python path
import sys
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from app.core.config import get_settings
from app.main import app
from app.services.mock_vector_store import get_mock_vector_store_service


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
	"""Create an instance of the default event loop for the test session."""
	loop = asyncio.get_event_loop_policy().new_event_loop()
	yield loop
	loop.close()


@pytest.fixture
def test_client() -> TestClient:
	"""Create a test client for the FastAPI application."""
	return TestClient(app, base_url="http://testserver/api/v1")


@pytest.fixture
def mock_settings():
	"""Mock settings for testing."""
	return {
		"openai_api_key": "test-key",
		"openai_model": "gpt-4",
		"openai_temperature": 0.1,
		"chroma_persist_directory": "./test_data/chroma",
		"langsmith_tracing": False,
		"enable_monitoring": False,
	}


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
	"""Create a temporary directory for test data."""
	with tempfile.TemporaryDirectory() as temp_dir:
		yield Path(temp_dir)


@pytest.fixture
def sample_contract_text() -> str:
	"""Sample contract text for testing."""
	return """
    SOFTWARE LICENSE AGREEMENT
    
    This Software License Agreement ("Agreement") is entered into between Company Inc. ("Licensor") and Client Corp. ("Licensee").
    
    1. GRANT OF LICENSE
    Subject to the terms and conditions of this Agreement, Licensor hereby grants to Licensee a non-exclusive, non-transferable license to use the Software.
    
    2. PAYMENT TERMS
    Licensee shall pay Licensor the sum of $10,000 within thirty (30) days of execution of this Agreement. All payments are non-refundable.
    
    3. INDEMNIFICATION
    Licensee agrees to indemnify, defend, and hold harmless Licensor from any claims arising from Licensee's use of the Software.
    
    4. LIMITATION OF LIABILITY
    In no event shall Licensor be liable for any indirect, incidental, special, or consequential damages.
    
    5. TERMINATION
    This Agreement may be terminated by either party upon thirty (30) days written notice.
    
    6. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of California.
    """


@pytest.fixture
def sample_risky_clauses():
	"""Sample risky clauses for testing."""
	return [
		{
			"clause_text": "Licensee agrees to indemnify, defend, and hold harmless Licensor from any claims arising from Licensee's use of the Software.",
			"risk_explanation": "This clause places all liability on the licensee, which is highly unfavorable.",
			"risk_level": "High",
			"clause_index": 3,
			"precedent_reference": "Standard indemnification clause",
		},
		{
			"clause_text": "All payments are non-refundable.",
			"risk_explanation": "Non-refundable payment terms can be problematic if the software doesn't meet expectations.",
			"risk_level": "Medium",
			"clause_index": 2,
			"precedent_reference": "Non-refundable payment clause",
		},
	]


@pytest.fixture
def sample_redlines():
	"""Sample redline suggestions for testing."""
	return [
		{
			"original_clause": "Licensee agrees to indemnify, defend, and hold harmless Licensor from any claims arising from Licensee's use of the Software.",
			"suggested_redline": "Each party shall indemnify the other for claims arising from its own negligence or willful misconduct.",
			"risk_explanation": "This clause places all liability on the licensee, which is highly unfavorable.",
			"clause_index": 3,
			"change_rationale": "Mutual indemnification is more balanced and fair to both parties.",
			"risk_mitigated": True,
		}
	]


@pytest.fixture
def mock_vector_store():
	"""Mock vector store service for testing."""
	return get_mock_vector_store_service()


@pytest.fixture
def sample_precedents():
	"""Sample precedent clauses for testing."""
	return [
		{
			"id": "test_001",
			"text": "Each party shall be liable only for direct damages arising from a material breach of this Agreement.",
			"category": "Liability and Indemnification",
			"risk_level": "Low",
			"source_document": "Balanced Liability Clause Template",
			"effectiveness_score": 0.9,
			"created_at": "2024-01-01T00:00:00Z",
		},
		{
			"id": "test_002",
			"text": "The Client agrees to indemnify and hold harmless the Company from any claims arising from the Client's use of the deliverables.",
			"category": "Liability and Indemnification",
			"risk_level": "High",
			"source_document": "Client-Favorable Service Agreement",
			"effectiveness_score": 0.7,
			"created_at": "2024-01-01T00:00:00Z",
		},
	]


@pytest.fixture(autouse=True)
def setup_test_environment(mock_settings, temp_dir):
	"""Set up test environment with mocked settings."""
	# Set environment variables for testing
	for key, value in mock_settings.items():
		os.environ[key.upper()] = str(value)

	# Set test data directory
	os.environ["CHROMA_PERSIST_DIRECTORY"] = str(temp_dir / "chroma")

	yield

	# Clean up environment variables
	for key in mock_settings.keys():
		os.environ.pop(key.upper(), None)
