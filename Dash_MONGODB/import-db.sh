#!/bin/bash
# Manual database import script for teammates
# Run this if the database is empty after starting services

set -e

echo "=================================================="
echo "  MongoDB Database Import Script"
echo "=================================================="
echo ""

# Check if Docker Compose services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: Services are not running!"
    echo "   Please run: docker-compose up -d"
    exit 1
fi

echo "📊 Checking current database state..."
USER_COUNT=$(docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})" 2>/dev/null || echo "0")

echo "   Current users in database: $USER_COUNT"
echo ""

if [ "$USER_COUNT" -eq "0" ]; then
    echo "🔄 Database is empty. Importing data..."
    echo ""
    
    docker-compose exec -T mongo mongorestore \
        --db=research_db_structure \
        /docker-entrypoint-initdb.d/research_db_structure/ \
        --drop
    
    echo ""
    echo "✅ Import completed! Verifying..."
    
    NEW_COUNT=$(docker-compose exec -T mongo mongosh research_db_structure --quiet --eval "db.users.countDocuments({})")
    
    echo ""
    echo "=================================================="
    echo "  ✅ SUCCESS!"
    echo "=================================================="
    echo "  Users imported: $NEW_COUNT"
    echo "  All users have password: 123"
    echo ""
    echo "  Test login:"
    echo "  - Open: http://localhost:8501"
    echo "  - Username: Flavien VERNIER"
    echo "  - Password: 123"
    echo "=================================================="
else
    echo "✅ Database already has data ($USER_COUNT users)"
    echo "   No import needed."
    echo ""
    echo "   If you need to re-import, run:"
    echo "   docker-compose down -v && docker-compose up -d"
    echo "   Then run this script again."
fi
