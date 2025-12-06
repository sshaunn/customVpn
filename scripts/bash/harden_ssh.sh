#!/bin/bash
# SSH hardening: change port to 2222, disable password auth, key-only

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

SSH_CONFIG="/etc/ssh/sshd_config"
SSH_PORT=2222
BACKUP_CONFIG="${SSH_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

echo "Hardening SSH configuration..."

# Backup original config
echo "Backing up SSH config to $BACKUP_CONFIG..."
cp "$SSH_CONFIG" "$BACKUP_CONFIG"

# Create hardened SSH config
echo "Applying security settings..."

# Helper function to update or add SSH config option
update_ssh_option() {
    local option=$1
    local value=$2
    if grep -q "^#*${option}" "$SSH_CONFIG"; then
        sed -i.tmp "s|^#*${option}.*|${option} ${value}|" "$SSH_CONFIG"
    else
        echo "${option} ${value}" >> "$SSH_CONFIG"
    fi
}

# Change SSH port to 2222
update_ssh_option "Port" "$SSH_PORT"

# Disable password authentication
update_ssh_option "PasswordAuthentication" "no"

# Disable root login
update_ssh_option "PermitRootLogin" "prohibit-password"

# Enable public key authentication
update_ssh_option "PubkeyAuthentication" "yes"

# Disable empty passwords
update_ssh_option "PermitEmptyPasswords" "no"

# Disable challenge-response authentication
update_ssh_option "ChallengeResponseAuthentication" "no"

# Disable PAM authentication
update_ssh_option "UsePAM" "no"

# Disable X11 forwarding
update_ssh_option "X11Forwarding" "no"

# Set login grace time
update_ssh_option "LoginGraceTime" "30"

# Maximum authentication attempts
update_ssh_option "MaxAuthTries" "3"

# Maximum sessions
update_ssh_option "MaxSessions" "5"

# Protocol version 2 only
update_ssh_option "Protocol" "2"

# Clean up temp files
rm -f "${SSH_CONFIG}.tmp"

# Test SSH config
echo "Testing SSH configuration..."
sshd -t

if [ $? -eq 0 ]; then
    echo "SSH configuration is valid"

    # Restart SSH service
    echo "Restarting SSH service..."
    systemctl restart sshd || systemctl restart ssh

    echo ""
    echo "SSH hardening complete!"
    echo ""
    echo "IMPORTANT:"
    echo "  - SSH is now on port $SSH_PORT"
    echo "  - Password authentication is DISABLED"
    echo "  - Only SSH keys will work"
    echo "  - Make sure you have SSH keys configured BEFORE logging out!"
    echo ""
    echo "To connect: ssh -p $SSH_PORT user@host"
    echo ""
    echo "Backup saved to: $BACKUP_CONFIG"
else
    echo "Error: SSH configuration test failed"
    echo "Restoring backup..."
    cp "$BACKUP_CONFIG" "$SSH_CONFIG"
    exit 1
fi
