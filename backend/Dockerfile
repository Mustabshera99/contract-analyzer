FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NLTK_DATA=/app/data/nltk_data

# Install system dependencies
RUN apt-get update && apt-get install -y curl gcc libmagic1 libmagic-dev && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - 
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the backend application code
COPY backend/app /app/app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/nltk_data /app/logs && \
    chown -R root:root /app/data /app/logs

EXPOSE 8000

HEALTHCHECK CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]