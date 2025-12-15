#!/usr/bin/env python3
"""
Client Config Generator - Generate VLESS and Shadowsocks client configs
"""

import json
import qrcode
from pathlib import Path
from urllib.parse import quote


class ClientConfigGenerator:
    def __init__(self, output_dir='../client_configs'):
        """
        Initialize the client config generator

        Args:
            output_dir: Directory to save client configs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_vless_link(self, uuid, domain, port=443, sni=None, public_key=None, short_id=None, fp='chrome'):
        """
        Generate VLESS Reality client link

        Args:
            uuid: User UUID
            domain: Server domain
            port: Server port (default 443)
            sni: Server Name Indication for Reality
            public_key: Reality public key
            short_id: Reality short ID
            fp: TLS fingerprint (default 'chrome')

        Returns:
            str: VLESS URI with Reality
        """
        # VLESS Reality URI format: vless://uuid@domain:port?parameters#tag
        vless_link = (
            f"vless://{uuid}@{domain}:{port}"
            f"?type=tcp"
            f"&security=reality"
            f"&pbk={public_key}"
            f"&fp={fp}"
            f"&sni={sni}"
            f"&sid={short_id}"
            f"&flow=xtls-rprx-vision"
            f"#{quote('CustomVPN-Reality')}"
        )

        return vless_link

    def generate_qr_code(self, data, filename):
        """
        Generate QR code from data

        Args:
            data: Data to encode
            filename: Output filename (without extension)

        Returns:
            Path: Path to saved QR code image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        output_file = self.output_dir / f"{filename}.png"
        img.save(output_file)

        return output_file

    def generate_all_configs(self, uuid, domain, sni, public_key, short_id):
        """
        Generate client configuration for Reality

        Args:
            uuid: VLESS user UUID
            domain: Server domain
            sni: Reality SNI
            public_key: Reality public key
            short_id: Reality short ID

        Returns:
            dict: Paths and links for config
        """
        # Generate VLESS Reality config
        vless_link = self.generate_vless_link(uuid, domain, sni=sni, public_key=public_key, short_id=short_id)
        vless_qr = self.generate_qr_code(vless_link, 'vless_reality_qr')

        # Save text configs
        config_data = {
            'vless_reality': {
                'link': vless_link,
                'uuid': uuid,
                'domain': domain,
                'port': 443,
                'sni': sni,
                'public_key': public_key,
                'short_id': short_id,
                'flow': 'xtls-rprx-vision',
                'security': 'reality',
                'network': 'tcp'
            }
        }

        config_file = self.output_dir / 'client_configs.json'
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Save links to text file
        links_file = self.output_dir / 'links.txt'
        with open(links_file, 'w') as f:
            f.write("=== CustomVPN Client Configuration (Reality) ===\n\n")
            f.write("VLESS Reality + Vision:\n")
            f.write(f"{vless_link}\n\n")
            f.write("QR Code:\n")
            f.write(f"  VLESS Reality: {vless_qr}\n")

        return {
            'vless_link': vless_link,
            'vless_qr': vless_qr,
            'config_file': config_file,
            'links_file': links_file
        }

    def print_client_instructions(self, results):
        """Print client setup instructions"""
        print("\n" + "=" * 60)
        print("Client Configuration Ready (Reality)")
        print("=" * 60)

        print("\n📱 Mobile Clients:")
        print("  - V2rayNG (Android): Scan VLESS Reality QR code")
        print("  - Shadowrocket (iOS): Scan VLESS Reality QR code")

        print("\n💻 Desktop Clients:")
        print("  - V2rayN (Windows): Import VLESS Reality link")
        print("  - NekoRay (Linux/Mac/Win): Import VLESS Reality link")

        print("\n📋 Configuration Files:")
        print(f"  Links: {results['links_file']}")
        print(f"  JSON: {results['config_file']}")
        print(f"  VLESS Reality QR: {results['vless_qr']}")

        print("\n🔗 Connection Link:")
        print(f"\n{results['vless_link']}")

        print("\n" + "=" * 60)


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 5:
        print("Usage: client_config.py <uuid> <domain> <ws_path> <ss_password> [ss_port]")
        sys.exit(1)

    uuid = sys.argv[1]
    domain = sys.argv[2]
    ws_path = sys.argv[3]
    ss_password = sys.argv[4]
    ss_port = int(sys.argv[5]) if len(sys.argv) > 5 else 8388

    generator = ClientConfigGenerator()
    results = generator.generate_all_configs(uuid, domain, ws_path, ss_password, ss_port)
    generator.print_client_instructions(results)
