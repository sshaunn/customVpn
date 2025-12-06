import json
import time
import socket
from pathlib import Path
import pytest
from testcontainers.core.container import DockerContainer
from scripts.python.config_generator import ConfigGenerator
from scripts.python.key_generator import KeyGenerator


@pytest.fixture(scope="module")
def xray_config():
    """Generate test Xray config"""
    generator = ConfigGenerator()
    users = [{"uuid": KeyGenerator.generate_uuid(), "email": "test@user"}]

    config = generator.render_xray_config(
        users=users,
        xray_port=443,
        reality_sni="www.apple.com",
        reality_private_key="test_private_key_placeholder",
        reality_short_id="abcd1234"
    )

    return config


@pytest.fixture(scope="module")
def shadowsocks_config():
    """Generate test Shadowsocks config"""
    generator = ConfigGenerator()

    config = generator.render_shadowsocks_config(
        ss_port=8388,
        ss_password=KeyGenerator.generate_shadowsocks_password()
    )

    return config


@pytest.mark.integration
@pytest.mark.requires_docker
def test_xray_container_starts():
    """Integration test: Check if Xray container is running on VPS"""
    import subprocess

    result = subprocess.run(
        ["docker", "ps", "--filter", "name=xray-reality", "--format", "{{.Status}}"],
        capture_output=True,
        text=True
    )

    assert "Up" in result.stdout, f"Xray container not running: {result.stdout}"


@pytest.mark.integration
@pytest.mark.requires_docker
def test_shadowsocks_container_starts():
    """Integration test: Check if Shadowsocks container is running on VPS"""
    import subprocess

    result = subprocess.run(
        ["docker", "ps", "--filter", "name=shadowsocks-fallback", "--format", "{{.Status}}"],
        capture_output=True,
        text=True
    )

    assert "Up" in result.stdout, f"Shadowsocks container not running: {result.stdout}"


def test_port_available():
    """Helper test to check if ports are available for testing"""
    def is_port_free(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return True
            except OSError:
                return False

    assert is_port_free(8443), "Port 8443 not available for Xray testing"
    assert is_port_free(18388), "Port 18388 not available for Shadowsocks testing"


@pytest.mark.integration
@pytest.mark.requires_docker
def test_both_containers_together():
    """Integration test: Check if both VPN containers are running together"""
    import subprocess

    # Check both containers are running
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=xray-reality", "--filter", "name=shadowsocks-fallback", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )

    assert "xray-reality" in result.stdout, "Xray container not found"
    assert "shadowsocks-fallback" in result.stdout, "Shadowsocks container not found"

    # Check both are healthy
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.strip().split('\n')
    containers = {line.split('\t')[0]: line.split('\t')[1] for line in lines if '\t' in line}

    assert "Up" in containers.get("xray-reality", ""), "Xray not running"
    assert "Up" in containers.get("shadowsocks-fallback", ""), "Shadowsocks not running"
