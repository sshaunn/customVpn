#!/usr/bin/env python3
"""
Main Deployment Script - Orchestrates entire VPN deployment
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(script_dir))

from config_generator import ConfigGenerator
from uploader import Uploader
from deployer import Deployer
from verifier import Verifier
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


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def main():
    print_banner("CustomVPN V2 - Automated Deployment")

    # Step 1: Load configuration
    print("Step 1: Loading configuration...")
    config = load_env_file()

    # Required config values
    required_keys = [
        'VPS_IP', 'VPS_USER', 'DOMAIN',
        'ADMIN_UUID', 'WEBSOCKET_PATH',
        'SHADOWSOCKS_PORT'
    ]

    for key in required_keys:
        if key not in config:
            print(f"Error: Missing required config: {key}")
            sys.exit(1)

    print(f"  ✓ Domain: {config['DOMAIN']}")
    print(f"  ✓ VPS: {config['VPS_IP']}")
    print(f"  ✓ UUID: {config['ADMIN_UUID']}")
    print(f"  ✓ WebSocket Path: {config['WEBSOCKET_PATH']}")

    # Step 2: Generate configurations
    print_banner("Step 2: Generating Configurations")

    project_dir = Path(__file__).parent
    config_dir = project_dir / 'configs'
    generated_dir = project_dir / 'generated'

    generator = ConfigGenerator(
        config_dir=config_dir,
        output_dir=generated_dir
    )

    result = generator.generate_all(
        uuid=config['ADMIN_UUID'],
        domain=config['DOMAIN'],
        ws_path=config['WEBSOCKET_PATH'],
        ss_port=int(config['SHADOWSOCKS_PORT'])
    )

    print("  ✓ Xray config")
    print("  ✓ Shadowsocks config")
    print("  ✓ Nginx config")
    print("  ✓ Static files")
    print(f"\n  Shadowsocks Password: {result['ss_password'][:40]}...")

    # Step 3: Upload to VPS
    print_banner("Step 3: Uploading Files to VPS")

    uploader = Uploader(
        ssh_alias='customvpn',
        remote_user=config['VPS_USER']
    )

    upload_results = uploader.upload_configs(
        generated_dir=generated_dir,
        remote_base_dir='/home/shaun/vpn'
    )

    success_count = sum(1 for v in upload_results.values() if v)
    print(f"\n  ✓ Uploaded {success_count}/{len(upload_results)} files")

    if not all(upload_results.values()):
        print("\n  ⚠ Some files failed to upload. Check errors above.")
        response = input("  Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)

    # Step 4: Deploy on VPS
    print_banner("Step 4: Deploying on VPS")

    # Use a default email or get from config
    email = config.get('ADMIN_EMAIL', f"{config['VPS_USER']}@{config['DOMAIN']}")

    deployer = Deployer(
        ssh_alias='customvpn',
        remote_user=config['VPS_USER']
    )

    deploy_success = deployer.deploy(
        domain=config['DOMAIN'],
        email=email
    )

    if not deploy_success:
        print("\n✗ Deployment failed!")
        sys.exit(1)

    # Step 5: Verify deployment
    print_banner("Step 5: Verifying Deployment")

    verifier = Verifier(
        ssh_alias='customvpn',
        domain=config['DOMAIN']
    )

    verify_results = verifier.verify_all()

    if not all(verify_results.values()):
        print("\n⚠ Some verification checks failed!")
        print("   VPN may still work, but some features might be unavailable.")

    # Step 6: Generate client configs
    print_banner("Step 6: Generating Client Configurations")

    client_gen = ClientConfigGenerator(
        output_dir=project_dir / 'client_configs'
    )

    client_results = client_gen.generate_all_configs(
        uuid=config['ADMIN_UUID'],
        domain=config['DOMAIN'],
        ws_path=config['WEBSOCKET_PATH'],
        ss_password=result['ss_password'],
        ss_port=int(config['SHADOWSOCKS_PORT'])
    )

    client_gen.print_client_instructions(client_results)

    # Final summary
    print_banner("Deployment Complete!")

    print("Next steps:")
    print("  1. Scan the QR code with your VPN client")
    print("  2. Or copy the VLESS link from client_configs/links.txt")
    print("  3. Test the connection")
    print(f"\n  Website: https://{config['DOMAIN']}")
    print(f"  Config files: {project_dir / 'client_configs'}")

    print("\n✓ VPN is ready to use!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
