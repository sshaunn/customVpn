#!/bin/bash
# Setup fail2ban to protect SSH on port 2222

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

SSH_PORT=2222
FAIL2BAN_JAIL="/etc/fail2ban/jail.local"

echo "Setting up fail2ban..."

# Install fail2ban if not present
if ! command -v fail2ban-client &> /dev/null; then
    echo "Installing fail2ban..."
    apt-get update -qq
    apt-get install -y fail2ban
fi

# Create jail.local configuration
echo "Creating fail2ban jail configuration..."

cat > "$FAIL2BAN_JAIL" <<EOF
# Custom fail2ban configuration for VPN server

[DEFAULT]
# Ban duration (10 minutes)
bantime = 600

# Time window for counting failures (10 minutes)
findtime = 600

# Max failures before ban
maxretry = 3

# Email alerts disabled
destemail = root@localhost
sendername = Fail2Ban
action = %(action_)s

[sshd]
enabled = true
port = $SSH_PORT
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 1800
findtime = 600

[sshd-ddos]
enabled = true
port = $SSH_PORT
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 2
bantime = 3600
findtime = 600
EOF

# Create sshd-ddos filter if it doesn't exist
DDOS_FILTER="/etc/fail2ban/filter.d/sshd-ddos.conf"
if [ ! -f "$DDOS_FILTER" ]; then
    echo "Creating sshd-ddos filter..."
    cat > "$DDOS_FILTER" <<EOF
[Definition]
failregex = ^.* Did not receive identification string from <HOST>
            ^.* Connection closed by <HOST> \[preauth\]
            ^.* Failed .* for .* from <HOST>
ignoreregex =
EOF
fi

# Enable and start fail2ban
echo "Enabling and starting fail2ban..."
systemctl enable fail2ban
systemctl restart fail2ban

# Wait for fail2ban to start
sleep 2

# Display status
echo ""
echo "fail2ban configured successfully!"
echo ""
fail2ban-client status

echo ""
echo "SSH protection status:"
fail2ban-client status sshd

echo ""
echo "Configuration:"
echo "  - SSH port: $SSH_PORT"
echo "  - Max retries: 3 attempts in 10 minutes"
echo "  - Ban time: 30 minutes (first offense)"
echo "  - DDOS protection: enabled"
echo ""
echo "To check banned IPs: fail2ban-client status sshd"
echo "To unban IP: fail2ban-client set sshd unbanip <IP>"
