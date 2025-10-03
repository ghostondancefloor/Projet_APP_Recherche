# Deployment Checklist

Quick reference checklist for deployment upgrades and maintenance tasks.

---

## Pre-Deployment Checklist

- [ ] Review all planned changes in DEPLOYMENT_UPGRADES.md
- [ ] Backup current database state
- [ ] Backup current configuration files
- [ ] Test changes in local development environment
- [ ] Document expected downtime (if any)
- [ ] Notify team members of planned deployment
- [ ] Prepare rollback plan

---

## Upgrade 1: Docker Volume Fix - Completed

**Status:** COMPLETED - October 3, 2025

- [x] Stop all running containers
- [x] Create backup of current data
- [x] Update docker-compose.yml volume configuration
- [x] Change volume mapping to mongodb_data:/data/db
- [x] Add auto-initialization configuration
- [x] Add environment variable for database name
- [x] Start containers with new configuration
- [x] Verify volume creation
- [x] Restore database from backup
- [x] Test data persistence with restart
- [x] Test data persistence with full shutdown
- [x] Verify all collections intact
- [x] Update documentation

**Verification:**
- Volume exists: dash_mongodb_mongodb_data
- Document count: 6,700 total
- Restart test: PASSED
- Shutdown test: PASSED

---

## Upgrade 2: Environment Configuration

**Status:** NOT STARTED

- [ ] Create .env file with all variables
- [ ] Create .env.example template
- [ ] Move MONGO_URI to environment variable
- [ ] Move JWT_SECRET_KEY to environment variable
- [ ] Move API_BASE_URL to environment variable
- [ ] Update docker-compose.yml to use env_file
- [ ] Create .env.production for production
- [ ] Add .env to .gitignore
- [ ] Test with development environment
- [ ] Test with production environment
- [ ] Verify no secrets in version control
- [ ] Update documentation

---

## Upgrade 3: Container Health Checks

**Status:** NOT STARTED

- [ ] Add MongoDB health check to docker-compose.yml
- [ ] Add API health check to docker-compose.yml
- [ ] Add Streamlit health check to docker-compose.yml
- [ ] Configure depends_on with health conditions
- [ ] Test health check success scenarios
- [ ] Test health check failure scenarios
- [ ] Verify automatic restart on failures
- [ ] Update documentation

---

## Upgrade 4: Health Endpoints

**Status:** NOT STARTED

- [ ] Add /health endpoint to FastAPI
- [ ] Implement database connectivity test
- [ ] Return proper status codes (200/503)
- [ ] Add timestamp to health response
- [ ] Add version info to health response
- [ ] Test health endpoint manually
- [ ] Test health endpoint with curl
- [ ] Integrate with Docker health checks
- [ ] Update API documentation
- [ ] Update deployment documentation

---

## Upgrade 5: Resource Limits

**Status:** NOT STARTED

- [ ] Add MongoDB resource limits (1 CPU, 1GB RAM)
- [ ] Add API resource limits (0.5 CPU, 512MB RAM)
- [ ] Add Streamlit resource limits (0.5 CPU, 512MB RAM)
- [ ] Configure resource reservations
- [ ] Test services with limits applied
- [ ] Monitor resource usage
- [ ] Adjust limits if needed
- [ ] Update documentation

---

## Upgrade 6: Multi-Stage Builds

**Status:** NOT STARTED

- [ ] Create multi-stage Dockerfile for API
- [ ] Create multi-stage Dockerfile for Streamlit
- [ ] Separate build and production stages
- [ ] Add non-root user to images
- [ ] Test image builds
- [ ] Compare image sizes before/after
- [ ] Test container functionality
- [ ] Update build instructions
- [ ] Update documentation

---

## Upgrade 7: Production Compose

**Status:** NOT STARTED

- [ ] Create docker-compose.prod.yml
- [ ] Configure production resource limits
- [ ] Add production logging configuration
- [ ] Remove development features
- [ ] Add production restart policies
- [ ] Test production configuration
- [ ] Create production deployment script
- [ ] Update deployment documentation

---

## Upgrade 8: Security Hardening

**Status:** NOT STARTED

- [ ] Add non-root user to Dockerfiles
- [ ] Switch to slim base images
- [ ] Create .dockerignore files
- [ ] Remove unnecessary packages
- [ ] Scan images for vulnerabilities
- [ ] Fix identified vulnerabilities
- [ ] Test security improvements
- [ ] Update security documentation

---

## Upgrade 9: Logging Configuration

**Status:** NOT STARTED

- [ ] Add logging driver to MongoDB
- [ ] Add logging driver to API
- [ ] Add logging driver to Streamlit
- [ ] Configure log rotation settings
- [ ] Set up structured logging in API
- [ ] Test log collection
- [ ] Verify log rotation works
- [ ] Update documentation

---

## Upgrade 10: Development Tools

**Status:** NOT STARTED

- [ ] Create docker-compose.override.yml
- [ ] Configure hot reload for API
- [ ] Configure hot reload for Streamlit
- [ ] Add source code volume mounts
- [ ] Add development debugging tools
- [ ] Test hot reload functionality
- [ ] Update development setup guide
- [ ] Update documentation

---

## Post-Deployment Verification

After each upgrade deployment:

- [ ] All containers running: `docker-compose ps`
- [ ] No errors in logs: `docker-compose logs`
- [ ] Database accessible: Test connection
- [ ] API responding: `curl http://localhost:8000/health`
- [ ] Dashboard accessible: http://localhost:8501
- [ ] Login functionality working
- [ ] Data integrity verified
- [ ] Performance acceptable
- [ ] No resource warnings
- [ ] Documentation updated

---

## Regular Maintenance Checklist

Weekly:
- [ ] Check container health status
- [ ] Review logs for errors
- [ ] Monitor disk space usage
- [ ] Verify backup completion

Monthly:
- [ ] Create database backup
- [ ] Review resource usage trends
- [ ] Update dependencies
- [ ] Review security advisories
- [ ] Test disaster recovery

Quarterly:
- [ ] Full system backup
- [ ] Review and update documentation
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Capacity planning review

---

## Emergency Rollback Procedure

If critical issues occur after deployment:

1. [ ] Stop all containers: `docker-compose down`
2. [ ] Identify the problematic change
3. [ ] Revert configuration files to previous version
4. [ ] Restore data from latest backup (if needed)
5. [ ] Start containers: `docker-compose up -d`
6. [ ] Verify service functionality
7. [ ] Document the issue and resolution
8. [ ] Plan fix for next deployment

---

## Common Commands

**View running containers:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker-compose logs [service]
docker-compose logs -f [service]  # Follow logs
```

**Restart services:**
```bash
docker-compose restart
docker-compose restart [service]
```

**Stop and remove containers:**
```bash
docker-compose down
```

**Start containers:**
```bash
docker-compose up -d
```

**Rebuild and start:**
```bash
docker-compose up -d --build
```

**Check volume status:**
```bash
docker volume ls
docker volume inspect dash_mongodb_mongodb_data
```

**Database backup:**
```bash
docker exec research_db_container mongodump --out=/dump/backup-$(date +%Y%m%d)
docker cp research_db_container:/dump/backup-YYYYMMDD ./backups/
```

---

## Contact and Escalation

For deployment issues:
1. Check this checklist and DEPLOYMENT_UPGRADES.md
2. Review Docker logs for errors
3. Attempt rollback if critical
4. Document issue for team review

---

Last Updated: October 3, 2025
