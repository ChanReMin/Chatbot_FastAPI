# ============================================
# Multi-stage Dockerfile for FastAPI + Uvicorn
# Optimized for Python 3.11-slim
# ============================================

# ============================================
# Stage 1: Build stage
# ============================================
# Purpose: Install all Python dependencies including:
# - SQLAlchemy (ORM for database)
# - psycopg2-binary (PostgreSQL driver)
# - pgvector (PostgreSQL vector extension support)
# ============================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies for building Python packages
# - gcc, g++: Compile Python C extensions
# - postgresql-client: psql command-line tool
# - libpq-dev: PostgreSQL C library headers (needed for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install ALL dependencies
# This includes SQLAlchemy, psycopg2-binary, pgvector, etc.
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime stage
# ============================================
# Purpose: Minimal runtime environment with only necessary libraries
# ============================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

WORKDIR /app

# Install runtime dependencies only
# - libpq5: PostgreSQL C library (runtime, smaller than libpq-dev)
#   Required for psycopg2 to connect to PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy ALL Python dependencies from builder stage
# This includes: SQLAlchemy, psycopg2-binary, pgvector, FastAPI, etc.
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user for security (optional but recommended)
# RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health-check')" || exit 1

# Run application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "1"]