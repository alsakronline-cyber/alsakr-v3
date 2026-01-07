# Git Workflow - Quick Reference Commands

## Push Phase 1 to GitHub

### Option 1: Automated Script (Recommended)

```bash
# Make executable and run
chmod +x alsakr_v2/git-push-phase1.sh
./alsakr_v2/git-push-phase1.sh
```

### Option 2: Manual Commands

```bash
# Navigate to repository
cd "c:\Users\pc shop\Downloads\alsakr-online"

# Pull latest changes first
git pull origin v2-industrial-ai

# Add all Phase 1 files
git add alsakr_v2/v2_project/backend/app/core/
git add alsakr_v2/v2_project/backend/app/main.py
git add alsakr_v2/*.md
git add alsakr_v2/v2_infra/

# Check what will be committed
git status

# Commit with message
git commit -m "Implement Phase 1: Data Foundation & Deployment

- Add data ingestion scripts (ES, Qdrant, PDFs)
- Create unified search service
- Enhance API with search endpoints
- Add deployment automation scripts
- Complete documentation guides"

# Push to GitHub
git push origin v2-industrial-ai
```

## Pull Latest from VPS

If you make changes on VPS and want to sync locally:

```bash
# Pull from GitHub
git pull origin v2-industrial-ai

# Or if you have conflicts
git fetch origin v2-industrial-ai
git merge origin/v2-industrial-ai
```

## Verify Push

```bash
# Check last commit
git log --oneline -1

# View remote URL
git remote -v

# Check branch status
git status
```

## After Pushing

1. **View on GitHub**: Check your repository online
2. **Deploy to VPS**: 
   ```bash
   ssh -i ~/.ssh/oracle_vps_key ubuntu@144.24.208.96
   cd ~/alsakr-online
   git pull origin v2-industrial-ai
   cd alsakr_v2/v2_infra
   ./deploy.sh
   ```
3. **Run data ingestion** on VPS:
   ```bash
   ./ops/run_phase1_ingestion.sh
   ```

## Troubleshooting

### Permission Denied

```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/alsakr-online.git
```

### Merge Conflicts

```bash
# Stash local changes
git stash

# Pull latest
git pull origin v2-industrial-ai

# Reapply changes
git stash pop
```

### Large Files Warning

If CSV or images are too large, add to `.gitignore`:

```bash
# Add to .gitignore
echo "alsakr_v2/Data/*.csv" >> .gitignore
echo "alsakr_v2/Data/scraped_data/" >> .gitignore

# Recommit
git add .gitignore
git commit --amend --no-edit
```
