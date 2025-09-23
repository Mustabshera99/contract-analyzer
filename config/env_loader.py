"""
Environment configuration loader for containerized deployment.
Handles loading and validation of environment variables.
"""

import os
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class EnvironmentConfig:
    """Environment configuration container."""
    
    # Application settings
    app_name: str = "Contract Risk Analyzer"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Backend API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    log_level: str = "INFO"
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:8501"])
    
    # Frontend configuration
    backend_url: str = "http://backend:8000"
    streamlit_port: int = 8501
    streamlit_address: str = "0.0.0.0"
    streamlit_headless: bool = True
    
    # Database configuration
    chroma_persist_directory: str = "/app/data/chroma"
    chroma_collection_name: str = "contract_embeddings"
    
    # AI/LLM configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 4000
    
    # LangSmith configuration
    langchain_tracing_v2: bool = False
    langchain_endpoint: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langchain_project: str = "contract-analyzer"
    
    # Security configuration
    security_level: str = "high"
    enable_rate_limiting: bool = True
    enable_audit_logging: bool = True
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = field(default_factory=lambda: ["pdf", "doc", "docx", "txt"])
    max_memory_mb: int = 1024
    
    # API Security
    api_key_secret: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Encryption
    encryption_key: Optional[str] = None
    
    # Redis configuration
    redis_url: str = "redis://redis:6379/0"
    redis_password: Optional[str] = None
    redis_max_connections: int = 20
    
    # Nginx configuration
    nginx_worker_processes: str = "auto"
    nginx_worker_connections: int = 1024
    nginx_client_max_body_size: str = "50M"
    
    # SSL configuration
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    # Monitoring and logging
    log_format: str = "json"
    log_file_path: str = "/app/logs"
    log_rotation_size: str = "10MB"
    log_retention_days: int = 30
    
    # Health check configuration
    health_check_interval: str = "30s"
    health_check_timeout: str = "10s"
    health_check_retries: int = 3
    
    # Development settings
    dev_mode: bool = False
    hot_reload: bool = False
    enable_debug_toolbar: bool = False
    
    # Testing
    test_database_url: str = "sqlite:///./test.db"
    test_redis_url: str = "redis://localhost:6379/1"
    
    # Production settings
    production_mode: bool = False
    enable_https: bool = False
    force_https: bool = False
    
    # Resource limits
    max_workers: int = 4
    worker_timeout: int = 300
    memory_limit: str = "2G"
    
    # Backup configuration
    backup_enabled: bool = False
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 7
    backup_storage_path: str = "/app/backups"
    
    # External services
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # File storage
    storage_type: str = "local"
    storage_path: str = "/app/storage"
    s3_bucket_name: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_region: str = "us-east-1"
    
    # Feature flags
    enable_websocket: bool = True
    enable_real_time_updates: bool = True
    enable_file_upload: bool = True
    enable_contract_analysis: bool = True
    enable_email_generation: bool = True
    enable_risk_assessment: bool = True


class EnvironmentLoader:
    """Loads and validates environment configuration."""
    
    def __init__(self, env_file_path: Optional[str] = None):
        """Initialize the environment loader."""
        self.env_file_path = env_file_path or ".env"
        self.logger = logging.getLogger(__name__)
        
    def load_environment(self) -> EnvironmentConfig:
        """Load environment configuration from file and environment variables."""
        # Load .env file if it exists
        if os.path.exists(self.env_file_path):
            load_dotenv(self.env_file_path)
            self.logger.info(f"Loaded environment from {self.env_file_path}")
        else:
            self.logger.warning(f"Environment file {self.env_file_path} not found, using system environment")
        
        # Create configuration from environment variables
        config = EnvironmentConfig()
        
        # Application settings
        config.app_name = os.getenv("APP_NAME", config.app_name)
        config.app_version = os.getenv("APP_VERSION", config.app_version)
        config.environment = os.getenv("ENVIRONMENT", config.environment)
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Backend API configuration
        config.api_host = os.getenv("API_HOST", config.api_host)
        config.api_port = int(os.getenv("API_PORT", str(config.api_port)))
        config.api_debug = os.getenv("API_DEBUG", "false").lower() == "true"
        config.log_level = os.getenv("LOG_LEVEL", config.log_level)
        config.cors_origins = os.getenv("CORS_ORIGINS", ",".join(config.cors_origins)).split(",")
        
        # Frontend configuration
        config.backend_url = os.getenv("BACKEND_URL", config.backend_url)
        config.streamlit_port = int(os.getenv("STREAMLIT_SERVER_PORT", str(config.streamlit_port)))
        config.streamlit_address = os.getenv("STREAMLIT_SERVER_ADDRESS", config.streamlit_address)
        config.streamlit_headless = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"
        
        # Database configuration
        config.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", config.chroma_persist_directory)
        config.chroma_collection_name = os.getenv("CHROMA_COLLECTION_NAME", config.chroma_collection_name)
        
        # AI/LLM configuration
        config.openai_api_key = os.getenv("OPENAI_API_KEY")
        config.openai_model = os.getenv("OPENAI_MODEL", config.openai_model)
        config.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", str(config.openai_temperature)))
        config.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", str(config.openai_max_tokens)))
        
        # LangSmith configuration
        config.langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        config.langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        config.langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        config.langchain_project = os.getenv("LANGCHAIN_PROJECT", config.langchain_project)
        
        # Security configuration
        config.security_level = os.getenv("SECURITY_LEVEL", config.security_level)
        config.enable_rate_limiting = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        config.enable_audit_logging = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
        config.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", str(config.max_file_size_mb)))
        config.allowed_file_types = os.getenv("ALLOWED_FILE_TYPES", ",".join(config.allowed_file_types)).split(",")
        config.max_memory_mb = int(os.getenv("MAX_MEMORY_MB", str(config.max_memory_mb)))
        
        # API Security
        config.api_key_secret = os.getenv("API_KEY_SECRET")
        config.jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        config.jwt_algorithm = os.getenv("JWT_ALGORITHM", config.jwt_algorithm)
        config.jwt_access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", str(config.jwt_access_token_expire_minutes)))
        
        # Encryption
        config.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # Redis configuration
        config.redis_url = os.getenv("REDIS_URL", config.redis_url)
        config.redis_password = os.getenv("REDIS_PASSWORD")
        config.redis_max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", str(config.redis_max_connections)))
        
        # Nginx configuration
        config.nginx_worker_processes = os.getenv("NGINX_WORKER_PROCESSES", config.nginx_worker_processes)
        config.nginx_worker_connections = int(os.getenv("NGINX_WORKER_CONNECTIONS", str(config.nginx_worker_connections)))
        config.nginx_client_max_body_size = os.getenv("NGINX_CLIENT_MAX_BODY_SIZE", config.nginx_client_max_body_size)
        
        # SSL configuration
        config.ssl_cert_path = os.getenv("SSL_CERT_PATH")
        config.ssl_key_path = os.getenv("SSL_KEY_PATH")
        
        # Monitoring and logging
        config.log_format = os.getenv("LOG_FORMAT", config.log_format)
        config.log_file_path = os.getenv("LOG_FILE_PATH", config.log_file_path)
        config.log_rotation_size = os.getenv("LOG_ROTATION_SIZE", config.log_rotation_size)
        config.log_retention_days = int(os.getenv("LOG_RETENTION_DAYS", str(config.log_retention_days)))
        
        # Health check configuration
        config.health_check_interval = os.getenv("HEALTH_CHECK_INTERVAL", config.health_check_interval)
        config.health_check_timeout = os.getenv("HEALTH_CHECK_TIMEOUT", config.health_check_timeout)
        config.health_check_retries = int(os.getenv("HEALTH_CHECK_RETRIES", str(config.health_check_retries)))
        
        # Development settings
        config.dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        config.hot_reload = os.getenv("HOT_RELOAD", "false").lower() == "true"
        config.enable_debug_toolbar = os.getenv("ENABLE_DEBUG_TOOLBAR", "false").lower() == "true"
        
        # Testing
        config.test_database_url = os.getenv("TEST_DATABASE_URL", config.test_database_url)
        config.test_redis_url = os.getenv("TEST_REDIS_URL", config.test_redis_url)
        
        # Production settings
        config.production_mode = os.getenv("PRODUCTION_MODE", "false").lower() == "true"
        config.enable_https = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
        config.force_https = os.getenv("FORCE_HTTPS", "false").lower() == "true"
        
        # Resource limits
        config.max_workers = int(os.getenv("MAX_WORKERS", str(config.max_workers)))
        config.worker_timeout = int(os.getenv("WORKER_TIMEOUT", str(config.worker_timeout)))
        config.memory_limit = os.getenv("MEMORY_LIMIT", config.memory_limit)
        
        # Backup configuration
        config.backup_enabled = os.getenv("BACKUP_ENABLED", "false").lower() == "true"
        config.backup_schedule = os.getenv("BACKUP_SCHEDULE", config.backup_schedule)
        config.backup_retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", str(config.backup_retention_days)))
        config.backup_storage_path = os.getenv("BACKUP_STORAGE_PATH", config.backup_storage_path)
        
        # External services
        config.smtp_host = os.getenv("SMTP_HOST")
        config.smtp_port = int(os.getenv("SMTP_PORT", str(config.smtp_port)))
        config.smtp_username = os.getenv("SMTP_USERNAME")
        config.smtp_password = os.getenv("SMTP_PASSWORD")
        config.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        
        # File storage
        config.storage_type = os.getenv("STORAGE_TYPE", config.storage_type)
        config.storage_path = os.getenv("STORAGE_PATH", config.storage_path)
        config.s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        config.s3_access_key = os.getenv("S3_ACCESS_KEY")
        config.s3_secret_key = os.getenv("S3_SECRET_KEY")
        config.s3_region = os.getenv("S3_REGION", config.s3_region)
        
        # Feature flags
        config.enable_websocket = os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"
        config.enable_real_time_updates = os.getenv("ENABLE_REAL_TIME_UPDATES", "true").lower() == "true"
        config.enable_file_upload = os.getenv("ENABLE_FILE_UPLOAD", "true").lower() == "true"
        config.enable_contract_analysis = os.getenv("ENABLE_CONTRACT_ANALYSIS", "true").lower() == "true"
        config.enable_email_generation = os.getenv("ENABLE_EMAIL_GENERATION", "true").lower() == "true"
        config.enable_risk_assessment = os.getenv("ENABLE_RISK_ASSESSMENT", "true").lower() == "true"
        
        return config
    
    def validate_config(self, config: EnvironmentConfig) -> List[str]:
        """Validate the configuration and return any errors."""
        errors = []
        
        # Required fields validation
        if not config.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if config.environment == "production":
            if not config.api_key_secret:
                errors.append("API_KEY_SECRET is required in production")
            if not config.jwt_secret_key:
                errors.append("JWT_SECRET_KEY is required in production")
            if not config.encryption_key:
                errors.append("ENCRYPTION_KEY is required in production")
        
        # Port validation
        if not (1 <= config.api_port <= 65535):
            errors.append(f"API_PORT must be between 1 and 65535, got {config.api_port}")
        
        if not (1 <= config.streamlit_port <= 65535):
            errors.append(f"STREAMLIT_SERVER_PORT must be between 1 and 65535, got {config.streamlit_port}")
        
        # File size validation
        if config.max_file_size_mb <= 0:
            errors.append(f"MAX_FILE_SIZE_MB must be positive, got {config.max_file_size_mb}")
        
        # Memory validation
        if config.max_memory_mb <= 0:
            errors.append(f"MAX_MEMORY_MB must be positive, got {config.max_memory_mb}")
        
        # SSL validation
        if config.enable_https:
            if not config.ssl_cert_path or not config.ssl_key_path:
                errors.append("SSL_CERT_PATH and SSL_KEY_PATH are required when ENABLE_HTTPS is true")
        
        return errors
    
    def create_env_file(self, config: EnvironmentConfig, output_path: str = ".env") -> None:
        """Create an .env file from the configuration."""
        env_content = []
        
        # Application settings
        env_content.append(f"APP_NAME={config.app_name}")
        env_content.append(f"APP_VERSION={config.app_version}")
        env_content.append(f"ENVIRONMENT={config.environment}")
        env_content.append(f"DEBUG={str(config.debug).lower()}")
        
        # Backend API configuration
        env_content.append(f"API_HOST={config.api_host}")
        env_content.append(f"API_PORT={config.api_port}")
        env_content.append(f"API_DEBUG={str(config.api_debug).lower()}")
        env_content.append(f"LOG_LEVEL={config.log_level}")
        env_content.append(f"CORS_ORIGINS={','.join(config.cors_origins)}")
        
        # Frontend configuration
        env_content.append(f"BACKEND_URL={config.backend_url}")
        env_content.append(f"STREAMLIT_SERVER_PORT={config.streamlit_port}")
        env_content.append(f"STREAMLIT_SERVER_ADDRESS={config.streamlit_address}")
        env_content.append(f"STREAMLIT_SERVER_HEADLESS={str(config.streamlit_headless).lower()}")
        
        # Database configuration
        env_content.append(f"CHROMA_PERSIST_DIRECTORY={config.chroma_persist_directory}")
        env_content.append(f"CHROMA_COLLECTION_NAME={config.chroma_collection_name}")
        
        # AI/LLM configuration
        if config.openai_api_key:
            env_content.append(f"OPENAI_API_KEY={config.openai_api_key}")
        env_content.append(f"OPENAI_MODEL={config.openai_model}")
        env_content.append(f"OPENAI_TEMPERATURE={config.openai_temperature}")
        env_content.append(f"OPENAI_MAX_TOKENS={config.openai_max_tokens}")
        
        # Security configuration
        env_content.append(f"SECURITY_LEVEL={config.security_level}")
        env_content.append(f"ENABLE_RATE_LIMITING={str(config.enable_rate_limiting).lower()}")
        env_content.append(f"ENABLE_AUDIT_LOGGING={str(config.enable_audit_logging).lower()}")
        env_content.append(f"MAX_FILE_SIZE_MB={config.max_file_size_mb}")
        env_content.append(f"ALLOWED_FILE_TYPES={','.join(config.allowed_file_types)}")
        env_content.append(f"MAX_MEMORY_MB={config.max_memory_mb}")
        
        # Write to file
        with open(output_path, "w") as f:
            f.write("\n".join(env_content))
        
        self.logger.info(f"Created environment file: {output_path}")


def load_environment_config(env_file_path: Optional[str] = None) -> EnvironmentConfig:
    """Load and validate environment configuration."""
    loader = EnvironmentLoader(env_file_path)
    config = loader.load_environment()
    
    # Validate configuration
    errors = loader.validate_config(config)
    if errors:
        error_msg = "Configuration validation errors:\n" + "\n".join(f"  - {error}" for error in errors)
        raise ValueError(error_msg)
    
    return config


# Global configuration instance
_config: Optional[EnvironmentConfig] = None


def get_config() -> EnvironmentConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_environment_config()
    return _config
