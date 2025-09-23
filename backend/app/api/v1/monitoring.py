"""
Monitoring Dashboard API
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ...core.audit_logger import get_audit_logger
from ...core.auth import get_current_user_or_api_key
from ...core.distributed_tracing import distributed_tracer
from ...core.health_checker import get_health_checker
from ...core.langsmith_integration import LangSmithMetrics, get_langsmith_health, get_langsmith_metrics_summary
from ...core.monitoring import (
	AlertSeverity,
	alert_manager,
	get_application_metrics,
	get_business_metrics,
	get_health_status,
	get_metrics_summary,
	get_system_metrics,
)
from ...core.performance_monitor import performance_monitor
from ...services.observability_service import get_observability_service

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/dashboard")
async def get_dashboard(current_user=Depends(get_current_user_or_api_key)):
	"""Get monitoring dashboard data"""
	try:
		# Get all monitoring data
		metrics = get_metrics_summary()
		health = get_health_status()
		system_metrics = get_system_metrics()
		app_metrics = get_application_metrics()
		business_metrics = get_business_metrics()

		# Get active alerts
		active_alerts = alert_manager.get_active_alerts()

		# Get recent traces
		recent_traces = []
		for span in distributed_tracer.completed_spans[-10:]:  # Last 10 spans
			recent_traces.append(span.to_dict())

		return {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"metrics": metrics,
			"health": health,
			"system": system_metrics,
			"application": app_metrics,
			"business": business_metrics,
			"alerts": {
				"active": len(active_alerts),
				"critical": len(alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL)),
				"high": len(alert_manager.get_alerts_by_severity(AlertSeverity.HIGH)),
				"medium": len(alert_manager.get_alerts_by_severity(AlertSeverity.MEDIUM)),
				"low": len(alert_manager.get_alerts_by_severity(AlertSeverity.LOW)),
			},
			"traces": recent_traces,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {e!s}")


@router.get("/metrics")
async def get_metrics(current_user=Depends(get_current_user_or_api_key)):
	"""Get detailed metrics"""
	try:
		return {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"summary": get_metrics_summary(),
			"system": get_system_metrics(),
			"application": get_application_metrics(),
			"business": get_business_metrics(),
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get metrics: {e!s}")


@router.get("/health")
async def get_health(current_user=Depends(get_current_user_or_api_key)):
	"""Get health status"""
	try:
		return get_health_status()
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get health status: {e!s}")


@router.get("/alerts")
async def get_alerts(
	severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
	status: Optional[str] = Query(None, description="Filter by status"),
	current_user=Depends(get_current_user_or_api_key),
):
	"""Get alerts"""
	try:
		alerts = alert_manager.active_alerts.values()

		if severity:
			alerts = [alert for alert in alerts if alert.severity == severity]

		if status:
			alerts = [alert for alert in alerts if alert.status.value == status]

		return {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"alerts": [
				{
					"id": alert.id,
					"rule_name": alert.rule_name,
					"severity": alert.severity.value,
					"message": alert.message,
					"timestamp": alert.timestamp.isoformat(),
					"status": alert.status.value,
					"acknowledged_by": alert.acknowledged_by,
					"acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
					"resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
				}
				for alert in alerts
			],
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get alerts: {e!s}")


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, current_user=Depends(get_current_user_or_api_key)):
	"""Acknowledge an alert"""
	try:
		alert_manager.acknowledge_alert(alert_id, current_user.get("username", "unknown"))
		return {"message": "Alert acknowledged successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {e!s}")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, current_user=Depends(get_current_user_or_api_key)):
	"""Resolve an alert"""
	try:
		alert_manager.resolve_alert(alert_id, current_user.get("username", "unknown"))
		return {"message": "Alert resolved successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {e!s}")


@router.get("/traces")
async def get_traces(
	trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
	limit: int = Query(50, description="Maximum number of traces to return"),
	current_user=Depends(get_current_user_or_api_key),
):
	"""Get distributed traces"""
	try:
		if trace_id:
			traces = distributed_tracer.get_trace(trace_id)
			return {"timestamp": datetime.now(timezone.utc).isoformat(), "trace": distributed_tracer.export_trace(trace_id)}
		else:
			# Get recent traces
			recent_spans = distributed_tracer.completed_spans[-limit:]
			traces = {}

			# Group by trace_id
			for span in recent_spans:
				if span.trace_id not in traces:
					traces[span.trace_id] = []
				traces[span.trace_id].append(span.to_dict())

			return {
				"timestamp": datetime.now(timezone.utc).isoformat(),
				"traces": [{"trace_id": trace_id, "spans": spans, "span_count": len(spans)} for trace_id, spans in traces.items()],
			}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get traces: {e!s}")


@router.get("/performance")
async def get_performance_metrics(current_user=Depends(get_current_user_or_api_key)):
	"""Get performance metrics"""
	try:
		active_spans = distributed_tracer.get_active_spans()

		return {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"active_traces": len(performance_monitor.active_traces),
			"active_spans": len(active_spans),
			"completed_spans": len(distributed_tracer.completed_spans),
			"spans": [span.to_dict() for span in active_spans],
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {e!s}")


@router.get("/audit-logs")
async def get_audit_logs(
	start_time: Optional[datetime] = Query(None, description="Start time for logs"),
	end_time: Optional[datetime] = Query(None, description="End time for logs"),
	event_type: Optional[str] = Query(None, description="Filter by event type"),
	user_id: Optional[str] = Query(None, description="Filter by user ID"),
	limit: int = Query(100, description="Maximum number of logs to return"),
	current_user=Depends(get_current_user_or_api_key),
):
	"""Get audit logs"""
	try:
		audit_logger = get_audit_logger()
		logs = audit_logger.get_logs(start_time=start_time, end_time=end_time, event_type=event_type, user_id=user_id, limit=limit)

		return {"timestamp": datetime.now(timezone.utc).isoformat(), "logs": logs, "count": len(logs)}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {e!s}")


@router.get("/system-info")
async def get_system_info(current_user=Depends(get_current_user_or_api_key)):
	"""Get system information"""
	try:
		health_checker = get_health_checker()

		return {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"system": {
				"python_version": health_checker.get_python_version(),
				"platform": health_checker.get_platform_info(),
				"memory": health_checker.get_memory_info(),
				"disk": health_checker.get_disk_info(),
				"network": health_checker.get_network_info(),
			},
			"application": {"version": "1.0.0", "environment": "production", "uptime": health_checker.get_uptime()},
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get system info: {e!s}")


@router.get("/langsmith/health")
async def get_langsmith_health_status(current_user=Depends(get_current_user_or_api_key)):
	"""Get LangSmith health status"""
	try:
		health = await get_langsmith_health()
		return {"timestamp": datetime.now(timezone.utc).isoformat(), "langsmith": health}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get LangSmith health: {e!s}")


@router.get("/langsmith/metrics")
async def get_langsmith_metrics(hours: int = Query(24, description="Time period in hours"), current_user=Depends(get_current_user_or_api_key)):
	"""Get LangSmith metrics"""
	try:
		metrics = LangSmithMetrics()

		performance = await metrics.get_performance_metrics(hours)
		errors = await metrics.get_error_analysis(hours)
		costs = await metrics.get_cost_analysis(hours)
		health = await get_langsmith_health()

		return {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"period_hours": hours,
			"health": health,
			"performance": performance,
			"errors": errors,
			"costs": costs,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get LangSmith metrics: {e!s}")


@router.get("/langsmith/summary")
async def get_langsmith_summary(current_user=Depends(get_current_user_or_api_key)):
	"""Get comprehensive LangSmith metrics summary"""
	try:
		summary = await get_langsmith_metrics_summary()
		return {"timestamp": datetime.now(timezone.utc).isoformat(), "langsmith": summary}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get LangSmith summary: {e!s}")


@router.get("/langsmith/runs")
async def get_langsmith_runs(
	hours: int = Query(24, description="Time period in hours"),
	limit: int = Query(100, description="Maximum number of runs to return"),
	current_user=Depends(get_current_user_or_api_key),
):
	"""Get recent LangSmith runs"""
	try:
		metrics = LangSmithMetrics()
		runs = await metrics.get_recent_runs(hours)

		# Limit results
		runs = runs[:limit]

		# Convert runs to dict format
		runs_data = []
		for run in runs:
			runs_data.append(
				{
					"id": str(run.id),
					"name": run.name,
					"run_type": run.run_type.value if run.run_type else "unknown",
					"status": "completed" if run.end_time else "running",
					"start_time": run.start_time.isoformat() if run.start_time else None,
					"end_time": run.end_time.isoformat() if run.end_time else None,
					"duration_seconds": (run.end_time - run.start_time).total_seconds() if run.start_time and run.end_time else None,
					"error": str(run.error) if run.error else None,
					"inputs": run.inputs if run.inputs else {},
					"outputs": run.outputs if run.outputs else {},
					"extra": run.extra if run.extra else {},
				}
			)

		return {"timestamp": datetime.now(timezone.utc).isoformat(), "period_hours": hours, "total_runs": len(runs_data), "runs": runs_data}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get LangSmith runs: {e!s}")


@router.get("/observability/summary")
async def get_observability_summary(current_user=Depends(get_current_user_or_api_key)):
	"""Get comprehensive observability summary"""
	try:
		observability_service = get_observability_service()
		summary = await observability_service.get_observability_summary()
		return summary
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get observability summary: {e!s}")


@router.get("/observability/health")
async def get_observability_health(current_user=Depends(get_current_user_or_api_key)):
	"""Get AI operations health status"""
	try:
		observability_service = get_observability_service()
		health = await observability_service.get_ai_operations_health()
		return health
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get observability health: {e!s}")


@router.get("/observability/performance")
async def get_observability_performance(
	hours: int = Query(24, description="Time period in hours"), current_user=Depends(get_current_user_or_api_key)
):
	"""Get comprehensive performance analysis"""
	try:
		observability_service = get_observability_service()
		performance = await observability_service.get_performance_analysis(hours)
		return performance
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get performance analysis: {e!s}")


@router.get("/observability/costs")
async def get_observability_costs(hours: int = Query(24, description="Time period in hours"), current_user=Depends(get_current_user_or_api_key)):
	"""Get comprehensive cost analysis"""
	try:
		observability_service = get_observability_service()
		costs = await observability_service.get_cost_analysis(hours)
		return costs
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get cost analysis: {e!s}")


@router.get("/observability/errors")
async def get_observability_errors(hours: int = Query(24, description="Time period in hours"), current_user=Depends(get_current_user_or_api_key)):
	"""Get comprehensive error analysis"""
	try:
		observability_service = get_observability_service()
		errors = await observability_service.get_error_analysis(hours)
		return errors
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get error analysis: {e!s}")


@router.get("/observability/metrics")
async def get_observability_metrics(hours: int = Query(24, description="Time period in hours"), current_user=Depends(get_current_user_or_api_key)):
	"""Get comprehensive metrics from all sources"""
	try:
		observability_service = get_observability_service()
		metrics = await observability_service.get_comprehensive_metrics(hours)
		return metrics
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get comprehensive metrics: {e!s}")
