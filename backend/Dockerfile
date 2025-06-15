FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Create a non-root user and install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        tzdata \
        gcc \
        libpq-dev \
        python3-dev && \
    # Set timezone to UTC
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /database /flask_session && \
    chown -R appuser:appuser /app /database /flask_session

# Switch to non-root user
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/api/health

# Use Gunicorn for production deployment
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 --access-logfile - --error-logfile - 'app:create_app()'"]
