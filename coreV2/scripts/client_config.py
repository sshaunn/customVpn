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

    def generate_vless_link(self, uuid, domain, ws_path, port=443, tls=True):
        """
        Generate VLESS client link

        Args:
            uuid: User UUID
            domain: Server domain
            ws_path: WebSocket path
            port: Server port (default 443)
            tls: Enable TLS (default True)

        Returns:
            str: VLESS URI
        """
        security = "tls" if tls else "none"
        encoded_path = quote(ws_path, safe='')

        # VLESS URI format: vless://uuid@domain:port?parameters#tag
        vless_link = (
            f"vless://{uuid}@{domain}:{port}"
            f"?type=ws"
            f"&security={security}"
            f"&path={encoded_path}"
            f"&host={domain}"
            f"#{quote('CustomVPN-VLESS')}"
        )

        return vless_link

    def generate_shadowsocks_link(self, password, domain, port, method='2022-blake3-aes-256-gcm'):
        """
        Generate Shadowsocks client link

        Args:
            password: Shadowsocks password (base64 encoded)
            domain: Server domain
            port: Server port
            method: Encryption method

        Returns:
            str: Shadowsocks URI
        """
        import base64

        # SS URI format: ss://base64(method:password)@domain:port#tag
        auth_string = f"{method}:{password}"
        encoded_auth = base64.urlsafe_b64encode(auth_string.encode()).decode().rstrip('=')

        ss_link = f"ss://{encoded_auth}@{domain}:{port}#{quote('CustomVPN-SS')}"

        return ss_link

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

    def generate_all_configs(self, uuid, domain, ws_path, ss_password, ss_port=8388):
        """
        Generate all client configurations

        Args:
            uuid: VLESS user UUID
            domain: Server domain
            ws_path: WebSocket path
            ss_password: Shadowsocks password
            ss_port: Shadowsocks port

        Returns:
            dict: Paths and links for all configs
        """
        # Generate VLESS config
        vless_link = self.generate_vless_link(uuid, domain, ws_path)
        vless_qr = self.generate_qr_code(vless_link, 'vless_qr')

        # Generate Shadowsocks config
        ss_link = self.generate_shadowsocks_link(ss_password, domain, ss_port)
        ss_qr = self.generate_qr_code(ss_link, 'shadowsocks_qr')

        # Save text configs
        config_data = {
            'vless': {
                'link': vless_link,
                'uuid': uuid,
                'domain': domain,
                'port': 443,
                'path': ws_path,
                'tls': True,
                'network': 'ws'
            },
            'shadowsocks': {
                'link': ss_link,
                'server': domain,
                'port': ss_port,
                'password': ss_password,
                'method': '2022-blake3-aes-256-gcm'
            }
        }

        config_file = self.output_dir / 'client_configs.json'
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Save links to text file
        links_file = self.output_dir / 'links.txt'
        with open(links_file, 'w') as f:
            f.write("=== CustomVPN Client Configuration ===\n\n")
            f.write("VLESS (Primary - Recommended):\n")
            f.write(f"{vless_link}\n\n")
            f.write("Shadowsocks (Fallback):\n")
            f.write(f"{ss_link}\n\n")
            f.write("QR Codes:\n")
            f.write(f"  VLESS: {vless_qr}\n")
            f.write(f"  Shadowsocks: {ss_qr}\n")

        return {
            'vless_link': vless_link,
            'vless_qr': vless_qr,
            'ss_link': ss_link,
            'ss_qr': ss_qr,
            'config_file': config_file,
            'links_file': links_file
        }

    def print_client_instructions(self, results):
        """Print client setup instructions"""
        print("\n" + "=" * 60)
        print("Client Configuration Ready")
        print("=" * 60)

        print("\n📱 Mobile Clients:")
        print("  - V2rayNG (Android): Scan VLESS QR code")
        print("  - Shadowrocket (iOS): Scan VLESS QR code")
        print("  - Or use Shadowsocks QR as fallback")

        print("\n💻 Desktop Clients:")
        print("  - V2rayN (Windows): Import VLESS link")
        print("  - Qv2ray (Linux/Mac): Import VLESS link")
        print("  - Clash: Use Shadowsocks config")

        print("\n📋 Configuration Files:")
        print(f"  Links: {results['links_file']}")
        print(f"  JSON: {results['config_file']}")
        print(f"  VLESS QR: {results['vless_qr']}")
        print(f"  SS QR: {results['ss_qr']}")

        print("\n🔗 Quick Links:")
        print(f"\nVLESS:\n{results['vless_link']}")
        print(f"\nShadowsocks:\n{results['ss_link']}")

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
