#!/bin/bash
# MongoDB initialization script - imports all BSON files

set -e

echo "Starting database initialization..."

# Check if we're already initialized
if mongosh research_db_structure --quiet --eval "db.users.countDocuments({})" | grep -q "^0$"; then
    echo "Database is empty, importing data..."
    
    # Import all collections
    mongorestore --db=research_db_structure /docker-entrypoint-initdb.d/research_db_structure/
    
    echo "Data import completed successfully!"
else
    echo "Database already initialized, skipping import."
fi
