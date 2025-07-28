# Multi-stage build for production optimization
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Add metadata
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="edunerve-content-quiz-service" \
      org.label-schema.description="EduNerve Content & Quiz Service" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/edunerve/backend" \
      org.label-schema.schema-version="1.0"

# Install system dependencies for building
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libmagic-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies only
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r edunerve && \
    useradd -r -g edunerve -d /app -s /bin/bash edunerve && \
    mkdir -p /app /var/log /tmp/uploads && \
    chown -R edunerve:edunerve /app /var/log /tmp/uploads

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=edunerve:edunerve app/ ./app/
COPY --chown=edunerve:edunerve .env.example ./.env

# Create necessary directories with proper permissions
RUN mkdir -p uploads logs cache && \
    chown -R edunerve:edunerve uploads logs cache && \
    chmod 755 uploads logs cache

# Switch to non-root user
USER edunerve

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8002 \
    HOST=0.0.0.0 \
    WORKERS=4

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Default command for development
CMD ["sh", "-c", "uvicorn app.main:app --host $HOST --port $PORT --workers $WORKERS --log-level info --access-log"]

# Production command (uncomment for production)
# CMD ["sh", "-c", "gunicorn app.main:app -w $WORKERS -k uvicorn.workers.UvicornWorker --bind $HOST:$PORT --log-level info --access-logfile -"]
