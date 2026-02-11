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
COPY streamlit/requirements.txt .

# ----------------------------------------------------------------------
# - Utilisation du cache BuildKit (--mount=type=cache) pour stocker les téléchargements pip.
# - Ajout de --extra-index-url pour trouver la version CPU de PyTorch.
# - Augmentation du timeout (--timeout 3000) pour les gros téléchargements.
# ----------------------------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    --verbose \
    --no-cache-dir \
    --user \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# Chargement des modèles
COPY streamlit/download_models.py .
# permettre au builder d'accéder aux librairies
ENV PATH=/root/.local/bin:$PATH
# lancer le téléchargement
RUN python download_models.py

# Stage 2: Runtime - Minimal final image
FROM python:3.10-slim

# Create non-root user for security
RUN useradd -m -u 1000 streamlituser

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/streamlituser/.local

# Récupérer les modèles téléchargés
COPY --from=builder --chown=streamlituser:streamlituser /app/models_local /app/models_local

# Copy MCP server code FIRST (depuis la racine du contexte)
COPY --chown=streamlituser:streamlituser mcp_server/ ./mcp_server/

# Copy application code (depuis streamlit/ vers /app)
COPY --chown=streamlituser:streamlituser streamlit/ ./

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