# Research Dashboard - MongoDB Version# Research Dashboard - MongoDB Version# Research Dashboard - MongoDB Version# Research Dashboard - MongoDB Version



A containerized analytics dashboard for tracking scientific publications, researchers, collaborations, and institutional data. Built with FastAPI for the backend, Streamlit for the interactive interface, and MongoDB for data storage.



---A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.



## Quick Start for New Users



After cloning this repository, follow these three simple steps:---A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.A containerized research analytics dashboard built with FastAPI, Streamlit, and MongoDB for tracking publications, researchers, collaborations, and institutional data.



```bash

# Step 1: Create your environment configuration

cp .env.example .env## 🚀 Quick Start



# Step 2: Build the Docker images

docker-compose build

```bash------

# Step 3: Start all services

docker-compose up -d# 1. Clone and navigate

```

git clone <repository-url>

Wait about 30 seconds for the database to initialize, then open your browser to:

**http://localhost:8501**cd Dash_MONGODB



Login with:## 🚀 Quick Start## ⚠️ IMPORTANT for Team Members

- Username: `Flavien VERNIER`

- Password: `123`# 2. Create environment file



That's it! The database will automatically populate with all research data (39 users, 181 researchers, 4,527 publications, and more).cp .env.example .env



---



## What This Application Does# 3. Build and start### First Time Setup**After cloning this repository, you MUST run the setup script first:**



This dashboard helps you explore and analyze scientific research data:docker-compose build



- View researcher profiles and their publicationsdocker-compose up -d

- Analyze collaboration networks between researchers

- Track publications across different institutions

- Visualize research statistics by country

- Access detailed publication metadata# 4. Wait 60 seconds for database initialization```bash```bash

- Explore co-authorship patterns



---

# 5. Open dashboard# 1. Clone the repository./setup.sh

## System Architecture

open http://localhost:8501

The application uses three main components that work together:

```git clone <repository-url>```

**Streamlit Dashboard (Port 8501)**

- The web interface you interact with

- Displays charts, tables, and visualizations

- Handles user authentication**Login:** Username: `Flavien VERNIER` | Password: `123`cd Dash_MONGODB



**FastAPI Backend (Port 8000)**

- Provides REST API endpoints for data access

- Manages authentication with JWT tokens> **Fixed!** Scripts are now executable via Dockerfile. No setup.sh needed!**Why?** Git doesn't preserve executable permissions on shell scripts. Without this, the database won't initialize automatically and will be empty.

- Validates and processes requests



**MongoDB Database (Port 27017)**

- Stores all research data---# 2. Run setup script (fixes permissions & creates .env)

- Automatically initializes from backup files

- Maintains 6 collections with research information



The workflow: Streamlit talks to FastAPI, which queries MongoDB, then sends results back through the chain.## 📋 Prerequisites./setup.shSee [`QUICKSTART.md`](QUICKSTART.md) for the fastest path to get running.



---



## What You Need Before Starting- Docker Desktop running



Make sure you have these installed on your computer:- Docker Compose v2.0+



- **Docker Desktop** - Must be running before you start the services- 4GB RAM minimum# 3. Build and start services---

- **Docker Compose** - Version 2.0 or higher

- **4GB of available RAM** - For running all three containers- 10GB disk space

- **10GB of disk space** - For Docker images and database

docker-compose build

To check if you have Docker ready:

```bash---

docker --version

docker-compose --versiondocker-compose up -d## Quick Start

```

## 🏗️ Architecture

---



## Database Content

```

The database automatically loads with real research data:

Streamlit (8501) → FastAPI (8000) → MongoDB (27017)# 4. Wait 60 seconds for database initialization### For Team Members (First Time Setup)

**Users Collection** - 39 accounts

- All users have password: `123````

- Includes researchers and administrators

- Used for dashboard authentication



**Researchers Collection** - 181 profiles**Services:**

- Individual researcher information

- Affiliated institutions- **MongoDB:** Database with auto-initialization from BSON dumps# 5. Access the dashboard```bash

- Contact details

- **FastAPI:** REST API with JWT authentication  

**Publications Collection** - 4,527 entries

- Scientific papers and articles- **Streamlit:** Interactive dashboardopen http://localhost:8501# 1. Run the setup script (IMPORTANT - fixes permissions!)

- Authors and co-authors

- Publication dates and venues



**Institutions Collection** - 1,264 organizations---```./setup.sh

- Universities and research centers

- Location information

- Associated researchers

## 📊 Database

**Collaborations Collection** - 131 partnerships

- Research collaboration networks

- Co-authorship patterns

**Collections:****Default Login:**# 2. Build and start services

**Country Statistics** - 558 records

- Research output by country- `users`: 39 authentication users (all password: `123`)

- Geographic distribution data

- `chercheurs`: 181 researchers- Username: `Flavien VERNIER`docker-compose build

**Total**: 6,700 documents across all collections

- `publications`: 4,527 publications

---

- `institutions`: 1,264 institutions- Password: `123`docker-compose up -d

## Common Tasks and Commands

- `collaborations`: 131 collaborations

### Starting and Stopping

- `stats_pays`: 558 country statistics

Start the dashboard:

```bash

docker-compose up -d

```---### If Database is Empty# 3. Wait 30-60 seconds for database initialization



Stop everything:

```bash

docker-compose down## 🔧 Common Commands

```



### Viewing Logs

```bash```bash# 4. Access the dashboard

See what's happening in real-time:

```bash# Start

docker-compose logs -f

```docker-compose up -d./import-db.shopen http://localhost:8501



View logs for a specific service:

```bash

docker-compose logs mongo# Stop``````

docker-compose logs api

docker-compose logs streamlitdocker-compose down

```



### Checking System Status

# View logs

See if all containers are running:

```bashdocker-compose logs -f---**Default Login:**

docker-compose ps

```



Expected output should show 3 services in "Up" status:# Rebuild- Username: `Flavien VERNIER` (or any researcher name)

- research_db_container

- api_servicedocker-compose build --no-cache

- streamlit_service

## 📋 Prerequisites- Password: `123`

### Verifying Database

# Verify database

Check if the database has data:

```bashdocker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"

```# Should return: 39



You should see: `39`- Docker Desktop installed and running### If Database is Empty After Starting



List all collections and their document counts:# Full reset

```bash

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.getCollectionNames().forEach(col => print(col + ': ' + db[col].countDocuments({})))"docker-compose down -v- Docker Compose v2.0+

```

docker-compose up -d

### Rebuilding from Scratch

```- 4GB RAM minimum```bash

If you need to start fresh:

```bash

# Stop services and delete all data

docker-compose down -v---- 10GB disk space# Run the manual import script



# Rebuild images and start

docker-compose build

docker-compose up -d## 🌐 Access./import-db.sh

```



The database will re-initialize automatically with all data.

- **Dashboard:** http://localhost:8501---```

---

- **API Docs:** http://localhost:8000/docs

## Accessing the Services

- **Health:** http://localhost:8000/health

Once running, you can access:



**Dashboard Interface**

http://localhost:8501---## 🏗️ Architecture---

- Main user interface

- Interactive visualizations

- Data exploration tools

## 📁 Structure

**API Documentation**

http://localhost:8000/docs

- Interactive API explorer

- Try endpoints directly``````## Architecture

- See request/response formats

Dash_MONGODB/

**API Root**

http://localhost:8000├── api/                    # FastAPI backend┌─────────────────────────────────────────┐

- API welcome message

- Version information├── streamlit/             # Streamlit dashboard



---├── mongo-dump/            # Database initialization│   Streamlit Dashboard (Port 8501)      │This application uses a three-tier containerized architecture:



## Troubleshooting│   ├── docker-entrypoint-wrapper.sh



### Problem: Database is Empty│   └── research_db_structure/*.bson│   - Interactive UI                      │



If you log in but see no users or data:├── docs/                  # Documentation



```bash│   ├── TROUBLESHOOTING.md│   - Data Visualizations                 │```

./import-db.sh

```│   └── SETUP_CHECKLIST.md



This script will manually import all data into the database.├── docker-compose.yml└────────────────┬────────────────────────┘MongoDB (Port 27017)



### Problem: Cannot Login├── mongo.Dockerfile       # Custom MongoDB image



First, verify the database has users:├── .env.example                 │    ↓

```bash

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"├── setup.sh              # Optional safety net

```

├── import-db.sh          # Manual DB import┌────────────────▼────────────────────────┐FastAPI REST API (Port 8000)

If it shows `0`, run the import script above.

└── README.md

If it shows `39`, make sure you're using the correct credentials:

- Username: `Flavien VERNIER` (case-sensitive, with space)```│   FastAPI Backend (Port 8000)          │    ↓

- Password: `123`



### Problem: Port Already in Use

---│   - REST API                            │Streamlit Dashboard (Port 8501)

If you see an error about ports already in use, you can change them.



Edit the `.env` file:

```## ⚠️ Troubleshooting│   - JWT Authentication                  │```

MONGO_PORT=27018

API_PORT=8001

STREAMLIT_PORT=8502

```### Database Empty (Rare)└────────────────┬────────────────────────┘



Then restart:

```bash

docker-compose down```bash                 │**Services:**

docker-compose up -d

```./import-db.sh



### Problem: Containers Won't Start```┌────────────────▼────────────────────────┐- **MongoDB:** Database with persistent volume storage



Check the logs for error messages:

```bash

docker-compose logs### Login Fails│   MongoDB Database (Port 27017)        │- **FastAPI:** REST API with JWT authentication

```



Common issues:

- Docker Desktop not running```bash│   - Persistent Storage                  │- **Streamlit:** Interactive web dashboard

- Insufficient memory allocated to Docker

- Conflicting services using the same ports# Verify database has users



### Problem: Slow Performancedocker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"│   - Auto-initialization                 │



Make sure Docker Desktop has enough resources:```

- At least 4GB RAM allocated

- At least 2 CPU cores└─────────────────────────────────────────┘---

- Sufficient disk space available

### Port in Use

For more detailed troubleshooting, see `docs/TROUBLESHOOTING.md`

```

---

Edit `.env`:

## Project Structure

```env## Prerequisites

```

Dash_MONGODB/MONGO_PORT=27018

│

├── README.md                          # This fileAPI_PORT=8001---

├── docker-compose.yml                 # Orchestrates all services

├── mongo.Dockerfile                   # Custom MongoDB with auto-initSTREAMLIT_PORT=8502

├── .env.example                       # Configuration template

├── import-db.sh                       # Manual database import script```- Docker Desktop installed and running

│

├── api/                               # FastAPI backend service

│   ├── api_to_db.py                  # Main API application

│   ├── Dockerfile                     # API container definition**More help:** See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)## 📊 Database- Docker Compose v2.0 or higher

│   └── requirements.txt               # Python dependencies

│

├── streamlit/                         # Streamlit dashboard

│   ├── dash.py                       # Dashboard application---- 4GB RAM available for containers

│   ├── Dockerfile                     # Streamlit container

│   └── requirements.txt               # Python dependencies

│

├── mongo-dump/                        # Database initialization## 🔄 Maintenance**Collections:**- 10GB disk space for data

│   ├── docker-entrypoint-wrapper.sh  # Initialization script

│   └── research_db_structure/        # Database backup files

│       ├── users.bson                # User data

│       ├── chercheurs.bson           # Researcher data### Update- `chercheurs`: 181 researchers

│       ├── publications.bson         # Publication data

│       └── ...                       # Other collections

│

└── docs/                              # Additional documentation```bash- `publications`: 4,527 publications---

    ├── TROUBLESHOOTING.md            # Detailed problem solving

    └── SETUP_CHECKLIST.md            # Verification stepsgit pull

```

docker-compose down- `institutions`: 1,264 institutions

---

docker-compose build

## Updating and Maintenance

docker-compose up -d- `collaborations`: 131 collaborations## Installation

### Pulling Latest Changes

```

If your team has pushed updates:

- `stats_pays`: 558 country statistics

```bash

git pull origin backup-main### Backup

docker-compose down

docker-compose build- `users`: 39 authentication users1. Clone the repository:

docker-compose up -d

``````bash



### Backing Up the Databasedocker-compose exec -T mongo mongodump --db=research_db_structure --out=/data/backup```bash



Create a backup of your current data:docker cp research_db_container:/data/backup ./backups/backup-$(date +%Y%m%d)



```bash```**Data Location:**git clone <repository-url>

docker-compose exec -T mongo mongodump --db=research_db_structure --out=/data/backup

docker cp research_db_container:/data/backup ./backups/backup-$(date +%Y%m%d)

```

---- Persistent Volume: `dash_mongodb_mongodb_data`cd Dash_MONGODB

### Restoring from Backup



If you need to restore a previous backup:

## 📚 Documentation- Initialization Dump: `./mongo-dump/research_db_structure/````

```bash

docker-compose exec -T mongo mongorestore --db=research_db_structure /path/to/backup --drop

```

- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

- [Setup Checklist](docs/SETUP_CHECKLIST.md)

## Configuration

- [API Docs](http://localhost:8000/docs) (when running)---2. Start the services:

The `.env` file controls service configuration. After copying from `.env.example`, you can modify:



**MongoDB Settings**

```---```bash

MONGO_INITDB_DATABASE=research_db_structure  # Database name

MONGO_PORT=27017                              # External port

```

## 🛠️ Technical Notes## 🔧 Common Commandsdocker-compose up -d

**API Settings**

```

API_PORT=8000                                 # External port

JWT_SECRET_KEY=your-secret-key               # Change for production!### Why No Setup Script Needed?```

JWT_ALGORITHM=HS256                           # Token encryption

ACCESS_TOKEN_EXPIRE_MINUTES=30               # Session duration

```

The `mongo.Dockerfile` now handles all permissions:```bash

**Streamlit Settings**

``````dockerfile

STREAMLIT_PORT=8501                           # External port

API_BASE_URL=http://api:8000                 # Internal API addressRUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh \# Start services3. Verify all containers are running:

```

    /docker-entrypoint-initdb.d/init-db.sh

**Important**: Never commit your `.env` file to Git (it's in `.gitignore`). The `.env.example` file is the template for sharing.

```docker-compose up -d```bash

---



## Understanding the Technology

This bakes executable permissions into the Docker image, solving the "Git doesn't preserve permissions" issue.docker-compose ps

**Why Docker?**

- Ensures everyone runs the same environment

- No "works on my machine" problems

- Easy to set up and tear down### Custom MongoDB Image# Stop services```

- Isolates the application from your system



**Why MongoDB?**

- Flexible schema for research dataWe build a custom MongoDB image that:docker-compose down

- Fast queries for large datasets

- JSON-like documents easy to work with1. Copies initialization scripts with correct permissions

- Good for complex nested data structures

2. Includes database dump files (BSON)4. The database will auto-initialize from dump files on first run

**Why FastAPI?**

- Fast and modern Python framework3. Automatically initializes on first run

- Automatic API documentation

- Built-in data validation# View logs

- Easy to test and maintain

---

**Why Streamlit?**

- Quick to build interactive dashboardsdocker-compose logs -f---

- Python-based (matches our backend)

- Built-in widgets and charts**Questions?** Check `docs/` folder or contact the team.

- Good for data science applications



---

# Rebuild containers## Database

## Security Notes

docker-compose build --no-cache

**For Development**

- Default password `123` is intentionally simple**Collections:**

- JWT secret key is generic

- Database has no authentication# Check database user count- chercheurs: 181 researchers

- All services use default ports

docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"- publications: 4,527 publications

**Before Production Deployment**

- Change all passwords to strong values- institutions: 1,264 institutions

- Update JWT_SECRET_KEY to a random string

- Enable MongoDB authentication# Complete reset (deletes all data)- collaborations: 131 collaborations

- Use environment-specific configurations

- Enable HTTPS/TLSdocker-compose down -v- stats_pays: 558 country statistics

- Review security settings in all services

./setup.sh- users: Authentication users

---

docker-compose up -d

## Getting Help

```**Data Location:**

If you encounter issues:

- Persistent Volume: `dash_mongodb_mongodb_data`

1. **Check the logs** - Most problems show error messages

   ```bash---- Auto-initialization: `./mongo-dump/research_db_structure/`

   docker-compose logs

   ```- Backups: `./backups/`



2. **Verify all services are running**## 🌐 Access URLs

   ```bash

   docker-compose ps---

   ```

- **Dashboard:** http://localhost:8501

3. **Check database has data**

   ```bash- **API Documentation:** http://localhost:8000/docs## API Endpoints

   docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"

   ```- **API Health Check:** http://localhost:8000/health



4. **Review documentation**Base URL: http://localhost:8000

   - `docs/TROUBLESHOOTING.md` - Common problems and solutions

   - `docs/SETUP_CHECKLIST.md` - Step-by-step verification---



5. **Start fresh if needed****Authentication:**

   ```bash

   docker-compose down -v## 🔐 Authentication- POST /token - Get JWT access token

   docker-compose build

   docker-compose up -d

   ```

All 39 users in the database have the default password: `123`**Data Endpoints:**

---

- GET /api/chercheurs - List all researchers

## Contributing

Example users:- GET /api/publications - List all publications

When making changes to the project:

- Flavien VERNIER- GET /api/institutions - List all institutions

1. Create a feature branch

2. Make your modifications- Ayoub BOUCHAOUI- GET /api/collaborations - List all collaborations

3. Test with `docker-compose up -d`

4. Commit with clear messages- (See database for full list)- GET /api/stats_pays - Country statistics

5. Push and create a pull request

- GET /api/me - Current user info

Please test that database initialization still works after your changes.

**Production Note:** Change passwords before deploying to production!

---

**Documentation:**

## Technical Details

---- Interactive API docs: http://localhost:8000/docs

**Automatic Database Initialization**



The system uses a custom approach to ensure the database initializes correctly:

## 📁 Project Structure---

1. The `mongo.Dockerfile` builds a custom MongoDB image

2. During build, it sets executable permissions on initialization scripts

3. When the container starts, `docker-entrypoint-wrapper.sh` runs automatically

4. The script waits for MongoDB to be ready```## Configuration

5. It checks if the database is empty

6. If empty, it restores from BSON backup filesDash_MONGODB/

7. All 6 collections are imported with full data

├── api/                    # FastAPI backend**Environment Files:**

This approach solves the common problem where Git doesn't preserve file permissions on shell scripts. By setting permissions in the Dockerfile during image build, we guarantee they're correct on every machine.

│   ├── api_to_db.py

**Why This Matters**

│   ├── DockerfileThe application uses environment files for configuration management:

Previous versions required manual setup scripts that teammates had to remember to run. Now, everything is automatic - you just build and start, and the database populates itself.

│   └── requirements.txt

---

├── streamlit/             # Streamlit dashboard- `.env` - Main configuration file (not committed to git)

## License

│   ├── dash.py- `.env.example` - Template with documentation

[Specify your license here]

│   ├── Dockerfile

---

│   └── requirements.txt**Setup:**

## Contact

├── mongo-dump/            # Database initialization

For questions or issues specific to this project, contact the development team.

│   ├── docker-entrypoint-wrapper.sh1. Copy the example file:

**Last Updated**: October 4, 2025

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
