#!/bin/bash

# Configuration
PROJECT_DIR="/home/ubuntu/alsakr-online/alsakr_v2"
DATA_DIR="$PROJECT_DIR/v2_infra/pb_data"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/pb_backup_$TIMESTAMP.tar.gz"
RETENTION_DAYS=7

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "========================================================"
echo "Starting Backup at $TIMESTAMP"
echo "Source: $DATA_DIR"
echo "Destination: $BACKUP_FILE"

# check if container exists/running (optional, but good practice)
if ! docker ps -a --format '{{.Names}}' | grep -q "^alsakr-pb$"; then
    echo "❌ Error: Container alsakr-pb does not exist!"
    exit 1
fi

echo "Stopping PocketBase container..."
docker stop alsakr-pb

echo "Copying data from container..."
# Copy from container to temp dir
TEMP_DIR="$BACKUP_DIR/temp_pb_data_$TIMESTAMP"
docker cp alsakr-pb:/pb_data "$TEMP_DIR"

echo "Restarting PocketBase container..."
docker start alsakr-pb

echo "Compressing data..."
tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" .

echo "Cleaning up temp files..."
rm -rf "$TEMP_DIR"

echo "✅ Backup created successfully."

# Cleanup old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "pb_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup process completed."
echo "========================================================"
