#!/usr/bin/env python3
"""Generate client configuration files"""

import os
from pathlib import Path
from scripts.python.client_config_generator import ClientConfigGenerator

def main():
    # Load VPN keys
    keys_file = Path(__file__).parent / ".vpn_keys"
    if not keys_file.exists():
        print("Error: .vpn_keys not found. Run deployment first.")
        return

    keys = {}
    with open(keys_file) as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                keys[key] = value

    # Load config
    config_file = Path(__file__).parent / "config.env"
    config = {}
    with open(config_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value

    # Generate configs
    generator = ClientConfigGenerator()

    server_ip = config.get('VPS_IP', '54.206.37.229')

    print("=" * 60)
    print("  CustomVPN Client Configuration")
    print("=" * 60)
    print()

    # VLESS+REALITY link
    vless_link = generator.generate_vless_share_link(
        username="admin",
        uuid=keys['ADMIN_UUID'],
        server_ip=server_ip,
        port=int(config.get('XRAY_PORT', '443')),
        reality_sni=config.get('REALITY_SNI', 'www.apple.com'),
        reality_public_key=keys['REALITY_PUBLIC_KEY'],
        reality_short_id=keys['REALITY_SHORT_ID']
    )

    print("📱 VLESS+REALITY (Recommended)")
    print("-" * 60)
    print(vless_link)
    print()

    # Shadowsocks link
    ss_link = generator.generate_shadowsocks_share_link(
        username="admin",
        server_ip=server_ip,
        ss_port=int(config.get('SHADOWSOCKS_PORT', '8388')),
        ss_password=keys['SHADOWSOCKS_PASSWORD'],
        ss_method="2022-blake3-aes-256-gcm"
    )

    print("🔒 Shadowsocks (Fallback)")
    print("-" * 60)
    print(ss_link)
    print()

    # JSON config
    json_config = generator.generate_client_json_config(
        username="admin",
        uuid=keys['ADMIN_UUID'],
        server_ip=server_ip,
        xray_port=int(config.get('XRAY_PORT', '443')),
        reality_sni=config.get('REALITY_SNI', 'www.apple.com'),
        reality_public_key=keys['REALITY_PUBLIC_KEY'],
        reality_short_id=keys['REALITY_SHORT_ID'],
        ss_port=int(config.get('SHADOWSOCKS_PORT', '8388')),
        ss_password=keys['SHADOWSOCKS_PASSWORD'],
        ss_method="2022-blake3-aes-256-gcm"
    )

    # Save to file
    output_dir = Path(__file__).parent / "clients"
    output_dir.mkdir(exist_ok=True)

    config_file = output_dir / "admin.json"
    with open(config_file, 'w') as f:
        f.write(json_config)

    print(f"📄 JSON Config saved to: {config_file}")
    print()

    # Generate QR codes
    vless_qr = output_dir / "vless_qr.png"
    ss_qr = output_dir / "shadowsocks_qr.png"

    generator.generate_qr_code(vless_link, vless_qr)
    generator.generate_qr_code(ss_link, ss_qr)

    print(f"🔲 QR Codes saved:")
    print(f"  - VLESS: {vless_qr}")
    print(f"  - Shadowsocks: {ss_qr}")
    print()

    print("=" * 60)
    print("📱 Client Apps:")
    print("=" * 60)
    print("iOS:      v2Box, Shadowrocket")
    print("Android:  v2rayNG, ShadowsocksAndroid")
    print("macOS:    Qv2ray, ClashX")
    print("Windows:  v2rayN, Clash for Windows")
    print()
    print("Import the share links above or scan the QR codes!")
    print()

if __name__ == "__main__":
    main()
