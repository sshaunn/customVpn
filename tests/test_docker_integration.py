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


@pytest.mark.skipif(True, reason="Requires Docker daemon running")
def test_xray_container_starts(xray_config, tmp_path_factory):
    """Integration test: Build and start Xray container"""
    tmpdir = tmp_path_factory.mktemp("xray")
    config_file = tmpdir / "config.json"
    config_file.write_text(xray_config)

    docker_dir = Path(__file__).parent.parent / "docker" / "xray"

    with DockerContainer(str(docker_dir)) as container:
        container.with_bind_ports(443, 8443)
        container.with_volume_mapping(str(config_file), "/etc/xray/config.json")
        container.start()

        time.sleep(2)

        assert container.get_wrapped_container().status == "running"


@pytest.mark.skipif(True, reason="Requires Docker daemon running")
def test_shadowsocks_container_starts(shadowsocks_config, tmp_path_factory):
    """Integration test: Build and start Shadowsocks container"""
    tmpdir = tmp_path_factory.mktemp("shadowsocks")
    config_file = tmpdir / "config.json"
    config_file.write_text(shadowsocks_config)

    docker_dir = Path(__file__).parent.parent / "docker" / "shadowsocks"

    with DockerContainer(str(docker_dir)) as container:
        container.with_bind_ports(8388, 18388)
        container.with_volume_mapping(str(config_file), "/etc/shadowsocks/config.json")
        container.start()

        time.sleep(2)

        assert container.get_wrapped_container().status == "running"


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


@pytest.mark.skipif(True, reason="Requires Docker daemon running")
def test_both_containers_together(xray_config, shadowsocks_config, tmp_path_factory):
    """Integration test: Run both containers simultaneously"""
    xray_tmpdir = tmp_path_factory.mktemp("xray_multi")
    ss_tmpdir = tmp_path_factory.mktemp("ss_multi")

    xray_config_file = xray_tmpdir / "config.json"
    xray_config_file.write_text(xray_config)

    ss_config_file = ss_tmpdir / "config.json"
    ss_config_file.write_text(shadowsocks_config)

    xray_docker_dir = Path(__file__).parent.parent / "docker" / "xray"
    ss_docker_dir = Path(__file__).parent.parent / "docker" / "shadowsocks"

    with DockerContainer(str(xray_docker_dir)) as xray_container, \
         DockerContainer(str(ss_docker_dir)) as ss_container:

        xray_container.with_bind_ports(443, 8443)
        xray_container.with_volume_mapping(str(xray_config_file), "/etc/xray/config.json")

        ss_container.with_bind_ports(8388, 18388)
        ss_container.with_volume_mapping(str(ss_config_file), "/etc/shadowsocks/config.json")

        xray_container.start()
        ss_container.start()

        time.sleep(3)

        assert xray_container.get_wrapped_container().status == "running"
        assert ss_container.get_wrapped_container().status == "running"
