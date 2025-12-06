#!/bin/bash
# Master deployment script for CustomVPN

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.env"

echo "======================================"
echo "  CustomVPN Deployment Script"
echo "======================================"
echo ""

# Check if config.env exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: config.env not found"
    echo "Please copy config.env.template to config.env and configure it"
    exit 1
fi

# Load configuration
source "$CONFIG_FILE"

# Verify required variables
REQUIRED_VARS=(
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
    "S3_BUCKET_NAME"
    "GPG_PASSPHRASE"
    "TELEGRAM_BOT_TOKEN"
    "TELEGRAM_CHAT_ID"
    "REALITY_SNI"
    "XRAY_PORT"
    "SHADOWSOCKS_PORT"
)

echo "Checking configuration..."
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var not set in config.env"
        exit 1
    fi
done
echo "Configuration validated"
echo ""

# Install Python dependencies
echo "[1/6] Installing Python dependencies..."
if command -v poetry &> /dev/null; then
    poetry install --no-dev
else
    echo "Warning: Poetry not found, skipping dependency installation"
fi
echo ""

# Generate VPN keys and configs
echo "[2/6] Generating VPN keys and configurations..."
poetry run python scripts/python/key_generator.py

# Generate server configs
poetry run python scripts/python/config_generator.py
echo ""

# Build Docker images
echo "[3/6] Building Docker images..."
docker compose build
echo ""

# Stop existing containers
echo "[4/6] Stopping existing containers (if any)..."
docker compose down || true
echo ""

# Start VPN services
echo "[5/6] Starting VPN services..."
docker compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10
echo ""

# Verify services are running
echo "[6/6] Verifying services..."
docker compose ps

echo ""
echo "Checking service health..."

# Check Xray port
if nc -zv 127.0.0.1 "$XRAY_PORT" 2>&1 | grep -q succeeded; then
    echo "✓ Xray (port $XRAY_PORT): Running"
else
    echo "✗ Xray (port $XRAY_PORT): NOT responding"
fi

# Check Shadowsocks port
if nc -zv 127.0.0.1 "$SHADOWSOCKS_PORT" 2>&1 | grep -q succeeded; then
    echo "✓ Shadowsocks (port $SHADOWSOCKS_PORT): Running"
else
    echo "✗ Shadowsocks (port $SHADOWSOCKS_PORT): NOT responding"
fi

echo ""

# Send Telegram notification
echo "Sending deployment notification..."
poetry run python -c "
from scripts.python.telegram_notifier import TelegramNotifier
import os

notifier = TelegramNotifier(
    os.getenv('TELEGRAM_BOT_TOKEN'),
    os.getenv('TELEGRAM_CHAT_ID')
)
notifier.send_deployment_alert('VPN services deployed successfully on $(hostname)')
"

echo ""
echo "======================================"
echo "  Deployment Complete!"
echo "======================================"
echo ""
echo "VPN Services:"
echo "  - Xray VLESS+REALITY: port $XRAY_PORT"
echo "  - Shadowsocks: port $SHADOWSOCKS_PORT"
echo ""
echo "Next Steps:"
echo "  1. Add users: poetry run python scripts/python/user_manager.py add <username> <email>"
echo "  2. Generate client configs: poetry run python scripts/python/client_config_generator.py"
echo "  3. Setup monitoring cron: bash scripts/bash/setup_cron.sh"
echo "  4. Create backup: poetry run python scripts/python/s3_backup.py"
echo ""
echo "View logs: docker compose logs -f"
echo "Check status: docker compose ps"
