# 🚀 Quick Setup Guide for Team Members

This guide helps you set up the Research Dashboard on your local machine after pulling from Git.

**✅ Verified Working**: This guide has been tested with a fresh Docker environment. All 39 users can login with password `123### ❌ Database has no data / 0 users

**This is the issue if auto-import didn't work!**

**Quick Fix** - Run the import script:
```bash
./import-db.sh
```

**OR** manually import:
```bash
docker-compose exec -T mongo mongorestore --db=research_db_structure /docker-entrypoint-initdb.d/research_db_structure/ --drop
```

**Verify data was imported:**
```bash
docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
# Should show: 39
```

**For completely fresh start:**
```bash
# Complete cleanup
docker-compose down -v
docker volume rm dash_mongodb_mongodb_data

# Verify mongo-dump exists
ls -la mongo-dump/research_db_structure/
# Should show: users.bson, chercheurs.bson, publications.bson, etc.

# Fresh start
docker-compose up -d

# Wait for services to be healthy, then import
./import-db.sh
```CAL: Clean Docker Environment First!

**If you've run this project before**, you MUST clean up old Docker data first to avoid authentication errors!

The database auto-initializes ONLY on first run. Old volumes contain outdated user passwords.

---

## 📋 Prerequisites

- Docker Desktop installed and running
- Git repository cloned
- Terminal/Command Prompt access

---

## 🛠️ Setup Steps

### Step 1: Navigate to Project Directory

```bash
cd Dash_MONGODB
```

### Step 2: Clean Up Docker Environment (CRITICAL IF NOT FIRST TIME!)

**⚠️ If this is your first time running the project**, skip to Step 3.

**⚠️ If you've run this before or getting authentication errors**, clean everything:

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove the specific MongoDB volume (if it still exists)
docker volume rm dash_mongodb_mongodb_data

# Optional: Remove old containers
docker rm -f research_db_container api_service streamlit_service
```

**Why this is necessary:**
- The MongoDB volume persists between runs
- Auto-initialization (`mongo-dump/`) only works on FIRST startup with empty volume
- Old volumes have different/missing passwords
- Without cleanup, you'll get "authentication failed" errors

### Step 3: Copy Environment File

```bash
cp .env.example .env
```

You can edit `.env` if needed, but defaults should work fine.

### Step 4: Build Docker Images (First Time Only)

**First time setup** - Build the optimized Docker images:

```bash
docker-compose build
```

This takes **2-3 minutes** on first run. You'll see:
- Building API image (~302MB final size)
- Building Streamlit image (~810MB final size)

**Subsequent runs**: Images are cached, so this step is instant (0.5s).

### Step 5: Start Services

```bash
docker-compose up -d
```

This will:
- Create MongoDB volume
- Auto-import database with all users and data (from `mongo-dump/`)
- Start all 3 services (mongo, api, streamlit)

### Step 6: Wait for Services to Start

```bash
# Check status (wait for "healthy" status)
docker-compose ps
```

Wait until you see:
```
api_service         Up X minutes (healthy)
streamlit_service   Up X minutes (healthy)
```

### Step 6b: Import Database (If Auto-Import Didn't Work)

**If the database didn't auto-import** (you can't login), run this script:

```bash
./import-db.sh
```

This will manually import all the database collections and users.

**Alternative - Manual command**:
```bash
docker-compose exec -T mongo mongorestore --db=research_db_structure /docker-entrypoint-initdb.d/research_db_structure/ --drop
```

### Step 7: Access the Dashboard

Open your browser: **http://localhost:8501**

---

## 🔑 Login Credentials

**All 39 users have the same password**: `123`

### Example Users:

- Username: `Flavien VERNIER` | Password: `123`
- Username: `Abdourrahmane ATTO` | Password: `123`
- Username: `Alexandre BENOIT` | Password: `123`
- Username: `Kavé SALAMATIAN` | Password: `123`

**Important**: Use exact username format with:
- First name with capital first letter
- Space
- LAST NAME IN UPPERCASE
- Accents where applicable (é, è, etc.)

---

## 🧪 Verify Installation

### Test API:
```bash
curl http://localhost:8000/
```

Expected: `{"message": "Bienvenue sur l'API de recherche scientifique"}`

### Test Authentication:
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=Flavien VERNIER&password=123"
```

Expected: JSON with `access_token` and `token_type: bearer`

### Check Database:
```bash
docker-compose exec mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
```

Expected: `39`

---

## 📊 Database Information

- **Database**: `research_db_structure`
- **Collections**: 6
- **Total Documents**: 6,700
  - users: 39
  - chercheurs: 181
  - collaborations: 131
  - institutions: 1,264
  - stats_pays: 558
  - publications: 4,527

---

## 🔧 Troubleshooting

### ❌ "Authentication failed" / "Incorrect username or password"

**This is the most common issue!**

**Cause**: Old Docker volume with outdated passwords

**Solution** (Clean Docker environment):
```bash
# Step 1: Stop everything and remove volumes
docker-compose down -v

# Step 2: Verify volume is removed
docker volume ls | grep mongodb_data
# (should return nothing)

# Step 3: If volume still exists, force remove it
docker volume rm dash_mongodb_mongodb_data

# Step 4: Fresh start
docker-compose up -d

# Step 5: Wait for healthy status
docker-compose ps
```

**Explanation**: The `mongo-dump/` folder auto-imports data ONLY when the volume is created for the first time. If you have an old volume, it contains old data and won't re-import.

### ❌ Services not starting

**Check logs**:
```bash
docker-compose logs api
docker-compose logs streamlit
docker-compose logs mongo
```

Common issues:
- MongoDB needs 10-15 seconds to initialize on first run
- Wait for "healthy" status before accessing dashboard

### ❌ "Port already in use"

**Change ports in `.env` file**:
```properties
MONGO_PORT=27018
API_PORT=8001
STREAMLIT_PORT=8502
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### ❌ Images too large / slow build

This is normal on first build. Optimized images:
- API: ~302MB
- Streamlit: ~810MB

Subsequent builds use cache and are much faster.

**Want to rebuild from scratch?** (Removes cached layers):
```bash
docker-compose build --no-cache
```

**Remove old images completely** (Forces fresh build next time):
```bash
# List images
docker images | grep dash_mongodb

# Remove specific images
docker rmi dash_mongodb-api dash_mongodb-streamlit

# Or remove all unused images
docker image prune -a
```

### ❌ Database has no data / 0 users

**Cause**: Auto-initialization didn't run

**Solution**:
```bash
# Complete cleanup
docker-compose down -v
docker volume rm dash_mongodb_mongodb_data

# Verify mongo-dump exists
ls -la mongo-dump/research_db_structure/
# Should show: users.bson, chercheurs.bson, publications.bson, etc.

# Fresh start - initialization happens automatically
docker-compose up -d

# Verify data loaded (should show 39)
docker-compose exec mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})"
```

---

## 🛑 Stopping Services

```bash
# Stop services (keeps data)
docker-compose down

# Stop and remove volumes (fresh start next time)
docker-compose down -v
```

---

## 📚 Additional Resources

- **API Endpoints**: http://localhost:8000/docs (FastAPI auto-docs)
- **Dashboard**: http://localhost:8501
- **MongoDB**: localhost:27017

---

## 🆘 Still Having Issues?

1. Make sure Docker Desktop is running
2. Try the cleanup script: `./cleanup.sh`
3. Check Docker disk space: `docker system df`
4. Clean Docker system: `docker system prune -a` (removes all unused images)
5. Contact the team lead

---

## ✅ Success Indicators

You're ready when you see:

✅ All 3 containers running: `docker-compose ps`
✅ Both services showing "(healthy)" status
✅ Dashboard accessible at http://localhost:8501
✅ Can login with any username + password `123`

**Happy developing! 🎉**
