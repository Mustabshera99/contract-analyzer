"""
Minimal monitoring system for testing.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
	"""Alert severity levels."""

	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"
	CRITICAL = "critical"


class AlertManager:
	"""Alert manager."""

	def __init__(self):
		self.alerts = []
		self.alert_rules = []

	def create_alert(self, message: str, severity: str = "low"):
		"""Create an alert."""
		self.alerts.append({"message": message, "severity": severity, "timestamp": "now"})


class MetricsCollector:
	"""Simple metrics collector for workflow tracing."""

	def __init__(self):
		self.traces = []

	def trace_workflow(self, workflow_name: str, execution_id: str, **kwargs):
		"""Context manager for tracing workflow execution."""

		class WorkflowTrace:
			def __init__(self, collector, workflow_name, execution_id, **kwargs):
				self.collector = collector
				self.workflow_name = workflow_name
				self.execution_id = execution_id
				self.kwargs = kwargs
				self.start_time = None

			async def __aenter__(self):
				self.start_time = datetime.utcnow()
				return self

			async def __aexit__(self, exc_type, exc_val, exc_tb):
				end_time = datetime.utcnow()
				duration = (end_time - self.start_time).total_seconds()
				self.collector.traces.append(
					{
						"workflow_name": self.workflow_name,
						"execution_id": self.execution_id,
						"start_time": self.start_time.isoformat(),
						"end_time": end_time.isoformat(),
						"duration": duration,
						"kwargs": self.kwargs,
					}
				)

		return WorkflowTrace(self, workflow_name, execution_id, **kwargs)


class MinimalMonitoringSystem:
	"""Minimal monitoring system."""

	def __init__(self):
		self.metrics = {}
		self.alert_manager = AlertManager()
		self.metrics_collector = MetricsCollector()

	def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
		"""Record a metric."""
		self.metrics[name] = {"value": value, "labels": labels or {}}

	def get_health_status(self) -> Dict[str, Any]:
		"""Get health status."""
		return {"status": "healthy"}


# Global instance
monitoring_system = MinimalMonitoringSystem()


# Convenience functions
def record_metric(name: str, value: float, labels: Dict[str, str] = None):
	"""Record a metric."""
	monitoring_system.record_metric(name, value, labels)


def get_health_status() -> Dict[str, Any]:
	"""Get health status."""
	return monitoring_system.get_health_status()


def log_audit_event(event_type: str, user_id: str = None, details: Dict[str, Any] = None, severity: str = "low"):
	"""Log audit event."""
	logger.info(f"AUDIT: {event_type}", extra={"user_id": user_id, "details": details, "severity": severity})


def monitor_performance(operation_name: str, component: str = "general"):
	"""Performance monitoring decorator."""

	def decorator(func):
		def wrapper(*args, **kwargs):
			logger.info(f"Performance monitoring - {operation_name}")
			return func(*args, **kwargs)

		return wrapper

	return decorator


def get_langsmith_health() -> Dict[str, Any]:
	"""Get LangSmith health status."""
	return {"status": "disabled", "message": "LangSmith not configured"}


def get_metrics_summary() -> Dict[str, Any]:
	"""Get metrics summary."""
	return {"total_metrics": len(monitoring_system.metrics), "metrics": monitoring_system.metrics}


def is_langsmith_enabled() -> bool:
	"""Check if LangSmith is enabled."""
	return False


def initialize_monitoring():
	"""Initialize monitoring system."""
	logger.info("Monitoring system initialized")


async def monitoring_background_task():
	"""Background monitoring task."""
	pass


def get_application_metrics() -> Dict[str, Any]:
	"""Get application metrics."""
	return {"requests_total": 0, "response_time_avg": 0.0}


def get_business_metrics() -> Dict[str, Any]:
	"""Get business metrics."""
	return {"contracts_analyzed": 0, "risk_score_avg": 0.0}


def get_system_metrics() -> Dict[str, Any]:
	"""Get system metrics."""
	return {"cpu_usage": 0.0, "memory_usage": 0.0, "disk_usage": 0.0}


class AlertSeverity(str, Enum):
	"""Alert severity levels."""

	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"
	CRITICAL = "critical"


class AlertManager:
	"""Alert manager."""

	def __init__(self):
		self.alerts = []
		self.alert_rules = []

	def create_alert(self, message: str, severity: str = "low"):
		"""Create an alert."""
		self.alerts.append({"message": message, "severity": severity, "timestamp": "now"})


alert_manager = AlertManager()


def get_prometheus_summary():
	"""Get Prometheus summary."""
	return {"total_requests": 0, "avg_response_time": 0.0}


# Export all functions
__all__ = [
	"AlertSeverity",
	"MetricsCollector",
	"alert_manager",
	"get_application_metrics",
	"get_business_metrics",
	"get_health_status",
	"get_langsmith_health",
	"get_metrics_summary",
	"get_prometheus_summary",
	"get_system_metrics",
	"initialize_monitoring",
	"is_langsmith_enabled",
	"log_audit_event",
	"monitor_performance",
	"monitoring_background_task",
	"monitoring_system",
	"record_metric",
]

# Create global metrics collector instance
metrics_collector = MetricsCollector()
