#!/usr/bin/env python3
"""Generate VPN keys and configurations"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.key_generator import KeyGenerator
from scripts.python.config_generator import ConfigGenerator


def main():
    # Load environment variables
    xray_port = int(os.getenv("XRAY_PORT", "443"))
    shadowsocks_port = int(os.getenv("SHADOWSOCKS_PORT", "8388"))
    reality_sni = os.getenv("REALITY_SNI", "www.apple.com")

    print("Generating VPN keys...")
    keys = KeyGenerator.generate_all_keys()

    print(f"✓ Admin UUID: {keys['admin_uuid']}")
    print(f"✓ REALITY Public Key: {keys['reality_public_key']}")
    print(f"✓ REALITY Short ID: {keys['reality_short_id']}")
    print(f"✓ Shadowsocks Password: {keys['shadowsocks_password'][:20]}...")

    # Save keys to .env file for persistence
    keys_file = project_root / ".vpn_keys"
    with open(keys_file, "w") as f:
        f.write(f"ADMIN_UUID={keys['admin_uuid']}\n")
        f.write(f"REALITY_PRIVATE_KEY={keys['reality_private_key']}\n")
        f.write(f"REALITY_PUBLIC_KEY={keys['reality_public_key']}\n")
        f.write(f"REALITY_SHORT_ID={keys['reality_short_id']}\n")
        f.write(f"SHADOWSOCKS_PASSWORD={keys['shadowsocks_password']}\n")

    print(f"\n✓ Keys saved to {keys_file}")

    # Generate configurations
    print("\nGenerating VPN configurations...")
    generator = ConfigGenerator()

    users = [
        {
            "uuid": keys["admin_uuid"],
            "email": "admin@customvpn.local"
        }
    ]

    output_dir = project_root / "docker"

    configs = generator.generate_all_configs(
        users=users,
        xray_port=xray_port,
        reality_sni=reality_sni,
        reality_private_key=keys["reality_private_key"],
        reality_short_id=keys["reality_short_id"],
        ss_port=shadowsocks_port,
        ss_password=keys["shadowsocks_password"],
        output_dir=output_dir
    )

    print(f"✓ Xray config: {configs['xray']}")
    print(f"✓ Shadowsocks config: {configs['shadowsocks']}")
    print("\n✓ Setup complete!")


if __name__ == "__main__":
    main()
