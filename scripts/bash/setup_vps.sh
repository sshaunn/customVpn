#!/bin/bash
# VPS initial setup: Docker, Python, system packages

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

echo "Starting VPS setup for CustomVPN..."
echo "Target: Ubuntu 24.04 LTS"
echo ""

# Update system
echo "[1/7] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# Install essential packages
echo "[2/7] Installing essential packages..."
apt-get install -y -qq \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    gnupg \
    gpg \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    apt-transport-https \
    software-properties-common

# Install Docker
echo "[3/7] Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Enable and start Docker
    systemctl enable docker
    systemctl start docker

    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

# Verify Docker
docker --version
docker compose version

# Install Poetry for Python dependency management
echo "[4/7] Installing Poetry..."
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="/root/.local/bin:$PATH"
    echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc
    echo "Poetry installed successfully"
else
    echo "Poetry already installed"
fi

# Verify Poetry
/root/.local/bin/poetry --version

# Install AWS CLI for S3 backups
echo "[5/7] Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install
    rm -rf /tmp/aws /tmp/awscliv2.zip
    echo "AWS CLI installed successfully"
else
    echo "AWS CLI already installed"
fi

# Verify AWS CLI
aws --version

# Create VPN user (non-root for running services)
echo "[6/7] Creating VPN service user..."
if ! id "vpnuser" &>/dev/null; then
    useradd -m -s /bin/bash vpnuser
    usermod -aG docker vpnuser
    echo "VPN user created: vpnuser"
else
    echo "VPN user already exists: vpnuser"
fi

# Set timezone to Singapore
echo "[7/7] Setting timezone to Asia/Singapore..."
timedatectl set-timezone Asia/Singapore

echo ""
echo "VPS setup complete!"
echo ""
echo "Installed:"
echo "  - Docker: $(docker --version | cut -d' ' -f3)"
echo "  - Docker Compose: $(docker compose version | cut -d' ' -f4)"
echo "  - Python: $(python3 --version | cut -d' ' -f2)"
echo "  - Poetry: $(/root/.local/bin/poetry --version | cut -d' ' -f3)"
echo "  - AWS CLI: $(aws --version | cut -d' ' -f1 | cut -d'/' -f2)"
echo "  - GPG: $(gpg --version | head -1 | cut -d' ' -f3)"
echo ""
echo "VPN user: vpnuser (member of docker group)"
echo "Timezone: $(timedatectl show -p Timezone --value)"
echo ""
echo "Next steps:"
echo "  1. Run harden_ssh.sh to secure SSH"
echo "  2. Run setup_firewall.sh to configure UFW"
echo "  3. Run setup_fail2ban.sh for intrusion prevention"
echo "  4. Run deploy.sh to deploy VPN services"
