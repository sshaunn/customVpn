import json
import tempfile
from pathlib import Path
import pytest
from scripts.python.config_generator import ConfigGenerator


@pytest.fixture
def generator():
    return ConfigGenerator()


@pytest.fixture
def sample_users():
    return [
        {"uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "email": "user1@test"},
        {"uuid": "b2c3d4e5-f6a7-8901-bcde-fa2345678901", "email": "user2@test"},
    ]


def test_render_xray_config(generator, sample_users):
    config = generator.render_xray_config(
        users=sample_users,
        xray_port=443,
        reality_sni="www.apple.com",
        reality_private_key="gM3fXxxx_test_private_key_xxx",
        reality_short_id="abc123"
    )

    parsed = json.loads(config)

    assert parsed["inbounds"][0]["port"] == 443
    assert parsed["inbounds"][0]["protocol"] == "vless"
    assert len(parsed["inbounds"][0]["settings"]["clients"]) == 2
    assert parsed["inbounds"][0]["settings"]["clients"][0]["id"] == sample_users[0]["uuid"]
    assert parsed["inbounds"][0]["settings"]["clients"][0]["email"] == sample_users[0]["email"]
    assert parsed["inbounds"][0]["streamSettings"]["security"] == "reality"
    assert parsed["inbounds"][0]["streamSettings"]["realitySettings"]["dest"] == "www.apple.com:443"
    assert parsed["inbounds"][0]["streamSettings"]["realitySettings"]["privateKey"] == "gM3fXxxx_test_private_key_xxx"


def test_render_shadowsocks_config(generator):
    config = generator.render_shadowsocks_config(
        ss_port=8388,
        ss_password="test_password_123"
    )

    parsed = json.loads(config)

    assert parsed["server_port"] == 8388
    assert parsed["password"] == "test_password_123"
    assert parsed["method"] == "2022-blake3-aes-256-gcm"
    assert parsed["mode"] == "tcp_and_udp"


def test_save_config(generator):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test" / "config.json"
        test_config = '{"test": "data"}'

        generator.save_config(test_config, output_path)

        assert output_path.exists()
        assert output_path.read_text() == test_config

        saved_json = json.loads(output_path.read_text())
        assert saved_json["test"] == "data"


def test_save_config_invalid_json(generator):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "config.json"
        invalid_config = "not json"

        with pytest.raises(json.JSONDecodeError):
            generator.save_config(invalid_config, output_path)


def test_generate_all_configs(generator, sample_users):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        result = generator.generate_all_configs(
            users=sample_users,
            xray_port=443,
            reality_sni="www.apple.com",
            reality_private_key="test_private_key",
            reality_short_id="abc123",
            ss_port=8388,
            ss_password="test_ss_password",
            output_dir=output_dir
        )

        assert "xray" in result
        assert "shadowsocks" in result
        assert result["xray"].exists()
        assert result["shadowsocks"].exists()

        xray_data = json.loads(result["xray"].read_text())
        assert xray_data["inbounds"][0]["port"] == 443

        ss_data = json.loads(result["shadowsocks"].read_text())
        assert ss_data["server_port"] == 8388


def test_template_directory_not_found():
    with pytest.raises(Exception):
        generator = ConfigGenerator(template_dir=Path("/nonexistent"))
        generator.render_xray_config(
            users=[],
            xray_port=443,
            reality_sni="test",
            reality_private_key="test",
            reality_short_id="test"
        )
