"""
Configuration management for the Contract Analyzer application.
Handles environment variables and application settings.
"""

import os
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	"""Application settings loaded from environment variables."""

	model_config = {"extra": "ignore", "env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}

	# API Configuration
	api_host: str = Field(default="0.0.0.0", env="API_HOST")
	api_port: int = Field(default=8000, env="API_PORT")
	api_debug: bool = Field(default=False, env="API_DEBUG")

	# OpenAI Configuration
	openai_api_key: SecretStr = Field(..., env="OPENAI_API_KEY")
	openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
	openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")

	# Database Configuration
	database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

	# ChromaDB Configuration
	chroma_persist_directory: str = Field(default="./data/chroma", env="CHROMA_PERSIST_DIRECTORY")
	chroma_collection_name: str = Field(default="precedent_clauses", env="CHROMA_COLLECTION_NAME")

	# Redis Configuration
	enable_redis_caching: bool = Field(default=True, env="ENABLE_REDIS_CACHING")
	redis_host: str = Field(default="localhost", env="REDIS_HOST")
	redis_port: int = Field(default=6379, env="REDIS_PORT")
	redis_db: int = Field(default=0, env="REDIS_DB")
	redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
	redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
	redis_socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
	redis_socket_connect_timeout: int = Field(default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT")

	# LangSmith Configuration (Optional)
	langsmith_api_key: Optional[str] = Field(default=None, env="LANGSMITH_API_KEY")
	langsmith_project: str = Field(default="contract-analyzer", env="LANGSMITH_PROJECT")
	langsmith_tracing: bool = Field(default=False, env="LANGSMITH_TRACING")

	# Gmail Configuration
	gmail_client_id: Optional[str] = Field(default=None, env="GMAIL_CLIENT_ID")
	gmail_client_secret: Optional[str] = Field(default=None, env="GMAIL_CLIENT_SECRET")
	gmail_redirect_uri: Optional[str] = Field(default=None, env="GMAIL_REDIRECT_URI")
	gmail_scopes: str = Field(default="https://www.googleapis.com/auth/gmail.send", env="GMAIL_SCOPES")
	gmail_enabled: bool = Field(default=False, env="GMAIL_ENABLED")

	# Slack Configuration
	slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
	slack_bot_token: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
	slack_default_channel: str = Field(default="#contracts", env="SLACK_DEFAULT_CHANNEL")
	slack_enabled: bool = Field(default=False, env="SLACK_ENABLED")

	# DocuSign Configuration
	docusign_client_id: Optional[str] = Field(default=None, env="DOCUSIGN_CLIENT_ID")
	docusign_client_secret: Optional[str] = Field(default=None, env="DOCUSIGN_CLIENT_SECRET")
	docusign_redirect_uri: Optional[str] = Field(default=None, env="DOCUSIGN_REDIRECT_URI")
	docusign_scopes: list = Field(default=["signature", "impersonation"], env="DOCUSIGN_SCOPES")
	docusign_enabled: bool = Field(default=False, env="DOCUSIGN_ENABLED")

	# HubSpot Configuration
	hubspot_api_key: Optional[str] = Field(default=None, env="HUBSPOT_API_KEY")
	hubspot_enabled: bool = Field(default=False, env="HUBSPOT_ENABLED")

	# DocuSign Sandbox Configuration (for backward compatibility)
	docusign_sandbox_client_id: Optional[str] = Field(default=None, env="DOCUSIGN_SANDBOX_CLIENT_ID")
	docusign_sandbox_client_secret: Optional[str] = Field(default=None, env="DOCUSIGN_SANDBOX_CLIENT_SECRET")
	docusign_sandbox_redirect_uri: Optional[str] = Field(default=None, env="DOCUSIGN_SANDBOX_REDIRECT_URI")
	docusign_sandbox_scopes: str = Field(default="signature,impersonation", env="DOCUSIGN_SANDBOX_SCOPES")
	docusign_sandbox_base_url: str = Field(default="https://demo.docusign.net/restapi", env="DOCUSIGN_SANDBOX_BASE_URL")

	# Google Drive Configuration
	google_drive_enabled: bool = Field(default=False, env="GOOGLE_DRIVE_ENABLED")
	google_drive_client_id: Optional[str] = Field(default=None, env="GOOGLE_DRIVE_CLIENT_ID")
	google_drive_client_secret: Optional[str] = Field(default=None, env="GOOGLE_DRIVE_CLIENT_SECRET")
	google_drive_redirect_uri: Optional[str] = Field(default=None, env="GOOGLE_DRIVE_REDIRECT_URI")
	google_drive_scopes: str = Field(default="https://www.googleapis.com/auth/drive.file", env="GOOGLE_DRIVE_SCOPES")

	# SQLite Configuration
	sqlite_database_path: str = Field(default="./data/contract_analyzer.db", env="SQLITE_DATABASE_PATH")
	sqlite_enabled: bool = Field(default=True, env="SQLITE_ENABLED")

	# Monitoring Configuration
	enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
	enable_prometheus: bool = Field(default=True, env="ENABLE_PROMETHEUS")
	enable_opentelemetry: bool = Field(default=True, env="ENABLE_OPENTELEMETRY")
	metrics_port: int = Field(default=9090, env="METRICS_PORT")
	jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
	otlp_endpoint: Optional[str] = Field(default=None, env="OTLP_ENDPOINT")

	# File Processing Configuration
	max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
	allowed_file_types: list[str] = Field(default=["pdf", "docx", "txt"], env="ALLOWED_FILE_TYPES")
	temp_file_cleanup_hours: int = Field(default=24, env="TEMP_FILE_CLEANUP_HOURS")

	# Security Configuration
	cors_origins: str = Field(default="http://localhost:8501", env="CORS_ORIGINS")
	api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")

	# Enhanced Security Settings
	master_api_key: Optional[SecretStr] = Field(default=None, env="MASTER_API_KEY")
	client_api_keys: Optional[str] = Field(default=None, env="CLIENT_API_KEYS")
	jwt_secret_key: SecretStr = Field(default="your-secret-key-change-in-production", env="JWT_SECRET_KEY")
	jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
	jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")

	# Rate Limiting
	rate_limit_requests_per_minute: int = Field(default=100, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
	rate_limit_burst: int = Field(default=200, env="RATE_LIMIT_BURST")
	api_key_rate_limit_per_hour: int = Field(default=1000, env="API_KEY_RATE_LIMIT_PER_HOUR")

	# File Security
	max_file_size_bytes: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE_BYTES")  # 50MB
	allowed_mime_types: list[str] = Field(
		default=["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"], env="ALLOWED_MIME_TYPES"
	)
	scan_uploaded_files: bool = Field(default=True, env="SCAN_UPLOADED_FILES")
	quarantine_suspicious_files: bool = Field(default=True, env="QUARANTINE_SUSPICIOUS_FILES")

	# Input Validation
	max_input_length: int = Field(default=10000, env="MAX_INPUT_LENGTH")
	enable_input_sanitization: bool = Field(default=True, env="ENABLE_INPUT_SANITIZATION")
	strict_validation: bool = Field(default=True, env="STRICT_VALIDATION")

	# Audit and Monitoring
	enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
	audit_log_retention_days: int = Field(default=90, env="AUDIT_LOG_RETENTION_DAYS")
	security_alert_webhook: Optional[str] = Field(default=None, env="SECURITY_ALERT_WEBHOOK")
	audit_log_file: Optional[str] = Field(default="./logs/audit.log", env="AUDIT_LOG_FILE")
	security_log_file: Optional[str] = Field(default="./logs/security.log", env="SECURITY_LOG_FILE")

	# Session Security
	session_timeout_minutes: int = Field(default=30, env="SESSION_TIMEOUT_MINUTES")
	secure_cookies: bool = Field(default=True, env="SECURE_COOKIES")

	# Encryption
	encryption_key: Optional[SecretStr] = Field(default=None, env="ENCRYPTION_KEY")
	encrypt_temp_files: bool = Field(default=True, env="ENCRYPT_TEMP_FILES")

	# IP Security
	allowed_ip_ranges: Optional[str] = Field(default=None, env="ALLOWED_IP_RANGES")
	blocked_ip_addresses: Optional[str] = Field(default=None, env="BLOCKED_IP_ADDRESSES")

	# Content Security Policy
	enable_csp: bool = Field(default=True, env="ENABLE_CSP")
	csp_report_uri: Optional[str] = Field(default=None, env="CSP_REPORT_URI")

	# Logging Configuration
	log_level: str = Field(default="INFO", env="LOG_LEVEL")
	log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
	log_file: Optional[str] = Field(default="./logs/app.log", env="LOG_FILE")

	# Configuration moved to model_config above


# Global settings instance
_settings_instance: Optional["Settings"] = None


def get_settings() -> "Settings":
	"""Get the application settings instance (singleton)."""
	global _settings_instance
	if _settings_instance is None:
		_settings_instance = Settings()
	return _settings_instance


# Create settings instance
settings = get_settings()


def validate_required_settings() -> None:
	"""Validate that all required settings are present."""
	current_settings = get_settings()
	required_settings = [
		("OPENAI_API_KEY", current_settings.openai_api_key),
	]

	missing_settings = []
	for setting_name, setting_value in required_settings:
		if not setting_value:
			missing_settings.append(setting_name)

	if missing_settings:
		raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")


def setup_langsmith() -> None:
	"""Set up LangSmith tracing if configured."""
	current_settings = get_settings()
	if current_settings.langsmith_tracing and current_settings.langsmith_api_key:
		os.environ["LANGCHAIN_TRACING_V2"] = "true"
		os.environ["LANGCHAIN_API_KEY"] = current_settings.langsmith_api_key
		os.environ["LANGCHAIN_PROJECT"] = current_settings.langsmith_project
