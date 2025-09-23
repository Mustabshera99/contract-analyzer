"""
Tests for service components.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.contract_analysis_service import ContractAnalysisService
from app.services.mock_vector_store import MockPrecedentClause, MockVectorStoreService


class TestMockVectorStoreService:
	"""Test cases for MockVectorStoreService."""

	@pytest.fixture
	def mock_store(self, temp_dir):
		"""Create a MockVectorStoreService instance for testing."""
		with patch("app.services.mock_vector_store.Path") as mock_path:
			mock_path.return_value = temp_dir / "precedents.json"
			return MockVectorStoreService()

	def test_add_precedent_clause(self, mock_store):
		"""Test adding a single precedent clause."""
		clause = MockPrecedentClause(
			id="test_001",
			text="Test clause text",
			category="Test Category",
			risk_level="High",
			source_document="Test Document",
			effectiveness_score=0.8,
			created_at="2024-01-01T00:00:00Z",
		)

		mock_store.add_precedent_clause(clause)

		assert clause.id in mock_store.precedents
		assert mock_store.precedents[clause.id].text == "Test clause text"

	def test_add_precedent_clauses(self, mock_store):
		"""Test adding multiple precedent clauses."""
		clauses = [
			MockPrecedentClause(
				id="test_001",
				text="Test clause 1",
				category="Test Category",
				risk_level="High",
				source_document="Test Document",
				effectiveness_score=0.8,
				created_at="2024-01-01T00:00:00Z",
			),
			MockPrecedentClause(
				id="test_002",
				text="Test clause 2",
				category="Test Category",
				risk_level="Low",
				source_document="Test Document",
				effectiveness_score=0.9,
				created_at="2024-01-01T00:00:00Z",
			),
		]

		mock_store.add_precedent_clauses(clauses)

		assert len(mock_store.precedents) == 2
		assert "test_001" in mock_store.precedents
		assert "test_002" in mock_store.precedents

	def test_search_similar_clauses(self, mock_store, sample_precedents):
		"""Test searching for similar clauses."""
		# Add sample precedents
		for precedent_data in sample_precedents:
			clause = MockPrecedentClause(**precedent_data)
			mock_store.add_precedent_clause(clause)

		# Search for similar clauses
		results = mock_store.search_similar_clauses("liability damages")

		assert isinstance(results, list)
		assert len(results) <= 5  # Should respect n_results limit

	def test_search_similar_clauses_with_filters(self, mock_store, sample_precedents):
		"""Test searching with category and risk level filters."""
		# Add sample precedents
		for precedent_data in sample_precedents:
			clause = MockPrecedentClause(**precedent_data)
			mock_store.add_precedent_clause(clause)

		# Search with category filter
		results = mock_store.search_similar_clauses("liability", category_filter="Liability and Indemnification")

		assert isinstance(results, list)
		# All results should match the category filter
		for result in results:
			assert result.category == "Liability and Indemnification"

	def test_get_clause_by_id(self, mock_store):
		"""Test getting a clause by ID."""
		clause = MockPrecedentClause(
			id="test_001",
			text="Test clause text",
			category="Test Category",
			risk_level="High",
			source_document="Test Document",
			effectiveness_score=0.8,
			created_at="2024-01-01T00:00:00Z",
		)
		mock_store.add_precedent_clause(clause)

		retrieved = mock_store.get_clause_by_id("test_001")

		assert retrieved is not None
		assert retrieved.text == "Test clause text"

	def test_get_clause_by_id_not_found(self, mock_store):
		"""Test getting a non-existent clause by ID."""
		retrieved = mock_store.get_clause_by_id("non_existent")

		assert retrieved is None

	def test_get_all_clauses(self, mock_store, sample_precedents):
		"""Test getting all clauses."""
		# Add sample precedents
		for precedent_data in sample_precedents:
			clause = MockPrecedentClause(**precedent_data)
			mock_store.add_precedent_clause(clause)

		all_clauses = mock_store.get_all_clauses()

		assert len(all_clauses) == len(sample_precedents)

	def test_delete_clause(self, mock_store):
		"""Test deleting a clause."""
		clause = MockPrecedentClause(
			id="test_001",
			text="Test clause text",
			category="Test Category",
			risk_level="High",
			source_document="Test Document",
			effectiveness_score=0.8,
			created_at="2024-01-01T00:00:00Z",
		)
		mock_store.add_precedent_clause(clause)

		# Delete the clause
		result = mock_store.delete_clause("test_001")

		assert result is True
		assert "test_001" not in mock_store.precedents

	def test_delete_clause_not_found(self, mock_store):
		"""Test deleting a non-existent clause."""
		result = mock_store.delete_clause("non_existent")

		assert result is False

	def test_get_collection_stats(self, mock_store, sample_precedents):
		"""Test getting collection statistics."""
		# Add sample precedents
		for precedent_data in sample_precedents:
			clause = MockPrecedentClause(**precedent_data)
			mock_store.add_precedent_clause(clause)

		stats = mock_store.get_collection_stats()

		assert "total_clauses" in stats
		assert "categories" in stats
		assert "risk_levels" in stats
		assert stats["total_clauses"] == len(sample_precedents)

	def test_reset_collection(self, mock_store):
		"""Test resetting the collection."""
		clause = MockPrecedentClause(
			id="test_001",
			text="Test clause text",
			category="Test Category",
			risk_level="High",
			source_document="Test Document",
			effectiveness_score=0.8,
			created_at="2024-01-01T00:00:00Z",
		)
		mock_store.add_precedent_clause(clause)

		# Reset the collection
		mock_store.reset_collection()

		assert len(mock_store.precedents) == 0


class TestContractAnalysisService:
	"""Test cases for ContractAnalysisService."""

	@pytest.fixture
	def analysis_service(self):
		"""Create a ContractAnalysisService instance for testing."""
		with (
			patch("app.services.contract_analysis_service.DocumentProcessingService") as mock_doc_processor,
			patch("app.services.contract_analysis_service.ContractAnalysisWorkflow") as mock_workflow,
		):
			# Mock document processor
			mock_doc_processor.return_value.process_document.return_value = MagicMock(content="Test contract content", file_type="pdf")

			# Mock workflow
			mock_workflow.return_value.execute = AsyncMock()
			mock_workflow.return_value.execute.return_value = {
				"risky_clauses": [],
				"overall_risk_score": 5.0,
				"suggested_redlines": [],
				"email_draft": "Test email",
			}

			return ContractAnalysisService()

	@pytest.mark.asyncio
	async def test_analyze_contract_success(self, analysis_service, sample_contract_text):
		"""Test successful contract analysis."""
		result = await analysis_service.analyze_contract(file_content=sample_contract_text.encode(), filename="test_contract.pdf")

		assert result["status"] == "completed"
		assert "analysis_id" in result
		assert "risky_clauses" in result
		assert "overall_risk_score" in result

	@pytest.mark.asyncio
	async def test_analyze_contract_with_metadata(self, analysis_service, sample_contract_text):
		"""Test contract analysis with metadata."""
		metadata = {"client_id": "test_client", "priority": "high"}

		result = await analysis_service.analyze_contract(file_content=sample_contract_text.encode(), filename="test_contract.pdf", metadata=metadata)

		assert result["status"] == "completed"
		assert result["metadata"]["file_type"] == "pdf"

	@pytest.mark.asyncio
	async def test_analyze_contract_error(self, analysis_service):
		"""Test contract analysis with error."""
		with patch.object(analysis_service, "_process_document") as mock_process:
			mock_process.side_effect = Exception("Processing failed")

			with pytest.raises(Exception):
				await analysis_service.analyze_contract(file_content=b"test content", filename="test_contract.pdf")

	@pytest.mark.asyncio
	async def test_get_analysis_result(self, analysis_service):
		"""Test getting analysis result."""
		# Add a result to cache
		analysis_service._analysis_cache["test_123"] = {"test": "result"}

		result = await analysis_service.get_analysis_result("test_123")

		assert result == {"test": "result"}

	@pytest.mark.asyncio
	async def test_get_analysis_result_not_found(self, analysis_service):
		"""Test getting non-existent analysis result."""
		result = await analysis_service.get_analysis_result("non_existent")

		assert result is None

	@pytest.mark.asyncio
	async def test_list_analyses(self, analysis_service):
		"""Test listing analyses."""
		# Add some results to cache
		analysis_service._analysis_cache["test_1"] = {"analysis_id": "test_1", "created_at": "2024-01-01T00:00:00Z"}
		analysis_service._analysis_cache["test_2"] = {"analysis_id": "test_2", "created_at": "2024-01-02T00:00:00Z"}

		analyses = await analysis_service.list_analyses()

		assert len(analyses) == 2
		# Should be sorted by creation time (newest first)
		assert analyses[0]["analysis_id"] == "test_2"

	@pytest.mark.asyncio
	async def test_list_analyses_with_user_filter(self, analysis_service):
		"""Test listing analyses with user filter."""
		# Add results with different user IDs
		analysis_service._analysis_cache["test_1"] = {"analysis_id": "test_1", "user_id": "user_1", "created_at": "2024-01-01T00:00:00Z"}
		analysis_service._analysis_cache["test_2"] = {"analysis_id": "test_2", "user_id": "user_2", "created_at": "2024-01-02T00:00:00Z"}

		analyses = await analysis_service.list_analyses(user_id="user_1")

		assert len(analyses) == 1
		assert analyses[0]["analysis_id"] == "test_1"

	@pytest.mark.asyncio
	async def test_delete_analysis(self, analysis_service):
		"""Test deleting an analysis."""
		# Add a result to cache
		analysis_service._analysis_cache["test_123"] = {"analysis_id": "test_123", "user_id": "user_1"}

		result = await analysis_service.delete_analysis("test_123", "user_1")

		assert result is True
		assert "test_123" not in analysis_service._analysis_cache

	@pytest.mark.asyncio
	async def test_delete_analysis_wrong_user(self, analysis_service):
		"""Test deleting analysis with wrong user."""
		# Add a result to cache
		analysis_service._analysis_cache["test_123"] = {"analysis_id": "test_123", "user_id": "user_1"}

		result = await analysis_service.delete_analysis("test_123", "user_2")

		assert result is False
		assert "test_123" in analysis_service._analysis_cache

	def test_get_cache_stats(self, analysis_service):
		"""Test getting cache statistics."""
		# Add some results to cache
		analysis_service._analysis_cache["test_1"] = {"analysis_id": "test_1", "created_at": "2024-01-01T00:00:00Z"}
		analysis_service._analysis_cache["test_2"] = {"analysis_id": "test_2", "created_at": "2024-01-02T00:00:00Z"}

		stats = analysis_service.get_cache_stats()

		assert stats["total_analyses"] == 2
		assert "cache_size_mb" in stats
		assert "oldest_analysis" in stats
		assert "newest_analysis" in stats
