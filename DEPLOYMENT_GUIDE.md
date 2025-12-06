# CustomVPN Deployment Guide

Complete guide for deploying your VPN to a Singapore VPS.

## Prerequisites

1. **VPS Requirements**
   - Ubuntu 24.04 LTS
   - 1GB RAM minimum
   - Singapore region
   - Root SSH access

2. **Local Requirements**
   - Git
   - SSH key pair
   - AWS account (S3 access)
   - Telegram bot token

## Quick Deployment (5 Steps)

### 1. Clone Repository on VPS

```bash
ssh root@your-vps-ip
git clone git@github.com:sshaunn/customVpn.git
cd customVpn
```

### 2. Run VPS Setup

```bash
# Install Docker, Python, Poetry, AWS CLI
bash scripts/bash/setup_vps.sh
```

### 3. Configure Environment

```bash
cp config.env.template config.env
nano config.env
```

Fill in your credentials:
- AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
- S3_BUCKET_NAME
- GPG_PASSPHRASE
- TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
- REALITY_SNI (keep: www.apple.com)

### 4. Harden Security

```bash
# Setup firewall (UFW)
bash scripts/bash/setup_firewall.sh

# Harden SSH (IMPORTANT: ensure you have SSH keys before running!)
bash scripts/bash/harden_ssh.sh

# Setup fail2ban
bash scripts/bash/setup_fail2ban.sh
```

### 5. Deploy VPN

```bash
bash deploy.sh
```

## Post-Deployment

### Add Users

```bash
poetry run python scripts/python/user_manager.py add john john@email.com
```

### Generate Client Configs

```bash
poetry run python scripts/python/client_config_generator.py
```

QR codes and configs will be in `clients/` directory.

### Setup Monitoring

```bash
# Install health check cron (runs every 5 minutes)
bash scripts/bash/setup_cron.sh
```

### Create Backup

```bash
poetry run python scripts/python/s3_backup.py
```

## Verification

Check services are running:

```bash
docker compose ps
poetry run python scripts/python/health_monitor.py --check-only
```

Expected output:
- xray-reality: Running
- shadowsocks-fallback: Running
- Port 443: Listening
- Port 8388: Listening

## Client Setup

### macOS (Qv2ray / V2RayU)

1. Import JSON config from `clients/macos/`
2. Or scan QR code

### Android (v2rayNG)

1. Scan QR code from `clients/android/`
2. Or import share link

### Windows (v2rayN)

1. Import JSON config from `clients/windows/`
2. Or paste share link

## Troubleshooting

### Services won't start

```bash
docker compose logs -f
```

### Firewall blocking connections

```bash
ufw status verbose
ufw allow 443/tcp
```

### SSH locked out

If you get locked out after SSH hardening, use VPS console to:
```bash
systemctl stop ssh
nano /etc/ssh/sshd_config
# Change Port back to 22 and PasswordAuthentication yes
systemctl start ssh
```

### Check health monitor

```bash
cat logs/health_monitor.log
```

## Maintenance

### View logs

```bash
docker compose logs -f xray
docker compose logs -f shadowsocks
```

### Restart services

```bash
docker compose restart
```

### Update containers

Watchtower auto-updates daily. Manual update:
```bash
docker compose pull
docker compose up -d
```

### Check banned IPs (fail2ban)

```bash
fail2ban-client status sshd
```

### Restore from backup

```bash
poetry run python scripts/python/s3_backup.py --restore
```

## Security Checklist

- [ ] SSH on port 2222, password auth disabled
- [ ] UFW firewall active with whitelist
- [ ] fail2ban monitoring SSH
- [ ] GPG encryption for backups
- [ ] Telegram alerts working
- [ ] Health monitoring cron active
- [ ] Docker containers running as non-root
- [ ] No secrets in git repository

## VPN Connection Details

**Primary (VLESS+REALITY)**
- Port: 443
- Protocol: VLESS
- Security: REALITY
- SNI: www.apple.com
- Best for: General use, looks like HTTPS

**Fallback (Shadowsocks)**
- Port: 8388
- Protocol: Shadowsocks-2022
- Cipher: 2022-blake3-aes-128-gcm
- Best for: High censorship scenarios

## Support

Issues: https://github.com/sshaunn/customVpn/issues

Telegram bot for alerts: @alert_notify_me_bot
