#!/bin/bash
set -e

echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

echo "Installing Git..."
sudo apt-get install -y git

echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

echo "Installing Docker Compose..."
sudo apt-get install -y docker-compose-plugin

echo "Cleaning up..."
rm get-docker.sh

echo "Infrastructure setup complete!"
docker --version
docker compose version
