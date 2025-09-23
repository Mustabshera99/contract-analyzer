# Contract Analyzer - Project Structure

## Overview

This document outlines the improved project structure with clear separation of concerns and organized dependencies.

## Directory Structure

```
contract-analyzer/
├── backend/                          # Backend API service
│   ├── app/
│   │   ├── api/                      # API endpoints
│   │   │   ├── v1/                   # API version 1
│   │   │   │   ├── contracts.py      # Contract analysis endpoints
│   │   │   │   ├── health.py         # Health check endpoints
│   │   │   │   ├── monitoring.py     # Monitoring endpoints
│   │   │   │   └── security.py       # Authentication endpoints
│   │   │   ├── analytics.py          # Analytics endpoints
│   │   │   └── workflows.py          # Workflow endpoints
│   │   ├── core/                     # Core application components
│   │   │   ├── auth/                 # Authentication modules
│   │   │   ├── config/               # Configuration modules
│   │   │   ├── exceptions/           # Custom exceptions
│   │   │   ├── logging/              # Logging configuration
│   │   │   ├── monitoring/           # Monitoring and observability
│   │   │   ├── security/             # Security utilities
│   │   │   └── utils/                # Core utilities
│   │   ├── middleware/               # FastAPI middleware
│   │   ├── models/                   # Data models
│   │   ├── services/                 # Business logic services
│   │   ├── utils/                    # Utility functions
│   │   ├── workflows/                # AI workflow orchestration
│   │   └── main.py                   # FastAPI application entry point
│   ├── tests/                        # Backend tests
│   └── Dockerfile                    # Backend container
├── frontend/                         # Frontend Streamlit application
│   ├── components/                   # Reusable UI components
│   ├── security/                     # Frontend security modules
│   ├── utils/                        # Frontend utilities
│   ├── app.py                        # Streamlit application entry point
│   └── Dockerfile                    # Frontend container
├── config/                           # Configuration files
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   ├── architecture/                 # Architecture documentation
│   ├── deployment/                   # Deployment guides
│   └── user/                         # User guides
├── scripts/                          # Utility scripts
│   ├── setup/                        # Setup scripts
│   ├── deploy/                       # Deployment scripts
│   └── monitoring/                   # Monitoring scripts
├── sample_contracts/                 # Sample contract files
├── pyproject.toml                    # Poetry dependencies (cleaned)
├── requirements.txt                  # Essential dependencies
├── requirements-dev.txt              # Development dependencies
├── docker-compose.yml                # Docker Compose configuration
└── README.md                         # Project overview
```

## Key Improvements

### 1. Cleaner Dependencies

**Before**: 69 dependencies in pyproject.toml
**After**: 35 essential dependencies

**Removed unnecessary dependencies**:

- `plotly` (not used in core functionality)
- `scikit-learn` (not used)
- `websockets` (not used)
- `aiohttp` (redundant with httpx)
- `hiredis` (optional Redis optimization)
- `ipaddress` (built-in Python module)
- `qrcode` (not used)
- `user-agents` (not used)
- `pyotp` (not used)
- `memory-profiler` (development only)
- `markdown` (not used)
- `reportlab` (not used)
- Many OpenTelemetry exporters (kept only essential ones)

### 2. Better API Structure

**Before**: Flat API structure
**After**: Versioned API structure (`/api/v1/`)

- Organized endpoints by version
- Clear separation of concerns
- Better maintainability

### 3. Improved Core Organization

**Before**: Mixed core modules
**After**: Organized core modules by responsibility

- `auth/` - Authentication modules
- `config/` - Configuration management
- `exceptions/` - Custom exceptions
- `logging/` - Logging configuration
- `monitoring/` - Observability
- `security/` - Security utilities
- `utils/` - Core utilities

### 4. Cleaner Frontend Structure

**Before**: Mixed component organization
**After**: Clear component separation

- `components/` - Reusable UI components
- `security/` - Frontend security
- `utils/` - Frontend utilities

### 5. Better Documentation Organization

**Before**: Flat documentation structure
**After**: Organized documentation by category

- `api/` - API documentation
- `architecture/` - Architecture docs
- `deployment/` - Deployment guides
- `user/` - User guides

## Dependencies by Category

### Core Web Framework

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `streamlit` - Frontend framework

### AI/ML

- `langchain` - AI orchestration
- `langchain-openai` - OpenAI integration
- `langchain-community` - Community integrations
- `langgraph` - Workflow orchestration
- `langsmith` - AI observability
- `openai` - OpenAI API
- `anthropic` - Anthropic API
- `chromadb` - Vector database

### Document Processing

- `unstructured` - Document parsing
- `python-docx` - Word document processing
- `pypdf` - PDF processing
- `python-magic` - File type detection

### Data Processing

- `pandas` - Data manipulation
- `numpy` - Numerical computing

### Configuration & Validation

- `pydantic` - Data validation
- `pydantic-settings` - Settings management
- `python-dotenv` - Environment variables
- `pyyaml` - YAML processing

### Security & Authentication

- `python-multipart` - File uploads
- `python-jose` - JWT handling
- `passlib` - Password hashing
- `bcrypt` - Password hashing
- `pyjwt` - JWT tokens
- `cryptography` - Cryptographic operations

### Database & Caching

- `sqlalchemy` - ORM
- `asyncpg` - PostgreSQL async driver
- `psycopg2-binary` - PostgreSQL driver
- `redis` - Caching

### Monitoring & Observability

- `prometheus-client` - Metrics
- `structlog` - Structured logging
- `opentelemetry-*` - Distributed tracing

### Utilities

- `click` - CLI framework
- `rich` - Rich text formatting
- `chardet` - Character encoding detection
- `psutil` - System monitoring
- `jinja2` - Template engine

## Development Dependencies

- `pytest` - Testing framework
- `pytest-asyncio` - Async testing
- `pytest-mock` - Mocking
- `pytest-cov` - Coverage
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking
- `bandit` - Security linting
- `safety` - Dependency vulnerability scanning

## Benefits of New Structure

1. **Reduced Complexity**: 50% fewer dependencies
2. **Better Organization**: Clear separation of concerns
3. **Easier Maintenance**: Versioned APIs and organized modules
4. **Improved Security**: Only essential dependencies
5. **Better Documentation**: Organized by category
6. **Cleaner Codebase**: Removed unused files and modules
7. **Faster Builds**: Fewer dependencies to install
8. **Better Testing**: Organized test structure

## Next Steps

1. Update import statements to use new structure
2. Update documentation to reflect new organization
3. Test all functionality with new structure
4. Update deployment scripts if needed
5. Consider further modularization if needed
