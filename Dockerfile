# =============================================================================
# Base Stage - Common dependencies for both dev and production
# =============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# Development Stage - Additional dev tools
# =============================================================================
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    django-debug-toolbar \
    ipython \
    ipdb \
    watchdog

# Copy project files
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs

# Expose port
EXPOSE 8000

# Default command for development (Django runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =============================================================================
# Production Stage - Optimized for production
# =============================================================================
FROM base AS production

# Copy project files
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command for production (Gunicorn)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
