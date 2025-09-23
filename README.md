# Contract Risk Analyzer

An AI-powered contract analysis and negotiation assistance platform with enterprise-grade security, built with a modern Python stack.

---

## ✨ Features

- **AI-Powered Analysis**: Identifies risky clauses, suggests redlines, and even drafts negotiation emails using models like GPT-4 and Claude.
- **Asynchronous Workflow**: Upload a contract and get a task ID to poll for results without tying up the frontend.
- **Enterprise-Grade Security**: Features secure file handling, input sanitization, audit logging, and JWT authentication.
- **Comprehensive Monitoring**: In-depth observability with structured logging, Prometheus metrics, and LangSmith tracing for AI operations.
- **Containerized**: Packaged with Docker and Docker Compose for easy, reproducible deployments.

## 🏗️ Architecture

This project uses a modern, decoupled architecture with clear separation of concerns and optimized dependencies.

| Component               | Technology                    |
| ----------------------- | ----------------------------- |
| **Backend**             | FastAPI, Uvicorn, Python 3.11 |
| **Frontend**            | Streamlit                     |
| **AI/ML Orchestration** | LangChain, LangGraph          |
| **Vector Store**        | ChromaDB                      |
| **Database**            | PostgreSQL                    |
| **Caching**             | Redis                         |
| **Dependency Mgmt**     | Poetry (35 essential deps)    |
| **Containerization**    | Docker, Docker Compose        |
| **API Versioning**      | REST API v1                   |

### Key Improvements

- **50% fewer dependencies** - Only essential packages included
- **Versioned API structure** - `/api/v1/` endpoints
- **Organized codebase** - Clear separation of concerns
- **Better documentation** - Categorized by type
- **Improved security** - Minimal attack surface

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose**
- **Poetry** (for local development)

### 1. Configuration

First, set up your environment variables. A template is provided in the `config/` directory.

```bash
# From the project root
cp config/env.template .env
```

Now, edit the `.env` file and fill in the required values, especially your `OPENAI_API_KEY` and secret keys.

### 2. Run with Docker Compose (Recommended)

This is the simplest way to get the entire application running.

```bash
# Build and start all services in the background
docker-compose up --build -d
```

Once the services are up, you can access:

- **Frontend UI**: [http://localhost:8501](http://localhost:8501)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the services:

```bash
docker-compose down
```

### 3. Local Development (Without Docker)

If you prefer to run the services directly on your machine:

```bash
# 1. Install all project dependencies
poetry install --with dev

# 2. Run the backend server (in one terminal)
poetry run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Run the frontend server (in another terminal)
poetry run streamlit run frontend/app.py
```

## 🧪 Testing

The project has a comprehensive test suite. To run the tests, first ensure you have installed the development dependencies (`poetry install --with dev`).

```bash
# Run all tests
poetry run pytest

# Run tests with coverage report
poetry run pytest --cov
```

## 📂 Project Structure

```
.
├── backend/         # FastAPI application, services, and core logic
├── frontend/        # Streamlit UI components and pages
├── config/          # Environment variable templates
├── docs/            # Project documentation
├── sample_contracts/  # Example contracts for testing
├── .github/         # CI/CD workflows (GitHub Actions)
├── docker-compose.yml # Docker orchestration
└── pyproject.toml   # Dependency management (Poetry)
```

## 🤖 CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration. The pipeline, defined in `.github/workflows/test.yml`, automatically runs the following checks on every push and pull request:

- **Unit & Integration Tests** across multiple Python versions.
- **Code Quality Checks** (linting, formatting) with Ruff/Black.
- **Static Type Checking** with MyPy.
- **Security Scans** with Bandit and Safety.
- **Docker Image Builds** to ensure containerization works correctly.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
