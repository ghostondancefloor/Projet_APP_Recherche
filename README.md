# Research Dashboard Application

A comprehensive research data management and visualization platform built with modern microservices architecture. This application provides authenticated access to research publications, institution data, and collaboration networks with AI-powered summarization capabilities.

## Overview

The Research Dashboard is a containerized application that aggregates and visualizes academic research data. It features:

- **Interactive Dashboard**: Streamlit-based frontend for data exploration and visualization
- **RESTful API**: FastAPI backend with JWT authentication
- **AI Summarization**: Automated research paper summarization using BART and T5 models
- **Data Clustering**: Machine learning-based publication clustering for topic discovery
- **Scalable Architecture**: Kubernetes-ready with horizontal pod autoscaling
- **Monitoring Stack**: Integrated Prometheus and Grafana for observability

## Architecture

The application consists of three primary services:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Streamlit  │─────▶│   FastAPI   │─────▶│   MongoDB   │
│  Frontend   │      │     API     │      │  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
```

### Components

**Streamlit Frontend** (Port 8501)
- User authentication interface
- Interactive data visualizations using Plotly
- Network graph generation with NetworkX
- AI-powered research presentation generation

**FastAPI Backend** (Port 8000)
- JWT-based authentication
- RESTful endpoints for data access
- Password hashing with bcrypt
- Prometheus metrics endpoint

**MongoDB Database** (Port 27017)
- Research data storage (publications, researchers, institutions)
- Pre-populated with sample data
- Automatic initialization on first run

**Monitoring Stack** (Optional)
- Prometheus: Metrics collection (Port 9090)
- Grafana: Visualization dashboards (Port 3000)
- MongoDB Exporter: Database metrics (Port 9216)

## Prerequisites

### For Docker Compose Deployment

- Docker Engine 20.10+
- Docker Compose 2.0+
- Minimum 8GB RAM available
- 10GB free disk space

### For Kubernetes Deployment

- Kubernetes 1.24+
- kubectl configured with cluster access
- Minimum cluster resources:
  - 2 CPU cores (requests)
  - 4GB RAM (requests)
  - 5GB storage for persistent volumes
- Recommended cluster resources:
  - 8 CPU cores (for resource limits)
  - 10GB RAM (for resource limits)
  - 10GB storage
- For local development: Docker Desktop with Kubernetes enabled

### For OpenShift Deployment

- OpenShift 4.10+ or OKD
- oc CLI tool installed
- Active OpenShift cluster access
- Container build capability enabled

---

## Quick Start

### Clone the Repository

```bash
git clone git@github.com:ghostondancefloor/Projet_APP_Recherche.git
cd Projet_APP_Recherche
```

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Development)

Docker Compose provides the fastest way to run the application locally with all services.

#### Step 1: Configure Environment

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# MongoDB Configuration
MONGO_PORT=27017
MONGO_INITDB_DATABASE=research_db_structure
MONGO_URI=mongodb://mongo:27017/research_db_structure

# API Configuration
API_PORT=8000
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Streamlit Configuration
STREAMLIT_PORT=8501
API_BASE_URL=http://api:8000

# Monitoring (Optional)
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=admin123
```

#### Step 2: Start Services

```bash
# Start all services (includes monitoring stack)
docker-compose up -d

# Or start only core services
docker-compose up -d mongo api streamlit
```

#### Step 3: Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Check MongoDB data initialization
docker-compose exec mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
```

#### Step 4: Access the Application

- Streamlit Dashboard: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Default Credentials:**
- Username: `admin`
- Password: `123` (change in production)

#### Stopping Services

```bash
# Stop services (preserves data)
docker-compose stop

# Stop and remove containers (preserves volumes)
docker-compose down

# Remove everything including data
docker-compose down -v
```

---

### Option 2: Kubernetes Deployment

Kubernetes deployment is suitable for production environments and multi-node clusters.

#### Prerequisites Check

```bash
# Verify Kubernetes cluster access
kubectl cluster-info

#### Prerequisites Check

```bash
# Verify Kubernetes cluster access
kubectl cluster-info

# Verify kubectl version
kubectl version --client

# Check available resources
kubectl top nodes
```

#### Quick Start (Automated Deployment)

The `deploy.sh` script handles everything automatically, including building images:

```bash
cd k8s
./deploy.sh
```

The script will:
1. Check Kubernetes cluster connectivity
2. Build Docker images using docker-compose
3. Create namespace and secrets
4. Create persistent volumes
5. Deploy MongoDB, API, and Streamlit
6. Wait for all pods to be ready

**Skip to Step 5 (Verify Deployment) if using the automated script.**

---

#### Manual Deployment (Step-by-Step)

If you prefer manual control or need to customize the deployment:

**Step 1: Build Container Images**

For local Kubernetes (Docker Desktop):

```bash
# Build all images
docker-compose build

# Verify images are available
docker images | grep projet_app_recherche
```

For remote Kubernetes clusters, push images to a container registry:

```bash
# Tag images
docker tag projet_app_recherche-mongo:latest your-registry/research-mongo:latest
docker tag projet_app_recherche-api:latest your-registry/research-api:latest
docker tag projet_app_recherche-streamlit:latest your-registry/research-streamlit:latest

# Push to registry
docker push your-registry/research-mongo:latest
docker push your-registry/research-api:latest
docker push your-registry/research-streamlit:latest
```

**Step 2: Update Image References (Remote Clusters Only)**

Edit the deployment files if using a remote registry:

```bash
# Update image references in k8s/*.yaml files
sed -i 's|projet_app_recherche-|your-registry/research-|g' k8s/*.yaml
sed -i 's|imagePullPolicy: Never|imagePullPolicy: Always|g' k8s/*.yaml
```

**Step 3: Configure Secrets (Optional)**

Edit `k8s/secrets.yaml` with your base64-encoded values:

```bash
# Generate base64 encoded secrets
echo -n "your-production-secret-key" | base64
echo -n "your-mongodb-password" | base64
```

Update the values in `k8s/secrets.yaml`.

**Step 4: Deploy Manifests**

```bash
# Apply in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/mongodb-pv.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/streamlit-deployment.yaml
```

---

#### Verify Deployment

After deployment (automated or manual), verify all components are running:

```bash
# Check all resources
kubectl get all -n research-dashboard

# Check pod status
kubectl get pods -n research-dashboard

# View pod logs
kubectl logs -n research-dashboard -l app=streamlit --tail=50

# Check persistent volumes
kubectl get pv,pvc -n research-dashboard
```

#### Access the Application

**For Docker Desktop Kubernetes:**

The application is accessible via NodePort at:
- Streamlit: http://localhost:30501
- Streamlit (network): http://YOUR_LOCAL_IP:30501

Get your local IP:
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'
```

**For Cloud Kubernetes:**

Get the LoadBalancer IP:
```bash
kubectl get svc streamlit-service -n research-dashboard
```

Access at: http://EXTERNAL-IP:8501

#### Monitoring Stack (Optional)

Deploy Prometheus and Grafana:

```bash
cd k8s/monitoring
./deploy-monitoring.sh
```

Access monitoring:
- Prometheus: http://localhost:30090
- Grafana: http://localhost:30300 (admin/admin)

#### Troubleshooting Kubernetes Deployment

**Pods not starting:**
```bash
kubectl describe pod POD_NAME -n research-dashboard
kubectl logs POD_NAME -n research-dashboard
```

**Image pull errors:**
```bash
# Verify image exists
docker images | grep research

# Check imagePullPolicy in deployment
kubectl get deployment -n research-dashboard -o yaml | grep imagePullPolicy
```

**PVC binding issues:**
```bash
kubectl get pv,pvc -n research-dashboard
kubectl describe pvc mongodb-pvc -n research-dashboard
```

**Service connectivity:**
```bash
# Test API from within cluster
kubectl run test-pod --rm -it --image=curlimages/curl -n research-dashboard -- sh
curl http://api-service:8000
```

---

### Option 3: OpenShift/OKD Deployment

OpenShift provides enterprise-grade container orchestration with built-in CI/CD.

#### Prerequisites

```bash
# Login to OpenShift cluster
oc login --token=YOUR_TOKEN --server=https://api.your-cluster.com:6443

# Verify login
oc whoami
oc project
```

#### Step 1: Deploy to OpenShift

The OpenShift manifests include BuildConfigs that automatically build images from the GitHub repository.

```bash
# Create secrets
oc apply -f k8s/secrets.yaml

# Create persistent storage
oc apply -f openshift/mongodb-pvc.yaml

# Create builds
oc apply -f openshift/builds.yaml

# Start builds
oc start-build mongodb
oc start-build api
oc start-build streamlit

# Monitor builds
oc get builds -w
```

#### Step 2: Deploy Applications

```bash
# Deploy services
oc apply -f openshift/mongodb.yaml
oc apply -f openshift/api.yaml
oc apply -f openshift/streamlit.yaml
```

#### Step 3: Access Application

```bash
# Get the route URL
oc get route streamlit -o jsonpath='{.spec.host}'
```

Access the application at the provided HTTPS URL.

#### Monitoring OpenShift Deployment

```bash
# Check pod status
oc get pods

# View logs
oc logs deployment/streamlit -f

# Check routes
oc get routes

# Check build logs
oc logs build/streamlit-1
```

---

## Project Structure

```
Projet_APP_Recherche/
├── README.md                          # Project documentation
├── docker-compose.yml                 # Docker Compose orchestration
├── mongo.Dockerfile                   # MongoDB container with auto-init
├── .env.example                       # Environment template
├── presentation.html                  # Project presentation page
│
├── api/                               # FastAPI backend
│   ├── api_to_db.py                  # Main API application
│   ├── Dockerfile                    # Multi-stage optimized build
│   └── requirements.txt              # Python dependencies
│
├── streamlit/                         # Frontend dashboard
│   ├── dash.py                       # Main dashboard app
│   ├── research_summarizer.py        # AI summarization engine
│   ├── download_models.py            # AI model downloader
│   ├── Dockerfile                    # Multi-stage build with AI models
│   └── requirements.txt              # Python + ML dependencies
│
├── mongo-dump/                        # Database initialization
│   ├── docker-entrypoint-wrapper.sh  # Auto-init script
│   └── research_db_structure/        # BSON backup files
│       ├── users.bson                # Authentication data
│       ├── chercheurs.bson          # Researcher profiles
│       ├── publications.bson        # Publication metadata
│       ├── institutions.bson        # Institution data
│       ├── collaborations.bson      # Collaboration networks
│       └── stats_pays.bson          # Country statistics
│
├── k8s/                               # Kubernetes manifests
│   ├── README.md                     # Kubernetes deployment guide
│   ├── deploy.sh                     # Automated deployment script
│   ├── namespace.yaml                # Namespace definition
│   ├── secrets.yaml                  # Sensitive configuration
│   ├── mongodb-pv.yaml               # Persistent volume
│   ├── mongodb-deployment.yaml       # MongoDB StatefulSet
│   ├── api-deployment.yaml           # API Deployment + Service
│   ├── streamlit-deployment.yaml     # Streamlit Deployment + Service
│   ├── docs/                         # Detailed documentation
│   │   ├── ARCHITECTURE.md          # Architecture diagrams
│   │   ├── DEPLOYMENT_EXPLAINED.md  # Technical deep-dive
│   │   └── README.md                # Documentation index
│   └── monitoring/                   # Observability stack
│       ├── deploy-monitoring.sh     # Monitoring setup
│       ├── prometheus-*.yaml        # Prometheus configs
│       └── grafana-*.yaml           # Grafana configs
│
├── openshift/                         # OpenShift/OKD manifests
│   ├── builds.yaml                   # BuildConfigs + ImageStreams
│   ├── mongodb.yaml                  # MongoDB deployment
│   ├── api.yaml                      # API deployment
│   └── streamlit.yaml                # Streamlit deployment + Route
│
├── deployment-docs/                   # Deployment procedures
│   ├── DEPLOYMENT_CHECKLIST.md      # Pre-deployment validation
│   └── DEPLOYMENT_UPGRADES.md       # Upgrade procedures
│
├── monitoring/                        # Local monitoring configs
│   ├── prometheus.yml                # Prometheus configuration
│   └── grafana/                      # Grafana provisioning
│       ├── dashboards/              # Pre-built dashboards
│       └── provisioning/            # Datasource configs
│
└── backups/                           # Database backups
    └── backup-YYYYMMDD-HHMMSS/      # Timestamped snapshots
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_URI` | MongoDB connection string | `mongodb://mongo:27017/research_db_structure` | Yes |
| `MONGO_PORT` | MongoDB exposed port | `27017` | Yes |
| `MONGO_INITDB_DATABASE` | Initial database name | `research_db_structure` | Yes |
| `API_PORT` | API service port | `8000` | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | - | Yes |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` | Yes |
| `STREAMLIT_PORT` | Streamlit service port | `8501` | Yes |
| `API_BASE_URL` | API endpoint for Streamlit | `http://api:8000` | Yes |
| `PROMETHEUS_PORT` | Prometheus port | `9090` | No |
| `GRAFANA_PORT` | Grafana port | `3000` | No |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password | `admin123` | No |

### Database Collections

The application uses six MongoDB collections:

| Collection | Description | Documents |
|------------|-------------|-----------|
| `users` | User authentication | Admin accounts |
| `chercheurs` | Researcher profiles | Names, affiliations, publications |
| `publications` | Research papers | Titles, authors, metadata |
| `institutions` | Organizations | Names, locations, stats |
| `collaborations` | Research networks | Researcher relationships |
| `stats_pays` | Country statistics | Aggregated metrics |

### Resource Requirements

**Production Recommended (Kubernetes with 2 API + 2 Streamlit replicas):**

| Service | CPU (Limits) | Memory (Limits) | Storage |
|---------|--------------|-----------------|---------|
| MongoDB (1 replica) | 2 cores | 2GB | 5GB |
| API (2 replicas) | 2 cores | 2GB | - |
| Streamlit (2 replicas) | 4 cores | 6GB | - |
| Prometheus (optional) | 0.5 cores | 512MB | 10GB |
| Grafana (optional) | 0.5 cores | 256MB | 1GB |
| **Total (without monitoring)** | **8 cores** | **10GB** | **5GB** |
| **Total (with monitoring)** | **9 cores** | **10.75GB** | **16GB** |

**Development Minimum (Kubernetes resource requests):**

| Service | CPU (Requests) | Memory (Requests) |
|---------|----------------|-------------------|
| MongoDB (1 replica) | 0.5 cores | 512MB |
| API (2 replicas) | 0.5 cores | 512MB |
| Streamlit (2 replicas) | 1 core | 3GB |
| **Total** | **2 cores** | **4GB** |

**Docker Compose (Single Replicas):**

| Service | CPU | Memory |
|---------|-----|--------|
| MongoDB | 2 cores | 2GB |
| API | 1 core | 1GB |
| Streamlit | 2 cores | 3GB |
| **Total** | **5 cores** | **6GB** |

---

## Maintenance

### Updating the Application

**Docker Compose:**

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify update
docker-compose ps
docker-compose logs -f
```

**Kubernetes:**

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Update deployments
kubectl rollout restart deployment/api -n research-dashboard
kubectl rollout restart deployment/streamlit -n research-dashboard
kubectl rollout restart deployment/mongodb -n research-dashboard

# Monitor rollout
kubectl rollout status deployment/streamlit -n research-dashboard
```

**OpenShift:**

```bash
# Trigger new builds
oc start-build mongodb
oc start-build api
oc start-build streamlit

# Monitor builds
oc get builds -w

# Deployments auto-update when builds complete
```

### Database Backup

**Docker Compose:**

```bash
# Create backup
docker-compose exec -T mongo mongodump \
  --db=research_db_structure \
  --out=/data/backup

# Copy to host
docker cp research_db_container:/data/backup \
  ./backups/backup-$(date +%Y%m%d-%H%M%S)

# Compress backup
tar -czf backups/backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  backups/backup-$(date +%Y%m%d-%H%M%S)
```

**Kubernetes:**

```bash
# Create backup
kubectl exec -n research-dashboard deployment/mongodb -- \
  mongodump --db=research_db_structure --out=/tmp/backup

# Copy to local
kubectl cp research-dashboard/POD_NAME:/tmp/backup \
  ./backups/backup-$(date +%Y%m%d-%H%M%S)
```

### Database Restore

```bash
# Restore from backup
docker-compose exec -T mongo mongorestore \
  --db=research_db_structure \
  --drop \
  /path/to/backup/research_db_structure
```

### Log Management

**View logs:**

```bash
# Docker Compose
docker-compose logs -f [service_name]
docker-compose logs --tail=100 streamlit

# Kubernetes
kubectl logs -n research-dashboard -l app=streamlit --tail=100 -f
kubectl logs -n research-dashboard deployment/api

# OpenShift
oc logs deployment/streamlit -f
oc logs build/streamlit-1
```

### Health Checks

**Docker Compose:**

```bash
# Check service health
docker-compose ps

# Test API health
curl http://localhost:8000/

# Test MongoDB
docker-compose exec mongo mongosh research_db_structure \
  --quiet --eval "db.stats()"
```

**Kubernetes:**

```bash
# Check pod health
kubectl get pods -n research-dashboard

# Check readiness/liveness probes
kubectl describe pod POD_NAME -n research-dashboard

# Test service connectivity
kubectl run test-pod --rm -it \
  --image=curlimages/curl \
  -n research-dashboard -- \
  curl http://api-service:8000
```

---

## Development

### Local Development Setup

```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt
pip install -r streamlit/requirements.txt

# Start MongoDB only
docker-compose up -d mongo

# Run API locally
cd api
uvicorn api_to_db:app --reload --host 0.0.0.0 --port 8000

# Run Streamlit locally (in another terminal)
cd streamlit
streamlit run dash.py --server.port 8501
```

### Testing

**API Tests:**

```bash
# Test authentication
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=123"

# Test authenticated endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/chercheurs
```

**Database Tests:**

```bash
# Connect to MongoDB
docker-compose exec mongo mongosh research_db_structure

# Count documents
db.users.countDocuments()
db.publications.countDocuments()
db.chercheurs.countDocuments()
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

---

## Security Considerations

### Development vs Production

**Development Default Values (NOT for production):**
- MongoDB: No authentication
- Default password: `123`
- JWT Secret: Generic value
- HTTP only (no TLS)

**Production Requirements:**
- Enable MongoDB authentication
- Strong passwords (min 16 characters)
- Rotate JWT secret key regularly
- Enable TLS/HTTPS
- Use secrets management (Vault, Sealed Secrets)
- Network policies to restrict pod communication
- Regular security updates
- Implement rate limiting
- Enable audit logging

### Securing Kubernetes Deployment

```bash
# Create secure JWT secret
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret-key=$(openssl rand -base64 32) \
  -n research-dashboard

# Enable network policies
kubectl apply -f k8s/network-policies.yaml

# Use pod security policies
kubectl apply -f k8s/pod-security-policy.yaml
```

---

## Troubleshooting

### Common Issues

**Service Won't Start**
- Check Docker Desktop is running and has sufficient resources
- Verify ports 8000, 8501, 27017 are not in use
- Check logs: `docker-compose logs [service]`

**Database Empty After Start**
- Wait 30 seconds for initialization to complete
- Check initialization logs: `docker-compose logs mongo`
- Verify BSON files exist in `mongo-dump/research_db_structure/`

**Cannot Login**
- Default credentials: `admin` / `123`
- Verify API is running: `curl http://localhost:8000/`
- Check API logs for authentication errors

**AI Models Not Loading**
- Streamlit container needs 4GB+ memory
- Models are downloaded during image build (large download)
- Check Streamlit logs for model loading errors

**Kubernetes Pods Pending**
- Check node resources: `kubectl top nodes`
- Verify PVC is bound: `kubectl get pvc -n research-dashboard`
- Check events: `kubectl get events -n research-dashboard --sort-by='.lastTimestamp'`

**Image Pull Errors (Kubernetes)**
- For local clusters, use `imagePullPolicy: Never`
- For remote clusters, push images to registry
- Verify image exists: `docker images | grep research`

### Getting Help

- Review documentation in `k8s/docs/`
- Check GitHub Issues
- Review container logs
- Verify network connectivity between services

---

## Performance Tuning

### Docker Compose

Adjust resource limits in `docker-compose.yml`:

```yaml
services:
  streamlit:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Kubernetes

Adjust HPA (Horizontal Pod Autoscaler):

```bash
# Scale API based on CPU
kubectl autoscale deployment api \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n research-dashboard

# Monitor scaling
kubectl get hpa -n research-dashboard -w
```

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Research data provided by academic institutions
- AI models: BART (Facebook AI), T5 (Google Research)
- Embedding models: sentence-transformers

---

## Contact

For questions or support, please open an issue on the GitHub repository.

**Last Updated:** February 2026
