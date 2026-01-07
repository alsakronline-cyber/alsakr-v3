#!/bin/bash

# Al Sakr Online - V2 Setup Script
# Initializes the directory structure and copies base files

PROJECT_ROOT="./v2_project"

echo "🚀 Initializing Al Sakr Online V2..."

# 1. Create Folder Structure
mkdir -p $PROJECT_ROOT/backend/app/agents
mkdir -p $PROJECT_ROOT/backend/app/core
mkdir -p $PROJECT_ROOT/backend/app/api
mkdir -p $PROJECT_ROOT/frontend/app/command-center
mkdir -p $PROJECT_ROOT/frontend/app/vendor/marketplace
mkdir -p $PROJECT_ROOT/data/scraped
mkdir -p $PROJECT_ROOT/data/manuals

echo "✅ Directories Created."

# 2. Copy Docker Config
cp ./docker-compose.yml $PROJECT_ROOT/

# 3. Create Placeholder Files (To be filled by the Agent)
touch $PROJECT_ROOT/backend/requirements.txt
touch $PROJECT_ROOT/backend/Dockerfile
touch $PROJECT_ROOT/frontend/package.json

echo "✨ Scaffolding Complete at $PROJECT_ROOT"
echo "👉 Next Step: Run 'docker-compose up -d' inside $PROJECT_ROOT"
