# Final Deployment & Testing Guide

## Step 1: Deploy UI Fixes (5 minutes)

Run these commands in your **SSH terminal** (already connected):

```bash
# Navigate to the repo
cd ~/alsakr-online
git pull origin v2-industrial-ai

# Copy ALL frontend files to production
cp -rf ~/alsakr-online/alsakr_v2/v2_project/frontend/* ~/alsakr_v2/v2_project/frontend/

# Verify Tailwind config exists
ls ~/alsakr_v2/v2_project/frontend/tailwind.config.js
ls ~/alsakr_v2/v2_project/frontend/postcss.config.js

# Rebuild frontend with Tailwind CSS
cd ~/alsakr_v2/v2_project
docker compose build frontend

# Start the rebuilt frontend
docker compose up -d frontend
```

**Expected**: Build will take ~2 minutes. You'll see "Installing tailwindcss..." in the logs.

---

## Step 2: Pull Ollama AI Model (10 minutes)

```bash
# Pull the llama3.2 model (this downloads ~2GB)
docker exec -it alsakr-ollama ollama pull llama3.2

# Verify the model is available
docker exec -it alsakr-ollama ollama list
```

**Expected**: You should see `llama3.2:latest` in the list.

---

## Step 3: Quick Testing (5 minutes)

### 3.1 Test Backend Health
```bash
curl http://localhost:8000/api/health
```
**Expected**: `{"status":"healthy","elasticsearch":true}`

### 3.2 Test Frontend
Open in browser: **https://app.alsakronline.com/command-center**

**Expected**: 
- ✅ Professional dark UI with proper colors
- ✅ Gradient backgrounds
- ✅ Colored agent cards (cyan/orange/gray)
- ✅ Smooth animations
- ✅ Readable text and proper spacing

### 3.3 Test Backend API (Optional)
```bash
# Test the chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -F "message=Hello" \
  -F "user_id=test123"
```

**Expected**: `{"response":"<agent response>"}`

---

## Verification Checklist

Once complete, verify:
- [ ] Frontend displays correctly at https://app.alsakronline.com/command-center
- [ ] All agent cards are visible with correct colors
- [ ] Backend /api/health returns healthy status
- [ ] Ollama model is downloaded
- [ ] All 8 Docker containers are running

Check container status:
```bash
docker ps
```

Should show 8 containers: `alsakr-frontend`, `alsakr-backend`, `alsakr-ollama`, `alsakr-qdrant`, `alsakr-n8n`, `alsakr-pocketbase`, `alsakr-elasticsearch`, `alsakr-caddy`

---

## If Something Goes Wrong

### Frontend still broken after rebuild?
```bash
# Check build logs
docker logs alsakr-frontend

# Force complete rebuild
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Ollama model download fails?
```bash
# Check Ollama logs
docker logs alsakr-ollama

# Retry pull
docker exec -it alsakr-ollama ollama pull llama3.2
```

### Backend not responding?
```bash
# Check backend logs
docker logs alsakr-backend --tail 50

# Restart if needed
docker compose restart backend
```

---

**Total Time**: ~20 minutes (mostly waiting for builds/downloads)
