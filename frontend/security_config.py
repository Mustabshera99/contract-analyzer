"""
Security configuration for the contract analyzer frontend.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SecurityConfig:
	"""Security configuration settings."""

	# File security settings
	max_file_size_mb: int = 50
	allowed_file_types: List[str] = None
	quarantine_suspicious_files: bool = True
	scan_file_content: bool = True

	# Input validation settings
	max_input_length: int = 10000
	enable_sql_injection_detection: bool = True
	enable_xss_detection: bool = True
	enable_command_injection_detection: bool = True
	enable_path_traversal_detection: bool = True

	# API security settings
	enable_rate_limiting: bool = True
	max_requests_per_minute: int = 60
	max_requests_per_hour: int = 1000
	require_api_key: bool = False
	enable_request_signing: bool = False

	# Audit logging settings
	enable_audit_logging: bool = True
	log_level: str = "INFO"
	log_retention_days: int = 30
	log_sensitive_data: bool = False

	# Memory management settings
	max_memory_mb: int = 500
	cleanup_interval_seconds: int = 300
	temp_file_ttl_hours: int = 24
	enable_secure_deletion: bool = True

	# Encryption settings
	enable_encryption: bool = True
	encryption_key_file: str = "security/encryption.key"

	# Security headers
	enable_security_headers: bool = True
	content_security_policy: str = "default-src 'self'"
	x_frame_options: str = "DENY"
	x_content_type_options: str = "nosniff"
	x_xss_protection: str = "1; mode=block"

	def __post_init__(self):
		"""Initialize default values after dataclass creation."""
		if self.allowed_file_types is None:
			self.allowed_file_types = ["pdf", "docx"]


def load_security_config() -> SecurityConfig:
	"""Load security configuration from environment variables."""
	config = SecurityConfig()

	# File security
	config.max_file_size_mb = int(os.getenv("SEC_MAX_FILE_SIZE_MB", "50"))
	config.allowed_file_types = os.getenv("SEC_ALLOWED_FILE_TYPES", "pdf,docx").split(",")
	config.quarantine_suspicious_files = os.getenv("SEC_QUARANTINE_FILES", "true").lower() == "true"
	config.scan_file_content = os.getenv("SEC_SCAN_CONTENT", "true").lower() == "true"

	# Input validation
	config.max_input_length = int(os.getenv("SEC_MAX_INPUT_LENGTH", "10000"))
	config.enable_sql_injection_detection = os.getenv("SEC_DETECT_SQL", "true").lower() == "true"
	config.enable_xss_detection = os.getenv("SEC_DETECT_XSS", "true").lower() == "true"
	config.enable_command_injection_detection = os.getenv("SEC_DETECT_CMD", "true").lower() == "true"
	config.enable_path_traversal_detection = os.getenv("SEC_DETECT_PATH", "true").lower() == "true"

	# API security
	config.enable_rate_limiting = os.getenv("SEC_RATE_LIMITING", "true").lower() == "true"
	config.max_requests_per_minute = int(os.getenv("SEC_RATE_LIMIT_MINUTE", "60"))
	config.max_requests_per_hour = int(os.getenv("SEC_RATE_LIMIT_HOUR", "1000"))
	config.require_api_key = os.getenv("SEC_REQUIRE_API_KEY", "false").lower() == "true"
	config.enable_request_signing = os.getenv("SEC_REQUEST_SIGNING", "false").lower() == "true"

	# Audit logging
	config.enable_audit_logging = os.getenv("SEC_AUDIT_LOGGING", "true").lower() == "true"
	config.log_level = os.getenv("SEC_LOG_LEVEL", "INFO")
	config.log_retention_days = int(os.getenv("SEC_LOG_RETENTION_DAYS", "30"))
	config.log_sensitive_data = os.getenv("SEC_LOG_SENSITIVE", "false").lower() == "true"

	# Memory management
	config.max_memory_mb = int(os.getenv("SEC_MAX_MEMORY_MB", "500"))
	config.cleanup_interval_seconds = int(os.getenv("SEC_CLEANUP_INTERVAL", "300"))
	config.temp_file_ttl_hours = int(os.getenv("SEC_TEMP_FILE_TTL", "24"))
	config.enable_secure_deletion = os.getenv("SEC_SECURE_DELETION", "true").lower() == "true"

	# Encryption
	config.enable_encryption = os.getenv("SEC_ENCRYPTION", "true").lower() == "true"
	config.encryption_key_file = os.getenv("SEC_ENCRYPTION_KEY_FILE", "security/encryption.key")

	# Security headers
	config.enable_security_headers = os.getenv("SEC_HEADERS", "true").lower() == "true"
	config.content_security_policy = os.getenv("SEC_CSP", "default-src 'self'")
	config.x_frame_options = os.getenv("SEC_X_FRAME_OPTIONS", "DENY")
	config.x_content_type_options = os.getenv("SEC_X_CONTENT_TYPE_OPTIONS", "nosniff")
	config.x_xss_protection = os.getenv("SEC_X_XSS_PROTECTION", "1; mode=block")

	return config


def validate_security_config(config: SecurityConfig) -> List[str]:
	"""Validate security configuration for potential issues."""
	issues = []

	# Check for insecure defaults
	if config.max_file_size_mb > 100:
		issues.append("File size limit is very high, consider reducing for security")

	if "*" in config.allowed_file_types:
		issues.append("Wildcard file types allowed, consider restricting to specific types")

	if not config.quarantine_suspicious_files:
		issues.append("File quarantine is disabled, suspicious files will not be isolated")

	if not config.scan_file_content:
		issues.append("File content scanning is disabled, malicious content may not be detected")

	if config.max_input_length > 50000:
		issues.append("Input length limit is very high, consider reducing to prevent DoS")

	if not config.enable_sql_injection_detection:
		issues.append("SQL injection detection is disabled")

	if not config.enable_xss_detection:
		issues.append("XSS detection is disabled")

	if not config.enable_command_injection_detection:
		issues.append("Command injection detection is disabled")

	if not config.enable_path_traversal_detection:
		issues.append("Path traversal detection is disabled")

	if not config.enable_rate_limiting:
		issues.append("Rate limiting is disabled, API may be vulnerable to DoS attacks")

	if config.max_requests_per_minute > 1000:
		issues.append("Rate limit is very high, consider reducing to prevent abuse")

	if not config.enable_audit_logging:
		issues.append("Audit logging is disabled, security monitoring will be limited")

	if config.log_retention_days < 7:
		issues.append("Log retention period is very short, consider increasing for compliance")

	if config.max_memory_mb > 2000:
		issues.append("Memory limit is very high, consider reducing to prevent resource exhaustion")

	if not config.enable_secure_deletion:
		issues.append("Secure deletion is disabled, sensitive data may persist on disk")

	if not config.enable_encryption:
		issues.append("Encryption is disabled, sensitive data may be stored in plain text")

	if not config.enable_security_headers:
		issues.append("Security headers are disabled, browser security features will not be enforced")

	return issues


def get_security_headers(config: SecurityConfig) -> Dict[str, str]:
	"""Get security headers based on configuration."""
	if not config.enable_security_headers:
		return {}

	headers = {
		"X-Frame-Options": config.x_frame_options,
		"X-Content-Type-Options": config.x_content_type_options,
		"X-XSS-Protection": config.x_xss_protection,
		"Content-Security-Policy": config.content_security_policy,
		"Referrer-Policy": "strict-origin-when-cross-origin",
		"Permissions-Policy": "geolocation=(), microphone=(), camera=()",
		"Strict-Transport-Security": "max-age=31536000; includeSubDomains",
	}

	return headers


def create_security_directories():
	"""Create necessary security directories."""
	directories = ["security", "logs/audit", "temp/secure", "quarantine"]

	for directory in directories:
		Path(directory).mkdir(parents=True, exist_ok=True)
		# Set restrictive permissions
		os.chmod(directory, 0o700)


# Global security configuration instance
security_config = load_security_config()
