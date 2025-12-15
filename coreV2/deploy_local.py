#!/usr/bin/env python3
"""
Local Deployment Script - Run this ON the VPS server
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(script_dir))

from config_generator import ConfigGenerator
from client_config import ClientConfigGenerator


def load_env_file(env_file='../config.env'):
    """Load environment variables from config file"""
    env_vars = {}
    env_path = Path(__file__).parent / env_file

    if not env_path.exists():
        print(f"Error: Config file not found: {env_path}")
        sys.exit(1)

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars


def run_command(cmd, shell=False):
    """Run command and return output"""
    result = subprocess.run(
        cmd if shell else cmd.split(),
        capture_output=True,
        text=True,
        shell=shell
    )
    return result.stdout, result.stderr, result.returncode


def main():
    print("\n" + "=" * 70)
    print("  CustomVPN V2 - Local Server Deployment")
    print("=" * 70 + "\n")

    # Step 1: Load configuration
    print("Step 1: Loading configuration...")
    config = load_env_file()

    domain = config['DOMAIN']
    uuid = config['ADMIN_UUID']
    reality_dest = config['REALITY_DEST']
    reality_server_names = [config['REALITY_SERVER_NAMES']]
    reality_private_key = config.get('REALITY_PRIVATE_KEY', '')
    reality_short_ids = [config.get('REALITY_SHORT_IDS', '')]

    # Generate keys if not provided
    if not reality_private_key:
        print("  Generating Reality keys...")
        private_key, public_key = ConfigGenerator.generate_reality_keypair()
        if private_key:
            reality_private_key = private_key
            print(f"  ✓ Private Key: {private_key}")
            print(f"  ✓ Public Key: {public_key}")
            print(f"\n  ⚠️  Add these to config.env:")
            print(f"     REALITY_PRIVATE_KEY={private_key}")
            print(f"     REALITY_PUBLIC_KEY={public_key}")
        else:
            print("  ✗ Failed to generate keys!")
            sys.exit(1)

    # Generate shortId if not provided
    if not reality_short_ids[0]:
        reality_short_ids = [ConfigGenerator.generate_short_id()]
        print(f"  ✓ Generated shortId: {reality_short_ids[0]}")
        print(f"  ⚠️  Add to config.env: REALITY_SHORT_IDS={reality_short_ids[0]}")

    print(f"  ✓ Domain: {domain}")
    print(f"  ✓ UUID: {uuid}")
    print(f"  ✓ Reality Dest: {reality_dest}")

    # Step 2: Generate configurations
    print("\n" + "=" * 70)
    print("  Step 2: Generating Configurations")
    print("=" * 70 + "\n")

    project_dir = Path(__file__).parent
    config_dir = project_dir / 'configs'
    generated_dir = project_dir / 'generated'
    deploy_dir = Path.home() / 'vpn'

    generator = ConfigGenerator(config_dir=config_dir, output_dir=generated_dir)
    result = generator.generate_all(uuid, reality_dest, reality_server_names, reality_private_key, reality_short_ids)

    print("  ✓ Xray Reality config")

    # Step 3: Create deployment directory
    print("\n" + "=" * 70)
    print("  Step 3: Setting up deployment directory")
    print("=" * 70 + "\n")

    deploy_dir.mkdir(exist_ok=True)
    (deploy_dir / 'configs').mkdir(exist_ok=True)

    # Copy files to deployment directory
    import shutil
    shutil.copy(generated_dir / 'xray-config.json', deploy_dir / 'configs/')
    shutil.copy(generated_dir / 'docker-compose.yml', deploy_dir)

    print(f"  ✓ Files copied to {deploy_dir}")

    # Step 4: Stop any existing containers
    print("\n" + "=" * 70)
    print("  Step 4: Stopping old containers")
    print("=" * 70 + "\n")

    run_command(f"docker compose -f {deploy_dir}/docker-compose.yml down", shell=True)
    print("  ✓ Old containers stopped")

    # Step 5: Pull Docker images
    print("\n" + "=" * 70)
    print("  Step 5: Pulling Docker images")
    print("=" * 70 + "\n")

    images = [
        "ghcr.io/xtls/xray-core:latest"
    ]

    for image in images:
        stdout, stderr, code = run_command(f"docker pull {image}")
        if code == 0:
            print(f"  ✓ {image}")

    # Step 6: Start containers
    print("\n" + "=" * 70)
    print("  Step 6: Starting containers")
    print("=" * 70 + "\n")

    stdout, stderr, code = run_command(f"docker compose -f {deploy_dir}/docker-compose.yml up -d", shell=True)
    if code == 0:
        print("  ✓ Containers started")
        time.sleep(3)

        # Show status
        stdout, _, _ = run_command("docker ps --format '{{.Names}}\t{{.Status}}'", shell=True)
        print("\n  Container Status:")
        for line in stdout.strip().split('\n'):
            print(f"    {line}")
    else:
        print(f"  ✗ Failed: {stderr}")

    # Step 7: Generate client configs
    print("\n" + "=" * 70)
    print("  Step 7: Generating Client Configurations")
    print("=" * 70 + "\n")

    # Get public key from config or generate
    reality_public_key = config.get('REALITY_PUBLIC_KEY', '')
    if not reality_public_key and reality_private_key:
        # Try to extract from generated keys
        _, reality_public_key = ConfigGenerator.generate_reality_keypair()

    client_gen = ClientConfigGenerator(output_dir=project_dir / 'client_configs')
    client_results = client_gen.generate_all_configs(
        uuid, domain, reality_server_names[0], reality_public_key, reality_short_ids[0]
    )

    print(f"\n  📋 Config files saved to: {project_dir / 'client_configs'}")
    print(f"\n  🔗 VLESS Reality Link:\n  {client_results['vless_link']}")

    print("\n" + "=" * 70)
    print("  Deployment Complete!")
    print("=" * 70)
    print(f"\n  Server: {domain}:443 (Reality)")
    print("  All systems ready!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
