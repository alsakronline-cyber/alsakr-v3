# Al Sakr V2 - Master Deployment Guide

This document consolidates all deployment instructions for the Alsakr V2 Industrial AI Platform.

## 📂 Project Structure Overview

```text
alsakr_v2/
├── v2_infra/               # Infrastructure & Docker Configuration
│   ├── docker-compose.prod.yml  # Production services definition
│   ├── deploy.sh                # Main infrastructure deployment script
│   ├── Caddyfile                # Web Server & Reverse Proxy config
│   └── ops/                     # Operational scripts
│       └── run_phase1_ingestion.sh  # Data import & vector generation
├── v2_project/             # Application Code
│   ├── frontend/           # Next.js Application
│   └── backend/            # FastAPI & AI Agents
└── DEPLOYMENT_MASTER_GUIDE.md   # This file
```

---

## 🚀 One-Command Deployment

We have consolidated the deployment into an orchestration script.
Run this on your VPS to deploy everything (Infra + Data).

### 1. Connect to VPS
```bash
ssh -i ~/.ssh/oracle_vps_key ubuntu@144.24.208.96
cd ~/alsakr-online
git pull origin v2-industrial-ai
```

### 2. Run the Deployment
```bash
# Make sure scripts are executable
chmod +x alsakr_v2/v2_infra/deploy.sh
chmod +x alsakr_v2/v2_infra/ops/run_phase1_ingestion.sh

# Run the master infra deployment
./alsakr_v2/v2_infra/deploy.sh
```

### 3. Run Data Ingestion (First Time Only)
After the services are up (green success message from `deploy.sh`), run:
```bash
./alsakr_v2/v2_infra/ops/run_phase1_ingestion.sh
```

---

## ⚡ Quick Update Workflow

Use this standard workflow to push changes and redeploy:

### 1. Local Machine (Push Changes)
Run inside `alsakr_v2/`:
```bash
# Stage changes (Code only - Data is ignored)
git add .

# Commit
git commit -m "Update: Description of changes"

# Push to branch
git push origin v2-industrial-ai
```

### 2. VPS (Pull & Redeploy)
SSH into verified server and run:
```bash
# Go to project root
cd /opt/alsakr_v2

# Pull latest code
git pull origin v2-industrial-ai

# Rebuild and restart containers
docker-compose -f v2_infra/docker-compose.prod.yml up -d --build
```

---

## 🛠️ Manual Troubleshooting

If the script fails, check these common issues:

### 1. Frontend Search Not Working?
Ensure `NEXT_PUBLIC_API_URL` is baked into the build:
```bash
cd ~/alsakr-online/alsakr_v2/v2_infra
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

### 2. Qdrant "Unhealthy"?
It might just be missing `curl/wget` in the container. If the logs say it's running, it's fine.
```bash
docker logs alsakr-qdrant
```

### 3. "Connection Refused" on Backend?
Check if the backend container is running and healthy:
```bash
curl http://localhost:8000/api/health
```

---

## 🌐 Access Points

| Service | URL | Note |
|---------|-----|------|
| **Command Center** | `https://app.alsakronline.com` | Main UI |
| **API Docs** | `https://api.app.alsakronline.com/docs` | Swagger UI |
| **PocketBase** | `https://crm.app.alsakronline.com/_/` | Admin Panel |
| **N8N** | `https://workflows.app.alsakronline.com` | Workflow Automation |

---

## 📝 Environment Variables (`.env`)

Ensure your `.env` in `v2_infra/` has these critical values:
```env
# Production
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://app.alsakronline.com

# Backend
ES_HOST=elasticsearch
OLLAMA_HOST=http://ollama:11434
QDRANT_HOST=qdrant
PB_URL=http://pocketbase:8090
```
