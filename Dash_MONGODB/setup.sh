#!/bin/bash
# Setup script for team members cloning the project
# Fixes file permissions and creates .env file

set -e

echo "=================================================="
echo "  Research Dashboard - Setup"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Step 1: Fix script permissions
echo "🔧 [1/4] Setting executable permissions..."
chmod +x mongo-dump/docker-entrypoint-wrapper.sh
chmod +x mongo-dump/init-db.sh
chmod +x import-db.sh
chmod +x scripts/*.sh 2>/dev/null || true
echo "   ✅ Done"
echo ""

# Step 2: Create .env file
echo "🔧 [2/4] Checking environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✅ Created .env file"
else
    echo "   ✅ .env already exists"
fi
echo ""

# Step 3: Clean old Docker data
echo "🔧 [3/4] Cleaning old Docker data..."
if docker volume ls | grep -q "dash_mongodb_mongodb_data"; then
    docker-compose down -v 2>/dev/null || true
    docker volume rm dash_mongodb_mongodb_data 2>/dev/null || true
    echo "   ✅ Old data cleaned"
else
    echo "   ✅ No old data (fresh install)"
fi
echo ""

# Step 4: Verify BSON files
echo "🔧 [4/4] Verifying database files..."
BSON_COUNT=$(find mongo-dump/research_db_structure -name "*.bson" 2>/dev/null | wc -l | xargs)
if [ "$BSON_COUNT" -ge 5 ]; then
    echo "   ✅ Found $BSON_COUNT BSON files"
else
    echo "   ⚠️  WARNING: Only $BSON_COUNT BSON files found!"
fi
echo ""

echo "=================================================="
echo "  ✅ SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  docker-compose build"
echo "  docker-compose up -d"
echo "  # Wait 60 seconds"
echo "  open http://localhost:8501"
echo ""
echo "Login: Flavien VERNIER / 123"
echo ""
echo "If database is empty: ./import-db.sh"
echo "=================================================="
