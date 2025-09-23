"""
Workflow Service for Contract Analysis
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
	PENDING = "pending"
	RUNNING = "running"
	COMPLETED = "completed"
	FAILED = "failed"
	TIMEOUT = "timeout"
	CANCELLED = "cancelled"


@dataclass
class AnalysisTask:
	task_id: str
	contract_text: str
	contract_filename: str
	status: TaskStatus
	start_time: datetime
	end_time: Optional[datetime] = None
	result: Optional[Dict[str, Any]] = None
	error: Optional[str] = None
	timeout_seconds: int = 300
	progress_updates: List[Dict[str, Any]] = None

	def __post_init__(self):
		if self.progress_updates is None:
			self.progress_updates = []


class WorkflowService:
	"""Service for managing contract analysis workflows."""

	def __init__(self):
		self.active_tasks: Dict[str, AnalysisTask] = {}
		self.max_concurrent_tasks = 10

	async def start_analysis(
		self,
		contract_text: str,
		contract_filename: str,
		timeout_seconds: int = 300,
		enable_progress: bool = True,
		resource_limits: Optional[Dict[str, Any]] = None,
	) -> str:
		"""Start a new analysis task."""
		task_id = str(uuid.uuid4())

		task = AnalysisTask(
			task_id=task_id,
			contract_text=contract_text,
			contract_filename=contract_filename,
			status=TaskStatus.PENDING,
			start_time=datetime.utcnow(),
			timeout_seconds=timeout_seconds,
		)

		self.active_tasks[task_id] = task

		# Start the analysis in background
		asyncio.create_task(self._execute_analysis(task))

		return task_id

	async def _execute_analysis(self, task: AnalysisTask) -> None:
		"""Execute the analysis task."""
		try:
			task.status = TaskStatus.RUNNING

			# Simulate analysis work
			await asyncio.sleep(2)  # Simulate processing time

			# Mock result
			task.result = {
				"risky_clauses": [
					{
						"clause_text": "The Company shall not be liable for any indirect damages.",
						"risk_explanation": "This clause limits liability too broadly and may not be enforceable.",
						"risk_level": "High",
						"precedent_reference": "Smith v. Company (2023)",
					}
				],
				"suggested_redlines": [
					{
						"original_clause": "The Company shall not be liable for any indirect damages.",
						"suggested_redline": "The Company shall not be liable for any indirect damages, except for those arising from gross negligence or willful misconduct.",
						"risk_explanation": "Added exception for gross negligence to make the clause more balanced and enforceable.",
					}
				],
				"email_draft": "Dear [Counterparty],\n\nI've reviewed the contract and identified several areas that need attention...",
				"processing_time": 2.0,
				"status": "completed",
			}

			task.status = TaskStatus.COMPLETED
			task.end_time = datetime.utcnow()

		except Exception as e:
			task.status = TaskStatus.FAILED
			task.error = str(e)
			task.end_time = datetime.utcnow()
			logger.error(f"Analysis task {task.task_id} failed: {e}")

	async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
		"""Get task status."""
		task = self.active_tasks.get(task_id)
		if not task:
			return None

		processing_duration = None
		if task.end_time:
			processing_duration = (task.end_time - task.start_time).total_seconds()
		elif task.status == TaskStatus.RUNNING:
			processing_duration = (datetime.utcnow() - task.start_time).total_seconds()

		return {
			"task_id": task.task_id,
			"status": task.status,
			"start_time": task.start_time.isoformat(),
			"end_time": task.end_time.isoformat() if task.end_time else None,
			"processing_duration": processing_duration,
			"progress_updates": task.progress_updates,
			"error": task.error,
		}

	async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
		"""Get task result."""
		task = self.active_tasks.get(task_id)
		if not task or task.status != TaskStatus.COMPLETED:
			return None
		return task.result

	async def get_active_tasks(self) -> List[Dict[str, Any]]:
		"""Get all active tasks."""
		active_tasks = []
		for task in self.active_tasks.values():
			if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
				status_info = await self.get_task_status(task.task_id)
				if status_info:
					active_tasks.append(status_info)
		return active_tasks

	async def cancel_task(self, task_id: str) -> bool:
		"""Cancel a task."""
		task = self.active_tasks.get(task_id)
		if not task or task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
			return False

		task.status = TaskStatus.CANCELLED
		task.end_time = datetime.utcnow()
		return True

	def get_service_metrics(self) -> Dict[str, Any]:
		"""Get service metrics."""
		total_tasks = len(self.active_tasks)
		completed_tasks = len([t for t in self.active_tasks.values() if t.status == TaskStatus.COMPLETED])
		failed_tasks = len([t for t in self.active_tasks.values() if t.status == TaskStatus.FAILED])
		running_tasks = len([t for t in self.active_tasks.values() if t.status == TaskStatus.RUNNING])

		return {
			"total_tasks": total_tasks,
			"completed_tasks": completed_tasks,
			"failed_tasks": failed_tasks,
			"running_tasks": running_tasks,
			"max_concurrent_tasks": self.max_concurrent_tasks,
		}


# Create global instance
workflow_service = WorkflowService()
