#!/bin/bash

################################################################################
# Quick Deploy Script - For Rapid Updates
# Use this for quick redeployments after code changes
################################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Redeploy Starting...${NC}\n"

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin v2-industrial-ai

# Navigate to infra
cd alsakr_v2/v2_infra

# Rebuild and restart
echo "🔨 Rebuilding containers..."
docker-compose -f docker-compose.prod.yml build

echo "♻️  Restarting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services..."
sleep 10

# Health check
echo "🏥 Checking health..."
curl -s http://localhost:8000/api/health | python3 -m json.tool

echo -e "\n${GREEN}✅ Redeploy complete!${NC}"
echo "View logs: docker-compose logs -f"
