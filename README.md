# Projet_APP_Recherche

## ⚙️ Setting up the Python Virtual Environment

Follow these steps to set up and use the virtual environment for this project.

### 1. Clone the Repository

```bash
git clone git@github.com:ghostondancefloor/Projet_APP_Recherche.git
```

If Python is not installed, you can download it from the official site:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

### 2. Create a Virtual Environment

Navigate to the root of the project and run:

```bash
python -m venv venv
```

This creates a `venv/` directory with an isolated Python environment.

### 3. Activate the Virtual Environment

**Windows:**

```bash
.\venv\Scripts\activate
```

**MacOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Project Dependencies

Make sure the environment is activated, then run:

```bash
pip install -r requirements.txt
```

### 5. Deactivate When Finished

```bash
deactivate
```

### 6. (Optional) Update Requirements File

Freeze current dependencies into `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## 🧪 Setting up the MongoDB Research Database

This guide explains how to run the `research_db_structure` MongoDB image and import the provided data into the container.

### 📦 What You Need

- [Docker](https://www.docker.com/products/docker-desktop) installed
- Docker Hub access to pull the image: `danlimao/research_db_structure:v2`
- Extracted `.rar` file containing the MongoDB dump (e.g., to `C:\mongo-dump`)

---

### 🚀 MongoDB Setup Steps

#### 1. Create a `docker-compose.yml`

```yaml
version: "3.8"
services:
  mongodb:
    image: danlimao/research_db_structure:v2
    container_name: research_db_container
    ports:
      - "27017:27017"
    volumes: []
```

Save this in your project directory.

#### 2. Start the MongoDB Container

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

**For detailed Kubernetes troubleshooting, see [k8s/README.md](k8s/README.md)**

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
Projet_APP_Recherche/
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
├── k8s/                               # Kubernetes deployment
│   ├── README.md                     # Kubernetes guide
│   ├── deploy.sh                     # Automated deployment
│   ├── docs/                         # K8s documentation
│   │   ├── ARCHITECTURE.md           # System diagrams
│   │   ├── DEPLOYMENT_EXPLAINED.md   # Technical deep-dive
│   │   └── README.md                 # Documentation index
│   └── *.yaml                        # K8s manifests
│
├── deployment-docs/                   # Deployment guides
│   ├── DEPLOYMENT_CHECKLIST.md       # Pre-deployment checks
│   └── DEPLOYMENT_UPGRADES.md        # Upgrade procedures
│
└── backups/                           # Database backups
    └── backup-YYYYMMDD-HHMMSS/       # Timestamped backups
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
   - [k8s/README.md](k8s/README.md) - Kubernetes deployment guide
   - [k8s/docs/DEPLOYMENT_EXPLAINED.md](k8s/docs/DEPLOYMENT_EXPLAINED.md) - Architecture deep-dive
   - [k8s/docs/ARCHITECTURE.md](k8s/docs/ARCHITECTURE.md) - Visual diagrams

5. **Start fresh if needed**
   ```bash
   docker-compose down -v
   docker-compose build
   docker-compose up -d
   ```

---

**Questions?** Check the \`docs/\` folder or contact the development team.

**Last Updated:** October 13, 2025
