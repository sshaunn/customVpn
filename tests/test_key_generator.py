import re
import base64
import pytest
from scripts.python.key_generator import KeyGenerator


def test_generate_uuid():
    uuid1 = KeyGenerator.generate_uuid()
    uuid2 = KeyGenerator.generate_uuid()

    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )

    assert uuid_pattern.match(uuid1), f"Invalid UUID format: {uuid1}"
    assert uuid_pattern.match(uuid2), f"Invalid UUID format: {uuid2}"
    assert uuid1 != uuid2, "UUIDs should be unique"


def test_generate_reality_short_id():
    short_id = KeyGenerator.generate_reality_short_id()

    assert len(short_id) == 8, f"Short ID should be 8 chars, got {len(short_id)}"
    assert re.match(r'^[0-9a-f]{8}$', short_id, re.IGNORECASE), "Short ID should be hex"

    short_id2 = KeyGenerator.generate_reality_short_id()
    assert short_id != short_id2, "Short IDs should be unique"


def test_generate_shadowsocks_password():
    password = KeyGenerator.generate_shadowsocks_password()

    assert isinstance(password, str), "Password should be string"

    try:
        decoded = base64.b64decode(password)
        assert len(decoded) == 32, f"Decoded password should be 32 bytes, got {len(decoded)}"
    except Exception as e:
        pytest.fail(f"Password is not valid base64: {e}")

    password2 = KeyGenerator.generate_shadowsocks_password()
    assert password != password2, "Passwords should be unique"


def test_generate_reality_keypair_without_xray():
    """Test that proper error is raised when xray is not installed"""
    import subprocess
    from unittest.mock import patch

    with patch('subprocess.run', side_effect=FileNotFoundError()):
        with pytest.raises(RuntimeError, match="xray binary not found"):
            KeyGenerator.generate_reality_keypair()


def test_generate_reality_keypair_timeout():
    """Test timeout handling"""
    import subprocess
    from unittest.mock import patch

    with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('xray', 5)):
        with pytest.raises(RuntimeError, match="timed out"):
            KeyGenerator.generate_reality_keypair()


def test_generate_reality_keypair_invalid_output():
    """Test handling of invalid xray output"""
    import subprocess
    from unittest.mock import patch, MagicMock

    mock_result = MagicMock()
    mock_result.stdout = "Invalid output without keys"

    with patch('subprocess.run', return_value=mock_result):
        with pytest.raises(ValueError, match="Failed to parse"):
            KeyGenerator.generate_reality_keypair()


@pytest.mark.skipif(True, reason="Requires xray binary installed")
def test_generate_reality_keypair_real():
    """Test real key generation if xray is available"""
    try:
        keys = KeyGenerator.generate_reality_keypair()

        assert "private_key" in keys
        assert "public_key" in keys
        assert len(keys["private_key"]) > 0
        assert len(keys["public_key"]) > 0
        assert keys["private_key"] != keys["public_key"]

    except RuntimeError:
        pytest.skip("xray binary not available")


@pytest.mark.skipif(True, reason="Requires xray binary installed")
def test_generate_all_keys_real():
    """Test generating all keys at once if xray is available"""
    try:
        keys = KeyGenerator.generate_all_keys()

        required_keys = [
            "admin_uuid",
            "reality_private_key",
            "reality_public_key",
            "reality_short_id",
            "shadowsocks_password"
        ]

        for key in required_keys:
            assert key in keys, f"Missing key: {key}"
            assert keys[key], f"Empty value for key: {key}"

    except RuntimeError:
        pytest.skip("xray binary not available")
