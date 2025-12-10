# Research Dashboard - Projet APP Recherche

A containerized research dashboard application built with MongoDB, FastAPI, and Streamlit, deployable with Docker Compose and Kubernetes.

## Project Structure

This repository contains the production-ready Research Dashboard application in `Dash_MONGODB/`.

## Quick Start

### Development (Docker Compose)

```bash
cd Dash_MONGODB
docker-compose up --build
```

Access the dashboard at `http://localhost:8501`

### Production (Kubernetes)

```bash
cd Dash_MONGODB/k8s
./deploy.sh
```

For multi-host access, the dashboard is available at `http://<any-node-ip>:30501`

## Documentation

Comprehensive documentation is available in the `Dash_MONGODB/k8s/` directory:

- **[Kubernetes Deployment Guide](Dash_MONGODB/k8s/README.md)** - Complete setup and operations guide
- **[Documentation Index](Dash_MONGODB/k8s/docs/README.md)** - All technical documentation
- **[Architecture Diagrams](Dash_MONGODB/k8s/docs/ARCHITECTURE.md)** - Visual system architecture
- **[Technical Deep-Dive](Dash_MONGODB/k8s/docs/DEPLOYMENT_EXPLAINED.md)** - Deployment mechanisms explained

## Version History

- **v1.1-multi-host** (Current) - Multi-host network access via NodePort
- **v1.0-localhost-only** - Initial localhost-only deployment

## Repository Branches

- `main` - Production application (Dash_MONGODB only)
- `backup-main` - Full project history and archived experiments

---

**Technology Stack**: MongoDB • FastAPI • Streamlit • Docker • Kubernetes
