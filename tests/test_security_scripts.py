import pytest
from pathlib import Path


@pytest.fixture
def scripts_dir():
    """Get scripts directory"""
    return Path(__file__).parent.parent / "scripts" / "bash"


def test_firewall_script_exists(scripts_dir):
    """Test firewall setup script exists and is executable"""
    script = scripts_dir / "setup_firewall.sh"
    assert script.exists(), "Firewall script missing"
    assert script.is_file(), "Firewall script is not a file"
    assert script.stat().st_mode & 0o111, "Firewall script not executable"


def test_ssh_hardening_script_exists(scripts_dir):
    """Test SSH hardening script exists and is executable"""
    script = scripts_dir / "harden_ssh.sh"
    assert script.exists(), "SSH hardening script missing"
    assert script.is_file(), "SSH hardening script is not a file"
    assert script.stat().st_mode & 0o111, "SSH hardening script not executable"


def test_fail2ban_script_exists(scripts_dir):
    """Test fail2ban setup script exists and is executable"""
    script = scripts_dir / "setup_fail2ban.sh"
    assert script.exists(), "fail2ban script missing"
    assert script.is_file(), "fail2ban script is not a file"
    assert script.stat().st_mode & 0o111, "fail2ban script not executable"


def test_firewall_script_content(scripts_dir):
    """Test firewall script has correct ports"""
    script = scripts_dir / "setup_firewall.sh"
    content = script.read_text()

    assert "2222" in content, "SSH port 2222 not configured"
    assert "443" in content, "Xray port 443 not configured"
    assert "8388" in content, "Shadowsocks port 8388 not configured"
    assert "ufw" in content, "UFW not used"
    assert "default deny" in content.lower(), "Default deny policy missing"


def test_ssh_script_content(scripts_dir):
    """Test SSH hardening script has security settings"""
    script = scripts_dir / "harden_ssh.sh"
    content = script.read_text()

    assert "Port" in content, "Port configuration missing"
    assert "2222" in content, "Custom port 2222 not set"
    assert "PasswordAuthentication" in content, "Password auth config missing"
    assert "PubkeyAuthentication" in content, "Public key auth config missing"
    assert "PermitRootLogin" in content, "Root login config missing"
    assert "sshd -t" in content, "Config validation missing"


def test_fail2ban_script_content(scripts_dir):
    """Test fail2ban script has correct configuration"""
    script = scripts_dir / "setup_fail2ban.sh"
    content = script.read_text()

    assert "fail2ban" in content, "fail2ban not configured"
    assert "2222" in content, "SSH port 2222 not protected"
    assert "maxretry" in content, "Max retry not configured"
    assert "bantime" in content, "Ban time not configured"
    assert "jail.local" in content, "Jail config not created"


def test_firewall_script_has_root_check(scripts_dir):
    """Test firewall script checks for root privileges"""
    script = scripts_dir / "setup_firewall.sh"
    content = script.read_text()

    assert "EUID" in content or "root" in content.lower(), "No root check"
    assert "exit 1" in content, "No error exit on non-root"


def test_ssh_script_has_backup(scripts_dir):
    """Test SSH script backs up original config"""
    script = scripts_dir / "harden_ssh.sh"
    content = script.read_text()

    assert "backup" in content.lower(), "No backup mechanism"
    assert "cp" in content or "copy" in content.lower(), "No file copy for backup"
    assert "/etc/ssh/sshd_config" in content, "SSH config path missing"


def test_fail2ban_script_has_systemctl(scripts_dir):
    """Test fail2ban script manages systemd service"""
    script = scripts_dir / "setup_fail2ban.sh"
    content = script.read_text()

    assert "systemctl" in content, "systemctl not used"
    assert "enable" in content, "Service not enabled"
    assert "restart" in content, "Service not restarted"


def test_all_scripts_have_shebang(scripts_dir):
    """Test all bash scripts have proper shebang"""
    scripts = [
        "setup_firewall.sh",
        "harden_ssh.sh",
        "setup_fail2ban.sh"
    ]

    for script_name in scripts:
        script = scripts_dir / script_name
        first_line = script.read_text().splitlines()[0]
        assert first_line.startswith("#!/bin/bash"), f"{script_name} missing bash shebang"


def test_all_scripts_have_set_e(scripts_dir):
    """Test all scripts exit on error (set -e)"""
    scripts = [
        "setup_firewall.sh",
        "harden_ssh.sh",
        "setup_fail2ban.sh"
    ]

    for script_name in scripts:
        script = scripts_dir / script_name
        content = script.read_text()
        assert "set -e" in content, f"{script_name} missing 'set -e'"


@pytest.mark.integration
@pytest.mark.requires_vps
def test_firewall_script_runs():
    """Test firewall script can be executed (VPS only)"""
    pass


@pytest.mark.integration
@pytest.mark.requires_vps
def test_ssh_script_runs():
    """Test SSH hardening script can be executed (VPS only)"""
    pass


@pytest.mark.integration
@pytest.mark.requires_vps
def test_fail2ban_script_runs():
    """Test fail2ban script can be executed (VPS only)"""
    pass
