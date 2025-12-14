#!/usr/bin/env python3
"""
Deployer - Remote deployment orchestration
"""

import time
import subprocess


class Deployer:
    def __init__(self, ssh_alias, remote_user, remote_base_dir='/home/shaun/vpn'):
        """
        Initialize the deployer

        Args:
            ssh_alias: SSH config alias
            remote_user: Remote username
            remote_base_dir: Base directory for VPN files on remote server
        """
        self.ssh_alias = ssh_alias
        self.remote_user = remote_user
        self.remote_base_dir = remote_base_dir

    def run_remote_command(self, command, check=True):
        """
        Run a command on the remote server

        Args:
            command: Command to execute
            check: Raise exception on non-zero exit code

        Returns:
            tuple: (stdout, stderr, return_code)
        """
        ssh_cmd = ['ssh', self.ssh_alias, command]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True)

        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {command}\nError: {result.stderr}")

        return result.stdout, result.stderr, result.returncode

    def install_dependencies(self):
        """Install required packages on VPS"""
        print("Installing dependencies...")

        commands = [
            "sudo apt-get update -qq",
            "sudo apt-get install -y certbot",
        ]

        for cmd in commands:
            stdout, stderr, code = self.run_remote_command(cmd)
            if code == 0:
                print(f"  ✓ {cmd.split()[-1]}")
            else:
                print(f"  ✗ {cmd}: {stderr}")

    def obtain_ssl_certificate(self, domain, email):
        """
        Obtain SSL certificate using certbot

        Args:
            domain: Domain name
            email: Email for certbot

        Returns:
            bool: True if successful
        """
        print(f"Obtaining SSL certificate for {domain}...")

        # Stop nginx if running
        self.run_remote_command("docker stop nginx 2>/dev/null || true", check=False)

        # Get certificate
        certbot_cmd = (
            f"sudo certbot certonly --standalone "
            f"--non-interactive --agree-tos "
            f"-m {email} -d {domain}"
        )

        stdout, stderr, code = self.run_remote_command(certbot_cmd, check=False)

        if code == 0:
            print("  ✓ SSL certificate obtained")

            # Copy certs to VPN directory
            self.run_remote_command(
                f"sudo cp /etc/letsencrypt/live/{domain}/fullchain.pem {self.remote_base_dir}/ssl/ && "
                f"sudo cp /etc/letsencrypt/live/{domain}/privkey.pem {self.remote_base_dir}/ssl/ && "
                f"sudo chown {self.remote_user}:{self.remote_user} {self.remote_base_dir}/ssl/*.pem"
            )
            print("  ✓ SSL certificates copied")
            return True
        else:
            print(f"  ✗ SSL certificate failed: {stderr}")
            return False

    def pull_docker_images(self):
        """Pull Docker images from registries"""
        print("Pulling Docker images...")

        images = [
            "ghcr.io/xtls/xray-core:latest",
            "ghcr.io/shadowsocks/ssserver-rust:latest",
            "nginx:alpine"
        ]

        for image in images:
            stdout, stderr, code = self.run_remote_command(f"docker pull {image}")
            if code == 0:
                print(f"  ✓ {image}")
            else:
                print(f"  ✗ {image}: {stderr}")

    def start_containers(self):
        """Start Docker containers using docker-compose"""
        print("Starting containers...")

        # Navigate to VPN directory and start
        cmd = f"cd {self.remote_base_dir} && docker compose up -d"
        stdout, stderr, code = self.run_remote_command(cmd)

        if code == 0:
            print("  ✓ Containers started")
            time.sleep(3)  # Wait for containers to start
            return True
        else:
            print(f"  ✗ Failed to start containers: {stderr}")
            return False

    def stop_containers(self):
        """Stop all running containers"""
        print("Stopping containers...")

        cmd = f"cd {self.remote_base_dir} && docker compose down"
        stdout, stderr, code = self.run_remote_command(cmd, check=False)

        if code == 0:
            print("  ✓ Containers stopped")
        else:
            print(f"  ✗ Failed to stop containers: {stderr}")

    def restart_containers(self):
        """Restart all containers"""
        print("Restarting containers...")
        self.stop_containers()
        time.sleep(2)
        return self.start_containers()

    def get_container_status(self):
        """Get status of all containers"""
        stdout, stderr, code = self.run_remote_command("docker ps --format '{{.Names}}\t{{.Status}}'")
        return stdout

    def deploy(self, domain, email):
        """
        Full deployment process

        Args:
            domain: Domain name
            email: Email for SSL certificate

        Returns:
            bool: True if deployment successful
        """
        print("=" * 60)
        print("Starting VPN Deployment")
        print("=" * 60)

        try:
            # Step 1: Install dependencies
            self.install_dependencies()

            # Step 2: Obtain SSL certificate
            if not self.obtain_ssl_certificate(domain, email):
                return False

            # Step 3: Pull Docker images
            self.pull_docker_images()

            # Step 4: Start containers
            if not self.start_containers():
                return False

            # Step 5: Show status
            print("\nContainer Status:")
            print(self.get_container_status())

            print("\n" + "=" * 60)
            print("Deployment Complete!")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n✗ Deployment failed: {e}")
            return False


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: deployer.py <domain> <email>")
        sys.exit(1)

    domain = sys.argv[1]
    email = sys.argv[2]

    deployer = Deployer(ssh_alias='customvpn', remote_user='shaun')
    success = deployer.deploy(domain, email)

    sys.exit(0 if success else 1)
