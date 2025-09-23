"""
FastAPI application factory and configuration with comprehensive security.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1 import contracts_router, health_router, monitoring_router, security_router
from .api import analytics, workflows
from .core.audit import AuditEventType, AuditSeverity, audit_logger
from .core.config import get_settings, setup_langsmith, validate_required_settings
from .core.exceptions import DocumentProcessingError, SecurityError, ValidationError
from .core.langsmith_integration import initialize_langsmith
from .core.logging import get_logger, setup_logging
from .core.monitoring import initialize_monitoring, monitoring_system
from .middleware.comprehensive_security import ComprehensiveSecurityMiddleware, SecurityHeadersMiddleware

# Enhanced rate limiting removed during cleanup
from .middleware.error_handler import error_handling_middleware
from .middleware.monitoring_middleware import (
	create_health_check_middleware,
	create_metrics_collection_middleware,
	create_monitoring_middleware,
)
from .models.api_models import ErrorResponse

logger = get_logger(__name__)


def create_app() -> FastAPI:
	"""Create and configure the FastAPI application with comprehensive security measures."""

	# Setup logging first
	setup_logging()

	# Validate required settings
	validate_required_settings()

	# Setup LangSmith if configured
	setup_langsmith()

	settings = get_settings()

	app = FastAPI(
		title="Contract Risk Analyzer API",
		description="AI-powered contract analysis and negotiation assistance with enterprise security",
		version="1.0.0",
		docs_url="/docs" if settings.api_debug else None,
		redoc_url="/redoc" if settings.api_debug else None,
	)

	# Add monitoring middleware first (for comprehensive tracking)
	if settings.enable_monitoring:
		app.add_middleware(create_monitoring_middleware())
		app.add_middleware(create_health_check_middleware())
		app.add_middleware(create_metrics_collection_middleware())

	# Enhanced rate limiting removed during cleanup

	# Add comprehensive security middleware (order matters!)
	app.add_middleware(ComprehensiveSecurityMiddleware)

	# Add security headers middleware as fallback
	app.add_middleware(SecurityHeadersMiddleware)

	# Add error handling middleware
	app.middleware("http")(error_handling_middleware)

	# Add CORS middleware with enhanced security
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.cors_origins.split(","),
		allow_credentials=True,
		allow_methods=["GET", "POST", "OPTIONS"],  # Restricted methods
		allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],  # Restricted headers
		expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"],
	)

	# Add security exception handlers
	@app.exception_handler(SecurityError)
	async def security_exception_handler(request: Request, exc: SecurityError) -> JSONResponse:
		"""Handle security errors."""
		logger.warning(f"Security error: {exc.message}")

		# Log security violation
		from .core.audit import audit_logger

		audit_logger.log_security_violation(violation_type="security_error", description=exc.message, request=request, severity="high")

		return JSONResponse(
			status_code=403,
			content=ErrorResponse(
				error="Security Error",
				message="Access denied due to security policy",
				suggestions=["Please ensure your request complies with security requirements"],
			).model_dump(),
		)

	@app.exception_handler(HTTPException)
	async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
		"""Handle HTTP exceptions with security logging."""
		# Log unauthorized access attempts
		if exc.status_code == 401:
			from .core.audit import audit_logger

			audit_logger.log_unauthorized_access(attempted_resource=str(request.url.path), reason="Invalid authentication", request=request)
		elif exc.status_code == 403:
			from .core.audit import audit_logger

			audit_logger.log_unauthorized_access(attempted_resource=str(request.url.path), reason="Insufficient permissions", request=request)
		elif exc.status_code == 429:
			from .core.audit import audit_logger

			audit_logger.log_rate_limit_exceeded(limit_type="http_rate_limit", request=request)

		return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

	# Include API routers
	# API v1 routes
	app.include_router(health_router, prefix="/api/v1")
	app.include_router(contracts_router, prefix="/api/v1")
	app.include_router(security_router, prefix="/api/v1/auth")
	app.include_router(monitoring_router)  # No prefix, already has /monitoring
	app.include_router(analytics.router, prefix="/api/v1")
	app.include_router(workflows.router, prefix="/api/v1")

	# Add startup event
	@app.on_event("startup")
	async def startup_event():
		logger.info("Contract Analyzer API starting up...")
		logger.info(f"API running on {settings.api_host}:{settings.api_port}")

		# Initialize security components
		from .core.env_manager import env_manager, env_validator

		# Validate environment security
		security_issues = env_validator.validate_security_config()
		if security_issues["critical"]:
			logger.error(f"Critical security issues detected: {security_issues['critical']}")
		if security_issues["warning"]:
			logger.warning(f"Security warnings: {security_issues['warning']}")

		audit_logger.log_event(
			event_type=AuditEventType.SYSTEM_START,
			action="Application startup",
			result="success",
			severity=AuditSeverity.MEDIUM,
			details={
				"version": "1.0.0",
				"security_enabled": True,
				"security_issues": len(security_issues["critical"]) + len(security_issues["warning"]),
			},
		)

		logger.info("Available endpoints:")
		logger.info("  - GET /api/v1/health - Health check")
		logger.info("  - GET /api/v1/health/detailed - Detailed health check")
		logger.info("  - GET /api/v1/health/readiness - Readiness check")
		logger.info("  - GET /api/v1/health/liveness - Liveness check")
		logger.info("  - POST /api/v1/analyze-contract - Contract analysis")

		# Enhanced monitoring endpoints
		if settings.enable_monitoring:
			logger.info("Enhanced monitoring endpoints:")
			logger.info("  - GET /monitoring/health - Basic health check")
			logger.info("  - GET /monitoring/health/detailed - Comprehensive health check")
			logger.info("  - GET /monitoring/health/live - Kubernetes liveness probe")
			logger.info("  - GET /monitoring/health/ready - Kubernetes readiness probe")
			logger.info("  - GET /monitoring/status - System status")
			logger.info("  - GET /monitoring/metrics - Application metrics")
			logger.info("  - GET /monitoring/metrics/prometheus - Prometheus metrics")
			logger.info("  - GET /monitoring/metrics/performance - Performance analysis")
			logger.info("  - GET /monitoring/alerts - Alert management")
			logger.info("  - GET /monitoring/langsmith/status - LangSmith integration status")
			logger.info("  - GET /monitoring/config - Monitoring configuration")

		if settings.api_debug:
			logger.info("  - GET /docs - API documentation")
			logger.info("  - GET /redoc - Alternative API documentation")

		# Initialize enhanced monitoring system
		if settings.enable_monitoring:
			initialize_monitoring()
			logger.info("Enhanced monitoring and observability initialized")
			logger.info(f"  - Prometheus metrics: {settings.enable_prometheus}")
			logger.info(f"  - OpenTelemetry tracing: {settings.enable_opentelemetry}")
			logger.info(f"  - LangSmith tracing: {settings.langsmith_tracing}")
			if settings.langsmith_tracing:
				logger.info(f"  - LangSmith project: {settings.langsmith_project}")
			logger.info(f"  - Structured logging: enabled")
			logger.info(f"  - Alert thresholds configured: {len(monitoring_system.alert_manager.alert_rules)} rules")

		# Initialize LangSmith integration
		if settings.langsmith_tracing:
			langsmith_success = initialize_langsmith()
			if langsmith_success:
				logger.info("LangSmith integration initialized successfully")
			else:
				logger.warning("LangSmith initialization failed - tracing will be disabled")

		# WebSocket monitoring removed during cleanup

		# Start enhanced monitoring background task
		import asyncio

		from .core.monitoring import monitoring_background_task

		asyncio.create_task(monitoring_background_task())

		# Initialize secure file handler
		from .core.file_handler import temp_file_handler

		logger.info("Secure file handler initialized")

		logger.info("Comprehensive security measures enabled:")
		logger.info("  - Advanced threat detection and analysis")
		logger.info("  - File upload validation and malware scanning")
		logger.info("  - Input sanitization and injection protection")
		logger.info("  - Rate limiting and IP blocking with honeypots")
		logger.info("  - Comprehensive audit logging and monitoring")
		logger.info("  - Secure temporary file management with encryption")
		logger.info("  - Content Security Policy and security headers")
		logger.info("  - API key management and authentication")
		logger.info("  - Memory management and cleanup")
		logger.info("  - Real-time security monitoring dashboard")

	# Add shutdown event
	@app.on_event("shutdown")
	async def shutdown_event():
		logger.info("Contract Analyzer API shutting down...")

		# WebSocket monitoring removed during cleanup

		# Clean up temporary files
		from .core.file_handler import temp_file_handler

		cleaned_files = temp_file_handler.cleanup_all()
		logger.info(f"Cleaned up {cleaned_files} temporary files")

		# Log shutdown
		audit_logger.log_event(
			event_type=AuditEventType.SYSTEM_SHUTDOWN,
			action="Application shutdown",
			result="success",
			severity=AuditSeverity.MEDIUM,
			details={"cleaned_files": cleaned_files},
		)

	return app


# Create the application instance
app = create_app()
