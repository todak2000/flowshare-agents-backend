# Production-grade Dockerfile with security best practices
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# COPY the shared directory FIRST
COPY shared/ ./shared/

# Install dependencies in a separate layer for better caching
# Fix the requirements path for Docker context (../shared -> shared)
COPY communicator-agent/requirements.txt .
RUN sed -i 's|../shared/requirements.txt|shared/requirements.txt|g' requirements.txt && \
    pip install --no-cache-dir --user -r requirements.txt


# Production image
FROM python:3.11-slim

# Install security updates and WeasyPrint dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        shared-mime-info && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code (entire directory structure)
COPY --chown=appuser:appuser shared/ ./shared/
COPY --chown=appuser:appuser communicator-agent/*.py ./
# Agent-specific modules (notifiers, routes, templates, and utils)
COPY --chown=appuser:appuser communicator-agent/notifiers/ ./notifiers/
COPY --chown=appuser:appuser communicator-agent/routes/ ./routes/
COPY --chown=appuser:appuser communicator-agent/templates/ ./templates/
COPY --chown=appuser:appuser communicator-agent/utils/ ./utils/
# Switch to non-root user
USER appuser

# Update PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Set environment variables
ENV PORT=8083 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health').read()" || exit 1

# Expose port
EXPOSE 8083

# Run application with security settings
CMD exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers 1 \
    --timeout-keep-alive 65 \
    --limit-concurrency 100 \
    --limit-max-requests 10000
