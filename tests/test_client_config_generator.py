import json
import base64
import tempfile
from pathlib import Path
import pytest
from scripts.python.client_config_generator import ClientConfigGenerator


@pytest.fixture
def generator():
    return ClientConfigGenerator()


@pytest.fixture
def sample_config_data():
    return {
        "username": "testuser",
        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "server_ip": "192.168.1.100",
        "port": 443,
        "reality_sni": "www.apple.com",
        "reality_public_key": "test_public_key_123",
        "reality_short_id": "abcd1234"
    }


def test_generate_vless_share_link(generator, sample_config_data):
    """Test VLESS share link generation"""
    link = generator.generate_vless_share_link(**sample_config_data)

    assert link.startswith("vless://")
    assert sample_config_data["uuid"] in link
    assert sample_config_data["server_ip"] in link
    assert str(sample_config_data["port"]) in link
    assert sample_config_data["reality_sni"] in link
    assert sample_config_data["reality_public_key"] in link
    assert sample_config_data["username"] in link
    assert "flow=xtls-rprx-vision" in link
    assert "security=reality" in link


def test_generate_shadowsocks_share_link(generator):
    """Test Shadowsocks share link generation"""
    link = generator.generate_shadowsocks_share_link(
        username="testuser",
        server_ip="192.168.1.100",
        ss_port=8388,
        ss_password="test_password_123"
    )

    assert link.startswith("ss://")
    assert "192.168.1.100:8388" in link
    assert "testuser-fallback" in link

    encoded_part = link.split("@")[0].replace("ss://", "")
    decoded = base64.b64decode(encoded_part).decode()
    assert "2022-blake3-aes-256-gcm:test_password_123" == decoded


def test_generate_client_json_config(generator, sample_config_data):
    """Test JSON config generation for desktop clients"""
    config = generator.generate_client_json_config(**sample_config_data)

    parsed = json.loads(config)

    assert "inbounds" in parsed
    assert "outbounds" in parsed
    assert len(parsed["inbounds"]) == 2
    assert parsed["inbounds"][0]["port"] == 10808
    assert parsed["inbounds"][0]["protocol"] == "socks"

    proxy_outbound = parsed["outbounds"][0]
    assert proxy_outbound["protocol"] == "vless"
    assert proxy_outbound["settings"]["vnext"][0]["address"] == sample_config_data["server_ip"]
    assert proxy_outbound["settings"]["vnext"][0]["port"] == sample_config_data["port"]
    assert proxy_outbound["settings"]["vnext"][0]["users"][0]["id"] == sample_config_data["uuid"]

    reality_settings = proxy_outbound["streamSettings"]["realitySettings"]
    assert reality_settings["serverName"] == sample_config_data["reality_sni"]
    assert reality_settings["publicKey"] == sample_config_data["reality_public_key"]
    assert reality_settings["shortId"] == sample_config_data["reality_short_id"]


def test_generate_qr_code(generator):
    """Test QR code generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_qr.png"
        test_content = "vless://test-uuid@192.168.1.1:443"

        generator.generate_qr_code(test_content, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_generate_all_client_configs(generator):
    """Test generating all configs for a user"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        result = generator.generate_all_client_configs(
            username="alice",
            uuid="alice-uuid-123",
            server_ip="192.168.1.100",
            xray_port=443,
            reality_sni="www.apple.com",
            reality_public_key="test_public_key",
            reality_short_id="abcd1234",
            ss_port=8388,
            ss_password="test_ss_password",
            output_dir=output_dir
        )

        assert "vless_link" in result
        assert "vless_qr" in result
        assert "shadowsocks_link" in result
        assert "shadowsocks_qr" in result
        assert "json_config" in result

        assert result["vless_link"].exists()
        assert result["vless_qr"].exists()
        assert result["shadowsocks_link"].exists()
        assert result["shadowsocks_qr"].exists()
        assert result["json_config"].exists()

        vless_content = result["vless_link"].read_text()
        assert vless_content.startswith("vless://")
        assert "alice-uuid-123" in vless_content

        ss_content = result["shadowsocks_link"].read_text()
        assert ss_content.startswith("ss://")

        json_content = json.loads(result["json_config"].read_text())
        assert json_content["outbounds"][0]["settings"]["vnext"][0]["users"][0]["id"] == "alice-uuid-123"


def test_vless_link_format_correctness(generator):
    """Test that VLESS link follows correct format"""
    link = generator.generate_vless_share_link(
        username="test",
        uuid="test-uuid",
        server_ip="1.2.3.4",
        port=443,
        reality_sni="www.example.com",
        reality_public_key="pubkey123",
        reality_short_id="sid123"
    )

    parts = link.split("?")
    assert len(parts) == 2

    params = parts[1].split("&")
    param_dict = {}
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            param_dict[key] = value

    assert param_dict.get("encryption") == "none"
    assert param_dict.get("flow") == "xtls-rprx-vision"
    assert param_dict.get("security") == "reality"
    assert param_dict.get("sni") == "www.example.com"
    assert param_dict.get("pbk") == "pubkey123"
    assert param_dict.get("sid") == "sid123"


def test_json_config_has_routing_rules(generator):
    """Test that JSON config includes routing rules for China"""
    config = generator.generate_client_json_config(
        username="test",
        uuid="test-uuid",
        server_ip="1.2.3.4",
        port=443,
        reality_sni="www.example.com",
        reality_public_key="pubkey",
        reality_short_id="sid"
    )

    parsed = json.loads(config)

    assert "routing" in parsed
    assert "rules" in parsed["routing"]

    rules = parsed["routing"]["rules"]
    assert len(rules) >= 2

    has_private_rule = any("geoip:private" in str(rule.get("ip", [])) for rule in rules)
    has_cn_rule = any("geosite:cn" in str(rule.get("domain", [])) for rule in rules)

    assert has_private_rule
    assert has_cn_rule
