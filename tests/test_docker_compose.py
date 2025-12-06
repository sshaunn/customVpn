import yaml
import subprocess
from pathlib import Path
import pytest


def test_docker_compose_exists():
    """Test that docker-compose.yml exists"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"
    assert compose_file.exists(), "docker-compose.yml not found"


def test_docker_compose_valid_yaml():
    """Test that docker-compose.yml is valid YAML"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        try:
            compose_config = yaml.safe_load(f)
            assert compose_config is not None
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML: {e}")


def test_docker_compose_has_required_services():
    """Test that docker-compose.yml defines required services"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    assert "services" in compose_config

    required_services = ["xray", "shadowsocks", "watchtower"]
    for service in required_services:
        assert service in compose_config["services"], f"Missing service: {service}"


def test_docker_compose_xray_config():
    """Test Xray service configuration"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    xray = compose_config["services"]["xray"]

    assert "build" in xray
    assert xray["build"]["context"] == "./docker/xray"
    assert xray["restart"] == "unless-stopped"
    assert "volumes" in xray
    assert xray["network_mode"] == "host"
    assert "healthcheck" in xray
    assert "cap_drop" in xray
    assert "ALL" in xray["cap_drop"]


def test_docker_compose_shadowsocks_config():
    """Test Shadowsocks service configuration"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    ss = compose_config["services"]["shadowsocks"]

    assert "build" in ss
    assert ss["build"]["context"] == "./docker/shadowsocks"
    assert ss["restart"] == "unless-stopped"
    assert "volumes" in ss
    assert ss["network_mode"] == "host"
    assert "healthcheck" in ss


def test_docker_compose_watchtower_config():
    """Test Watchtower auto-update service"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    watchtower = compose_config["services"]["watchtower"]

    assert watchtower["image"] == "containrrr/watchtower:latest"
    env_str = " ".join(watchtower["environment"])
    assert "WATCHTOWER_CLEANUP" in env_str
    assert watchtower["restart"] == "unless-stopped"


def test_docker_compose_security_features():
    """Test security hardening in compose file"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    for service_name in ["xray", "shadowsocks"]:
        service = compose_config["services"][service_name]

        assert "cap_drop" in service, f"{service_name} should drop capabilities"
        assert "ALL" in service["cap_drop"], f"{service_name} should drop all caps"

        assert "security_opt" in service, f"{service_name} should have security options"
        assert "no-new-privileges:true" in service["security_opt"]


def test_docker_compose_logging_configured():
    """Test that logging is configured for all services"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    for service_name in ["xray", "shadowsocks", "watchtower"]:
        service = compose_config["services"][service_name]
        assert "logging" in service, f"{service_name} should have logging configured"
        assert "max-size" in service["logging"]["options"]


def test_docker_compose_volumes_defined():
    """Test that volumes are properly defined"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    assert "volumes" in compose_config
    assert "xray-logs" in compose_config["volumes"]


@pytest.mark.skipif(True, reason="Requires docker-compose installed")
def test_docker_compose_validation():
    """Test docker-compose config validation"""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "config"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"docker-compose validation failed: {result.stderr}"

    except FileNotFoundError:
        pytest.skip("docker-compose not installed")
    except subprocess.TimeoutExpired:
        pytest.fail("docker-compose validation timed out")
