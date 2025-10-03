# Multi-stage build for optimized Streamlit image
# Stage 1: Builder - Install dependencies
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Minimal final image
FROM python:3.10-slim

# Create non-root user for security
RUN useradd -m -u 1000 streamlituser

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/streamlituser/.local

# Copy application code
COPY --chown=streamlituser:streamlituser . .

# Update PATH to include user-installed packages
ENV PATH=/home/streamlituser/.local/bin:$PATH

# Switch to non-root user
USER streamlituser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)" || exit 1

# Run application
CMD ["streamlit", "run", "dash.py", "--server.port=8501", "--server.enableCORS=false"]