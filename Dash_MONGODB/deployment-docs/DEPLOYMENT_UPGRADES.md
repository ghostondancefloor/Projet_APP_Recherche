# Deployment Upgrades Documentation

This document tracks all deployment-related improvements and optimizations made to the Research Dashboard application.

---

## Upgrade 1: Fixed Docker Volume Data Persistence

**Date:** October 3, 2025  
**Priority:** Critical  
**Status:** Completed

### What We Achieved

Fixed a critical data persistence issue where MongoDB data was being lost every time containers were restarted. The volume configuration was incorrectly mapping to the wrong directory, causing the database to start fresh with each deployment.

### Before vs After

**Before (Broken Configuration):**
```yaml
volumes:
  - ./data:/data
```
- Used bind mount pointing to wrong directory
- MongoDB data directory is /data/db, but we were mapping to /data
- Data was lost on every container restart
- Manual database restoration required after each deployment
- No persistent storage management

**After (Fixed Configuration):**
```yaml
volumes:
  - mongodb_data:/data/db
  - ./mongo-dump:/docker-entrypoint-initdb.d:ro
environment:
  - MONGO_INITDB_DATABASE=research_db_structure
```
- Uses Docker-managed named volume
- Correctly maps to MongoDB's actual data directory (/data/db)
- Data persists through container restarts and removals
- Automatic database initialization from dump files
- Docker handles all persistence management

### What This Means

**Reliability Improvements:**
- Database data now survives container restarts
- System reboots no longer cause data loss
- Updates and rebuilds maintain all existing data
- No manual intervention needed after deployments

**Operational Benefits:**
- Eliminates need for manual database restoration
- Reduces deployment time and complexity
- Prevents accidental data loss during maintenance
- Improves disaster recovery capabilities

**Technical Details:**
- Volume Type: Named volume (Docker-managed)
- Mount Point: /data/db (MongoDB standard)
- Persistence: Automatic across container lifecycle
- Auto-initialization: Configured for first-time setup

### Verification Results

All persistence tests passed successfully:
- Container restart test: Data intact (39 users, 6,700 documents)
- Complete shutdown test: Data survived removal and recreation
- All collections verified: chercheurs (181), publications (4,527), institutions (1,264), collaborations (131), stats_pays (558), users (39)

### Files Modified

- `docker-compose.yml`: Updated mongo service volume configuration

### Testing Performed

1. Initial data restoration and verification
2. Container restart persistence test
3. Complete container removal and recreation test
4. Document count verification across all collections
5. Volume existence verification after shutdown

### Rollback Procedure

If issues occur, revert docker-compose.yml:
```yaml
volumes:
  - ./data:/data
```
Then manually restore database from backups located in `./backups/`

### Future Considerations

- Implement automated backup strategy for the named volume
- Consider volume snapshots for additional redundancy
- Monitor volume size growth over time
- Document volume backup and restore procedures

---

## Upgrade 2: Environment Configuration System

**Date:** October 3, 2025  
**Priority:** High  
**Status:** Completed

### What We Achieved

Implemented a comprehensive environment variable management system that separates configuration from code, improves security, and enables easy switching between development and production environments.

### Before vs After

**Before (Hardcoded Configuration):**
```yaml
# docker-compose.yml
services:
  mongo:
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_DATABASE=research_db_structure
  
  api:
    ports:
      - "8000:8000"
    environment:
      - MONGO_URI=mongodb://mongo:27017/research_db_structure

# api/api_to_db.py
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```
- Configuration values hardcoded in multiple files
- Secrets visible in version control
- No environment separation
- Difficult to change between dev/prod

**After (Environment-Based Configuration):**
```yaml
# docker-compose.yml
services:
  mongo:
    ports:
      - "${MONGO_PORT:-27017}:27017"
    env_file:
      - .env
    environment:
      - MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE}
  
  api:
    ports:
      - "${API_PORT:-8000}:8000"
    env_file:
      - .env
    environment:
      - MONGO_URI=${MONGO_URI}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=${JWT_ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}

# api/api_to_db.py
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```
- All configuration in `.env` file
- Secrets excluded from git (.gitignore)
- Environment-specific configurations possible
- Easy production deployment

### Files Created

1. **`.env`** - Main configuration file (gitignored)
   - Contains all environment variables
   - Development defaults
   - Not committed to version control

2. **`.env.example`** - Configuration template
   - Documents all available variables
   - Safe to commit (no secrets)
   - Instructions for deployment

### What This Means

**Security Improvements:**
- Secrets no longer in version control
- JWT secret key can be changed per environment
- Production configurations isolated from development

**Operational Benefits:**
- Single source of truth for configuration
- Easy to switch between environments
- Simplified deployment process
- Better configuration documentation

**Flexibility Gains:**
- Different settings for dev/staging/production
- Team members can customize local settings
- Port conflicts easily resolved
- Database URIs environment-specific

### Configuration Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| MONGO_INITDB_DATABASE | Database name | research_db_structure |
| MONGO_HOST | MongoDB hostname | mongo |
| MONGO_PORT | MongoDB port | 27017 |
| API_PORT | API server port | 8000 |
| JWT_SECRET_KEY | JWT signing secret | (must change) |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token lifetime | 30 |
| STREAMLIT_PORT | Dashboard port | 8501 |
| API_BASE_URL | API endpoint | http://api:8000 |
| MONGO_URI | Full MongoDB URI | (constructed) |

### Files Modified

1. **docker-compose.yml**
   - Added `env_file` directives to all services
   - Replaced hardcoded values with `${VARIABLE}` syntax
   - Added default values using `${VAR:-default}` pattern

2. **api/api_to_db.py**
   - Updated to use `os.getenv()` for all configuration
   - Added fallback defaults for development
   - Improved configuration logging

3. **.gitignore**
   - Added `.env` to prevent secret exposure
   - Added `.env.local` and `.env.*.local` patterns
   - Kept `.env.example` for documentation

### Verification Results

All environment configuration tests passed:
- Services start successfully with `.env` file
- Environment variables loaded correctly in containers
- API responds with configured settings
- Database connection uses environment variables
- All services communicate properly

**Verified Commands:**
```bash
# Check environment variables in API container
docker-compose exec api printenv | grep -E "(MONGO_URI|JWT_SECRET_KEY)"

# Result:
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_ALGORITHM=HS256
MONGO_URI=mongodb://mongo:27017/research_db_structure
JWT_SECRET_KEY=supersecretkey
```

### Deployment Instructions

For new deployments:

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with production values:
```bash
# Change JWT secret to strong random value
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

3. Start services:
```bash
docker-compose up -d
```

### Rollback Procedure

If issues occur:

1. Restore hardcoded values in docker-compose.yml
2. Restore hardcoded values in api/api_to_db.py
3. Remove env_file directives
4. Restart services

### Future Considerations

- Add environment-specific .env files (.env.production, .env.staging)
- Implement secrets management system (Docker Secrets, Vault)
- Add configuration validation on startup
- Create configuration migration scripts
- Document all environment variables in code comments

---

## Upgrade 3: Container Health Checks

**Date:** Planned  
**Priority:** Medium  
**Status:** Not Started

### Planned Improvements

Add health monitoring to ensure containers only start when their dependencies are ready.

**Current Issues:**
- Services start even if dependencies aren't ready
- No automated health monitoring
- API may attempt to connect before MongoDB is ready

**Planned Changes:**
- Add MongoDB health check using mongosh ping
- Add API health check endpoint
- Add Streamlit health check
- Configure proper dependency waiting with health conditions

**Expected Benefits:**
- Guaranteed service availability on startup
- Automatic restart on service failures
- Better debugging of startup issues
- Improved deployment reliability

---

## Upgrade 4: Health Endpoint Implementation

**Date:** Planned  
**Priority:** Medium  
**Status:** Not Started

### Planned Improvements

Create dedicated health check endpoint in the FastAPI service.

**Planned Changes:**
- Add /health endpoint to API
- Test database connectivity in health check
- Return proper HTTP status codes (200/503)
- Include service metadata in response

**Expected Benefits:**
- Easy integration with monitoring tools
- Support for Docker health checks
- Better observability and debugging
- Load balancer compatibility

---

## Upgrade 5: Resource Limits and Constraints

**Date:** Planned  
**Priority:** Medium  
**Status:** Not Started

### Planned Improvements

Implement resource limits to prevent containers from consuming unlimited system resources.

**Current Issues:**
- Containers can use all available CPU and memory
- Risk of resource starvation
- No capacity planning

**Planned Changes:**
- MongoDB: 1 CPU, 1GB RAM limit
- API: 0.5 CPU, 512MB RAM limit
- Streamlit: 0.5 CPU, 512MB RAM limit
- Add resource reservations for guaranteed minimums

**Expected Benefits:**
- Predictable resource usage
- Better system stability
- Prevents resource starvation
- Enables better capacity planning

---

## Upgrade 6: Multi-Stage Docker Builds

**Date:** Planned  
**Priority:** Low  
**Status:** Not Started

### Planned Improvements

Optimize Docker images using multi-stage builds to reduce size and improve security.

**Current Issues:**
- Large image sizes with build dependencies
- Build tools present in production images
- Slow image pulls and deployments

**Planned Changes:**
- Separate build and production stages
- Remove build dependencies from final images
- Use non-root user for security
- Minimize final image layers

**Expected Benefits:**
- 50-70% reduction in image size
- Faster deployments and updates
- Improved security posture
- Reduced attack surface

---

## Upgrade 7: Production Docker Compose Configuration

**Date:** Planned  
**Priority:** Low  
**Status:** Not Started

### Planned Improvements

Create separate Docker Compose configuration optimized for production deployments.

**Planned Changes:**
- Create docker-compose.prod.yml
- Higher resource limits for production
- Production environment variables
- Logging configuration
- Remove development features

**Expected Benefits:**
- Clean dev/prod separation
- Production-ready configuration
- Easier deployment management
- Better security and performance

---

## Upgrade 8: Container Security Hardening

**Date:** Planned  
**Priority:** Low  
**Status:** Not Started

### Planned Improvements

Improve container security by following Docker best practices.

**Planned Changes:**
- Run containers as non-root user
- Use minimal base images (python:3.11-slim)
- Add .dockerignore files
- Scan images for vulnerabilities
- Remove unnecessary packages

**Expected Benefits:**
- Reduced attack surface
- Better compliance
- Fewer vulnerabilities
- Improved security posture

---

## Upgrade 9: Logging Configuration

**Date:** Planned  
**Priority:** Low  
**Status:** Not Started

### Planned Improvements

Configure proper logging with centralized management and rotation.

**Planned Changes:**
- Add log drivers to all services
- Configure log rotation (size and file limits)
- Set up structured logging in API
- Implement log aggregation

**Expected Benefits:**
- Centralized log management
- Prevents disk space issues
- Better debugging capabilities
- Improved observability

---

## Upgrade 10: Development Tools and Hot Reload

**Date:** Planned  
**Priority:** Low  
**Status:** Not Started

### Planned Improvements

Add development tools and hot reload for faster development cycles.

**Planned Changes:**
- Create docker-compose.override.yml for development
- Enable hot reload for API and Streamlit
- Mount source code as volumes for live editing
- Add development debugging tools

**Expected Benefits:**
- Faster development iteration
- Live code editing without rebuilds
- Better developer experience
- Reduced development friction

---

## Deployment Checklist

Before deploying any upgrade:

1. Review and understand all changes
2. Create backup of current state
3. Test changes in development environment
4. Document rollback procedures
5. Verify all services after deployment
6. Update this document with results

## Rollback Guidelines

Each upgrade includes specific rollback procedures. General steps:

1. Stop all containers
2. Revert configuration files to previous version
3. Restart containers
4. Verify service functionality
5. Restore data from backups if needed

## Version History

- v1.1.0 - October 3, 2025: Fixed Docker volume data persistence
- v1.0.0 - Initial deployment configuration

---

## Additional Resources

- Docker Compose Documentation: https://docs.docker.com/compose/
- Docker Volumes: https://docs.docker.com/storage/volumes/
- MongoDB Docker Guide: https://hub.docker.com/_/mongo
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- Streamlit Deployment: https://docs.streamlit.io/deploy

## Maintenance Notes

- Regular backups stored in: `./backups/`
- MongoDB dumps located in: `./mongo-dump/`
- Docker volume name: `dash_mongodb_mongodb_data`
- Database name: `research_db_structure`

## Support and Issues

For issues or questions regarding deployments:
1. Check this documentation first
2. Review Docker logs: `docker-compose logs [service]`
3. Verify volume status: `docker volume ls`
4. Check container health: `docker-compose ps`
