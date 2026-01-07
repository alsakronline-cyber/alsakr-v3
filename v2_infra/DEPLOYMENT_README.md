# Deployment Scripts - README

## 🚀 Quick Reference

### Initial Deployment

```bash
# Make scripts executable
chmod +x deploy.sh quick-deploy.sh ops/*.sh

# Run full deployment
./deploy.sh
```

### Quick Updates

```bash
# After code changes
./quick-deploy.sh
```

### Data Ingestion

```bash
# Run Phase 1 data ingestion
./ops/run_phase1_ingestion.sh
```

### Backup

```bash
# Create backup
./ops/backup.sh
```

---

## 📁 File Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `deploy.sh` | Full deployment | Initial setup, major updates |
| `quick-deploy.sh` | Fast redeploy | Code changes, minor updates |
| `docker-compose.prod.yml` | Production config | Production deployment |
| `.env.example` | Environment template | First-time setup |
| `ops/run_phase1_ingestion.sh` | Data import | After deployment |
| `ops/backup.sh` | Backup volumes | Regular backups |

---

## 🔧 Usage Examples

### First Time Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/alsakr-online.git
cd alsakr-online/alsakr_v2/v2_infra

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 3. Deploy
chmod +x deploy.sh
./deploy.sh

# 4. Import data
./ops/run_phase1_ingestion.sh
```

### Update After Code Changes

```bash
# Fast update
cd ~/alsakr_v2/alsakr_v2/v2_infra
./quick-deploy.sh
```

### Regular Backup

```bash
# Run backup (recommended: daily cron job)
./ops/backup.sh

# Add to crontab for daily backup at 2 AM:
# 0 2 * * * /path/to/ops/backup.sh >> /var/log/alsakr_backup.log 2>&1
```

---

## ⚙️ Configuration

### Environment Variables (.env)

**Required Changes:**
- `JWT_SECRET` - Long random string (min 32 chars)
- `ADMIN_PASSWORD` - Strong password
- `DOMAIN` - Your domain name

**Optional:**
- `ES_JAVA_OPTS` - Elasticsearch memory (adjust for VPS)
- `N8N_HOST` - n8n subdomain
- Timezone settings

### Docker Compose

Use `docker-compose.prod.yml` for production:

```bash
# Production
docker-compose -f docker-compose.prod.yml up -d

# Development (default)
docker-compose up -d
```

---

## 🔍 Monitoring

### Check Status

```bash
# All services
docker-compose ps

# Logs
docker-compose logs -f

# Resource usage
docker stats

# Data status
curl http://localhost:8000/api/data/status
```

### Health Checks

```bash
# API
curl http://localhost:8000/api/health

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Qdrant
curl http://localhost:6333/collections
```

---

## 🛠️ Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs -f <service>

# Restart specific service
docker-compose restart <service>

# Full restart
docker-compose down && docker-compose up -d
```

### Out of memory

Edit `docker-compose.prod.yml` and reduce memory limits:

```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Reduce from 2G
```

### Deployment fails

```bash
# Check prerequisites
docker --version
docker-compose --version
git --version

# Verify .env exists
cat .env

# Check system resources
free -h
df -h
```

---

## 📦 Production Checklist

Before going live:

- [ ] Update `.env` with production values
- [ ] Change `JWT_SECRET` and passwords
- [ ] Configure `Caddyfile` with your domain
- [ ] Point DNS to VPS IP
- [ ] Enable firewall (UFW)
- [ ] Set up SSL certificates (Caddy auto)
- [ ] Run data ingestion
- [ ] Test all endpoints
- [ ] Set up backup cron job
- [ ] Configure monitoring

---

## 🔐 Security

### Firewall Setup

```bash
# Allow essential ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

### SSH Hardening

```bash
# Disable password auth (use keys only)
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no

sudo systemctl restart sshd
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Resource Optimization

Monitor and adjust in `docker-compose.prod.yml`:
- CPU limits
- Memory limits
- Elasticsearch heap size

---

## 🆘 Support

- **Logs**: `docker-compose logs -f`
- **Status**: `curl localhost:8000/api/data/status`
- **Docs**: See VPS_DEPLOYMENT_GUIDE.md

**Emergency Rollback:**
```bash
git checkout PREVIOUS_COMMIT_HASH
./quick-deploy.sh
```
