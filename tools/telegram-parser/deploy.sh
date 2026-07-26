#!/bin/bash
# AION Invite Machine — One-command Deploy
# Usage: bash deploy.sh

set -e

echo "⟁ AION Invite Machine — Deploy"
echo "========================================"

# Check docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Install Docker first."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    # Generate random secret
    SECRET=$(openssl rand -hex 32 2>/dev/null || echo "change-this-in-production")
    sed -i "s/change-this-in-production/$SECRET/" .env
    echo "  → Set random SECRET_KEY"
fi

# Build and start
echo ""
echo "Building Docker image..."
docker compose build

echo ""
echo "Starting server..."
docker compose up -d

echo ""
echo "⟁ Deploy complete!"
echo "  Admin panel : http://localhost:5000"
echo "  Login       : http://localhost:5000/login"
echo ""
echo "  Node clients: python node.py --server http://<THIS_IP>:5000"
echo "========================================"
