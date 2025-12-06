import tempfile
from pathlib import Path
import json
import pytest
from scripts.python.user_manager import UserManager
from scripts.python.config_generator import ConfigGenerator


def test_integration_user_manager_with_config_generator():
    """Test that UserManager integrates with ConfigGenerator"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("alice", uuid="alice-uuid-123")
        manager.add_user("bob", uuid="bob-uuid-456")

        users_for_config = manager.get_users_for_config()

        generator = ConfigGenerator()
        config = generator.render_xray_config(
            users=users_for_config,
            xray_port=443,
            reality_sni="www.apple.com",
            reality_private_key="test-key",
            reality_short_id="abcd1234"
        )

        parsed = json.loads(config)
        clients = parsed["inbounds"][0]["settings"]["clients"]

        assert len(clients) == 2
        assert clients[0]["id"] == "alice-uuid-123"
        assert clients[0]["email"] == "alice@vpn"
        assert clients[1]["id"] == "bob-uuid-456"
        assert clients[1]["email"] == "bob@vpn"


def test_integration_add_remove_regenerate_config():
    """Test full workflow: add users, generate config, remove user, regenerate"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        output_dir = Path(tmpdir) / "output"

        manager = UserManager(users_file)
        generator = ConfigGenerator()

        manager.add_user("user1", uuid="uuid-1")
        manager.add_user("user2", uuid="uuid-2")
        manager.add_user("user3", uuid="uuid-3")

        config_paths = generator.generate_all_configs(
            users=manager.get_users_for_config(),
            xray_port=443,
            reality_sni="www.apple.com",
            reality_private_key="test-key",
            reality_short_id="test-id",
            ss_port=8388,
            ss_password="test-password",
            output_dir=output_dir
        )

        xray_config = json.loads(config_paths["xray"].read_text())
        assert len(xray_config["inbounds"][0]["settings"]["clients"]) == 3

        manager.remove_user("user2")

        config_paths = generator.generate_all_configs(
            users=manager.get_users_for_config(),
            xray_port=443,
            reality_sni="www.apple.com",
            reality_private_key="test-key",
            reality_short_id="test-id",
            ss_port=8388,
            ss_password="test-password",
            output_dir=output_dir
        )

        xray_config = json.loads(config_paths["xray"].read_text())
        clients = xray_config["inbounds"][0]["settings"]["clients"]

        assert len(clients) == 2
        client_ids = [c["id"] for c in clients]
        assert "uuid-1" in client_ids
        assert "uuid-2" not in client_ids
        assert "uuid-3" in client_ids


def test_integration_empty_users():
    """Test config generation with no users"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        generator = ConfigGenerator()

        config = generator.render_xray_config(
            users=manager.get_users_for_config(),
            xray_port=443,
            reality_sni="www.apple.com",
            reality_private_key="test-key",
            reality_short_id="test-id"
        )

        parsed = json.loads(config)
        clients = parsed["inbounds"][0]["settings"]["clients"]

        assert len(clients) == 0
