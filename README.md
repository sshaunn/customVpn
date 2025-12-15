# CustomVPN - VLESS Reality

Stealth VPN for bypassing GFW using VLESS + Reality + Vision protocol.

## Setup

**VPS**: Bandwagon 80.251.215.127
**Domain**: shaunstudio.vip
**Protocol**: VLESS + Reality + Vision (mimics Microsoft)
**SSH**: `ssh customvpn`

## Project Structure

```
customVpn/
├── config.env              # VPN configuration
├── vless_reality_qr.png    # Client QR code
└── coreV2/
    ├── configs/            # Xray templates
    ├── scripts/            # Python deployment tools
    ├── deploy.py           # Local → VPS deployment
    └── deploy_local.py     # VPS-side deployment
```

## Deployment

### From Local Machine
```bash
cd coreV2
python deploy.py
```

### On VPS Directly
```bash
ssh customvpn
cd customVpn/coreV2
source venv/bin/activate
python deploy_local.py
```

## Client Setup

1. Scan QR code: `vless_reality_qr.png`
2. Import to v2rayNG (Android) or V2rayN (Windows)
3. Connect and enjoy

## How It Works

Reality makes your VPN traffic look like legitimate HTTPS to Microsoft:
- GFW sees: Valid Microsoft certificate
- GFW probes: Get real Microsoft website
- Your traffic: Fully encrypted and undetectable

## License

Private use only
