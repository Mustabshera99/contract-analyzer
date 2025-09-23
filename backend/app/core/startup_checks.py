"""
Startup validation and health checks for the Contract Analyzer application.
Performs comprehensive validation of configuration, dependencies, and system requirements.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import psutil
import redis
from chromadb import ClientAPI
from chromadb.config import Settings

from .config import settings
from .exceptions import ConfigurationError, DependencyError, ResourceError
from .logging import get_logger

logger = get_logger(__name__)


class StartupValidator:
    """Validates system configuration and dependencies during startup."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.start_time = time.time()
    
    async def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Perform all startup validations.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        logger.info("Starting comprehensive startup validation...")
        
        # Core validations
        await self._validate_environment()
        await self._validate_configuration()
        await self._validate_dependencies()
        await self._validate_resources()
        await self._validate_network()
        await self._validate_directories()
        await self._validate_security()
        
        # Performance validations
        await self._validate_performance()
        
        # Final validation
        is_valid = len(self.errors) == 0
        
        validation_time = time.time() - self.start_time
        logger.info(f"Startup validation completed in {validation_time:.2f}s")
        logger.info(f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
        
        return is_valid, self.errors, self.warnings
    
    async def _validate_environment(self) -> None:
        """Validate environment variables and system environment."""
        logger.debug("Validating environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.errors.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check required environment variables
        required_vars = [
            "OPENAI_API_KEY",
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Required environment variable {var} not set")
        
        # Check optional but recommended variables
        optional_vars = [
            "CHROMA_PERSIST_DIRECTORY",
            "REDIS_URL",
            "LANGSMITH_API_KEY",
        ]
        
        for var in optional_vars:
            if not os.getenv(var):
                self.warnings.append(f"Optional environment variable {var} not set")
        
        # Check environment type
        env = os.getenv("ENVIRONMENT", "development")
        if env not in ["development", "staging", "production"]:
            self.warnings.append(f"Unknown environment type: {env}")
    
    async def _validate_configuration(self) -> None:
        """Validate application configuration."""
        logger.debug("Validating configuration...")
        
        try:
            # Validate API configuration
            if settings.api_port < 1 or settings.api_port > 65535:
                self.errors.append(f"Invalid API port: {settings.api_port}")
            
            if settings.api_host not in ["0.0.0.0", "localhost", "127.0.0.1"]:
                self.warnings.append(f"Non-standard API host: {settings.api_host}")
            
            # Validate file processing configuration
            if settings.max_file_size_mb < 1 or settings.max_file_size_mb > 100:
                self.errors.append(f"Invalid max file size: {settings.max_file_size_mb}MB")
            
            if not settings.allowed_file_types:
                self.errors.append("No allowed file types configured")
            
            # Validate OpenAI configuration
            if not settings.openai_api_key:
                self.errors.append("OpenAI API key not configured")
            elif not settings.openai_api_key.startswith("sk-"):
                self.warnings.append("OpenAI API key format may be incorrect")
            
            # Validate model configuration
            if settings.openai_model not in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]:
                self.warnings.append(f"Uncommon OpenAI model: {settings.openai_model}")
            
            if settings.openai_temperature < 0 or settings.openai_temperature > 2:
                self.errors.append(f"Invalid OpenAI temperature: {settings.openai_temperature}")
            
            # Validate ChromaDB configuration
            if not settings.chroma_persist_directory:
                self.errors.append("ChromaDB persist directory not configured")
            
            # Validate CORS configuration
            if not settings.cors_origins:
                self.warnings.append("CORS origins not configured")
            
        except Exception as e:
            self.errors.append(f"Configuration validation failed: {e}")
    
    async def _validate_dependencies(self) -> None:
        """Validate external dependencies and services."""
        logger.debug("Validating dependencies...")
        
        # Validate Redis connection
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.from_url(redis_url, decode_responses=True)
            r.ping()
            logger.debug("Redis connection successful")
        except Exception as e:
            self.warnings.append(f"Redis connection failed: {e}")
        
        # Validate ChromaDB
        try:
            chroma_client = ClientAPI(Settings(
                persist_directory=settings.chroma_persist_directory,
                anonymized_telemetry=False
            ))
            # Test basic operations
            collections = chroma_client.list_collections()
            logger.debug(f"ChromaDB connection successful, {len(collections)} collections found")
        except Exception as e:
            self.warnings.append(f"ChromaDB connection failed: {e}")
        
        # Validate OpenAI API (basic check)
        try:
            import openai
            openai.api_key = settings.openai_api_key
            
            # Simple API test
            response = await asyncio.to_thread(
                openai.models.list
            )
            logger.debug("OpenAI API connection successful")
        except Exception as e:
            self.errors.append(f"OpenAI API connection failed: {e}")
        
        # Validate LangSmith (optional)
        if settings.langsmith_api_key:
            try:
                import langsmith
                # Basic validation
                logger.debug("LangSmith configuration found")
            except Exception as e:
                self.warnings.append(f"LangSmith configuration issue: {e}")
    
    async def _validate_resources(self) -> None:
        """Validate system resources and limits."""
        logger.debug("Validating system resources...")
        
        # Check available memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        if memory_gb < 2:
            self.errors.append(f"Insufficient memory: {memory_gb:.1f}GB (minimum 2GB required)")
        elif memory_gb < 4:
            self.warnings.append(f"Low memory: {memory_gb:.1f}GB (4GB+ recommended)")
        
        # Check available disk space
        disk = psutil.disk_usage('/')
        disk_gb = disk.free / (1024**3)
        
        if disk_gb < 5:
            self.errors.append(f"Insufficient disk space: {disk_gb:.1f}GB (minimum 5GB required)")
        elif disk_gb < 10:
            self.warnings.append(f"Low disk space: {disk_gb:.1f}GB (10GB+ recommended)")
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        if cpu_count < 2:
            self.warnings.append(f"Low CPU count: {cpu_count} cores (2+ recommended)")
        
        # Check if running in container
        if os.path.exists('/.dockerenv'):
            logger.debug("Running in Docker container")
        else:
            self.warnings.append("Not running in Docker container (recommended for production)")
    
    async def _validate_network(self) -> None:
        """Validate network connectivity and ports."""
        logger.debug("Validating network...")
        
        # Check if required ports are available
        required_ports = [settings.api_port]
        if hasattr(settings, 'metrics_port'):
            required_ports.append(settings.metrics_port)
        
        for port in required_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    self.errors.append(f"Port {port} is already in use")
            except Exception as e:
                self.warnings.append(f"Could not check port {port}: {e}")
        
        # Check external connectivity
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.openai.com/v1/models', timeout=5) as response:
                    if response.status == 200:
                        logger.debug("External connectivity to OpenAI successful")
                    else:
                        self.warnings.append(f"OpenAI API returned status {response.status}")
        except Exception as e:
            self.warnings.append(f"External connectivity check failed: {e}")
    
    async def _validate_directories(self) -> None:
        """Validate required directories and permissions."""
        logger.debug("Validating directories...")
        
        # Check ChromaDB directory
        chroma_dir = settings.chroma_persist_directory
        if not os.path.exists(chroma_dir):
            try:
                os.makedirs(chroma_dir, exist_ok=True)
                logger.debug(f"Created ChromaDB directory: {chroma_dir}")
            except Exception as e:
                self.errors.append(f"Cannot create ChromaDB directory {chroma_dir}: {e}")
        else:
            if not os.access(chroma_dir, os.W_OK):
                self.errors.append(f"No write permission for ChromaDB directory: {chroma_dir}")
        
        # Check log directory
        log_file = settings.log_file
        if log_file:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                    logger.debug(f"Created log directory: {log_dir}")
                except Exception as e:
                    self.warnings.append(f"Cannot create log directory {log_dir}: {e}")
        
        # Check temp directory
        temp_dir = "/tmp"
        if not os.access(temp_dir, os.W_OK):
            self.warnings.append(f"No write permission for temp directory: {temp_dir}")
    
    async def _validate_security(self) -> None:
        """Validate security configuration."""
        logger.debug("Validating security...")
        
        # Check for development settings in production
        if os.getenv("ENVIRONMENT") == "production":
            if settings.api_debug:
                self.errors.append("Debug mode enabled in production")
            
            if not settings.cors_origins or "*" in settings.cors_origins:
                self.warnings.append("CORS configured to allow all origins in production")
            
            if settings.log_level == "DEBUG":
                self.warnings.append("Debug logging enabled in production")
        
        # Check API key security
        if settings.openai_api_key:
            if len(settings.openai_api_key) < 20:
                self.warnings.append("OpenAI API key appears to be too short")
            
            if settings.openai_api_key in ["your_openai_api_key_here", "sk-test", "sk-demo"]:
                self.errors.append("Default or test OpenAI API key detected")
        
        # Check file upload security
        if settings.max_file_size_mb > 100:
            self.warnings.append(f"Large file size limit: {settings.max_file_size_mb}MB")
        
        # Check for sensitive data in logs
        sensitive_vars = ["API_KEY", "SECRET", "PASSWORD", "TOKEN"]
        for var in os.environ:
            if any(sensitive in var.upper() for sensitive in sensitive_vars):
                if os.getenv(var) and len(os.getenv(var)) > 10:
                    # Check if it's being logged
                    if var in str(settings.dict()):
                        self.warnings.append(f"Potentially sensitive variable {var} may be logged")
    
    async def _validate_performance(self) -> None:
        """Validate performance-related configuration."""
        logger.debug("Validating performance configuration...")
        
        # Check memory limits
        memory = psutil.virtual_memory()
        available_memory_gb = memory.available / (1024**3)
        
        # Estimate memory requirements
        estimated_requirements = 2.0  # Base requirements
        if settings.enable_monitoring:
            estimated_requirements += 0.5
        if settings.enable_prometheus:
            estimated_requirements += 0.3
        
        if available_memory_gb < estimated_requirements:
            self.warnings.append(
                f"Available memory ({available_memory_gb:.1f}GB) may be insufficient "
                f"for estimated requirements ({estimated_requirements:.1f}GB)"
            )
        
        # Check CPU performance
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            self.warnings.append(f"High CPU usage detected: {cpu_percent}%")
        
        # Check disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io and disk_io.read_time > 1000:  # High read time
            self.warnings.append("High disk I/O detected, may affect performance")
    
    def get_validation_report(self) -> Dict:
        """Get a detailed validation report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "validation_time": time.time() - self.start_time,
            "is_valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "cpu_count": psutil.cpu_count(),
                "disk_free_gb": psutil.disk_usage('/').free / (1024**3),
            },
            "configuration": {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "api_debug": settings.api_debug,
                "log_level": settings.log_level,
                "monitoring_enabled": settings.enable_monitoring,
            }
        }


async def run_startup_validation() -> Tuple[bool, List[str], List[str]]:
    """
    Run comprehensive startup validation.
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = StartupValidator()
    return await validator.validate_all()


def validate_configuration() -> None:
    """
    Validate configuration and raise exceptions for critical errors.
    This is a synchronous version for use in application startup.
    """
    logger.info("Validating configuration...")
    
    # Critical validations that must pass
    if not settings.openai_api_key:
        raise ConfigurationError("OpenAI API key is required")
    
    if not settings.chroma_persist_directory:
        raise ConfigurationError("ChromaDB persist directory is required")
    
    if settings.api_port < 1 or settings.api_port > 65535:
        raise ConfigurationError(f"Invalid API port: {settings.api_port}")
    
    if settings.max_file_size_mb < 1:
        raise ConfigurationError(f"Invalid max file size: {settings.max_file_size_mb}MB")
    
    # Check if running in production with debug enabled
    if os.getenv("ENVIRONMENT") == "production" and settings.api_debug:
        raise ConfigurationError("Debug mode cannot be enabled in production")
    
    logger.info("Configuration validation passed")


def check_system_requirements() -> None:
    """
    Check system requirements and raise exceptions for critical issues.
    """
    logger.info("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        raise DependencyError(f"Python 3.8+ required, found {sys.version}")
    
    # Check available memory
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024**3)
    
    if memory_gb < 2:
        raise ResourceError(f"Insufficient memory: {memory_gb:.1f}GB (minimum 2GB required)")
    
    # Check available disk space
    disk = psutil.disk_usage('/')
    disk_gb = disk.free / (1024**3)
    
    if disk_gb < 5:
        raise ResourceError(f"Insufficient disk space: {disk_gb:.1f}GB (minimum 5GB required)")
    
    logger.info("System requirements check passed")


def print_validation_report(report: Dict) -> None:
    """Print a formatted validation report."""
    print("\n" + "="*60)
    print("CONTRACT ANALYZER STARTUP VALIDATION REPORT")
    print("="*60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Validation Time: {report['validation_time']:.2f}s")
    print(f"Status: {'PASSED' if report['is_valid'] else 'FAILED'}")
    print(f"Errors: {report['error_count']}, Warnings: {report['warning_count']}")
    
    if report['errors']:
        print("\nERRORS:")
        for i, error in enumerate(report['errors'], 1):
            print(f"  {i}. {error}")
    
    if report['warnings']:
        print("\nWARNINGS:")
        for i, warning in enumerate(report['warnings'], 1):
            print(f"  {i}. {warning}")
    
    print("\nSYSTEM INFORMATION:")
    sys_info = report['system_info']
    print(f"  Python Version: {sys_info['python_version']}")
    print(f"  Platform: {sys_info['platform']}")
    print(f"  Memory: {sys_info['memory_gb']:.1f}GB")
    print(f"  CPU Cores: {sys_info['cpu_count']}")
    print(f"  Disk Free: {sys_info['disk_free_gb']:.1f}GB")
    
    print("\nCONFIGURATION:")
    config = report['configuration']
    print(f"  Environment: {config['environment']}")
    print(f"  Debug Mode: {config['api_debug']}")
    print(f"  Log Level: {config['log_level']}")
    print(f"  Monitoring: {config['monitoring_enabled']}")
    
    print("="*60)


if __name__ == "__main__":
    """Run startup validation as a standalone script."""
    import asyncio
    
    async def main():
        is_valid, errors, warnings = await run_startup_validation()
        
        validator = StartupValidator()
        report = validator.get_validation_report()
        print_validation_report(report)
        
        if not is_valid:
            print("\n❌ Startup validation FAILED")
            sys.exit(1)
        else:
            print("\n✅ Startup validation PASSED")
            if warnings:
                print("⚠️  Please review warnings above")
    
    asyncio.run(main())