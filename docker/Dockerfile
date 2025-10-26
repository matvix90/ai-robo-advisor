# Multi-stage Dockerfile for AI Robo Advisor
# Use Python 3.11 as base (compatible with >=3.10 requirement)
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app:/app/src


# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# ===== DEPENDENCIES STAGE =====
FROM base AS dependencies

# Copy dependency files and source structure
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install dependencies (install and later remove build tools to minimize final image size)
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && \
    pip install --upgrade pip setuptools wheel && \
    pip install . && \
    apt-get purge -y --auto-remove gcc g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ===== DEVELOPMENT STAGE =====
FROM dependencies AS development

# Install development dependencies
RUN pip install -e ".[dev,test]"

# Copy additional development files
COPY tests/ ./tests/
COPY run_tests.sh ./

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose any ports if needed (none specified in current app)
# EXPOSE 8000

# Default command for development
CMD ["python", "-m", "main", "--help"]

# ===== PRODUCTION STAGE =====
FROM dependencies AS production

# Source code is already copied in dependencies stage
# Just need to set up the user and environment

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check (simple Python import test)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import main" || exit 1

# Default command for production
CMD ["python", "-m", "main"]

# ===== INTERACTIVE STAGE =====
FROM development AS interactive

# Install additional tools for interactive use
USER root
RUN apt-get update && apt-get install -y \
    curl \
    nano \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Set interactive environment
ENV TERM=xterm-256color

# Default to interactive shell
CMD ["/bin/bash"]