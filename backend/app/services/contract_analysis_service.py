"""
Contract Analysis Service
Main service for contract analysis operations with AI integration.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..core.config import get_settings
from ..core.logging import get_logger
from ..core.monitoring import log_audit_event
from ..workflows.core import ContractAnalysisWorkflow
from .document_processor import DocumentProcessingService, ProcessedDocument

logger = get_logger(__name__)
settings = get_settings()


class ContractAnalysisService:
	"""Main service for contract analysis operations."""

	def __init__(self):
		self.document_processor = DocumentProcessingService()
		self.workflow = ContractAnalysisWorkflow()
		self._analysis_cache = {}

	async def analyze_contract(
		self,
		file_content: bytes,
		filename: str,
		analysis_type: str = "standard",
		user_id: Optional[str] = None,
		metadata: Optional[Dict[str, Any]] = None,
	) -> Dict[str, Any]:
		"""
		Analyze a contract document for risks and generate recommendations.

		Args:
		    file_content: Raw file content
		    filename: Name of the file
		    analysis_type: Type of analysis to perform
		    user_id: ID of the user requesting analysis
		    metadata: Additional metadata for analysis

		Returns:
		    Analysis results dictionary
		"""
		start_time = time.time()
		analysis_id = f"analysis_{int(time.time())}_{hash(filename) % 10000}"

		try:
			# Log analysis start
			log_audit_event(
				"contract_analysis_started",
				user_id=user_id,
				details={"analysis_id": analysis_id, "filename": filename, "analysis_type": analysis_type, "file_size": len(file_content)},
			)

			# Process document to extract text
			logger.info(f"Processing document: {filename}")
			processed_doc = await self._process_document(file_content, filename)

			if not processed_doc.content.strip():
				raise ValueError("No text content could be extracted from the document")

			# Execute analysis workflow
			logger.info(f"Executing analysis workflow for: {filename}")
			workflow_result = await self.workflow.execute(
				contract_text=processed_doc.content, contract_filename=filename, analysis_type=analysis_type, metadata=metadata or {}
			)

			# Calculate processing time
			processing_time = time.time() - start_time

			# Prepare response
			analysis_result = {
				"analysis_id": analysis_id,
				"status": "completed",
				"contract_filename": filename,
				"analysis_type": analysis_type,
				"risky_clauses": workflow_result.get("risky_clauses", []),
				"overall_risk_score": workflow_result.get("overall_risk_score", 0.0),
				"risk_level": self._determine_risk_level(workflow_result.get("overall_risk_score", 0.0)),
				"suggested_redlines": workflow_result.get("suggested_redlines", []),
				"email_draft": workflow_result.get("email_draft"),
				"recommendations": workflow_result.get("recommendations", []),
				"processing_time": processing_time,
				"confidence_score": workflow_result.get("confidence_score", 0.8),
				"model_used": workflow_result.get("model_used", "gpt-4"),
				"token_usage": workflow_result.get("token_usage", {}),
				"cost": workflow_result.get("cost", 0.0),
				"created_at": datetime.utcnow().isoformat(),
				"completed_at": datetime.utcnow().isoformat(),
				"metadata": {
					"file_type": processed_doc.file_type,
					"content_length": len(processed_doc.content),
					"processing_warnings": workflow_result.get("processing_metadata", {}).get("warnings", []),
				},
			}

			# Cache result
			self._analysis_cache[analysis_id] = analysis_result

			# Log successful completion
			log_audit_event(
				"contract_analysis_completed",
				user_id=user_id,
				details={
					"analysis_id": analysis_id,
					"processing_time": processing_time,
					"risky_clauses_count": len(analysis_result["risky_clauses"]),
					"risk_score": analysis_result["overall_risk_score"],
				},
			)

			logger.info(f"Analysis completed successfully: {analysis_id}")
			return analysis_result

		except Exception as e:
			processing_time = time.time() - start_time
			logger.error(f"Contract analysis failed: {e}", exc_info=True)

			# Log error
			log_audit_event(
				"contract_analysis_failed", user_id=user_id, details={"analysis_id": analysis_id, "error": str(e), "processing_time": processing_time}
			)

			raise

	async def _process_document(self, file_content: bytes, filename: str) -> ProcessedDocument:
		"""Process document to extract text content."""
		try:
			# Save to temporary file
			import os
			import tempfile

			with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}") as temp_file:
				temp_file.write(file_content)
				temp_file_path = temp_file.name

			try:
				# Process the document
				processed_doc = self.document_processor.process_document(temp_file_path, filename)
				return processed_doc
			finally:
				# Clean up temporary file
				if os.path.exists(temp_file_path):
					os.unlink(temp_file_path)

		except Exception as e:
			logger.error(f"Document processing failed: {e}")
			raise ValueError(f"Failed to process document: {e}")

	def _determine_risk_level(self, risk_score: float) -> str:
		"""Determine risk level based on score."""
		if risk_score >= 0.8:
			return "Critical"
		elif risk_score >= 0.6:
			return "High"
		elif risk_score >= 0.4:
			return "Medium"
		elif risk_score >= 0.2:
			return "Low"
		else:
			return "Minimal"

	async def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
		"""Get cached analysis result."""
		return self._analysis_cache.get(analysis_id)

	async def list_analyses(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
		"""List recent analyses."""
		analyses = list(self._analysis_cache.values())

		if user_id:
			# Filter by user if user_id is provided
			analyses = [a for a in analyses if a.get("user_id") == user_id]

		# Sort by creation time (newest first)
		analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)

		return analyses[:limit]

	async def delete_analysis(self, analysis_id: str, user_id: Optional[str] = None) -> bool:
		"""Delete an analysis result."""
		if analysis_id in self._analysis_cache:
			analysis = self._analysis_cache[analysis_id]

			# Check user permission if user_id is provided
			if user_id and analysis.get("user_id") != user_id:
				return False

			del self._analysis_cache[analysis_id]
			logger.info(f"Analysis deleted: {analysis_id}")
			return True

		return False

	def get_cache_stats(self) -> Dict[str, Any]:
		"""Get cache statistics."""
		return {
			"total_analyses": len(self._analysis_cache),
			"cache_size_mb": sum(len(str(analysis)) for analysis in self._analysis_cache.values()) / (1024 * 1024),
			"oldest_analysis": min((analysis.get("created_at", "") for analysis in self._analysis_cache.values()), default="None"),
			"newest_analysis": max((analysis.get("created_at", "") for analysis in self._analysis_cache.values()), default="None"),
		}


# Global instance
contract_analysis_service = ContractAnalysisService()


def get_contract_analysis_service() -> ContractAnalysisService:
	"""Get the global contract analysis service instance."""
	return contract_analysis_service
