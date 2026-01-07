# Git Workflow Guide for Alsakr V2 Project

## Overview
This guide covers how to manage your code with Git and push/pull changes to your GitHub repository.

---

## Initial Git Setup (One-Time)

### 1. Configure Git Identity
```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

### 2. Initialize Repository (if not done)
```bash
cd "c:\Users\pc shop\Downloads\alsakr-online"

# Initialize Git (skip if already initialized)
git init

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/alsakr-online.git

# Verify remote
git remote -v
```

---

## Daily Workflow

### 1. Check Status
Before making changes, see what's modified:

```bash
# Check current status
git status

# See what files changed
git diff
```

### 2. Pull Latest Changes
Always pull before starting work to avoid conflicts:

```bash
# Pull from v2-industrial-ai branch
git pull origin v2-industrial-ai

# Or pull from main branch
git pull origin main
```

### 3. Stage Your Changes
Add files you want to commit:

```bash
# Add specific files
git add alsakr_v2/v2_project/backend/app/core/config.py
git add alsakr_v2/v2_project/backend/app/main.py

# Add all files in a directory
git add alsakr_v2/v2_project/backend/app/core/

# Add all changed files (use carefully!)
git add .
```

### 4. Commit Changes
Save your staged changes with a descriptive message:

```bash
# Commit with message
git commit -m "Add Phase 1 data ingestion scripts"

# Or commit with detailed message
git commit -m "Add Phase 1 data ingestion scripts

- Created Elasticsearch product importer
- Added Qdrant vector embedding generator
- Implemented PDF processing pipeline
- Enhanced API with search endpoints"
```

#### Commit Message Best Practices:
- **Be descriptive**: "Add data ingestion scripts" not "Updated files"
- **Use present tense**: "Add feature" not "Added feature"
- **Keep first line under 50 characters**
- **Add details in body if needed**

### 5. Push to GitHub
Upload your commits to GitHub:

```bash
# Push to your current branch
git push origin v2-industrial-ai

# Or push to main branch
git push origin main

# Force push (use ONLY if you know what you're doing)
git push --force origin v2-industrial-ai
```

---

## Common Scenarios

### Scenario 1: Push All Phase 1 Changes

```bash
# 1. Check status
git status

# 2. Stage all new files in backend
git add alsakr_v2/v2_project/backend/app/core/

# 3. Stage main.py changes
git add alsakr_v2/v2_project/backend/app/main.py

# 4. Commit
git commit -m "Implement Phase 1 data foundation

- Add configuration module with environment settings
- Create Elasticsearch product ingestion script
- Add Qdrant vector embedding generator
- Implement PDF processing with chunking
- Create unified search service (text/semantic/hybrid)
- Enhance API with search and data status endpoints"

# 5. Push
git push origin v2-industrial-ai
```

### Scenario 2: Pull Updates from VPS

If you made changes on the VPS and want them locally:

```bash
# Pull latest from GitHub
git pull origin v2-industrial-ai

# If conflicts occur, resolve them manually
# Then commit the merge
git commit -m "Merge remote changes"
```

### Scenario 3: Undo Uncommitted Changes

Made a mistake and want to reset?

```bash
# Discard changes to a specific file
git checkout -- filename.py

# Discard all uncommitted changes (CAREFUL!)
git reset --hard HEAD
```

### Scenario 4: View Commit History

```bash
# See recent commits
git log --oneline -10

# See detailed history
git log --stat

# See changes in a specific commit
git show COMMIT_HASH
```

---

## Branch Management

### Create a New Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/new-agent

# Make changes, commit
git add .
git commit -m "Add new agent feature"

# Push branch to GitHub
git push origin feature/new-agent

# Switch back to main branch
git checkout v2-industrial-ai
```

### Merge Branch

```bash
# Switch to target branch
git checkout v2-industrial-ai

# Merge feature branch
git merge feature/new-agent

# Push merged changes
git push origin v2-industrial-ai
```

---

## .gitignore Best Practices

Ensure `.gitignore` excludes unnecessary files:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.env

# Data files (optional - exclude if too large)
*.csv
alsakr_v2/Data/pdfs/
alsakr_v2/Data/scraped_data/

# IDE
. vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker volumes
**/data/
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `git status` | Show current status |
| `git add <file>` | Stage file for commit |
| `git commit -m "msg"` | Commit staged changes |
| `git push origin <branch>` | Push commits to GitHub |
| `git pull origin <branch>` | Pull latest from GitHub |
| `git log --oneline` | View commit history |
| `git diff` | See uncommitted changes |
| `git checkout -- <file>` | Discard file changes |
| `git branch` | List branches |
| `git checkout <branch>` | Switch branches |

---

## Troubleshooting

### Issue: "Permission denied (publickey)"

Set up SSH keys or use HTTPS with credentials:

```bash
# Use HTTPS instead
git remote set-url origin https://github.com/YOUR_USERNAME/alsakr-online.git
```

### Issue: "Merge conflicts"

1. Open conflicted files
2. Look for `<<<<<<`, `======`, `>>>>>>` markers
3. Manually resolve conflicts
4. Stage resolved files: `git add filename`
5. Complete merge: `git commit`

### Issue: "Diverged branches"

```bash
# Pull with rebase
git pull --rebase origin v2-industrial-ai

# Or merge
git pull origin v2-industrial-ai
```

---

## Best Practices

1. **Commit often**: Small, focused commits are better than large ones
2. **Pull before push**: Always pull before pushing to avoid conflicts
3. **Write good messages**: Future you will thank you
4. **Test before commit**: Don't commit broken code
5. **Use branches**: Keep experimental work separate
6. **Backup important work**: Push to GitHub regularly

---

## Next Steps

After mastering Git basics:
- Learn about **Git tags** for versioning
- Explore **Git stash** for temporary saves
- Set up **GitHub Actions** for CI/CD
- Use **Pull Requests** for code review
