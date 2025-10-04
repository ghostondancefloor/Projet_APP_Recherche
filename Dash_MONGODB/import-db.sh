#!/bin/bash
# Manual database import script
# Run this if the database is empty after starting services

set -e

echo "=================================================="
echo "  Database Import Script"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: Services not running!"
    echo "   Run: docker-compose up -d"
    exit 1
fi

# Check current database state
echo "📊 Checking database..."
USER_COUNT=$(docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})" 2>/dev/null || echo "0")
echo "   Current users: $USER_COUNT"
echo ""

if [ "$USER_COUNT" -eq "0" ]; then
    # Verify BSON files exist
    if [ ! -f "mongo-dump/research_db_structure/users.bson" ]; then
        echo "❌ Error: Database dump files not found!"
        echo "   Expected: mongo-dump/research_db_structure/"
        exit 1
    fi
    
    echo "🔄 Importing database..."
    docker-compose exec -T mongo mongorestore \
        --db=research_db_structure \
        /docker-entrypoint-initdb.d/research_db_structure/ \
        --drop
    
    echo ""
    NEW_COUNT=$(docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})")
    
    echo "=================================================="
    echo "  ✅ SUCCESS!"
    echo "=================================================="
    echo "  Users imported: $NEW_COUNT"
    echo "  Password for all users: 123"
    echo ""
    echo "  Login at: http://localhost:8501"
    echo "  Username: Flavien VERNIER"
    echo "  Password: 123"
    echo "=================================================="
else
    echo "=================================================="
    echo "  ℹ️  Database Already Has Data"
    echo "=================================================="
    echo "  Users in database: $USER_COUNT"
    echo ""
    echo "  To re-import from scratch:"
    echo "  1. docker-compose down -v"
    echo "  2. docker-compose up -d"
    echo "  3. Wait 60 seconds"
    echo "=================================================="
fi
