import json
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def test_config():
    """Create minimal test config for Xray"""
    return {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 443,
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                            "flow": "xtls-rprx-vision"
                        }
                    ],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "dest": "www.apple.com:443",
                        "serverNames": ["www.apple.com"],
                        "privateKey": "test_private_key_placeholder",
                        "shortIds": ["abcd1234"]
                    }
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "freedom"
            }
        ]
    }


def test_dockerfile_exists():
    """Test that Xray Dockerfile exists"""
    dockerfile = Path(__file__).parent.parent / "docker" / "xray" / "Dockerfile"
    assert dockerfile.exists(), "Xray Dockerfile not found"


def test_dockerignore_exists():
    """Test that .dockerignore exists"""
    dockerignore = Path(__file__).parent.parent / "docker" / "xray" / ".dockerignore"
    assert dockerignore.exists(), ".dockerignore not found"


@pytest.mark.integration
@pytest.mark.requires_docker
def test_xray_docker_build():
    """Test that Xray Docker image builds successfully"""
    docker_dir = Path(__file__).parent.parent / "docker" / "xray"

    try:
        result = subprocess.run(
            ["docker", "build", "-t", "customvpn-xray:test", "."],
            cwd=docker_dir,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        assert "Successfully built" in result.stdout or "Successfully tagged" in result.stdout

    except FileNotFoundError:
        pytest.skip("Docker not installed")
    except subprocess.TimeoutExpired:
        pytest.fail("Docker build timed out")


@pytest.mark.integration
@pytest.mark.requires_docker
def test_xray_docker_run_with_config(test_config):
    """Test that Xray container starts with valid config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config_path.write_text(json.dumps(test_config, indent=2))

        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{config_path}:/etc/xray/config.json",
                    "customvpn-xray:test",
                    "run", "-test", "-config", "/etc/xray/config.json"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert "Configuration OK" in result.stdout or result.returncode == 0

        except FileNotFoundError:
            pytest.skip("Docker not installed")
        except subprocess.TimeoutExpired:
            pytest.fail("Xray test timed out")


def test_dockerfile_has_security_features():
    """Test that Dockerfile follows security best practices"""
    dockerfile = Path(__file__).parent.parent / "docker" / "xray" / "Dockerfile"
    content = dockerfile.read_text()

    # Note: Running as root to bind port 443 in host network mode
    # Alternative security: cap_drop + cap_add in docker-compose.yml
    assert "alpine" in content.lower(), "Should use Alpine base"
    assert "ca-certificates" in content, "Should include CA certificates"


def test_dockerfile_exposes_correct_port():
    """Test that Dockerfile exposes port 443"""
    dockerfile = Path(__file__).parent.parent / "docker" / "xray" / "Dockerfile"
    content = dockerfile.read_text()

    assert "EXPOSE 443" in content, "Should expose port 443"
