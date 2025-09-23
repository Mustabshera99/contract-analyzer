"""
Logging configuration and utilities for the Contract Analyzer application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_settings


def setup_logging(log_level: Optional[str] = None, log_format: Optional[str] = None, log_file: Optional[str] = None, audit_log_file: Optional[str] = None) -> None:
	"""
	Set up application logging configuration.

	Args:
	    log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
	    log_format: Log message format string
	    log_file: Optional log file path
	    audit_log_file: Optional audit log file path
	"""
	settings = get_settings()
	level = log_level or settings.log_level
	format_str = log_format or settings.log_format

	# Configure root logger
	logging.basicConfig(
		level=getattr(logging, level.upper()),
		format=format_str,
		handlers=[
			logging.StreamHandler(sys.stdout),
		],
	)

	# Add file handler if specified
	if log_file:
		log_path = Path(log_file)
		log_path.parent.mkdir(parents=True, exist_ok=True)

		file_handler = logging.FileHandler(log_file)
		file_handler.setFormatter(logging.Formatter(format_str))
		logging.getLogger().addHandler(file_handler)

	# Add audit log handler if specified
	if audit_log_file:
		audit_log_path = Path(audit_log_file)
		audit_log_path.parent.mkdir(parents=True, exist_ok=True)

		audit_handler = logging.FileHandler(audit_log_file)
		audit_handler.setFormatter(logging.Formatter(format_str))
		audit_logger = logging.getLogger("audit")
		audit_logger.addHandler(audit_handler)
		audit_logger.setLevel(logging.INFO)

	# Set specific logger levels
	logging.getLogger("uvicorn").setLevel(logging.INFO)
	logging.getLogger("httpx").setLevel(logging.WARNING)
	logging.getLogger("chromadb").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
	"""
	Get a logger instance for the specified name.

	Args:
	    name: Logger name (typically __name__)

	Returns:
	    Configured logger instance
	"""
	return logging.getLogger(name)


class LoggerMixin:
	"""Mixin class to add logging capabilities to any class."""

	@property
	def logger(self) -> logging.Logger:
		"""Get logger instance for this class."""
		return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)
