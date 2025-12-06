#!/bin/bash
# Complete VPS setup script for CustomVPN
# Run this on a fresh Ubuntu VPS

set -e

echo "========================================"
echo "  CustomVPN VPS Setup Script"
echo "========================================"
echo ""

# Update system
echo "[1/5] Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Install Docker
echo "[2/5] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    sudo usermod -aG docker ubuntu
    echo "✓ Docker installed"
else
    echo "✓ Docker already installed"
fi

# Install Docker Compose
echo "[3/5] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✓ Docker Compose installed"
else
    echo "✓ Docker Compose already installed"
fi

# Install Poetry
echo "[4/5] Installing Poetry..."
if ! command -v poetry &> /dev/null && [ ! -f /root/.local/bin/poetry ]; then
    curl -sSL https://install.python-poetry.org | sudo python3 -
    echo "✓ Poetry installed at /root/.local/bin/poetry"
else
    echo "✓ Poetry already installed"
fi

# Install Xray
echo "[5/5] Installing Xray..."
if ! command -v xray &> /dev/null; then
    sudo bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
    echo "✓ Xray installed"
else
    echo "✓ Xray already installed"
fi

# Install other dependencies
sudo apt-get install -y git unzip python3-pip netcat-openbsd

echo ""
echo "========================================"
echo "  Installation Summary"
echo "========================================"
docker --version
docker-compose --version
if [ -f /root/.local/bin/poetry ]; then
    sudo /root/.local/bin/poetry --version
else
    poetry --version
fi
xray version | head -1
git --version

echo ""
echo "✓ VPS setup complete!"
echo ""
echo "Next steps:"
echo "  1. Clone repository: git clone https://github.com/sshaunn/customVpn.git"
echo "  2. Copy config.env to customVpn/"
echo "  3. Run deployment: cd customVpn && sudo bash deploy.sh"
