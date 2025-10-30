# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash pulsar

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Configure poetry: Don't create virtual environment, install dependencies
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --only=main --no-dev

# Copy source code
COPY . .

# Change ownership to non-root user
RUN chown -R pulsar:pulsar /app

# Switch to non-root user
USER pulsar

# Create directories for user data
RUN mkdir -p /home/pulsar/.pulsar /home/pulsar/workflows

# Set environment variables for configuration
ENV PULSAR_CONFIG_FILE=/home/pulsar/.pulsar/config.toml \
    PULSAR_WORKFLOW_DIR=/home/pulsar/workflows

# Expose port for potential web interface (future feature)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["pulsar"]

# Default command
CMD ["--help"]