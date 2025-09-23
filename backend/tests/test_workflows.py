"""
Tests for workflow components.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.mock_vector_store import MockPrecedentClause
from app.workflows.analyzer import ContractAnalyzer
from app.workflows.state import ContractAnalysisState, WorkflowStatus, add_warning, create_initial_state, update_state_status, validate_state


class TestContractAnalyzer:
	"""Test cases for ContractAnalyzer class."""

	@pytest.fixture
	def analyzer(self):
		"""Create a ContractAnalyzer instance for testing."""
		with (
			patch("app.workflows.analyzer.get_ai_manager") as mock_ai_manager,
			patch("app.workflows.analyzer.get_mock_vector_store_service") as mock_vector_store,
		):
			# Mock AI manager
			mock_ai_manager.return_value.analyze_with_fallback = AsyncMock()
			mock_ai_manager.return_value.analyze_with_fallback.return_value = MagicMock(
				content='{"risky_clauses": [], "overall_risk_score": 5.0, "analysis_summary": "Test analysis", "recommendations": []}',
				model_used="gpt-4",
				confidence_score=0.8,
				processing_time=1.0,
				token_usage={"total_tokens": 100},
				cost=0.01,
			)

			# Mock vector store
			mock_vector_store.return_value.search_similar_clauses.return_value = []

			analyzer = ContractAnalyzer()
			analyzer.use_mock_store = True
			return analyzer

	def test_extract_key_phrases(self, analyzer, sample_contract_text):
		"""Test key phrase extraction from contract text."""
		key_phrases = analyzer._extract_key_phrases(sample_contract_text)

		assert isinstance(key_phrases, list)
		assert len(key_phrases) > 0

		# Should contain legal keywords
		legal_keywords = ["liability", "indemnification", "payment", "termination"]
		found_keywords = any(keyword in phrase.lower() for phrase in key_phrases for keyword in legal_keywords)
		assert found_keywords

	@pytest.mark.asyncio
	async def test_retrieve_precedent_context(self, analyzer, sample_contract_text):
		"""Test precedent context retrieval."""
		precedents = await analyzer._retrieve_precedent_context(sample_contract_text)

		assert isinstance(precedents, list)

	def test_build_analysis_prompt(self, analyzer, sample_contract_text):
		"""Test analysis prompt building."""
		precedents = []
		prompt = analyzer._build_analysis_prompt(sample_contract_text, "test_contract.pdf", precedents)

		assert isinstance(prompt, str)
		assert "test_contract.pdf" in prompt
		assert sample_contract_text in prompt

	def test_parse_analysis_response(self, analyzer):
		"""Test parsing of AI analysis response."""
		response = '{"risky_clauses": [], "overall_risk_score": 5.0, "analysis_summary": "Test", "recommendations": []}'

		result = analyzer._parse_analysis_response(response)

		assert result.overall_risk_score == 5.0
		assert result.analysis_summary == "Test"
		assert isinstance(result.risky_clauses, list)

	def test_parse_analysis_response_with_markdown(self, analyzer):
		"""Test parsing of AI response wrapped in markdown."""
		response = """```json
        {"risky_clauses": [], "overall_risk_score": 5.0, "analysis_summary": "Test", "recommendations": []}
        ```"""

		result = analyzer._parse_analysis_response(response)

		assert result.overall_risk_score == 5.0

	def test_parse_analysis_response_invalid_json(self, analyzer):
		"""Test parsing of invalid JSON response."""
		response = "Invalid JSON response"

		with pytest.raises(Exception):
			analyzer._parse_analysis_response(response)

	def test_enhance_with_precedent_references(self, analyzer):
		"""Test enhancement of analysis with precedent references."""
		from app.workflows.analyzer import ContractRiskAnalysis

		analysis = ContractRiskAnalysis(risky_clauses=[], overall_risk_score=5.0, analysis_summary="Test", recommendations=[])

		precedents = [
			MockPrecedentClause(
				id="test_001",
				text="Test precedent",
				category="Test",
				risk_level="High",
				source_document="Test Doc",
				effectiveness_score=0.8,
				created_at="2024-01-01T00:00:00Z",
			)
		]

		enhanced = analyzer._enhance_with_precedent_references(analysis, precedents)

		assert enhanced == analysis  # Should return unchanged if no risky clauses


class TestWorkflowState:
	"""Test cases for workflow state management."""

	def test_create_initial_state(self, sample_contract_text):
		"""Test creation of initial workflow state."""
		state = create_initial_state(sample_contract_text, "test_contract.pdf")

		assert state["contract_text"] == sample_contract_text
		assert state["contract_filename"] == "test_contract.pdf"
		assert state["status"] == WorkflowStatus.INITIALIZED
		assert state["risky_clauses"] == []
		assert state["suggested_redlines"] == []
		assert state["email_draft"] == ""

	def test_create_initial_state_with_config(self, sample_contract_text):
		"""Test creation of initial state with configuration."""
		config = {"test_param": "test_value"}
		state = create_initial_state(sample_contract_text, "test_contract.pdf", config)

		assert state["config"]["test_param"] == "test_value"

	def test_validate_state_valid(self, sample_contract_text):
		"""Test validation of valid state."""
		state = create_initial_state(sample_contract_text, "test_contract.pdf")
		errors = validate_state(state)

		assert errors == []

	def test_validate_state_invalid_contract_text(self):
		"""Test validation of state with invalid contract text."""
		state = create_initial_state("", "test_contract.pdf")
		errors = validate_state(state)

		assert "contract_text is required" in errors[0]

	def test_validate_state_invalid_filename(self, sample_contract_text):
		"""Test validation of state with invalid filename."""
		state = create_initial_state(sample_contract_text, "")
		errors = validate_state(state)

		assert "contract_filename is required" in errors[0]

	def test_validate_state_invalid_risky_clauses(self, sample_contract_text):
		"""Test validation of state with invalid risky clauses."""
		state = create_initial_state(sample_contract_text, "test_contract.pdf")
		state["risky_clauses"] = [{"invalid": "clause"}]  # Missing required fields

		errors = validate_state(state)

		assert any("missing required field" in error for error in errors)

	def test_update_state_status(self, sample_contract_text):
		"""Test updating workflow state status."""
		state = create_initial_state(sample_contract_text, "test_contract.pdf")

		updated_state = update_state_status(state, WorkflowStatus.ANALYZING, "analyzer")

		assert updated_state["status"] == WorkflowStatus.ANALYZING
		assert updated_state["current_node"] == "analyzer"

	def test_update_state_status_with_error(self, sample_contract_text):
		"""Test updating state status with error."""
		state = create_initial_state(sample_contract_text, "test_contract.pdf")

		updated_state = update_state_status(state, WorkflowStatus.FAILED, "analyzer", "Test error")

		assert updated_state["status"] == WorkflowStatus.FAILED
		assert updated_state["last_error"] == "Test error"
		assert "Test error" in updated_state["errors"]

	def test_add_warning(self, sample_contract_text):
		"""Test adding warning to state."""
		state = create_initial_state(sample_contract_text, "test_contract.pdf")

		updated_state = add_warning(state, "Test warning")

		assert "Test warning" in updated_state["processing_metadata"]["warnings"]


class TestWorkflowIntegration:
	"""Integration tests for workflow components."""

	@pytest.mark.asyncio
	async def test_analyzer_node_integration(self, sample_contract_text):
		"""Test analyzer node integration."""
		from app.workflows.analyzer import analyzer_node

		state = create_initial_state(sample_contract_text, "test_contract.pdf")

		with patch("app.workflows.analyzer.ContractAnalyzer") as mock_analyzer_class:
			mock_analyzer = AsyncMock()
			mock_analyzer.analyze_contract.return_value = MagicMock(
				risky_clauses=[], overall_risk_score=5.0, analysis_summary="Test analysis", recommendations=[]
			)
			mock_analyzer_class.return_value = mock_analyzer

			result_state = await analyzer_node(state)

			assert result_state["status"] in [WorkflowStatus.ANALYZING, WorkflowStatus.FAILED]
			mock_analyzer.analyze_contract.assert_called_once()

	def test_negotiator_node_creation(self):
		"""Test negotiator node creation."""
		from app.workflows.negotiator import create_negotiator_node

		negotiator_func = create_negotiator_node()

		assert callable(negotiator_func)

	def test_communicator_node_creation(self):
		"""Test communicator node creation."""
		from app.workflows.communicator import create_communicator_node

		communicator_func = create_communicator_node()

		assert callable(communicator_func)
