"""
Error handling utilities.
"""

from typing import List, Optional

from ..core.exceptions import ValidationError


def create_validation_error(
	message: str, field: Optional[str] = None, value: Optional[str] = None, suggestions: Optional[List[str]] = None
) -> ValidationError:
	"""Create a validation error with details."""
	return ValidationError(message=message, field=field, value=value, suggestions=suggestions or [])


class ErrorTracker:
	"""Simple error tracker for monitoring."""

	def __init__(self):
		self.errors = []

	def track_error(self, error: Exception, context: str = ""):
		"""Track an error."""
		self.errors.append({"error": str(error), "context": context, "timestamp": "now"})

	def get_errors(self):
		"""Get all tracked errors."""
		return self.errors


# Global error tracker instance
error_tracker = ErrorTracker()
