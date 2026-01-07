#!/bin/bash

# Phase 1 Data Ingestion - Automated Execution Script
# This script automates the entire Phase 1 data foundation setup

set -e  # Exit on error

echo "=========================================="
echo "🚀 ALSAKR V2 - PHASE 1 DATA INGESTION"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "[Step 1/6] Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Check services are running
echo "[Step 2/6] Verifying services..."

# Wait for Elasticsearch
echo "  Waiting for Elasticsearch..."
timeout=60
counter=0
until docker exec alsakr-es curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        echo -e "${RED}✗ Elasticsearch not responding${NC}"
        exit 1
    fi
    sleep 1
done
echo -e "${GREEN}  ✓ Elasticsearch ready${NC}"

# Wait for Qdrant
echo "  Waiting for Qdrant..."
counter=0
until docker exec alsakr-qdrant wget --no-verbose --tries=1 --spider http://localhost:6333/collections > /dev/null 2>&1 || [ "$(docker inspect -f '{{.State.Running}}' alsakr-qdrant)" == "true" ]; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        echo -e "${RED}✗ Qdrant not responding${NC}"
        exit 1
    fi
    sleep 1
done
echo -e "${GREEN}  ✓ Qdrant ready${NC}"

# Wait for Ollama
echo "  Waiting for Ollama..."
counter=0
until docker exec alsakr-ollama ollama list > /dev/null 2>&1; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        echo -e "${RED}✗ Ollama not responding${NC}"
        exit 1
    fi
    sleep 1
done
echo -e "${GREEN}  ✓ Ollama ready${NC}"
echo ""

# Pull AI models
echo "[Step 3/6] Pulling AI models..."

# Check if embedding model exists
if ! docker exec alsakr-ollama ollama list | grep -q "nomic-embed-text"; then
    echo "  Pulling nomic-embed-text..."
    docker exec alsakr-ollama ollama pull nomic-embed-text
    echo -e "${GREEN}  ✓ Embedding model ready${NC}"
else
    echo -e "${YELLOW}  ℹ Embedding model already exists${NC}"
fi

# Check if chat model exists
if ! docker exec alsakr-ollama ollama list | grep -q "llama3.2"; then
    echo "  Pulling llama3.2..."
    docker exec alsakr-ollama ollama pull llama3.2
    echo -e "${GREEN}  ✓ Chat model ready${NC}"
else
    echo -e "${YELLOW}  ℹ Chat model already exists${NC}"
fi
echo ""

# Run product ingestion
echo "[Step 4/6] Importing products to Elasticsearch..."
docker exec alsakr-backend python -m app.core.ingest_products
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Product import completed${NC}"
else
    echo -e "${RED}✗ Product import failed${NC}"
    exit 1
fi
echo ""

# Generate embeddings
echo "[Step 5/6] Generating vector embeddings..."
echo -e "${YELLOW}⏳ This may take 20-30 minutes...${NC}"
docker exec alsakr-backend python -m app.core.generate_embeddings
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Embeddings generated${NC}"
else
    echo -e "${RED}✗ Embedding generation failed${NC}"
    exit 1
fi
echo ""

# Verify data
echo "[Step 6/6] Verifying data ingestion..."

# Check via API (internal)
response=$(docker exec alsakr-backend curl -s http://localhost:8000/api/data/status)
echo "  Data Status:"
echo "  $response" | python3 -m json.tool || echo "  $response"
echo ""

# Final summary
echo "=========================================="
echo -e "${GREEN}✨ PHASE 1 COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Test search: curl 'http://localhost:8000/api/search/products?q=reflector'"
echo "  2. View API docs: http://localhost:8000/docs"
echo "  3. Check frontend: http://localhost:3000/command-center"
echo ""
echo "Data foundation is ready for Phase 2!"
