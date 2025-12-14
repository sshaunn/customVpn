#!/usr/bin/env python3
"""
Verifier - Health check and verification
"""

import subprocess
import socket
import ssl
import requests
from urllib.parse import urlparse


class Verifier:
    def __init__(self, ssh_alias, domain):
        """
        Initialize the verifier

        Args:
            ssh_alias: SSH config alias
            domain: Domain name to verify
        """
        self.ssh_alias = ssh_alias
        self.domain = domain

    def run_remote_command(self, command):
        """Run command on remote server"""
        ssh_cmd = ['ssh', self.ssh_alias, command]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode

    def check_docker_containers(self):
        """Check if all containers are running"""
        print("Checking Docker containers...")

        stdout, stderr, code = self.run_remote_command(
            "docker ps --format '{{.Names}}\t{{.Status}}' | grep -E '(xray|shadowsocks|nginx)'"
        )

        if code == 0:
            containers = stdout.strip().split('\n')
            expected = {'xray', 'shadowsocks', 'nginx'}
            running = set()

            for line in containers:
                if '\t' in line:
                    name, status = line.split('\t', 1)
                    if 'Up' in status:
                        running.add(name)
                        print(f"  ✓ {name}: {status}")

            if expected.issubset(running):
                return True
            else:
                missing = expected - running
                print(f"  ✗ Missing containers: {missing}")
                return False
        else:
            print(f"  ✗ Failed to check containers: {stderr}")
            return False

    def check_port(self, port, protocol='tcp'):
        """Check if a port is open"""
        try:
            if protocol == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.domain, port))
                sock.close()
                return result == 0
            return False
        except Exception as e:
            print(f"  ✗ Port check error: {e}")
            return False

    def check_ports(self):
        """Check if required ports are accessible"""
        print("\nChecking ports...")

        ports = {
            80: 'HTTP',
            443: 'HTTPS',
            8388: 'Shadowsocks'
        }

        results = {}
        for port, service in ports.items():
            is_open = self.check_port(port)
            results[service] = is_open
            status = "✓" if is_open else "✗"
            print(f"  {status} {service} (port {port})")

        return all(results.values())

    def check_ssl_certificate(self):
        """Check if SSL certificate is valid"""
        print("\nChecking SSL certificate...")

        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    print(f"  ✓ SSL certificate valid")
                    print(f"    Issued to: {cert.get('subject', [[('commonName', 'Unknown')]])[0][0][1]}")
                    print(f"    Issued by: {cert.get('issuer', [[('organizationName', 'Unknown')]])[0][0][1]}")
                    return True
        except ssl.SSLError as e:
            print(f"  ✗ SSL error: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Certificate check failed: {e}")
            return False

    def check_website(self):
        """Check if the fake website is accessible"""
        print("\nChecking website...")

        try:
            # Check HTTPS
            response = requests.get(f"https://{self.domain}", timeout=10, verify=True)
            if response.status_code == 200 and 'Shaun Studio' in response.text:
                print(f"  ✓ Website accessible (HTTPS)")
                print(f"    Status: {response.status_code}")
                return True
            else:
                print(f"  ✗ Website returned unexpected content")
                return False
        except requests.exceptions.SSLError as e:
            print(f"  ✗ SSL verification failed: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Website check failed: {e}")
            return False

    def check_http_redirect(self):
        """Check if HTTP redirects to HTTPS"""
        print("\nChecking HTTP to HTTPS redirect...")

        try:
            response = requests.get(
                f"http://{self.domain}",
                timeout=10,
                allow_redirects=False
            )
            if response.status_code == 301 and 'https://' in response.headers.get('Location', ''):
                print(f"  ✓ HTTP redirects to HTTPS")
                return True
            else:
                print(f"  ✗ No redirect (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"  ✗ Redirect check failed: {e}")
            return False

    def verify_all(self):
        """
        Run all verification checks

        Returns:
            dict: Results of all checks
        """
        print("=" * 60)
        print("Starting Verification")
        print("=" * 60)

        results = {
            'containers': self.check_docker_containers(),
            'ports': self.check_ports(),
            'ssl': self.check_ssl_certificate(),
            'website': self.check_website(),
            'redirect': self.check_http_redirect(),
        }

        print("\n" + "=" * 60)
        print("Verification Summary")
        print("=" * 60)

        all_passed = all(results.values())

        for check, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {check.capitalize()}")

        print("=" * 60)

        if all_passed:
            print("✓ All checks passed! VPN is ready to use.")
        else:
            print("✗ Some checks failed. Please review the output above.")

        return results


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: verifier.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]

    verifier = Verifier(ssh_alias='customvpn', domain=domain)
    results = verifier.verify_all()

    sys.exit(0 if all(results.values()) else 1)
