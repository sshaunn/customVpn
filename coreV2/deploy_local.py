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
    ws_path = config['WEBSOCKET_PATH']
    ss_port = int(config['SHADOWSOCKS_PORT'])
    email = config.get('ADMIN_EMAIL', f"{config['VPS_USER']}@{domain}")

    print(f"  ✓ Domain: {domain}")
    print(f"  ✓ UUID: {uuid}")
    print(f"  ✓ WebSocket: {ws_path}")

    # Step 2: Generate configurations
    print("\n" + "=" * 70)
    print("  Step 2: Generating Configurations")
    print("=" * 70 + "\n")

    project_dir = Path(__file__).parent
    config_dir = project_dir / 'configs'
    generated_dir = project_dir / 'generated'
    deploy_dir = Path.home() / 'vpn'

    generator = ConfigGenerator(config_dir=config_dir, output_dir=generated_dir)
    result = generator.generate_all(uuid, domain, ws_path, ss_port)

    print("  ✓ Xray config")
    print("  ✓ Shadowsocks config")
    print("  ✓ Nginx config")
    print(f"\n  Shadowsocks Password: {result['ss_password']}")

    # Step 3: Create deployment directory
    print("\n" + "=" * 70)
    print("  Step 3: Setting up deployment directory")
    print("=" * 70 + "\n")

    deploy_dir.mkdir(exist_ok=True)
    (deploy_dir / 'configs').mkdir(exist_ok=True)
    (deploy_dir / 'www').mkdir(exist_ok=True)
    (deploy_dir / 'ssl').mkdir(exist_ok=True)

    # Copy files to deployment directory
    import shutil
    shutil.copy(generated_dir / 'xray-config.json', deploy_dir / 'configs/')
    shutil.copy(generated_dir / 'shadowsocks-config.json', deploy_dir / 'configs/')
    shutil.copy(generated_dir / 'nginx.conf', deploy_dir / 'configs/')
    shutil.copy(generated_dir / 'docker-compose.yml', deploy_dir/)
    shutil.copy(generated_dir / 'index.html', deploy_dir / 'www/')

    print(f"  ✓ Files copied to {deploy_dir}")

    # Step 4: Install certbot if needed
    print("\n" + "=" * 70)
    print("  Step 4: Installing dependencies")
    print("=" * 70 + "\n")

    stdout, stderr, code = run_command("sudo apt-get install -y certbot")
    if code == 0:
        print("  ✓ Certbot installed")

    # Step 5: Get SSL certificate
    print("\n" + "=" * 70)
    print("  Step 5: Obtaining SSL certificate")
    print("=" * 70 + "\n")

    # Stop any existing containers
    run_command(f"docker compose -f {deploy_dir}/docker-compose.yml down", shell=True)

    # Get certificate
    cert_cmd = f"sudo certbot certonly --standalone --non-interactive --agree-tos -m {email} -d {domain}"
    stdout, stderr, code = run_command(cert_cmd, shell=True)

    if code == 0:
        print("  ✓ SSL certificate obtained")

        # Copy certs
        run_command(f"sudo cp /etc/letsencrypt/live/{domain}/fullchain.pem {deploy_dir}/ssl/", shell=True)
        run_command(f"sudo cp /etc/letsencrypt/live/{domain}/privkey.pem {deploy_dir}/ssl/", shell=True)
        run_command(f"sudo chown -R $USER:$USER {deploy_dir}/ssl/", shell=True)
        print("  ✓ Certificates copied")
    else:
        print(f"  ✗ SSL failed: {stderr}")
        print("  Continuing anyway...")

    # Step 6: Pull Docker images
    print("\n" + "=" * 70)
    print("  Step 6: Pulling Docker images")
    print("=" * 70 + "\n")

    images = [
        "ghcr.io/xtls/xray-core:latest",
        "ghcr.io/shadowsocks/ssserver-rust:latest",
        "nginx:alpine"
    ]

    for image in images:
        stdout, stderr, code = run_command(f"docker pull {image}")
        if code == 0:
            print(f"  ✓ {image}")

    # Step 7: Start containers
    print("\n" + "=" * 70)
    print("  Step 7: Starting containers")
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

    # Step 8: Generate client configs
    print("\n" + "=" * 70)
    print("  Step 8: Generating Client Configurations")
    print("=" * 70 + "\n")

    client_gen = ClientConfigGenerator(output_dir=project_dir / 'client_configs')
    client_results = client_gen.generate_all_configs(uuid, domain, ws_path, result['ss_password'], ss_port)

    print(f"\n  📋 Config files saved to: {project_dir / 'client_configs'}")
    print(f"\n  🔗 VLESS Link:\n  {client_results['vless_link']}")
    print(f"\n  🔗 Shadowsocks Link:\n  {client_results['ss_link']}")

    print("\n" + "=" * 70)
    print("  Deployment Complete!")
    print("=" * 70)
    print(f"\n  Website: https://{domain}")
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
