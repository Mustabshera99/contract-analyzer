"""
API request and response models for contract analysis.
"""

import asyncio
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskyClause(BaseModel):
	"""Model for a risky clause identified in a contract."""

	clause_text: str = Field(..., description="The text of the risky clause")
	risk_explanation: str = Field(..., description="Explanation of why this clause is risky")
	risk_level: str = Field(..., description="Risk level: Low, Medium, or High")
	precedent_reference: Optional[str] = Field(None, description="Reference to relevant precedent")
	clause_index: int = Field(..., description="Index of the clause in the contract")

	@field_validator("risk_level")
	@classmethod
	def validate_risk_level(cls, v):
		if v not in ["Low", "Medium", "High"]:
			raise ValueError("Risk level must be Low, Medium, or High")
		return v


class RedlineSuggestion(BaseModel):
	"""Model for a suggested redline/alternative clause."""

	original_clause: str = Field(..., description="The original risky clause text")
	suggested_redline: str = Field(..., description="Suggested alternative language")
	risk_explanation: str = Field(..., description="Explanation of the risk being addressed")
	clause_index: int = Field(..., description="Index of the clause in the contract")
	change_rationale: str = Field("", description="Rationale for the suggested change")
	risk_mitigated: Optional[bool] = Field(None, description="Whether the risk is mitigated by the change")


class AnalysisResponse(BaseModel):
	"""Response model for contract analysis results."""

	model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

	risky_clauses: List[RiskyClause] = Field(default_factory=list, description="List of identified risky clauses")
	suggested_redlines: List[RedlineSuggestion] = Field(default_factory=list, description="List of suggested redlines")
	email_draft: str = Field("", description="Draft email for negotiation communication")
	processing_time: Optional[float] = Field(None, description="Time taken to process the contract in seconds")
	analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the analysis was completed")
	status: str = Field(..., description="Analysis status")
	overall_risk_score: Optional[float] = Field(None, description="Overall risk score for the contract")
	warnings: List[str] = Field(default_factory=list, description="Processing warnings")
	errors: List[str] = Field(default_factory=list, description="Processing errors")


class ProgressUpdate(BaseModel):
	"""Model for progress updates during analysis."""

	node: str = Field(..., description="Current workflow node")
	progress_percentage: float = Field(..., description="Progress percentage (0-100)")
	message: str = Field(..., description="Progress message")
	timestamp: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")
	estimated_remaining_seconds: Optional[int] = Field(None, description="Estimated remaining time")


class AnalysisStatusResponse(BaseModel):
	"""Response model for analysis status checks."""

	model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

	status: str = Field(..., description="Current analysis status")
	current_node: str = Field(..., description="Current workflow node")
	execution_id: str = Field(..., description="Unique execution identifier")
	error_count: int = Field(0, description="Number of errors encountered")
	warnings: List[str] = Field(default_factory=list, description="Processing warnings")
	last_error: Optional[str] = Field(None, description="Last error message")
	start_time: Optional[datetime] = Field(None, description="Analysis start time")
	end_time: Optional[datetime] = Field(None, description="Analysis end time")
	processing_duration: Optional[float] = Field(None, description="Processing duration in seconds")
	risky_clauses_count: int = Field(0, description="Number of risky clauses found")
	redlines_count: int = Field(0, description="Number of redlines generated")
	overall_risk_score: Optional[float] = Field(None, description="Overall risk score")
	contract_filename: str = Field("unknown", description="Contract filename")
	progress_updates: List[ProgressUpdate] = Field(default_factory=list, description="Progress tracking updates")
	resource_usage: Optional[dict] = Field(None, description="Resource usage metrics")


class AsyncAnalysisRequest(BaseModel):
	"""Request model for asynchronous analysis with comprehensive validation."""

	timeout_seconds: Optional[int] = Field(
		300,
		description="Timeout for analysis in seconds",
		ge=30,  # Minimum 30 seconds
		le=3600,  # Maximum 1 hour
	)
	priority: Optional[str] = Field("normal", description="Analysis priority: low, normal, high")
	callback_url: Optional[str] = Field(None, description="URL to call when analysis is complete")
	enable_progress_tracking: bool = Field(True, description="Enable real-time progress tracking")

	@field_validator("priority")
	@classmethod
	def validate_priority(cls, v):
		if v not in ["low", "normal", "high"]:
			raise ValueError("Priority must be one of: low, normal, high")
		return v

	@field_validator("callback_url")
	@classmethod
	def validate_callback_url(cls, v):
		if v is not None:
			import re

			# Basic URL validation
			url_pattern = re.compile(
				r"^https?://"  # http:// or https://
				r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
				r"localhost|"  # localhost...
				r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
				r"(?::\d+)?"  # optional port
				r"(?:/?|[/?]\S+)$",
				re.IGNORECASE,
			)

			if not url_pattern.match(v):
				raise ValueError("Invalid callback URL format. Must be a valid HTTP/HTTPS URL")

			# Security check - don't allow localhost/private IPs in production
			if any(host in v.lower() for host in ["localhost", "127.0.0.1", "0.0.0.0"]):
				import os

				if os.getenv("ENVIRONMENT", "development") == "production":
					raise ValueError("Localhost URLs not allowed in production")

		return v

	@field_validator("timeout_seconds")
	@classmethod
	def validate_timeout(cls, v):
		if v is not None:
			if v < 30:
				raise ValueError("Timeout must be at least 30 seconds")
			if v > 3600:
				raise ValueError("Timeout cannot exceed 1 hour (3600 seconds)")
		return v


class AsyncAnalysisResponse(BaseModel):
	"""Response model for asynchronous analysis initiation."""

	model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

	task_id: str = Field(..., description="Unique task identifier")
	status: str = Field(..., description="Initial task status")
	estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")
	status_url: str = Field(..., description="URL to check task status")


# Task management for async processing
class AnalysisTask:
	"""Internal task management for asynchronous analysis."""

	def __init__(self, task_id: str, contract_text: str, contract_filename: str, timeout_seconds: int = 60):
		self.task_id = task_id
		self.contract_text = contract_text
		self.contract_filename = contract_filename
		self.timeout_seconds = timeout_seconds
		self.status = "pending"
		self.result = None
		self.error = None
		self.start_time = datetime.utcnow()
		self.end_time = None
		self.future: Optional[asyncio.Future] = None

	def to_status_response(self) -> AnalysisStatusResponse:
		"""Convert task to status response."""
		processing_duration = None
		if self.end_time:
			processing_duration = (self.end_time - self.start_time).total_seconds()

		return AnalysisStatusResponse(
			status=self.status,
			current_node="task_manager",
			execution_id=self.task_id,
			error_count=1 if self.error else 0,
			warnings=[],
			last_error=self.error,
			start_time=self.start_time,
			end_time=self.end_time,
			processing_duration=processing_duration,
			risky_clauses_count=len(self.result.get("risky_clauses", [])) if self.result else 0,
			redlines_count=len(self.result.get("suggested_redlines", [])) if self.result else 0,
			overall_risk_score=self.result.get("overall_risk_score") if self.result else None,
			contract_filename=self.contract_filename,
		)


class ErrorResponse(BaseModel):
	"""Standard error response model."""

	model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

	error_type: str = Field(..., description="Type of error that occurred")
	message: str = Field(..., description="Human-readable error message")
	details: Optional[dict] = Field(None, description="Additional error details")
	timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the error occurred")
	request_id: Optional[str] = Field(None, description="Unique request identifier for tracking")


class SuccessResponse(BaseModel):
	"""Standard success response model."""

	model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

	message: str = Field(..., description="Success message")
	data: Optional[dict] = Field(None, description="Response data")
	timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the response was generated")
	request_id: Optional[str] = Field(None, description="Unique request identifier for tracking")


class HealthResponse(BaseModel):
	"""Health check response model."""

	model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

	status: str = Field(..., description="Service status")
	timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
	version: str = Field(..., description="API version")
	dependencies: dict = Field(default_factory=dict, description="Status of external dependencies")
