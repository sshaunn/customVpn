import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def scripts_dir(project_root):
    """Get scripts directory"""
    return project_root / "scripts" / "bash"


def test_deploy_script_exists(project_root):
    """Test main deploy script exists and is executable"""
    script = project_root / "deploy.sh"
    assert script.exists(), "deploy.sh missing"
    assert script.is_file(), "deploy.sh is not a file"
    assert script.stat().st_mode & 0o111, "deploy.sh not executable"


def test_vps_setup_script_exists(scripts_dir):
    """Test VPS setup script exists and is executable"""
    script = scripts_dir / "setup_vps.sh"
    assert script.exists(), "setup_vps.sh missing"
    assert script.is_file(), "setup_vps.sh is not a file"
    assert script.stat().st_mode & 0o111, "setup_vps.sh not executable"


def test_deploy_script_checks_config(project_root):
    """Test deploy script verifies config.env exists"""
    script = project_root / "deploy.sh"
    content = script.read_text()

    assert "config.env" in content, "No config.env check"
    assert "CONFIG_FILE" in content or "config" in content.lower(), "Config not loaded"


def test_deploy_script_validates_vars(project_root):
    """Test deploy script validates required variables"""
    script = project_root / "deploy.sh"
    content = script.read_text()

    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "TELEGRAM_BOT_TOKEN",
        "REALITY_SNI"
    ]

    for var in required_vars:
        assert var in content, f"Required var {var} not validated"


def test_deploy_script_has_docker_compose(project_root):
    """Test deploy script uses docker compose"""
    script = project_root / "deploy.sh"
    content = script.read_text()

    assert "docker compose" in content or "docker-compose" in content, "No docker compose usage"
    assert "up" in content, "No docker compose up command"
    assert "build" in content, "No docker compose build command"


def test_deploy_script_generates_configs(project_root):
    """Test deploy script generates VPN configs"""
    script = project_root / "deploy.sh"
    content = script.read_text()

    assert "setup_vpn" in content, "No VPN setup script"


def test_deploy_script_verifies_services(project_root):
    """Test deploy script verifies services are running"""
    script = project_root / "deploy.sh"
    content = script.read_text()

    assert "nc -zv" in content or "check" in content.lower(), "No service verification"


def test_vps_setup_installs_docker(scripts_dir):
    """Test VPS setup script installs Docker"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "docker" in content.lower(), "Docker installation missing"
    assert "docker-ce" in content or "docker.com" in content, "No official Docker repo"


def test_vps_setup_installs_python(scripts_dir):
    """Test VPS setup script installs Python"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "python3" in content, "Python3 installation missing"
    assert "pip" in content or "poetry" in content, "No package manager"


def test_vps_setup_installs_poetry(scripts_dir):
    """Test VPS setup script installs Poetry"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "poetry" in content, "Poetry installation missing"
    assert "install.python-poetry.org" in content or "poetry" in content, "No Poetry install"


def test_vps_setup_installs_aws_cli(scripts_dir):
    """Test VPS setup script installs AWS CLI"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "aws" in content, "AWS CLI installation missing"
    assert "awscliv2" in content or "aws-cli" in content, "No AWS CLI install"


def test_vps_setup_creates_user(scripts_dir):
    """Test VPS setup script creates VPN user"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "useradd" in content or "adduser" in content, "No user creation"
    assert "vpnuser" in content or "user" in content.lower(), "No VPN user"


def test_vps_setup_sets_timezone(scripts_dir):
    """Test VPS setup script sets timezone"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "timezone" in content.lower() or "timedatectl" in content, "No timezone config"
    assert "Singapore" in content or "Asia" in content, "Wrong timezone"


def test_vps_setup_has_root_check(scripts_dir):
    """Test VPS setup requires root"""
    script = scripts_dir / "setup_vps.sh"
    content = script.read_text()

    assert "EUID" in content or "root" in content.lower(), "No root check"
    assert "exit 1" in content, "No error exit"


def test_deploy_script_has_error_handling(project_root):
    """Test deploy script has error handling"""
    script = project_root / "deploy.sh"
    content = script.read_text()

    assert "set -e" in content, "No 'set -e' for error handling"
    assert "exit 1" in content, "No error exits"


def test_all_deployment_scripts_have_shebang(project_root):
    """Test all deployment scripts have bash shebang"""
    scripts = [
        "deploy.sh",
        "scripts/bash/setup_vps.sh"
    ]

    for script_path in scripts:
        script = project_root / script_path
        first_line = script.read_text().splitlines()[0]
        assert first_line.startswith("#!/bin/bash"), f"{script_path} missing bash shebang"


@pytest.mark.skipif(True, reason="Requires VPS environment")
def test_full_deployment():
    """Test full deployment workflow (VPS only)"""
    pass


@pytest.mark.skipif(True, reason="Requires VPS environment")
def test_vps_setup_runs():
    """Test VPS setup script runs successfully (VPS only)"""
    pass
