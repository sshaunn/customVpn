#!/bin/bash
# Setup UFW firewall with whitelist for VPN ports

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

echo "Setting up UFW firewall..."

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    echo "Installing UFW..."
    apt-get update -qq
    apt-get install -y ufw
fi

# Reset UFW to defaults
echo "Resetting UFW to defaults..."
ufw --force reset

# Set default policies
echo "Setting default policies (deny incoming, allow outgoing)..."
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (custom port 2222)
echo "Allowing SSH on port 2222..."
ufw allow 2222/tcp comment 'SSH custom port'

# Allow Xray REALITY (HTTPS port 443)
echo "Allowing Xray on port 443..."
ufw allow 443/tcp comment 'Xray VLESS+REALITY'

# Allow Shadowsocks (port 8388)
echo "Allowing Shadowsocks on port 8388..."
ufw allow 8388/tcp comment 'Shadowsocks fallback'
ufw allow 8388/udp comment 'Shadowsocks fallback UDP'

# Limit SSH connections to prevent brute force
echo "Limiting SSH connection rate..."
ufw limit 2222/tcp comment 'SSH rate limiting'

# Enable UFW
echo "Enabling UFW..."
ufw --force enable

# Display status
echo ""
echo "UFW firewall configured successfully!"
echo ""
ufw status verbose

echo ""
echo "Firewall rules:"
echo "  - SSH: port 2222 (rate limited)"
echo "  - Xray: port 443 (TCP)"
echo "  - Shadowsocks: port 8388 (TCP/UDP)"
echo "  - Default: DENY all other incoming"
