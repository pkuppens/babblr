# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.12-slim AS builder

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
# Note: README.md is required by pyproject.toml
COPY pyproject.toml uv.lock README.md ./

# Install dependencies with uv (creates .venv)
# Note: Production builds should use --no-dev to exclude dev dependencies
RUN uv sync --frozen --no-dev

# ============================================
# Stage 2: Runtime - Minimal image
# ============================================
FROM python:3.12-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 babblr && \
    mkdir -p /app /data /cache && \
    chown -R babblr:babblr /app /data /cache

# Copy virtual environment from builder
COPY --from=builder --chown=babblr:babblr /app/.venv /app/.venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=babblr:babblr . .

# Switch to non-root user
USER babblr

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BABBLR_API_HOST=0.0.0.0 \
    BABBLR_API_PORT=8000 \
    BABBLR_AUDIO_STORAGE_PATH=/data/audio \
    WHISPER_MODEL=base

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
