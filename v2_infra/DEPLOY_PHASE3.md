# Deploying Phase 3 (Vision & RAG)

This guide covers how to push your local changes and deploy them to the Oracle Cloud VPS.

## 1. Commit and Push Local Changes

First, ensure all your code is committed locally.

```bash
# In your local project root (c:\Users\pc shop\Downloads\alsakr-online\alsakr_v2)
git add .
git commit -m "feat: Implement Phase 3 - Vision & RAG Logic"
git push origin main
```

## 2. Deploy on VPS

SSH into your Oracle Cloud VPS and pull the changes.

```bash
# SSH into VPS (adjust key path and IP as needed)
ssh -i /path/to/key opc@<VPS_IP>

# Go to project directory
cd /opt/alsakr_v2

# Pull latest changes
git pull origin main
```

## 3. Rebuild Containers

Since we added new Python dependencies (`pdfplumber`, `pillow`, `faster-whisper`), we **MUST** rebuild the backend image.

```bash
# Navigate to infrastructure folder
cd v2_infra

# Stop current backend
docker-compose stop backend

# Rebuild backend (this might take a few minutes)
# We use --no-cache to ensure pip install runs freshly
docker-compose build --no-cache backend

# Start everything up again
docker-compose up -d
```

## 4. Verification

### Check Logs
Check if the backend started correctly:
```bash
docker-compose logs -f backend
```
You should see: `🚀 API Started. Elasticsearch Ready.`

### Check dependencies
Verify that `faster-whisper` and `pdfplumber` are installed:
```bash
docker-compose exec backend pip list | grep -E "whisper|pdfplumber"
```

## 5. Download Vision Model (Optional)

If you have enough RAM (16GB+) and want to run the vision model locally:

```bash
docker-compose exec ollama ollama pull llava
# OR for smaller footprint
docker-compose exec ollama ollama pull moondream
```

*Note: If your VPS is small (ARM Ampere 24GB is strictly fine, but verify memory usage with `htop`).*
