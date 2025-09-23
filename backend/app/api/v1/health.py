"""
Health check endpoints for monitoring and deployment verification.
"""

import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.logging import get_logger
from ..core.monitoring import get_langsmith_health, get_metrics_summary, is_langsmith_enabled
from ..models.api_models import HealthResponse

logger = get_logger(__name__)
router = APIRouter()

# Application start time for uptime calculation
app_start_time = datetime.utcnow()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
	"""
	Health check endpoint for monitoring and deployment verification.

	Returns:
	    HealthResponse: Current service status and dependency health
	"""
	logger.debug("Health check requested")

	# Check dependencies
	dependencies = {}

	# Check if required environment variables are set
	dependencies["openai_api_key"] = "configured" if settings.openai_api_key else "missing"
	dependencies["chroma_persist_dir"] = "configured" if settings.chroma_persist_directory else "missing"
	dependencies["langsmith"] = "configured" if is_langsmith_enabled() else "optional"
	dependencies["monitoring"] = "enabled" if settings.enable_monitoring else "disabled"

	# Determine overall status
	critical_deps = ["openai_api_key", "chroma_persist_dir"]
	critical_status = all(dependencies[dep] == "configured" for dep in critical_deps)
	status = "healthy" if critical_status else "degraded"

	return HealthResponse(status=status, version="0.1.0", dependencies=dependencies)


@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check() -> JSONResponse:
	"""
	Detailed health check endpoint with comprehensive system information.

	Returns:
	    JSONResponse: Detailed health information including metrics
	"""
	try:
		# Get basic health info
		basic_health = await health_check()

		# Get metrics summary
		metrics = get_metrics_summary()

		# Calculate uptime
		uptime_seconds = (datetime.utcnow() - app_start_time).total_seconds()

		# System information
		system_info = {
			"uptime_seconds": uptime_seconds,
			"uptime_human": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s",
			"timestamp": datetime.utcnow().isoformat(),
			"version": "0.1.0",
			"environment": "production" if not settings.api_debug else "development",
		}

		# Combine all information
		detailed_health = {
			"status": basic_health.status,
			"dependencies": basic_health.dependencies,
			"system": system_info,
			"metrics": metrics,
			"configuration": {
				"monitoring_enabled": settings.enable_monitoring,
				"prometheus_enabled": settings.enable_prometheus,
				"opentelemetry_enabled": settings.enable_opentelemetry,
				"langsmith_tracing": settings.langsmith_tracing,
				"debug_mode": settings.api_debug,
			},
		}

		return JSONResponse(content=detailed_health)

	except Exception as e:
		logger.error(f"Detailed health check failed: {e}")
		raise HTTPException(status_code=500, detail=f"Health check failed: {e!s}")


@router.get("/health/readiness", tags=["Health"])
async def readiness_check() -> JSONResponse:
	"""
	Readiness check for Kubernetes/container orchestration.

	Returns:
	    JSONResponse: Readiness status
	"""
	try:
		# Check critical dependencies
		critical_checks = {
			"openai_api_key": bool(settings.openai_api_key),
			"chroma_directory": bool(settings.chroma_persist_directory),
		}

		all_ready = all(critical_checks.values())

		response = {"ready": all_ready, "checks": critical_checks, "timestamp": datetime.utcnow().isoformat()}

		status_code = 200 if all_ready else 503
		return JSONResponse(content=response, status_code=status_code)

	except Exception as e:
		logger.error(f"Readiness check failed: {e}")
		return JSONResponse(content={"ready": False, "error": str(e), "timestamp": datetime.utcnow().isoformat()}, status_code=503)


@router.get("/health/liveness", tags=["Health"])
async def liveness_check() -> JSONResponse:
	"""
	Liveness check for Kubernetes/container orchestration.

	Returns:
	    JSONResponse: Liveness status
	"""
	try:
		# Simple liveness check - if we can respond, we're alive
		response = {"alive": True, "timestamp": datetime.utcnow().isoformat(), "uptime_seconds": (datetime.utcnow() - app_start_time).total_seconds()}

		return JSONResponse(content=response)

	except Exception as e:
		logger.error(f"Liveness check failed: {e}")
		return JSONResponse(content={"alive": False, "error": str(e), "timestamp": datetime.utcnow().isoformat()}, status_code=503)
