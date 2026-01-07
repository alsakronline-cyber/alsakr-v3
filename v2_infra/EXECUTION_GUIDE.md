# V2 Deployment Guide: From Clean Slate to Launch

Follow these steps exactly to migrate from the old version to the new **Industrial AI Command Center**.

## 💻 LOCAL VS ☁️ VPS: Where to run commands?

> [!WARNING]
> You have two terminals open. Make sure you are in the right one!
> - **Antigravity Agent**: Local Windows (PowerShell).
> - **ssh**: Remote Oracle Cloud (Linux).

---

## Step 1: Consolidate on the VPS (SSH Terminal)
Run these commands in your **SSH terminal** (Ubuntu@alsakr):

```bash
# 1. Create the new production directory
mkdir -p ~/alsakr_v2

# 2. Copy the V2 components
cp -r ~/alsakr-online/v2_infra ~/alsakr_v2/
cp -r ~/alsakr-online/v2_project ~/alsakr_v2/

# 3. Move the .env file from the FOUND location (infrastructure folder)
cp ~/alsakr-online/infrastructure/.env ~/alsakr_v2/v2_project/backend/.env
```

---

## Step 2: Final Launch 🚀 (SSH Terminal)
```bash
# Go to the new project location
cd ~/alsakr_v2/v2_project

# Reboot the system
docker compose down
docker compose up -d --build
```

---

## Step 3: Troubleshooting the Backend (SSH Terminal)
If the backend doesn't show up in `docker ps`, run:
```bash
docker logs alsakr-backend
```

---

## 🛠️ Troubleshooting: Docker Compose Not Found
If neither command works, run this to install the modern plugin:
```bash
sudo apt update
sudo apt install docker-compose-v2
```
Or the legacy one:
```bash
sudo apt install docker-compose
```
3.  **Check Health**:
    *   **PocketBase**: `http://<your-vps-ip>:8090/_/` (CRM)
    *   **Elasticsearch**: `http://<your-vps-ip>:9200` (Search)
    *   **n8n**: `http://<your-vps-ip>:5678` (Automation)

---

## Step 4: Loading the "Fuel" (Data Ingestion)
1.  **Products**: Place your `products.csv` in `v2_project/data/scraped/`.
2.  **Manuals**: Place your PDFs in `v2_project/data/manuals/`.
3.  **Verification**: I will provide ingestion scripts in the next phase to index these into Elasticsearch.

---

## Next Steps for the Developer (Antigravity):
Once you confirm these services are running, I will:
1.  Build the **Base Agent Class** in `backend/app/agents/base.py`.
2.  Refactor the **Visual Agent** with the Anti-Counterfeit logic.
3.  Configure the **WhatsApp n8n Workflows**.

**Proceed with Step 1 and Step 2 now?**
