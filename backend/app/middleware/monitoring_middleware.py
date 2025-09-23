"""
Monitoring middleware for request tracking and metrics collection.
Simplified version that works with the consolidated monitoring system.
"""

import time
import uuid
from typing import Any, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.config import get_settings
from ..core.monitoring import (
	monitor_performance,
	monitoring_system,
	record_metric,
)

# Global active connections counter
active_connections = 0


class MonitoringMiddleware(BaseHTTPMiddleware):
	"""Middleware for comprehensive request monitoring and tracing."""

	def __init__(self, app: ASGIApp):
		super().__init__(app)
		self.settings = get_settings()
		self.active_requests = 0
		self.request_count = 0
		self.error_count = 0

	async def dispatch(self, request: Request, call_next):
		"""Process incoming requests and collect metrics."""
		global active_connections

		# Generate correlation ID
		correlation_id = str(uuid.uuid4())

		# Increment active requests
		self.active_requests += 1
		active_connections = self.active_requests
		self.request_count += 1

		# Record active connections metric
		record_metric("active_connections", active_connections)

		# Start timing
		start_time = time.time()

		# Add correlation ID to request state
		request.state.correlation_id = correlation_id

		try:
			# Process request
			response = await call_next(request)

			# Calculate duration
			duration = time.time() - start_time

			# Record request metrics
			record_metric(
				"request_duration", duration, {"method": request.method, "endpoint": str(request.url.path), "status_code": str(response.status_code)}
			)

			record_metric(
				"requests_total", 1, {"method": request.method, "endpoint": str(request.url.path), "status_code": str(response.status_code)}
			)

			# Record success metrics
			if 200 <= response.status_code < 400:
				record_metric("requests_successful", 1)
			else:
				record_metric("requests_failed", 1)
				self.error_count += 1

			# Add correlation ID to response headers
			response.headers["X-Correlation-ID"] = correlation_id

			return response

		except Exception as e:
			# Calculate duration
			duration = time.time() - start_time

			# Record error metrics
			self.error_count += 1
			record_metric("requests_failed", 1, {"method": request.method, "endpoint": str(request.url.path), "error_type": type(e).__name__})

			record_metric("request_duration", duration, {"method": request.method, "endpoint": str(request.url.path), "status_code": "500"})

			# Return error response
			return JSONResponse(
				status_code=500,
				content={
					"error": "Internal server error",
					"correlation_id": correlation_id,
					"message": str(e) if self.settings.api_debug else "An error occurred",
				},
			)

		finally:
			# Decrement active requests
			self.active_requests -= 1
			active_connections = self.active_requests
			record_metric("active_connections", active_connections)


def create_monitoring_middleware():
	"""Create monitoring middleware factory."""

	def middleware_factory(app):
		return MonitoringMiddleware(app)

	return middleware_factory


def create_health_check_middleware():
	"""Create health check middleware factory."""

	def middleware_factory(app):
		return MonitoringMiddleware(app)

	return middleware_factory


def create_metrics_collection_middleware():
	"""Create metrics collection middleware factory."""

	def middleware_factory(app):
		return MonitoringMiddleware(app)

	return middleware_factory
