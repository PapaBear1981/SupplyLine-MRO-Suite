FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    FLASK_ENV=production

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory and set permissions
WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache/pip

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /database /flask_session && \
    chown -R appuser:appuser /app /database /flask_session

# Set proper file permissions
RUN chmod -R 755 /app && \
    chmod -R 777 /database /flask_session

# Expose port
EXPOSE 5000

# Switch to non-root user
USER appuser

# Set secure umask
RUN echo "umask 027" >> ~/.bashrc

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
