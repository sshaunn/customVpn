#!/bin/bash
# Run integration tests on VPS
set -e

VPS_IP="54.206.37.229"
SSH_KEY="/Users/shenpeng/Git/customVpn/customvpn-key.pem"
SSH_USER="ubuntu"

echo "=================================="
echo "  Running Integration Tests on VPS"
echo "=================================="
echo ""
echo "VPS: $VPS_IP"
echo ""

# Make sure code is up to date on VPS
echo "[1/3] Syncing code to VPS..."
ssh -i "$SSH_KEY" "$SSH_USER@$VPS_IP" "cd customVpn && git pull"

# Run integration tests on VPS
echo "[2/3] Running tests on VPS..."
ssh -i "$SSH_KEY" "$SSH_USER@$VPS_IP" "cd customVpn && sudo /root/.local/bin/poetry run pytest tests/ -v -m integration --tb=short 2>&1"

echo ""
echo "[3/3] Test Summary"
echo "✓ Integration tests completed on VPS"
echo ""
