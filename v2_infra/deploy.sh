#!/bin/bash

# Al Sakr V3 - Deployment Script
# ------------------------------
# 1. Pulls latest changes
# 2. Stops old containers
# 3. Prunes unused docker objects
# 4. Starts new stack (Open WebUI + Postgres + Haystack)

echo "🚀 Starting Deployment..."

# Git Pull
git pull origin main

# Stop Old Stack
echo "🛑 Stopping containers..."
cd v2_infra
docker-compose down

# Cleanup
echo "🧹 Cleaning up..."
docker system prune -f

# Start New Stack
echo "🔥 Igniting V3 Engine..."
docker-compose up -d --build

echo "✅ Deployment Complete!"
echo "👉 Open WebUI: http://localhost:3000"
echo "👉 n8n Workflow: http://localhost:5678"
