# VPS Deployment Guide for Alsakr V2

## Overview
Complete guide to deploy the Alsakr V2 Industrial AI Platform to Oracle Cloud VPS with Docker Compose.

---

## Prerequisites

- **VPS**: Oracle Cloud free tier (or similar)
- **OS**: Ubuntu 20.04+ or compatible Linux
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 50GB+
- **SSH Access**: Key-based authentication set up
- **Domain**: DNS pointed to VPS IP (for SSL)

---

## Part 1: Initial VPS Setup (One-Time)

### 1. Connect to VPS

```bash
# SSH into your VPS (use your key)
ssh -i ~/.ssh/your-key.pem ubuntu@your-vps-ip

# Or if using password
ssh root@your-vps-ip
```

### 2. Update System

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget vim htop
```

### 3. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
# Then SSH back in
```

### 4. Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

---

## Part 2: Deploy Application

### 1. Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/YOUR_USERNAME/alsakr-online.git

# Or if already cloned, pull latest
cd ~/alsakr-online
git pull origin v2-industrial-ai

# Navigate to infrastructure directory
cd ~/alsakr-online/alsakr_v2/v2_infra
```

### 2. Configure Environment

```bash
# Create production .env file
cat > .env << 'EOF'
# Production Environment Variables
ES_HOST=elasticsearch
OLLAMA_HOST=http://ollama:11434
PB_URL=http://pocketbase:8090
QDRANT_HOST=qdrant

# Add any secrets
JWT_SECRET=your-super-secret-key-change-this
ADMIN_EMAIL=admin@alsakronline.com
EOF

# Secure the file
chmod 600 .env
```

### 3. Update Caddyfile for Production

```bash
# Edit Caddyfile
nano Caddyfile
```

Update with your domain:

```caddy
# Production Caddyfile
app.alsakronline.com {
    # Frontend
    reverse_proxy frontend:3000
}

api.alsakronline.com {
    # Backend API
    reverse_proxy backend:8000
}

# Optional: Admin interfaces
n8n.alsakronline.com {
    reverse_proxy n8n:5678
}

pb.alsakronline.com {
    reverse_proxy pocketbase:8090
}
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

### 4. Start Services

```bash
# Build and start all services
docker-compose up -d

# This will start:
# - Ollama (AI)
# - Elasticsearch (Search)
# - Qdrant (Vectors)
# - PocketBase (Auth/CRM)
# - n8n (Automation)
# - Frontend (Next.js)
# - Backend (FastAPI)
# - Caddy (Reverse Proxy)

# Check all containers are running
docker ps

# Should show 8 containers running
```

### 5. Monitor Logs

```bash
# View logs for all services
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Exit logs with Ctrl+C
```

---

## Part 3: Data Ingestion (Phase 1)

### 1. Verify Services are Ready

```bash
# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check Qdrant
curl http://localhost:6333/collections

# Check Ollama
docker exec alsakr-ollama ollama list

# Check backend health
curl http://localhost:8000/api/health
```

### 2. Pull AI Models

```bash
# Pull embedding model (required for vector search)
docker exec alsakr-ollama ollama pull nomic-embed-text

# Pull chat model (for AI agents)
docker exec alsakr-ollama ollama pull llama3.2

# Verify models
docker exec alsakr-ollama ollama list
```

Expected output:
```
NAME                    ID              SIZE    MODIFIED
nomic-embed-text:latest 0a109f422b47    274MB   2 minutes ago
llama3.2:latest         a80c4f17acd5    2.0GB   5 minutes ago
```

### 3. Run Data Ingestion

```bash
# Enter backend container
docker exec -it alsakr-backend bash

# Run product ingestion
python -m app.core.ingest_products

# Expected: "✅ 211 products indexed"

# Generate embeddings (takes 20-30 minutes)
python -m app.core.generate_embeddings

# Expected: "✅ 211 vectors stored"

# Optional: Process PDFs
python -m app.core.process_pdfs

# Exit container
exit
```

### 4. Verify Data

```bash
# Check data status via API
curl http://localhost:8000/api/data/status

# Test search
curl "http://localhost:8000/api/search/products?q=reflector&size=3"

# Test semantic search
curl -X POST http://localhost:8000/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "temperature sensors", "limit": 3}'
```

---

## Part 4: Verification & Testing

### 1. Test Frontend

Open browser and navigate to:
- **https://app.alsakronline.com** - Main app
- **https://api.alsakronline.com/docs** - API documentation

### 2. Test API Endpoints

```bash
# Health check
curl https://api.alsakronline.com/api/health

# Search products
curl "https://api.alsakronline.com/api/search/products?q=sensor"

# Get product details
curl https://api.alsakronline.com/api/products/1008562

# List categories
curl https://api.alsakronline.com/api/categories
```

### 3. Monitor Resources

```bash
# Check container resource usage
docker stats

# Check disk usage
df -h

# Check memory
free -h

# View system load
htop
```

---

## Part 5: Maintenance & Updates

### Update Application

```bash
# Navigate to repo
cd ~/alsakr-online

# Pull latest code
git pull origin v2-industrial-ai

# Rebuild and restart
cd alsakr_v2/v2_infra
docker-compose down
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Backup Data

```bash
# Create backup directory
mkdir -p ~/backups

# Backup Elasticsearch data
docker exec alsakr-es curl -X POST "localhost:9200/_snapshot/my_backup/snapshot_$(date +%Y%m%d)/_create"

# Backup volumes (manual)
sudo tar -czf ~/backups/volumes_$(date +%Y%m%d).tar.gz \
  /var/lib/docker/volumes/

# Backup configuration
cp -r ~/alsakr-online ~/backups/alsakr_$(date +%Y%m%d)
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

### View Logs

```bash
# All logs
docker-compose logs --tail=100

# Follow logs
docker-compose logs -f backend

#Grep logs
docker-compose logs backend | grep ERROR
```

---

## Part 6: Troubleshooting

### Issue: Containers won't start

```bash
# Check logs
docker-compose logs

# Check individual container
docker logs alsakr-backend

# Restart stack
docker-compose down
docker-compose up -d
```

### Issue: Out of memory

```bash
# Check memory
free -h

# Adjust Docker Compose limits in docker-compose.yml
# Reduce Elasticsearch heap in v2_infra/docker-compose.yml:
#   ES_JAVA_OPTS: "-Xms512m -Xmx512m"

# Restart with new limits
docker-compose down
docker-compose up -d
```

### Issue: Port already in use

```bash
# Check what's using port
sudo lsof -i :8000

# Kill process
sudo kill -9 PID

# Or change port in docker-compose.yml
```

### Issue: SSL certificate errors

```bash
# Check Caddy logs
docker logs alsakr-proxy

# Verify DNS is pointing to VPS
nslookup app.alsakronline.com

# Restart Caddy
docker-compose restart caddy
```

### Issue: Elasticsearch won't start

```bash
# Increase vm.max_map_count
sudo sysctl -w vm.max_map_count=262144

# Make permanent
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf

# Restart Elasticsearch
docker-compose restart elasticsearch
```

---

## Security Checklist

- [ ] Change default passwords in PocketBase admin
- [ ] Set strong JWT_SECRET in .env
- [ ] Enable UFW firewall
- [ ] Set up SSH key authentication (disable password auth)
- [ ] Regular updates: `apt update && apt upgrade`
- [ ] Monitor logs for suspicious activity
- [ ] Set up fail2ban for SSH protection
- [ ] Regular backups
- [ ] Use HTTPS only (Caddy handles this)
- [ ] Restrict API access if needed

---

## Performance Optimization

```bash
# 1. Monitor resource usage
docker stats

# 2. Optimize Elasticsearch
# In docker-compose.yml, adjust:
# - ES_JAVA_OPTS for heap size
# - index.refresh_interval for write performance

# 3. Scale services
docker-compose up -d --scale backend=3

# 4. Use caching
# Implement Redis caching in backend for frequent queries

# 5. Compress static assets
# Caddy handles this automatically
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| View all containers | `docker ps` |
| View logs | `docker-compose logs -f` |
| Restart service | `docker-compose restart <service>` |
| Stop all | `docker-compose down` |
| Start all | `docker-compose up -d` |
| Shell into container | `docker exec -it <container> bash` |
| Check resources | `docker stats` |
| Pull latest code | `git pull origin v2-industrial-ai` |
| Rebuild containers | `docker-compose build` |
| View disk usage | `df -h` |

---

## Support & Next Steps

After successful deployment:

1. **Configure PocketBase**: Set up user collections and admin account
2. **Configure n8n**: Create automation workflows
3. **Monitor Performance**: Set up Grafana/Prometheus
4. **Scale**: Add load balancing if needed
5. **Optimize**: Fine-tune AI models and search relevance

---

## Emergency Procedures

### Complete Restart

```bash
# Stop everything
docker-compose down

# Remove volumes (CAUTION: deletes data!)
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Re-run data ingestion
docker exec -it alsakr-backend bash
python -m app.core.ingest_products
python -m app.core.generate_embeddings
exit
```

### Rollback to Previous Version

```bash
# View recent commits
git log --oneline -10

# Checkout previous commit
git checkout COMMIT_HASH

# Rebuild
docker-compose down
docker-compose build
docker-compose up -d
```

---

**Need Help?** Check logs first: `docker-compose logs -f`
