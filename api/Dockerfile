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

WORKDIR /app

# Copy Python packages from builder stage to global location
COPY --from=builder /root/.local /opt/python-packages

# Copy application code
COPY . .

# Update PATH to include packages and ensure app dir is writable
ENV PATH=/opt/python-packages/bin:$PATH
ENV PYTHONPATH=/opt/python-packages/lib/python3.10/site-packages:$PYTHONPATH

# Make app directory writable for OpenShift arbitrary UID
RUN chmod -R g+rwX /app && chgrp -R 0 /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)" || exit 1

# Run application
CMD ["uvicorn", "api_to_db:app", "--host", "0.0.0.0", "--port", "8000"]