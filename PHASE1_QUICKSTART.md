# Phase 1 Quick Start Guide

## 🚀 Getting Started with Data Ingestion

This guide walks you through executing Phase 1 Data Foundation in both local and production environments.

---

## Option 1: Automated Execution (Recommended)

### Linux/Mac/WSL:

```bash
# Navigate to infrastructure directory
cd alsakr_v2/v2_infra

# Make script executable
chmod +x ops/run_phase1_ingestion.sh

# Run automated ingestion
./ops/run_phase1_ingestion.sh
```

### Windows (PowerShell):

```powershell
# Run each step manually (see Manual Execution below)
```

---

## Option 2: Manual Execution

### Step 1: Start Services

```bash
cd alsakr_v2/v2_infra
docker-compose up -d

# Wait for services to be ready (~30 seconds)
docker-compose ps
```

### Step 2: Verify Services

```bash
# Elasticsearch
curl http://localhost:9200/_cluster/health

# Qdrant
curl http://localhost:6333/collections

# Ollama
docker exec alsakr-ollama ollama list

# Backend
curl http://localhost:8000/api/health
```

### Step 3: Pull AI Models

```bash
# Embedding model (required)
docker exec alsakr-ollama ollama pull nomic-embed-text

# Chat model (for agents)
docker exec alsakr-ollama ollama pull llama3.2

# Verify
docker exec alsakr-ollama ollama list
```

### Step 4: Import Products

```bash
# Enter backend container
docker exec -it alsakr-backend bash

# Run ingestion (2-3 minutes)
python -m app.core.ingest_products

# Expected output:
# ✅ 211 products indexed

# Exit container
exit
```

### Step 5: Generate Embeddings

```bash
# Enter backend container
docker exec -it alsakr-backend bash

# Run embedding generation (20-30 minutes)
python -m app.core.generate_embeddings

# Expected output:
# ✅ 211 vectors stored

# Exit container
exit
```

### Step 6: (Optional) Process PDFs

```bash
docker exec -it alsakr-backend bash

# Note: Requires PyPDF2 or pdfplumber for full text extraction
python -m app.core.process_pdfs

exit
```

---

## Verification

### Check Data Status

```bash
curl http://localhost:8000/api/data/status | python -m json.tool
```

Expected output:
```json
{
  "elasticsearch": {
    "connected": true,
    "products_count": 211,
    "pdf_count": 0
  },
  "qdrant": {
    "connected": true,
    "vectors_count": 211
  }
}
```

### Test Search

```bash
# Text search
curl "http://localhost:8000/api/search/products?q=reflector&size=3" | python -m json.tool

# Semantic search
curl -X POST http://localhost:8000/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "temperature sensors", "limit": 3}' | python -m json.tool

# Get product details
curl http://localhost:8000/api/products/1008562 | python -m json.tool
```

### View API Documentation

Open in browser: `http://localhost:8000/docs`

---

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Import fails

```bash
# Check backend logs
docker logs alsakr-backend --tail 50

# Verify CSV exists
ls -lh ../Data/products.csv

# Check Elasticsearch
curl localhost:9200/_cat/indices?v
```

### Embedding generation stuck

```bash
# Check Ollama logs
docker logs alsakr-ollama --tail 50

# Verify model is pulled
docker exec alsakr-ollama ollama list

# Check Qdrant
curl localhost:6333/collections
```

### Out of memory

```bash
# Check resources
docker stats

# Adjust limits in docker-compose.yml if needed
# Restart: docker-compose down && docker-compose up -d
```

---

## Git Workflow

### After Successful Implementation

```bash
# Add all Phase 1 files
cd alsakr-online
git add alsakr_v2/v2_project/backend/app/core/
git add alsakr_v2/v2_project/backend/app/main.py
git add alsakr_v2/*.md
git add alsakr_v2/v2_infra/ops/

# Commit
git commit -m "Implement Phase 1 data foundation

- Add configuration module
- Create Elasticsearch ingestion
- Add Qdrant embeddings
- Implement search service
- Enhance API endpoints
- Add deployment guides"

# Push to GitHub
git push origin v2-industrial-ai
```

---

## VPS Deployment

See detailed guide: [VPS_DEPLOYMENT_GUIDE.md](./VPS_DEPLOYMENT_GUIDE.md)

Quick steps:
1. SSH into VPS
2. Clone/update repo
3. Run `docker-compose up -d`
4. Execute ingestion script
5. Verify with API tests

---

## Next Steps

Once Phase 1 is complete:

1. **Test the API** - Use `/docs` endpoint
2. **Integrate Frontend** - Connect search UI
3. **Configure PocketBase** - Set up auth
4. **Start Phase 2** - Agent integration

---

## Support

- **Documentation**: Check implementation_plan.md and walkthrough.md
- **Logs**: `docker-compose logs -f`
- **Status**: `curl localhost:8000/api/data/status`
- **Health**: `curl localhost:8000/api/health`

✨ **You're all set! The data foundation is ready.**
