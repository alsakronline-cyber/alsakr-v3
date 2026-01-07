#!/bin/bash

# Al Sakr Online - VPS Cleanup Script
# CAUTION: This will WIPE all Docker data. Use only for a fresh install.

echo "⚠️  WARNING: This will delete ALL Docker containers, volumes, and networks."
echo "⚠️  Are you sure you want to proceed? (y/n)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "🛑 Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null

echo "🗑️  Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null

echo "🧹 Pruning Docker System (Images, Volumes, Networks)..."
# Force prune everything to reclaim Oracle VPS disk space
docker system prune -a --volumes -f

echo "✨ System Cleaned."
echo "Free Disk Space:"
df -h /
