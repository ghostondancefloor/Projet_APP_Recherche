# Research Dashboard - MongoDB Version# Research Dashboard - MongoDB Version# Research Dashboard - MongoDB Version



A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.



---A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.



## 🚀 Quick Start



```bash------

# 1. Clone and navigate

git clone <repository-url>

cd Dash_MONGODB

## 🚀 Quick Start## ⚠️ IMPORTANT for Team Members

# 2. Create environment file

cp .env.example .env



# 3. Build and start### First Time Setup**After cloning this repository, you MUST run the setup script first:**

docker-compose build

docker-compose up -d



# 4. Wait 60 seconds for database initialization```bash```bash



# 5. Open dashboard# 1. Clone the repository./setup.sh

open http://localhost:8501

```git clone <repository-url>```



**Login:** Username: `Flavien VERNIER` | Password: `123`cd Dash_MONGODB



> **Fixed!** Scripts are now executable via Dockerfile. No setup.sh needed!**Why?** Git doesn't preserve executable permissions on shell scripts. Without this, the database won't initialize automatically and will be empty.



---# 2. Run setup script (fixes permissions & creates .env)



## 📋 Prerequisites./setup.shSee [`QUICKSTART.md`](QUICKSTART.md) for the fastest path to get running.



- Docker Desktop running

- Docker Compose v2.0+

- 4GB RAM minimum# 3. Build and start services---

- 10GB disk space

docker-compose build

---

docker-compose up -d## Quick Start

## 🏗️ Architecture



```

Streamlit (8501) → FastAPI (8000) → MongoDB (27017)# 4. Wait 60 seconds for database initialization### For Team Members (First Time Setup)

```



**Services:**

- **MongoDB:** Database with auto-initialization from BSON dumps# 5. Access the dashboard```bash

- **FastAPI:** REST API with JWT authentication  

- **Streamlit:** Interactive dashboardopen http://localhost:8501# 1. Run the setup script (IMPORTANT - fixes permissions!)



---```./setup.sh



## 📊 Database



**Collections:****Default Login:**# 2. Build and start services

- `users`: 39 authentication users (all password: `123`)

- `chercheurs`: 181 researchers- Username: `Flavien VERNIER`docker-compose build

- `publications`: 4,527 publications

- `institutions`: 1,264 institutions- Password: `123`docker-compose up -d

- `collaborations`: 131 collaborations

- `stats_pays`: 558 country statistics



---### If Database is Empty# 3. Wait 30-60 seconds for database initialization



## 🔧 Common Commands



```bash```bash# 4. Access the dashboard

# Start

docker-compose up -d./import-db.shopen http://localhost:8501



# Stop``````

docker-compose down



# View logs

docker-compose logs -f---**Default Login:**



# Rebuild- Username: `Flavien VERNIER` (or any researcher name)

docker-compose build --no-cache

## 📋 Prerequisites- Password: `123`

# Verify database

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"

# Should return: 39

- Docker Desktop installed and running### If Database is Empty After Starting

# Full reset

docker-compose down -v- Docker Compose v2.0+

docker-compose up -d

```- 4GB RAM minimum```bash



---- 10GB disk space# Run the manual import script



## 🌐 Access./import-db.sh



- **Dashboard:** http://localhost:8501---```

- **API Docs:** http://localhost:8000/docs

- **Health:** http://localhost:8000/health



---## 🏗️ Architecture---



## 📁 Structure



``````## Architecture

Dash_MONGODB/

├── api/                    # FastAPI backend┌─────────────────────────────────────────┐

├── streamlit/             # Streamlit dashboard

├── mongo-dump/            # Database initialization│   Streamlit Dashboard (Port 8501)      │This application uses a three-tier containerized architecture:

│   ├── docker-entrypoint-wrapper.sh

│   └── research_db_structure/*.bson│   - Interactive UI                      │

├── docs/                  # Documentation

│   ├── TROUBLESHOOTING.md│   - Data Visualizations                 │```

│   └── SETUP_CHECKLIST.md

├── docker-compose.yml└────────────────┬────────────────────────┘MongoDB (Port 27017)

├── mongo.Dockerfile       # Custom MongoDB image

├── .env.example                 │    ↓

├── setup.sh              # Optional safety net

├── import-db.sh          # Manual DB import┌────────────────▼────────────────────────┐FastAPI REST API (Port 8000)

└── README.md

```│   FastAPI Backend (Port 8000)          │    ↓



---│   - REST API                            │Streamlit Dashboard (Port 8501)



## ⚠️ Troubleshooting│   - JWT Authentication                  │```



### Database Empty (Rare)└────────────────┬────────────────────────┘



```bash                 │**Services:**

./import-db.sh

```┌────────────────▼────────────────────────┐- **MongoDB:** Database with persistent volume storage



### Login Fails│   MongoDB Database (Port 27017)        │- **FastAPI:** REST API with JWT authentication



```bash│   - Persistent Storage                  │- **Streamlit:** Interactive web dashboard

# Verify database has users

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"│   - Auto-initialization                 │

```

└─────────────────────────────────────────┘---

### Port in Use

```

Edit `.env`:

```env## Prerequisites

MONGO_PORT=27018

API_PORT=8001---

STREAMLIT_PORT=8502

```- Docker Desktop installed and running



**More help:** See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)## 📊 Database- Docker Compose v2.0 or higher



---- 4GB RAM available for containers



## 🔄 Maintenance**Collections:**- 10GB disk space for data



### Update- `chercheurs`: 181 researchers



```bash- `publications`: 4,527 publications---

git pull

docker-compose down- `institutions`: 1,264 institutions

docker-compose build

docker-compose up -d- `collaborations`: 131 collaborations## Installation

```

- `stats_pays`: 558 country statistics

### Backup

- `users`: 39 authentication users1. Clone the repository:

```bash

docker-compose exec -T mongo mongodump --db=research_db_structure --out=/data/backup```bash

docker cp research_db_container:/data/backup ./backups/backup-$(date +%Y%m%d)

```**Data Location:**git clone <repository-url>



---- Persistent Volume: `dash_mongodb_mongodb_data`cd Dash_MONGODB



## 📚 Documentation- Initialization Dump: `./mongo-dump/research_db_structure/````



- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

- [Setup Checklist](docs/SETUP_CHECKLIST.md)

- [API Docs](http://localhost:8000/docs) (when running)---2. Start the services:



---```bash



## 🛠️ Technical Notes## 🔧 Common Commandsdocker-compose up -d



### Why No Setup Script Needed?```



The `mongo.Dockerfile` now handles all permissions:```bash

```dockerfile

RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh \# Start services3. Verify all containers are running:

    /docker-entrypoint-initdb.d/init-db.sh

```docker-compose up -d```bash



This bakes executable permissions into the Docker image, solving the "Git doesn't preserve permissions" issue.docker-compose ps



### Custom MongoDB Image# Stop services```



We build a custom MongoDB image that:docker-compose down

1. Copies initialization scripts with correct permissions

2. Includes database dump files (BSON)4. The database will auto-initialize from dump files on first run

3. Automatically initializes on first run

# View logs

---

docker-compose logs -f---

**Questions?** Check `docs/` folder or contact the team.



# Rebuild containers## Database

docker-compose build --no-cache

**Collections:**

# Check database user count- chercheurs: 181 researchers

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"- publications: 4,527 publications

- institutions: 1,264 institutions

# Complete reset (deletes all data)- collaborations: 131 collaborations

docker-compose down -v- stats_pays: 558 country statistics

./setup.sh- users: Authentication users

docker-compose up -d

```**Data Location:**

- Persistent Volume: `dash_mongodb_mongodb_data`

---- Auto-initialization: `./mongo-dump/research_db_structure/`

- Backups: `./backups/`

## 🌐 Access URLs

---

- **Dashboard:** http://localhost:8501

- **API Documentation:** http://localhost:8000/docs## API Endpoints

- **API Health Check:** http://localhost:8000/health

Base URL: http://localhost:8000

---

**Authentication:**

## 🔐 Authentication- POST /token - Get JWT access token



All 39 users in the database have the default password: `123`**Data Endpoints:**

- GET /api/chercheurs - List all researchers

Example users:- GET /api/publications - List all publications

- Flavien VERNIER- GET /api/institutions - List all institutions

- Ayoub BOUCHAOUI- GET /api/collaborations - List all collaborations

- (See database for full list)- GET /api/stats_pays - Country statistics

- GET /api/me - Current user info

**Production Note:** Change passwords before deploying to production!

**Documentation:**

---- Interactive API docs: http://localhost:8000/docs



## 📁 Project Structure---



```## Configuration

Dash_MONGODB/

├── api/                    # FastAPI backend**Environment Files:**

│   ├── api_to_db.py

│   ├── DockerfileThe application uses environment files for configuration management:

│   └── requirements.txt

├── streamlit/             # Streamlit dashboard- `.env` - Main configuration file (not committed to git)

│   ├── dash.py- `.env.example` - Template with documentation

│   ├── Dockerfile

│   └── requirements.txt**Setup:**

├── mongo-dump/            # Database initialization

│   ├── docker-entrypoint-wrapper.sh1. Copy the example file:

│   └── research_db_structure/```bash

│       └── *.bson         # Database dump filescp .env.example .env

├── docs/                  # Documentation```

│   ├── TROUBLESHOOTING.md

│   └── SETUP_CHECKLIST.md2. Edit `.env` with your configuration:

├── scripts/               # Utility scripts```bash

│   └── verify-setup.sh# MongoDB Configuration

├── docker-compose.yml     # Docker configurationMONGO_INITDB_DATABASE=research_db_structure

├── .env.example           # Environment templateMONGO_HOST=mongo

├── setup.sh              # Initial setup scriptMONGO_PORT=27017

├── import-db.sh          # Manual DB import

└── README.md             # This file# API Configuration

```API_PORT=8000

JWT_SECRET_KEY=your-secret-key-here-change-this-in-production

---JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

## ⚠️ Troubleshooting

# Streamlit Configuration

### Database is Empty (0 users)STREAMLIT_PORT=8501

API_BASE_URL=http://api:8000

**Solution:**

```bash# MongoDB URI

./import-db.shMONGO_URI=mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_INITDB_DATABASE}

``````



### Login Fails**Security Notes:**

- Never commit `.env` file to version control

**Check database has data:**- Change `JWT_SECRET_KEY` to a strong random value in production

```bash- Use different secrets for development and production environments

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"

# Should show: 39**Environment Variables Reference:**

```

| Variable | Description | Default |

### Containers Won't Start|----------|-------------|---------|

| MONGO_INITDB_DATABASE | Database name | research_db_structure |

**Check logs and restart:**| MONGO_HOST | MongoDB host | mongo |

```bash| MONGO_PORT | MongoDB port | 27017 |

docker-compose logs| API_PORT | API server port | 8000 |

docker-compose restart| JWT_SECRET_KEY | JWT signing secret | (change in production) |

```| JWT_ALGORITHM | JWT algorithm | HS256 |

| ACCESS_TOKEN_EXPIRE_MINUTES | Token lifetime | 30 |

### Port Already in Use| STREAMLIT_PORT | Dashboard port | 8501 |

| API_BASE_URL | API endpoint URL | http://api:8000 |

**Change port in `.env` file:**

```env**Ports:**

MONGO_PORT=27018- 27017: MongoDB

API_PORT=8001- 8000: FastAPI

STREAMLIT_PORT=8502- 8501: Streamlit

```

---

**For more solutions, see:** [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

## Data Persistence

---

The application uses Docker named volumes for persistent storage:

## 🔄 Updates & Maintenance

```yaml

### Pull Latest Changesvolumes:

  mongodb_data:/data/db

```bash```

git pull origin main

docker-compose down**What this means:**

docker-compose build- Database survives container restarts

docker-compose up -d- Data persists through updates and rebuilds

```- No manual restoration needed



### Backup Database**Backup and Restore:**



```bashCreate backup:

docker-compose exec -T mongo mongodump --db=research_db_structure --out=/data/backup```bash

docker cp research_db_container:/data/backup ./backups/backup-$(date +%Y%m%d)docker exec research_db_container mongodump --out=/dump/backup-$(date +%Y%m%d)

```docker cp research_db_container:/dump/backup-YYYYMMDD ./backups/

```

### Restore Database

Restore from backup:

```bash```bash

docker-compose exec -T mongo mongorestore --db=research_db_structure /path/to/backupdocker cp ./backups/backup-YYYYMMDD research_db_container:/dump/

```docker exec research_db_container mongorestore /dump/backup-YYYYMMDD

```

---

---

## 📚 Additional Documentation

## Development

- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Solutions for common issues

- [Setup Checklist](docs/SETUP_CHECKLIST.md) - Verification steps**View logs:**

- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)```bash

docker-compose logs -f [service]

---```



## 🤝 Contributing**Restart a service:**

```bash

1. Create a feature branchdocker-compose restart [service]

2. Make your changes```

3. Test with `docker-compose up -d`

4. Submit a pull request**Rebuild containers:**

```bash

---docker-compose up -d --build

```

**Questions?** Check the docs folder or contact the development team.

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
