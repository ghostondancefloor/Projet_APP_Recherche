#!/bin/bash
# Wrapper script for MongoDB entrypoint
# This runs AFTER MongoDB starts and imports data if needed

set -e

# Start MongoDB in background using original entrypoint
/usr/local/bin/docker-entrypoint.sh mongod --bind_ip_all &
MONGO_PID=$!

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to start..."
for i in {1..30}; do
    if mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "MongoDB is ready!"
        break
    fi
    sleep 2
    echo "Waiting for MongoDB..."
done

# Check if database needs initialization
USER_COUNT=$(mongosh research_db_structure --quiet --eval "db.users.countDocuments({})" 2>/dev/null || echo "0")

if [ "$USER_COUNT" = "0" ]; then
    echo "Database is empty, importing data..."
    mongorestore --db=research_db_structure /docker-entrypoint-initdb.d/research_db_structure/
    
    # Verify import succeeded
    sleep 2
    FINAL_COUNT=$(mongosh research_db_structure --quiet --eval 'db.users.countDocuments({})' 2>/dev/null || echo "0")
    echo "Database import completed! Users imported: $FINAL_COUNT"
else
    echo "Database already initialized with $USER_COUNT users"
fi

# Keep MongoDB running in foreground
wait $MONGO_PID
