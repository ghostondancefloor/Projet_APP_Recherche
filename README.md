# Research Dashboard - MongoDB Version

A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.

---

## Quick Start

```bash
# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:8501
```

**Default Login:**
- Username: See available users in database
- Password: Contact system administrator

---

## Architecture

This application uses a three-tier containerized architecture:

```
MongoDB (Port 27017)
    ↓
FastAPI REST API (Port 8000)
    ↓
Streamlit Dashboard (Port 8501)
```

**Services:**
- **MongoDB:** Database with persistent volume storage
- **FastAPI:** REST API with JWT authentication
- **Streamlit:** Interactive web dashboard

---

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v2.0 or higher
- 4GB RAM available for containers
- 10GB disk space for data

---

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Start the services:
```bash
docker-compose up -d
```

3. Verify all containers are running:
```bash
docker-compose ps
```

4. The database will auto-initialize from dump files on first run

---

## Database

**Collections:**
- chercheurs: 181 researchers
- publications: 4,527 publications
- institutions: 1,264 institutions
- collaborations: 131 collaborations
- stats_pays: 558 country statistics
- users: Authentication users

**Data Location:**
- Persistent Volume: `dash_mongodb_mongodb_data`
- Auto-initialization: `./mongo-dump/research_db_structure/`
- Backups: `./backups/`

---

## API Endpoints

Base URL: http://localhost:8000

**Authentication:**
- POST /token - Get JWT access token

**Data Endpoints:**
- GET /api/chercheurs - List all researchers
- GET /api/publications - List all publications
- GET /api/institutions - List all institutions
- GET /api/collaborations - List all collaborations
- GET /api/stats_pays - Country statistics
- GET /api/me - Current user info

**Documentation:**
- Interactive API docs: http://localhost:8000/docs

---

## Configuration

**Environment Files:**

The application uses environment files for configuration management:

- `.env` - Main configuration file (not committed to git)
- `.env.example` - Template with documentation

**Setup:**

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```bash
# MongoDB Configuration
MONGO_INITDB_DATABASE=research_db_structure
MONGO_HOST=mongo
MONGO_PORT=27017

# API Configuration
API_PORT=8000
JWT_SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Streamlit Configuration
STREAMLIT_PORT=8501
API_BASE_URL=http://api:8000

# MongoDB URI
MONGO_URI=mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_INITDB_DATABASE}
```

**Security Notes:**
- Never commit `.env` file to version control
- Change `JWT_SECRET_KEY` to a strong random value in production
- Use different secrets for development and production environments

**Environment Variables Reference:**

| Variable | Description | Default |
|----------|-------------|---------|
| MONGO_INITDB_DATABASE | Database name | research_db_structure |
| MONGO_HOST | MongoDB host | mongo |
| MONGO_PORT | MongoDB port | 27017 |
| API_PORT | API server port | 8000 |
| JWT_SECRET_KEY | JWT signing secret | (change in production) |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token lifetime | 30 |
| STREAMLIT_PORT | Dashboard port | 8501 |
| API_BASE_URL | API endpoint URL | http://api:8000 |

**Ports:**
- 27017: MongoDB
- 8000: FastAPI
- 8501: Streamlit

---

## Data Persistence

The application uses Docker named volumes for persistent storage:

```yaml
volumes:
  mongodb_data:/data/db
```

**What this means:**
- Database survives container restarts
- Data persists through updates and rebuilds
- No manual restoration needed

**Backup and Restore:**

Create backup:
```bash
docker exec research_db_container mongodump --out=/dump/backup-$(date +%Y%m%d)
docker cp research_db_container:/dump/backup-YYYYMMDD ./backups/
```

Restore from backup:
```bash
docker cp ./backups/backup-YYYYMMDD research_db_container:/dump/
docker exec research_db_container mongorestore /dump/backup-YYYYMMDD
```

---

## Development

**View logs:**
```bash
docker-compose logs -f [service]
```

**Restart a service:**
```bash
docker-compose restart [service]
```

**Rebuild containers:**
```bash
docker-compose up -d --build
```

**Access MongoDB shell:**
```bash
docker exec -it research_db_container mongosh research_db_structure
```

---

## Deployment

See detailed deployment documentation:

- **DEPLOYMENT_UPGRADES.md** - Complete upgrade history and planned improvements
- **DEPLOYMENT_CHECKLIST.md** - Step-by-step deployment checklists

**Current Status:**
- Version: 1.1.0
- Latest Upgrade: Docker volume data persistence (October 3, 2025)
- Data Persistence: FIXED
- Status: Production Ready

---

## Troubleshooting

**Containers won't start:**
```bash
docker-compose down
docker-compose up -d
```

**Database is empty:**
- Check if volume exists: `docker volume ls`
- Restore from backup or mongo-dump

**API connection errors:**
- Verify MongoDB is running: `docker-compose ps`
- Check API logs: `docker-compose logs api`

**Dashboard won't load:**
- Verify API is responding: `curl http://localhost:8000/health`
- Check Streamlit logs: `docker-compose logs streamlit`

---

## Maintenance

**Weekly:**
- Check container health
- Review logs for errors
- Monitor disk space

**Monthly:**
- Create database backup
- Review resource usage
- Update dependencies

**Quarterly:**
- Full system backup
- Security audit
- Performance review

---

## Project Structure

```
Dash_MONGODB/
├── api/                        # FastAPI application
│   ├── api_to_db.py           # Main API file
│   ├── Dockerfile             # API container config
│   └── requirements.txt       # Python dependencies
├── streamlit/                  # Streamlit dashboard
│   ├── dash.py                # Main dashboard file
│   ├── Dockerfile             # Streamlit container config
│   └── requirements.txt       # Python dependencies
├── mongo-dump/                 # Database initialization files
│   └── research_db_structure/ # Collection dumps
├── backups/                    # Database backups
├── docker-compose.yml          # Service orchestration
├── DEPLOYMENT_UPGRADES.md      # Upgrade documentation
└── DEPLOYMENT_CHECKLIST.md     # Deployment checklists
```

---

## Security Notes

**Authentication:**
- JWT-based authentication required for all API endpoints
- Passwords stored with bcrypt hashing
- Session tokens expire after 30 minutes

**Network:**
- Services communicate via internal Docker network
- Only necessary ports exposed to host
- MongoDB not directly accessible from outside

**Secrets:**
- Keep .env file out of version control
- Rotate JWT secret keys regularly
- Use strong passwords for all users

---

## Contributing

When making changes:

1. Create a feature branch
2. Test changes locally
3. Update documentation
4. Submit pull request
5. Follow deployment checklist for production

---

## Version History

- **v1.1.0** (October 3, 2025): Fixed Docker volume data persistence
- **v1.0.0**: Initial deployment configuration

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review deployment documentation
3. Check Docker logs for errors
4. Refer to DEPLOYMENT_UPGRADES.md for known issues






Last Updated: October 3, 2025
