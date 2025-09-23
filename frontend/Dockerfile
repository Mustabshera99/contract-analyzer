# Multi-stage build for an optimized production image

# --- Builder Stage --- #
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Install system dependencies required for building packages
RUN apt-get update && apt-get install -y curl gcc

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - 
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# Install only production dependencies
RUN poetry install --only main --no-root


# --- Production Stage --- #
FROM python:3.11-slim as production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0
WORKDIR /app

# Create a non-root user with proper home directory
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the frontend application code
COPY --chown=appuser:appuser frontend/ /app/

# Switch to the non-root user
USER appuser

EXPOSE 8501

HEALTHCHECK CMD curl -f http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app.py"]