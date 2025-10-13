# Research Dashboard - MongoDB Version

A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.

---

## Table of Contents

- [Quick Start](#quick-start)
  - [Docker Compose (Recommended for Development)](#docker-compose-recommended-for-development)
  - [Kubernetes (Production & Learning)](#kubernetes-production--learning)
- [What This Application Does](#what-this-application-does)
- [Prerequisites](#prerequisites)
- [System Architecture](#system-architecture)
- [Database Content](#database-content)
- [Installation](#installation)
- [Configuration](#configuration)
- [Common Commands](#common-commands)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Accessing Services](#accessing-services)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)
- [Technical Details](#technical-details)
- [Support](#support)

---

## Quick Start

Choose your deployment method:

### Docker Compose (Recommended for Development)

After cloning this repository, follow these steps:

```bash
# 1. Create environment configuration
cp .env.example .env

# 2. Build Docker images
docker-compose build

# 3. Start all services
docker-compose up -d

# 4. Wait 30-60 seconds for database initialization
```

Then open your browser to **http://localhost:8501**

**Default Login:**
- Username: `Flavien VERNIER`
- Password: `123`

The database will automatically populate with all research data (39 users, 181 researchers, 4,527 publications, and more).

### Kubernetes (Production & Learning)

For production deployments or learning Kubernetes:

```bash
# 1. Ensure Kubernetes is running (Docker Desktop or Minikube)
kubectl cluster-info

# 2. Navigate to the k8s directory
cd k8s

# 3. Run the automated deployment script
./deploy.sh

# 4. Access the dashboard
# Open http://localhost:8501 in your browser
```

For detailed Kubernetes instructions, see the [Kubernetes Deployment](#kubernetes-deployment) section below.

---

## What This Application Does

This dashboard helps you explore and analyze scientific research data:

- View researcher profiles and their publications
- Analyze collaboration networks between researchers
- Track publications across different institutions
- Visualize research statistics by country
- Access detailed publication metadata
- Explore co-authorship patterns

---

## Prerequisites

### For Docker Compose (Development)

Make sure you have these installed before starting:

- **Docker Desktop** - Must be running before you start the services
- **Docker Compose** - Version 2.0 or higher
- **4GB of available RAM** - Minimum for running all three containers
- **10GB of disk space** - For Docker images and database

### For Kubernetes (Production/Learning)

- **Docker Desktop with Kubernetes enabled**, OR **Minikube**
- **kubectl** - Kubernetes command-line tool
- **4.5GB of available RAM** - For all pods
- **10GB of disk space** - For images and persistent volumes

**Resource Allocation:**

The application uses the following resource limits:

| Service | CPU Limit | Memory Limit | CPU Reserved | Memory Reserved |
|---------|-----------|--------------|--------------|-----------------|
| MongoDB | 2.0 cores | 2GB | 0.5 cores | 512MB |
| FastAPI | 1.0 core | 1GB | 0.25 cores | 256MB |
| Streamlit | 1.5 cores | 1.5GB | 0.25 cores | 256MB |
| **Total** | **4.5 cores** | **4.5GB** | **1.0 core** | **1GB** |

**Note:** These limits can be adjusted in `docker-compose.yml` or the Kubernetes manifests in `k8s/` directory.

To verify Docker is ready:

```bash
docker --version
docker-compose --version
```

---

## System Architecture

The application uses three main components that work together:

```
┌─────────────────────────────────────────┐
│   Streamlit Dashboard (Port 8501)      │
│   - Interactive UI                      │
│   - Data Visualizations                 │
│   - User Authentication                 │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌────────────────▼────────────────────────┐
│   FastAPI Backend (Port 8000)           │
│   - REST API                            │
│   - JWT Authentication                  │
│   - Request Validation                  │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌────────────────▼────────────────────────┐
│   MongoDB Database (Port 27017)         │
│   - Persistent Storage                  │
│   - Auto-initialization                 │
│   - 6 Collections                       │
└─────────────────────────────────────────┘
```

**Workflow:** Streamlit → FastAPI → MongoDB → FastAPI → Streamlit

---

## Database Content

The database automatically loads with real research data:

| Collection | Documents | Description |
|------------|-----------|-------------|
| users | 39 | Authentication accounts (all password: \`123\`) |
| chercheurs | 181 | Researcher profiles and affiliations |
| publications | 4,527 | Scientific papers and articles |
| institutions | 1,264 | Universities and research centers |
| collaborations | 131 | Research collaboration networks |
| stats_pays | 558 | Research statistics by country |

**Total:** 6,700 documents across all collections

**Data Location:**
- Persistent Volume: \`dash_mongodb_mongodb_data\`
- Initialization Dump: \`./mongo-dump/research_db_structure/\`

---

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Dash_MONGODB

# 2. Create environment configuration
cp .env.example .env

# 3. Build and start services
docker-compose build
docker-compose up -d

# 4. Wait 30-60 seconds for database initialization

# 5. Access the dashboard
open http://localhost:8501
```

**Default Login:**
- Username: \`Flavien VERNIER\`
- Password: \`123\`

---

## Configuration

The \`.env\` file controls service configuration. After copying from \`.env.example\`, you can modify:

### MongoDB Settings

```env
MONGO_INITDB_DATABASE=research_db_structure  # Database name
MONGO_HOST=mongo                              # Container hostname
MONGO_PORT=27017                              # External port
```

### API Settings

```env
API_PORT=8000                                 # External port
JWT_SECRET_KEY=your-secret-key               # Change for production!
JWT_ALGORITHM=HS256                           # Token encryption
ACCESS_TOKEN_EXPIRE_MINUTES=30               # Session duration
```

### Streamlit Settings

```env
STREAMLIT_PORT=8501                           # External port
API_BASE_URL=http://api:8000                 # Internal API address
```

**Important:** Never commit your \`.env\` file to Git (it's in \`.gitignore\`).

---

## Common Commands

### Starting and Stopping

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (full cleanup)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs mongo
docker-compose logs api
docker-compose logs streamlit
```

### Checking Status

```bash
# Check if containers are running
docker-compose ps

# Check database user count
docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
# Should return: 39

# List all collections with document counts
docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.getCollectionNames().forEach(col => print(col + ': ' + db[col].countDocuments({})))"
```

### Rebuilding

```bash
# Rebuild with cache
docker-compose build

# Rebuild without cache (clean build)
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

### Monitoring Resources

```bash
# View resource usage for all containers
docker stats

# View resource usage for specific container
docker stats research_db_container
docker stats api_service
docker stats streamlit_service

# Check resource limits
docker inspect research_db_container | grep -A 10 "Memory"
```

### Adjusting Resource Limits

To modify resource limits, edit `docker-compose.yml` and change the values under `deploy.resources`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Adjust CPU limit
      memory: 2G       # Adjust memory limit
    reservations:
      cpus: '0.5'      # Adjust CPU reservation
      memory: 512M     # Adjust memory reservation
```

Then restart the services:

```bash
docker-compose down
docker-compose up -d
```

---

## Kubernetes Deployment

### Why Kubernetes?

Kubernetes provides:
- **High Availability**: Automatic pod restart if containers fail
- **Scalability**: Easy horizontal scaling of API and dashboard replicas
- **Load Balancing**: Built-in load balancing across pods
- **Rolling Updates**: Zero-downtime deployments
- **Resource Management**: CPU and memory limits/requests
- **Production-Ready**: Industry-standard orchestration platform

### Prerequisites

- Docker Desktop with Kubernetes enabled, OR
- Minikube installed and running
- kubectl CLI tool installed

### Quick Deploy

```bash
# 1. Navigate to k8s directory
cd k8s

# 2. Run automated deployment
./deploy.sh

# 3. Monitor deployment
kubectl get pods -n research-dashboard --watch

# 4. Access dashboard at http://localhost:8501
```

### Manual Deployment

If you prefer step-by-step deployment:

```bash
cd k8s

# 1. Create namespace
kubectl apply -f namespace.yaml

# 2. Create secrets
kubectl apply -f secrets.yaml

# 3. Create persistent storage
kubectl apply -f mongodb-pv.yaml

# 4. Deploy MongoDB
kubectl apply -f mongodb-deployment.yaml
kubectl wait --for=condition=ready pod -l app=mongodb -n research-dashboard --timeout=120s

# 5. Deploy API
kubectl apply -f api-deployment.yaml
kubectl wait --for=condition=ready pod -l app=api -n research-dashboard --timeout=90s

# 6. Deploy Streamlit
kubectl apply -f streamlit-deployment.yaml
kubectl wait --for=condition=ready pod -l app=streamlit -n research-dashboard --timeout=90s
```

### Kubernetes Architecture

**Deployed Resources:**
- **Namespace**: `research-dashboard` (isolated environment)
- **Secrets**: JWT keys and MongoDB password
- **Persistent Volume**: 5Gi for MongoDB data
- **Deployments**:
  - MongoDB: 1 replica with persistent storage
  - API: 2 replicas with load balancing
  - Streamlit: 2 replicas with load balancing
- **Services**:
  - `mongodb-service`: ClusterIP (internal)
  - `api-service`: ClusterIP (internal)
  - `streamlit-service`: LoadBalancer (external access)

### Useful Kubernetes Commands

```bash
# View all resources
kubectl get all -n research-dashboard

# Check pod status
kubectl get pods -n research-dashboard

# View logs
kubectl logs -n research-dashboard -l app=api --tail=50

# Scale deployments
kubectl scale deployment api --replicas=5 -n research-dashboard

# Restart a deployment (rolling update)
kubectl rollout restart deployment streamlit -n research-dashboard

# Exec into a pod
kubectl exec -it -n research-dashboard <pod-name> -- /bin/bash

# Delete everything
kubectl delete namespace research-dashboard
```

### Learning Resources

For a comprehensive Kubernetes learning guide with exercises and best practices, see:
- **[k8s/README.md](k8s/README.md)** - Complete Kubernetes tutorial and reference
- **[k8s/ARCHITECTURE.md](k8s/ARCHITECTURE.md)** - Visual architecture diagrams with Mermaid

---

## Accessing Services

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:8501 | Main user interface |
| API Docs | http://localhost:8000/docs | Interactive API explorer |
| API Health | http://localhost:8000/health | Service health check |
| MongoDB | localhost:27017 | Database (internal access only) |

---

## Troubleshooting

### Database is Empty

If you log in but see no data:

```bash
./import-db.sh
```

This script will manually import all data into the database.

### Cannot Login

First, verify the database has users:

```bash
docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
```

If it shows \`0\`, run the import script above.

If it shows \`39\`, make sure you're using correct credentials:
- Username: \`Flavien VERNIER\` (case-sensitive, with space)
- Password: \`123\`

### Port Already in Use

If you see port conflict errors, edit the \`.env\` file:

```env
MONGO_PORT=27018
API_PORT=8001
STREAMLIT_PORT=8502
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

### Containers Won't Start

Check the logs for error messages:

```bash
docker-compose logs
```

Common issues:
- Docker Desktop not running
- Insufficient memory allocated to Docker
- Conflicting services using the same ports

### Slow Performance

Make sure Docker Desktop has enough resources:
- At least 4GB RAM allocated
- At least 2 CPU cores
- Sufficient disk space available

**Check current resource usage:**

```bash
docker stats --no-stream
```

If containers are hitting their limits, you may need to:
1. Increase limits in `docker-compose.yml`
2. Allocate more resources to Docker Desktop (Preferences → Resources)
3. Close other resource-intensive applications

**For more detailed troubleshooting, see \`docs/TROUBLESHOOTING.md\`**

---

## Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin backup-main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backing Up the Database

```bash
# Create backup
docker-compose exec -T mongo mongodump --db=research_db_structure --out=/data/backup
docker cp research_db_container:/data/backup ./backups/backup-\$(date +%Y%m%d)
```

### Restoring from Backup

```bash
# Restore from backup directory
docker-compose exec -T mongo mongorestore --db=research_db_structure /path/to/backup --drop
```

### Regular Maintenance Tasks

**Weekly:**
- Check container health with \`docker-compose ps\`
- Review logs for errors
- Monitor disk space usage

**Monthly:**
- Create database backup
- Review resource usage
- Update dependencies if needed

---

## Project Structure

```
Dash_MONGODB/
├── README.md                          # This file
├── docker-compose.yml                 # Orchestrates all services
├── mongo.Dockerfile                   # Custom MongoDB with auto-init
├── .env.example                       # Configuration template
├── import-db.sh                       # Manual database import script
│
├── api/                               # FastAPI backend service
│   ├── api_to_db.py                  # Main API application
│   ├── Dockerfile                     # API container definition
│   └── requirements.txt               # Python dependencies
│
├── streamlit/                         # Streamlit dashboard
│   ├── dash.py                       # Dashboard application
│   ├── Dockerfile                     # Streamlit container
│   └── requirements.txt               # Python dependencies
│
├── mongo-dump/                        # Database initialization
│   ├── docker-entrypoint-wrapper.sh  # Initialization script
│   └── research_db_structure/        # Database backup files
│       ├── users.bson                # User data
│       ├── chercheurs.bson           # Researcher data
│       ├── publications.bson         # Publication data
│       └── ...                       # Other collections
│
└── docs/                              # Additional documentation
    ├── TROUBLESHOOTING.md            # Detailed problem solving
    └── SETUP_CHECKLIST.md            # Verification steps
```

---

## Security Notes

### Development Environment

- Default password \`123\` is intentionally simple
- JWT secret key is generic
- Database has no authentication
- All services use default ports

### Production Deployment

Before deploying to production:

- Change all passwords to strong values
- Update \`JWT_SECRET_KEY\` to a random string
- Enable MongoDB authentication
- Use environment-specific configurations
- Enable HTTPS/TLS
- Review security settings in all services
- Restrict network access to services

---

## Technical Details

### Automatic Database Initialization

The system uses a custom approach to ensure the database initializes correctly:

1. The \`mongo.Dockerfile\` builds a custom MongoDB image
2. During build, it sets executable permissions on initialization scripts
3. When the container starts, \`docker-entrypoint-wrapper.sh\` runs automatically
4. The script waits for MongoDB to be ready
5. It checks if the database is empty
6. If empty, it restores from BSON backup files
7. All 6 collections are imported with full data

**Why This Matters:**

This approach solves the common problem where Git doesn't preserve file permissions on shell scripts. By setting permissions in the Dockerfile during image build, we guarantee they're correct on every machine.

The \`mongo.Dockerfile\` includes:

```dockerfile
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh
```

This bakes executable permissions into the Docker image, solving the "Git doesn't preserve permissions" issue.

### Technology Stack

**Docker:**
- Ensures everyone runs the same environment
- No "works on my machine" problems
- Easy to set up and tear down
- Isolates the application from your system

**MongoDB:**
- Flexible schema for research data
- Fast queries for large datasets
- JSON-like documents easy to work with
- Good for complex nested data structures

**FastAPI:**
- Fast and modern Python framework
- Automatic API documentation
- Built-in data validation
- Easy to test and maintain

**Streamlit:**
- Quick to build interactive dashboards
- Python-based (matches our backend)
- Built-in widgets and charts
- Good for data science applications

---

## Support

If you encounter issues:

1. **Check the logs** - Most problems show error messages
   ```bash
   docker-compose logs
   ```

2. **Verify all services are running**
   ```bash
   docker-compose ps
   ```

3. **Check database has data**
   ```bash
   docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
   ```

4. **Review documentation**
   - \`docs/TROUBLESHOOTING.md\` - Common problems and solutions
   - \`docs/SETUP_CHECKLIST.md\` - Step-by-step verification

5. **Start fresh if needed**
   ```bash
   docker-compose down -v
   docker-compose build
   docker-compose up -d
   ```

---

**Questions?** Check the \`docs/\` folder or contact the development team.

**Last Updated:** October 13, 2025
