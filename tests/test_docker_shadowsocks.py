import json
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def test_config():
    """Create minimal test config for Shadowsocks"""
    return {
        "server": "::",
        "server_port": 8388,
        "password": "test_password_base64_encoded",
        "method": "2022-blake3-aes-256-gcm",
        "mode": "tcp_and_udp"
    }


def test_dockerfile_exists():
    """Test that Shadowsocks Dockerfile exists"""
    dockerfile = Path(__file__).parent.parent / "docker" / "shadowsocks" / "Dockerfile"
    assert dockerfile.exists(), "Shadowsocks Dockerfile not found"


def test_dockerignore_exists():
    """Test that .dockerignore exists"""
    dockerignore = Path(__file__).parent.parent / "docker" / "shadowsocks" / ".dockerignore"
    assert dockerignore.exists(), ".dockerignore not found"


def test_dockerfile_has_security_features():
    """Test that Dockerfile follows security best practices"""
    dockerfile = Path(__file__).parent.parent / "docker" / "shadowsocks" / "Dockerfile"
    content = dockerfile.read_text()

    assert "adduser" in content, "Should create non-root user"
    assert "USER shadowsocks" in content, "Should run as non-root user"
    assert "alpine" in content.lower(), "Should use Alpine base"
    assert "ca-certificates" in content, "Should include CA certificates"


def test_dockerfile_exposes_correct_port():
    """Test that Dockerfile exposes port 8388"""
    dockerfile = Path(__file__).parent.parent / "docker" / "shadowsocks" / "Dockerfile"
    content = dockerfile.read_text()

    assert "EXPOSE 8388" in content, "Should expose port 8388"


def test_dockerfile_uses_ss_rust():
    """Test that Dockerfile uses shadowsocks-rust"""
    dockerfile = Path(__file__).parent.parent / "docker" / "shadowsocks" / "Dockerfile"
    content = dockerfile.read_text()

    assert "shadowsocks-rust" in content, "Should use shadowsocks-rust"
    assert "ssserver" in content, "Should use ssserver binary"


@pytest.mark.skipif(True, reason="Requires Docker installed")
def test_shadowsocks_docker_build():
    """Test that Shadowsocks Docker image builds successfully"""
    docker_dir = Path(__file__).parent.parent / "docker" / "shadowsocks"

    try:
        result = subprocess.run(
            ["docker", "build", "-t", "customvpn-shadowsocks:test", "."],
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
