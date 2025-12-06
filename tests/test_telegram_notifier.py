from pathlib import Path
import pytest
from scripts.python.telegram_notifier import TelegramNotifier


@pytest.fixture
def notifier():
    """Create notifier from config.env"""
    config_file = Path(__file__).parent.parent / "config.env"

    env = {}
    if config_file.exists():
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value

    if not env.get('TELEGRAM_BOT_TOKEN') or not env.get('TELEGRAM_CHAT_ID'):
        pytest.skip("Telegram credentials not configured")

    return TelegramNotifier(
        bot_token=env['TELEGRAM_BOT_TOKEN'],
        chat_id=env['TELEGRAM_CHAT_ID']
    )


def test_notifier_initialization():
    """Test TelegramNotifier can be initialized"""
    notifier = TelegramNotifier(
        bot_token="test_token",
        chat_id="test_chat_id"
    )

    assert notifier.bot_token == "test_token"
    assert notifier.chat_id == "test_chat_id"
    assert "https://api.telegram.org/bot" in notifier.api_url


@pytest.mark.integration
@pytest.mark.requires_telegram
def test_send_message(notifier):
    """Test sending a simple message"""
    result = notifier.send_message("✅ Test message from pytest integration tests")
    assert result is True


@pytest.mark.integration
@pytest.mark.requires_telegram
def test_send_alert(notifier):
    """Test sending formatted alert"""
    result = notifier.send_alert(
        title="Test Alert",
        details="This is a test alert from the VPN monitoring system",
        severity="INFO"
    )
    assert result is True


@pytest.mark.integration
@pytest.mark.requires_telegram
def test_send_service_down_alert(notifier):
    """Test service down alert"""
    result = notifier.send_service_down_alert("Xray", 443)
    assert result is True


@pytest.mark.integration
@pytest.mark.requires_telegram
def test_send_backup_alert(notifier):
    """Test backup completion alert"""
    result = notifier.send_backup_alert("test-backup-20251206", 5.2, success=True)
    assert result is True


@pytest.mark.integration
@pytest.mark.requires_telegram
def test_connection(notifier):
    """Test Telegram connection"""
    result = notifier.test_connection()
    assert result is True
