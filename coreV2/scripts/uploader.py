#!/usr/bin/env python3
"""
Uploader - Upload files to VPS via SSH
"""

import subprocess
from pathlib import Path


class Uploader:
    def __init__(self, ssh_alias, remote_user, remote_host=None):
        """
        Initialize the uploader

        Args:
            ssh_alias: SSH config alias (e.g., 'customvpn')
            remote_user: Remote username
            remote_host: Optional remote host (used if ssh_alias not in config)
        """
        self.ssh_alias = ssh_alias
        self.remote_user = remote_user
        self.remote_host = remote_host

    def run_ssh_command(self, command):
        """
        Run a command on the remote server

        Args:
            command: Command to execute

        Returns:
            tuple: (stdout, stderr, return_code)
        """
        ssh_cmd = ['ssh', self.ssh_alias, command]

        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True
        )

        return result.stdout, result.stderr, result.returncode

    def upload_file(self, local_path, remote_path):
        """
        Upload a single file to the VPS

        Args:
            local_path: Local file path
            remote_path: Remote destination path

        Returns:
            bool: True if successful
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        scp_cmd = [
            'scp',
            str(local_path),
            f"{self.ssh_alias}:{remote_path}"
        ]

        result = subprocess.run(scp_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error uploading {local_path}: {result.stderr}")
            return False

        return True

    def upload_directory(self, local_dir, remote_dir):
        """
        Upload an entire directory to the VPS

        Args:
            local_dir: Local directory path
            remote_dir: Remote destination directory

        Returns:
            bool: True if successful
        """
        local_dir = Path(local_dir)
        if not local_dir.exists():
            raise FileNotFoundError(f"Local directory not found: {local_dir}")

        # Create remote directory
        self.run_ssh_command(f"mkdir -p {remote_dir}")

        # Upload directory recursively
        scp_cmd = [
            'scp',
            '-r',
            str(local_dir) + '/*',
            f"{self.ssh_alias}:{remote_dir}/"
        ]

        result = subprocess.run(scp_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error uploading directory {local_dir}: {result.stderr}")
            return False

        return True

    def upload_configs(self, generated_dir, remote_base_dir='/home/shaun/vpn'):
        """
        Upload all generated config files to VPS

        Args:
            generated_dir: Directory containing generated configs
            remote_base_dir: Base directory on remote server

        Returns:
            dict: Status of each upload
        """
        generated_dir = Path(generated_dir)

        # Create remote directories
        self.run_ssh_command(f"mkdir -p {remote_base_dir}/configs")
        self.run_ssh_command(f"mkdir -p {remote_base_dir}/www")
        self.run_ssh_command(f"mkdir -p {remote_base_dir}/ssl")

        results = {}

        # Upload config files
        config_files = {
            'xray-config.json': f"{remote_base_dir}/configs/xray-config.json",
            'shadowsocks-config.json': f"{remote_base_dir}/configs/shadowsocks-config.json",
            'nginx.conf': f"{remote_base_dir}/configs/nginx.conf",
            'docker-compose.yml': f"{remote_base_dir}/docker-compose.yml",
            'index.html': f"{remote_base_dir}/www/index.html",
        }

        for local_file, remote_file in config_files.items():
            local_path = generated_dir / local_file
            if local_path.exists():
                results[local_file] = self.upload_file(local_path, remote_file)
            else:
                print(f"Warning: {local_file} not found, skipping")
                results[local_file] = False

        return results


if __name__ == '__main__':
    # Example usage
    uploader = Uploader(ssh_alias='customvpn', remote_user='shaun')

    # Test SSH connection
    stdout, stderr, code = uploader.run_ssh_command('whoami')
    print(f"SSH test: {stdout.strip()} (exit code: {code})")

    # Upload configs
    results = uploader.upload_configs(generated_dir='../generated')
    print("\nUpload results:")
    for file, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {file}")
