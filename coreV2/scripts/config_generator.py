#!/usr/bin/env python3
"""
Config Generator - Renders Jinja2 templates with user configuration
"""

import os
import secrets
import base64
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class ConfigGenerator:
    def __init__(self, config_dir, output_dir):
        """
        Initialize the config generator

        Args:
            config_dir: Directory containing Jinja2 templates
            output_dir: Directory to write rendered configs
        """
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(self.config_dir),
            autoescape=False
        )

    @staticmethod
    def generate_reality_keypair():
        """Generate Reality private/public key pair using xray"""
        import subprocess
        try:
            result = subprocess.run(['xray', 'x25519'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            private_key = lines[0].split(': ')[1]
            public_key = lines[1].split(': ')[1]
            return private_key, public_key
        except Exception as e:
            print(f"Warning: Could not generate keys with xray x25519: {e}")
            print("Please generate keys manually and update config.env")
            return None, None

    @staticmethod
    def generate_short_id():
        """Generate a random 16-char hex shortId for Reality"""
        return secrets.token_hex(8)

    def render_xray_config(self, uuid, reality_dest, reality_server_names, reality_private_key, reality_short_ids):
        """Render Xray configuration with Reality"""
        template = self.env.get_template('xray.json.j2')
        content = template.render(
            uuid=uuid,
            reality_dest=reality_dest,
            reality_server_names=json.dumps(reality_server_names),
            reality_private_key=reality_private_key,
            reality_short_ids=json.dumps(reality_short_ids)
        )

        output_file = self.output_dir / 'xray-config.json'
        output_file.write_text(content)
        return output_file

    def copy_static_files(self):
        """Copy static files like docker-compose.yml"""
        import shutil

        static_files = ['docker-compose.yml']
        for filename in static_files:
            src = self.config_dir / filename
            if src.exists():
                dst = self.output_dir / filename
                shutil.copy(src, dst)

    def generate_all(self, uuid, reality_dest, reality_server_names, reality_private_key, reality_short_ids):
        """
        Generate all configuration files for Reality setup

        Args:
            uuid: VLESS user UUID
            reality_dest: Reality destination (e.g., "www.microsoft.com:443")
            reality_server_names: List of server names for Reality SNI
            reality_private_key: Reality private key
            reality_short_ids: List of short IDs for Reality

        Returns:
            dict: Paths to generated files
        """
        xray_config = self.render_xray_config(uuid, reality_dest, reality_server_names, reality_private_key, reality_short_ids)
        self.copy_static_files()

        return {
            'xray_config': xray_config
        }


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 5:
        print("Usage: config_generator.py <uuid> <domain> <ws_path> <ss_port>")
        sys.exit(1)

    uuid = sys.argv[1]
    domain = sys.argv[2]
    ws_path = sys.argv[3]
    ss_port = int(sys.argv[4])

    generator = ConfigGenerator(
        config_dir='../configs',
        output_dir='../generated'
    )

    result = generator.generate_all(uuid, domain, ws_path, ss_port)

    print("Generated configurations:")
    for key, value in result.items():
        print(f"  {key}: {value}")
