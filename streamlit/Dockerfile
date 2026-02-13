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
COPY download_models.py .
# permettre au builder d'accéder aux librairies
ENV PATH=/root/.local/bin:$PATH
# lancer le téléchargement
RUN python download_models.py

# Stage 2: Runtime - Minimal final image
FROM python:3.10-slim

WORKDIR /app

# Copy Python packages from builder stage to global location
COPY --from=builder /root/.local /opt/python-packages

# Récupérer les modèles téléchargés
COPY --from=builder /app/models_local /app/models_local

# Copy application code
COPY . .

# Update PATH to include packages
ENV PATH=/opt/python-packages/bin:$PATH
ENV PYTHONPATH=/opt/python-packages/lib/python3.10/site-packages:$PYTHONPATH

# Make directories writable for OpenShift arbitrary UID
RUN chmod -R g+rwX /app && chgrp -R 0 /app

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)" || exit 1

# Run application
CMD ["streamlit", "run", "dash.py", "--server.port=8501", "--server.enableCORS=false"]