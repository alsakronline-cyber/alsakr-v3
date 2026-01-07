#!/bin/bash

################################################################################
# Backup Script - Backup all data volumes and configurations
################################################################################

set -e

BACKUP_DIR="$HOME/alsakr_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}💾 Starting Backup...${NC}\n"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup Docker volumes
echo "📦 Backing up Docker volumes..."
docker run --rm \
  -v alsakr_v2_ollama_data:/data/ollama:ro \
  -v alsakr_v2_es_data:/data/es:ro \
  -v alsakr_v2_qdrant_data:/data/qdrant:ro \
  -v alsakr_v2_pb_data:/data/pb:ro \
  -v alsakr_v2_n8n_data:/data/n8n:ro \
  -v "$BACKUP_PATH:/backup" \
  alpine tar czf /backup/volumes.tar.gz /data

# Backup configuration files
echo "📄 Backing up configurations..."
cp .env "$BACKUP_PATH/.env"
cp Caddyfile "$BACKUP_PATH/Caddyfile"
cp docker-compose.yml "$BACKUP_PATH/docker-compose.yml"

# Create backup manifest
cat > "$BACKUP_PATH/manifest.txt" << EOF
Backup created: $(date)
Hostname: $(hostname)
Docker version: $(docker --version)
Services backed up:
- Ollama (AI models)
- Elasticsearch (product data)
- Qdrant (vectors)
- PocketBase (users/CRM)
- n8n (workflows)
- Configuration files
EOF

echo -e "\n${GREEN}✅ Backup complete!${NC}"
echo "Location: $BACKUP_PATH"
echo "Size: $(du -sh $BACKUP_PATH | cut -f1)"

# Cleanup old backups (keep last 7)
echo "🗑️  Cleaning old backups (keeping last 7)..."
cd "$BACKUP_DIR"
ls -t | tail -n +8 | xargs -r rm -rf

echo -e "${GREEN}✨ Done!${NC}"
