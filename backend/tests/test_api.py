"""
Tests for API endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
	"""Test cases for health check endpoint."""

	def test_health_check(self, test_client):
		"""Test health check endpoint."""
		response = test_client.get("/health")

		assert response.status_code == 200
		data = response.json()
		assert "status" in data
		assert data["status"] == "healthy"

	def test_health_check_detailed(self, test_client):
		"""Test detailed health check endpoint."""
		response = test_client.get("/health/detailed")

		assert response.status_code == 200
		data = response.json()
		assert "status" in data
		assert "components" in data


class TestContractAnalysisEndpoint:
	"""Test cases for contract analysis endpoint."""

	def test_analyze_contract_success(self, test_client, sample_contract_text):
		"""Test successful contract analysis."""
		with patch("app.api.contracts.get_contract_analysis_service") as mock_service:
			mock_service.return_value.analyze_contract = AsyncMock()
			mock_service.return_value.analyze_contract.return_value = {
				"analysis_id": "test_123",
				"status": "completed",
				"risky_clauses": [],
				"overall_risk_score": 5.0,
				"suggested_redlines": [],
				"email_draft": "Test email",
				"processing_time": 1.0,
			}

			files = {"file": ("test_contract.pdf", sample_contract_text.encode(), "text/plain")}
			response = test_client.post("/analyze", files=files)

			assert response.status_code == 200
			data = response.json()
			assert data["status"] == "completed"
			assert "analysis_id" in data

	def test_analyze_contract_no_file(self, test_client):
		"""Test contract analysis without file."""
		response = test_client.post("/analyze")

		assert response.status_code == 400

	def test_analyze_contract_invalid_file_type(self, test_client):
		"""Test contract analysis with invalid file type."""
		files = {"file": ("test.txt", b"test content", "text/plain")}
		response = test_client.post("/analyze", files=files)

		# Should still work with text files
		assert response.status_code in [200, 400]

	def test_analyze_contract_with_analysis_type(self, test_client, sample_contract_text):
		"""Test contract analysis with specific analysis type."""
		with patch("app.api.contracts.get_contract_analysis_service") as mock_service:
			mock_service.return_value.analyze_contract = AsyncMock()
			mock_service.return_value.analyze_contract.return_value = {
				"analysis_id": "test_123",
				"status": "completed",
				"risky_clauses": [],
				"overall_risk_score": 5.0,
				"suggested_redlines": [],
				"email_draft": "Test email",
				"processing_time": 1.0,
			}

			files = {"file": ("test_contract.pdf", sample_contract_text.encode(), "text/plain")}
			data = {"analysis_type": "comprehensive"}
			response = test_client.post("/analyze", files=files, data=data)

			assert response.status_code == 200

	def test_analyze_contract_error(self, test_client, sample_contract_text):
		"""Test contract analysis with error."""
		with patch("app.api.contracts.get_contract_analysis_service") as mock_service:
			mock_service.return_value.analyze_contract = AsyncMock()
			mock_service.return_value.analyze_contract.side_effect = Exception("Analysis failed")

			files = {"file": ("test_contract.pdf", sample_contract_text.encode(), "text/plain")}
			response = test_client.post("/analyze", files=files)

			assert response.status_code == 500


class TestWorkflowEndpoint:
	"""Test cases for workflow endpoint."""

	def test_execute_workflow_success(self, test_client, sample_contract_text):
		"""Test successful workflow execution."""
		with patch("app.api.workflows.ContractAnalysisWorkflow") as mock_workflow_class:
			mock_workflow = AsyncMock()
			mock_workflow.execute.return_value = {
				"status": "completed",
				"risky_clauses": [],
				"overall_risk_score": 5.0,
				"suggested_redlines": [],
				"email_draft": "Test email",
			}
			mock_workflow_class.return_value = mock_workflow

			data = {"contract_text": sample_contract_text, "contract_filename": "test_contract.pdf"}
			response = test_client.post("/workflow/execute", json=data)

			assert response.status_code == 200
			result = response.json()
			assert result["status"] == "completed"

	def test_execute_workflow_invalid_input(self, test_client):
		"""Test workflow execution with invalid input."""
		data = {"contract_text": "", "contract_filename": "test_contract.pdf"}
		response = test_client.post("/workflow/execute", json=data)

		assert response.status_code == 400

	def test_get_workflow_status(self, test_client):
		"""Test getting workflow status."""
		with patch("app.api.workflows.ContractAnalysisWorkflow") as mock_workflow_class:
			mock_workflow = AsyncMock()
			mock_workflow.get_workflow_status.return_value = {"status": "completed", "current_node": "finalize", "execution_id": "test_123"}
			mock_workflow_class.return_value = mock_workflow

			response = test_client.get("/workflow/status")

			assert response.status_code == 200
			data = response.json()
			assert data["status"] == "completed"


class TestAnalyticsEndpoint:
	"""Test cases for analytics endpoint."""

	def test_get_analytics(self, test_client):
		"""Test getting analytics data."""
		with patch("app.api.analytics.get_analytics_service") as mock_service:
			mock_service.return_value.get_analytics.return_value = {"total_analyses": 10, "success_rate": 0.9, "average_processing_time": 2.5}

			response = test_client.get("/analytics")

			assert response.status_code == 200
			data = response.json()
			assert "total_analyses" in data

	def test_get_analytics_with_filters(self, test_client):
		"""Test getting analytics with filters."""
		with patch("app.api.analytics.get_analytics_service") as mock_service:
			mock_service.return_value.get_analytics.return_value = {"total_analyses": 5, "success_rate": 0.8, "average_processing_time": 3.0}

			params = {"start_date": "2024-01-01", "end_date": "2024-01-31"}
			response = test_client.get("/analytics", params=params)

			assert response.status_code == 200


class TestMonitoringEndpoint:
	"""Test cases for monitoring endpoint."""

	def test_get_metrics(self, test_client):
		"""Test getting metrics."""
		response = test_client.get("/metrics")

		assert response.status_code == 200

	def test_get_health_detailed(self, test_client):
		"""Test getting detailed health information."""
		response = test_client.get("/monitoring/health")

		assert response.status_code == 200
		data = response.json()
		assert "status" in data
		assert "timestamp" in data

	def test_get_system_status(self, test_client):
		"""Test getting system status."""
		response = test_client.get("/monitoring/status")

		assert response.status_code == 200
		data = response.json()
		assert "status" in data
		assert "components" in data
