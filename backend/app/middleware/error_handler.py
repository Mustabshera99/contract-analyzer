"""
Enhanced error handling middleware for the FastAPI application.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from ..core.exceptions import (
	AuthenticationError,
	AuthorizationError,
	ConfigurationError,
	ContractAnalysisError,
	DatabaseError,
	DocumentProcessingError,
	ErrorSeverity,
	ExternalServiceError,
	FileSizeError,
	InvalidFileTypeError,
	NetworkError,
	ResourceExhaustionError,
	ValidationError,
	WorkflowExecutionError,
)
from ..core.logging import get_logger
from ..utils.error_handler import error_tracker

logger = get_logger(__name__)


def get_status_code_for_error(error: Exception) -> int:
	"""
	Determine appropriate HTTP status code for an error.

	Args:
	    error: The exception that occurred

	Returns:
	    int: HTTP status code
	"""
	if isinstance(error, ValidationError):
		return status.HTTP_400_BAD_REQUEST
	elif isinstance(error, InvalidFileTypeError):
		return status.HTTP_400_BAD_REQUEST
	elif isinstance(error, FileSizeError):
		return status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
	elif isinstance(error, AuthenticationError):
		return status.HTTP_401_UNAUTHORIZED
	elif isinstance(error, AuthorizationError):
		return status.HTTP_403_FORBIDDEN
	elif isinstance(error, ResourceExhaustionError):
		return status.HTTP_429_TOO_MANY_REQUESTS
	elif isinstance(error, DocumentProcessingError):
		return status.HTTP_422_UNPROCESSABLE_ENTITY
	elif isinstance(error, WorkflowExecutionError):
		return status.HTTP_500_INTERNAL_SERVER_ERROR
	elif isinstance(error, ExternalServiceError):
		return status.HTTP_502_BAD_GATEWAY
	elif isinstance(error, NetworkError):
		return status.HTTP_503_SERVICE_UNAVAILABLE
	elif isinstance(error, DatabaseError):
		return status.HTTP_503_SERVICE_UNAVAILABLE
	elif isinstance(error, ConfigurationError):
		return status.HTTP_500_INTERNAL_SERVER_ERROR
	elif isinstance(error, ContractAnalysisError):
		# Use severity to determine status code
		if error.severity == ErrorSeverity.CRITICAL:
			return status.HTTP_500_INTERNAL_SERVER_ERROR
		elif error.severity == ErrorSeverity.HIGH:
			return status.HTTP_500_INTERNAL_SERVER_ERROR
		elif error.severity == ErrorSeverity.MEDIUM:
			return status.HTTP_422_UNPROCESSABLE_ENTITY
		else:
			return status.HTTP_400_BAD_REQUEST
	else:
		return status.HTTP_500_INTERNAL_SERVER_ERROR


def create_error_response(error: Exception, request_id: str, include_debug_info: bool = False) -> Dict[str, Any]:
	"""
	Create a standardized error response.

	Args:
	    error: The exception that occurred
	    request_id: Unique request identifier
	    include_debug_info: Whether to include debug information

	Returns:
	    Dict containing error response data
	"""
	timestamp = datetime.utcnow().isoformat()

	if isinstance(error, ContractAnalysisError):
		# Use structured error information
		response = {
			"error": {
				"code": error.error_code,
				"type": error.__class__.__name__,
				"message": error.user_message,
				"severity": error.severity.value,
				"category": error.category.value,
				"recovery_suggestions": error.recovery_suggestions,
				"details": {**error.details, "request_id": request_id, "timestamp": timestamp},
			}
		}

		if include_debug_info:
			response["error"]["debug"] = {"technical_message": error.message, "error_class": error.__class__.__name__}

	elif isinstance(error, PydanticValidationError):
		# Handle Pydantic validation errors
		response = {
			"error": {
				"code": "VALIDATION_PYDANTIC_VALIDATION_ERROR",
				"type": "ValidationError",
				"message": "Input validation failed. Please check your request data.",
				"severity": ErrorSeverity.LOW.value,
				"category": "validation",
				"recovery_suggestions": [
					"Check the request format and required fields",
					"Ensure all values meet the specified constraints",
					"Refer to the API documentation for correct format",
				],
				"details": {
					"validation_errors": [
						{"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"], "type": err["type"]} for err in error.errors()
					],
					"request_id": request_id,
					"timestamp": timestamp,
				},
			}
		}

	else:
		# Handle unexpected errors
		response = {
			"error": {
				"code": "SYSTEM_UNEXPECTED_ERROR",
				"type": "UnexpectedError",
				"message": "An unexpected error occurred. Please try again later.",
				"severity": ErrorSeverity.HIGH.value,
				"category": "system",
				"recovery_suggestions": [
					"Please try your request again",
					"If the problem persists, contact support",
					"Check if all required parameters are provided correctly",
				],
				"details": {"request_id": request_id, "timestamp": timestamp},
			}
		}

		if include_debug_info:
			response["error"]["debug"] = {"technical_message": str(error), "error_class": error.__class__.__name__}

	return response


async def error_handling_middleware(request: Request, call_next) -> Response:
	"""
	Enhanced middleware to handle errors and provide consistent error responses.

	Args:
	    request: The incoming request
	    call_next: The next middleware or route handler

	Returns:
	    Response: The response with error handling applied
	"""
	# Generate a unique request ID for tracking
	request_id = str(uuid.uuid4())
	request.state.request_id = request_id

	# Log request start
	logger.info(
		f"Request started: {request.method} {request.url}",
		extra={
			"request_id": request_id,
			"method": request.method,
			"url": str(request.url),
			"client_ip": request.client.host if request.client else None,
		},
	)

	try:
		response = await call_next(request)

		# Log successful request completion
		logger.info(
			f"Request completed successfully: {request_id}",
			extra={"request_id": request_id, "status_code": response.status_code, "response_time": getattr(request.state, "response_time", None)},
		)

		return response

	except PydanticValidationError as e:
		# Handle Pydantic validation errors
		error_id = error_tracker.record_error(e, {"request_id": request_id})

		logger.warning(f"Pydantic validation error in request {request_id}: {e}", extra={"request_id": request_id, "error_id": error_id})

		status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
		error_response = create_error_response(e, request_id)

		return JSONResponse(status_code=status_code, content=error_response)

	except ContractAnalysisError as e:
		# Handle application-specific errors
		error_id = error_tracker.record_error(e, {"request_id": request_id})

		# Log with appropriate level based on severity
		log_level = logging.ERROR
		if e.severity == ErrorSeverity.CRITICAL:
			log_level = logging.CRITICAL
		elif e.severity == ErrorSeverity.HIGH:
			log_level = logging.ERROR
		elif e.severity == ErrorSeverity.MEDIUM:
			log_level = logging.WARNING
		else:
			log_level = logging.INFO

		logger.log(
			log_level,
			f"{e.__class__.__name__} in request {request_id}: {e.message}",
			extra={
				"request_id": request_id,
				"error_id": error_id,
				"error_code": e.error_code,
				"severity": e.severity.value,
				"category": e.category.value,
			},
		)

		status_code = get_status_code_for_error(e)
		error_response = create_error_response(e, request_id)

		return JSONResponse(status_code=status_code, content=error_response)

	except Exception as e:
		# Handle unexpected errors
		error_id = error_tracker.record_error(e, {"request_id": request_id})

		logger.error(f"Unexpected error in request {request_id}: {e}", exc_info=True, extra={"request_id": request_id, "error_id": error_id})

		status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		error_response = create_error_response(e, request_id)

		return JSONResponse(status_code=status_code, content=error_response)
