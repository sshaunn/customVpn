# CustomVPN V2

**Status**: V2 Rewrite in Progress

Clean Python-based VPN deployment for bypassing GFW.

## Current Setup
- **VPS**: Bandwagon 80.251.215.127 (user: shaun)
- **Domain**: shaunstudio.vip
- **Stack**: Python 3, Docker, Xray, Shadowsocks
- **SSH**: `ssh customvpn`

## Project Structure

```
customVpn/
├── coreV2/              # V2 implementation (active)
│   ├── TASKS_V2.md      # 14 tasks breakdown
│   ├── CHANGELOG_V2.md  # V2 changelog
│   ├── scripts/         # Python deployment scripts
│   ├── configs/         # Config templates
│   ├── docker/          # Dockerfiles
│   └── tests/           # Unit tests
├── config.env           # VPS credentials
└── README.md            # This file
```

## Quick Start (V2)

```bash
cd coreV2
# TODO: Coming soon
python deploy.py
```

## Old Version (V1)

The previous implementation has been cleaned up. See git history for reference.

## License

Private use only
