# CustomVPN

Secure VPN solution for bypassing GFW using VLESS+REALITY and Shadowsocks.

## Quick Start

```bash
# 1. Configure
cp config.env.template config.env
nano config.env

# 2. Deploy to VPS
./deploy.sh

# 3. Add user and get client config
python3 scripts/python/vpn_manager.py add-user yourname --platform macos
```

## Requirements

- VPS: Ubuntu 24.04 LTS, 1GB RAM, Singapore region
- Python: 3.10+
- Docker: 24.0+
- AWS S3: For encrypted backups

## Documentation

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Full deployment guide
- [docs/USER_MANAGEMENT.md](docs/USER_MANAGEMENT.md) - Managing users
- [docs/CLIENT_SETUP.md](docs/CLIENT_SETUP.md) - Client configuration

## Architecture

- Primary: VLESS + REALITY (port 443, SNI: www.apple.com)
- Fallback: Shadowsocks-2022 (port 8388)
- Monitoring: Health checks + Telegram alerts (real-time)
- Backup: Encrypted to S3 Melbourne (daily)

## Project Structure

```
customVpn/
├── scripts/
│   ├── bash/           # System operations
│   └── python/         # VPN management tools
├── templates/          # Jinja2 config templates
├── docker/             # Container definitions
├── clients/            # Client config outputs
├── docs/               # Documentation
└── tests/              # Test suite
```

## Security

- SSH: Port 2222, key-only authentication
- Firewall: UFW whitelist (443, 8388, 2222)
- Secrets: Never committed, .gitignore enforced
- Backups: GPG encrypted before S3 upload

## License

Private use only
