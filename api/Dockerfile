# Multi-stage build for optimized API image
# Stage 1: Builder - Install dependencies
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Minimal final image
FROM python:3.10-slim

# Create non-root user for security
RUN useradd -m -u 1000 apiuser

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/apiuser/.local

# Copy application code
COPY --chown=apiuser:apiuser . .

# Update PATH to include user-installed packages
ENV PATH=/home/apiuser/.local/bin:$PATH

# Switch to non-root user
USER apiuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)" || exit 1

# Run application
CMD ["uvicorn", "api_to_db:app", "--host", "0.0.0.0", "--port", "8000"]