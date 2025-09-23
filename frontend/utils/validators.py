"""
File validation utilities for the frontend.
"""

from dataclasses import dataclass
from typing import List, NamedTuple

from config import config


@dataclass
class ValidationResult:
	"""Result of file validation."""

	is_valid: bool
	error_message: str = ""


class FileValidator:
	"""Validates uploaded files for format and size constraints."""

	def __init__(self):
		self.allowed_extensions = [f".{ext}" for ext in config.ALLOWED_FILE_TYPES]
		self.max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024

	def validate_file(self, uploaded_file) -> ValidationResult:
		"""
		Validate an uploaded file.

		Args:
		    uploaded_file: Streamlit uploaded file object

		Returns:
		    ValidationResult: Validation result with success status and error message
		"""
		# Check if file exists
		if uploaded_file is None:
			return ValidationResult(False, "No file uploaded")

		# Check file name
		if not uploaded_file.name:
			return ValidationResult(False, "File name is required")

		# Check file extension
		file_extension = self._get_file_extension(uploaded_file.name)
		if file_extension not in self.allowed_extensions:
			allowed_str = ", ".join(config.ALLOWED_FILE_TYPES)
			return ValidationResult(False, f"Unsupported file format. Allowed formats: {allowed_str}")

		# Check file size
		if uploaded_file.size > self.max_size_bytes:
			max_size_mb = config.MAX_FILE_SIZE_MB
			actual_size_mb = uploaded_file.size / (1024 * 1024)
			return ValidationResult(False, f"File size ({actual_size_mb:.1f}MB) exceeds maximum limit of {max_size_mb}MB")

		# Check if file is empty
		if uploaded_file.size == 0:
			return ValidationResult(False, "Uploaded file is empty")

		return ValidationResult(True)

	def _get_file_extension(self, filename: str) -> str:
		"""Extract file extension from filename."""
		if "." not in filename:
			return ""
		return "." + filename.split(".")[-1].lower()

	def validate_file_content(self, file_content: bytes) -> ValidationResult:
		"""
		Validate file content for basic integrity checks.

		Args:
		    file_content: Raw file content as bytes

		Returns:
		    ValidationResult: Validation result
		"""
		if not file_content:
			return ValidationResult(False, "File content is empty")

		# Check for minimum content length (at least 100 bytes)
		if len(file_content) < 100:
			return ValidationResult(False, "File appears to be too small or corrupted")

		# Basic PDF validation (starts with %PDF)
		if file_content.startswith(b"%PDF"):
			return ValidationResult(True)

		# Basic DOCX validation (ZIP file with specific structure)
		if file_content.startswith(b"PK"):
			return ValidationResult(True)

		# If we can't determine the format, assume it's valid
		# (the backend will handle more detailed validation)
		return ValidationResult(True)
