import pytest
import socket
from unittest.mock import Mock, patch, MagicMock
from scripts.python.health_monitor import HealthMonitor


@pytest.fixture
def monitor():
    """Create a monitor without Telegram"""
    return HealthMonitor()


@pytest.fixture
def monitor_with_telegram():
    """Create a monitor with Telegram"""
    return HealthMonitor(
        telegram_bot_token="test_token",
        telegram_chat_id="test_chat_id"
    )


def test_health_monitor_init(monitor):
    """Test health monitor initialization"""
    assert "xray" in monitor.services
    assert "shadowsocks" in monitor.services
    assert monitor.services["xray"]["port"] == 443
    assert monitor.services["shadowsocks"]["port"] == 8388
    assert monitor.notifier is None


def test_health_monitor_with_telegram(monitor_with_telegram):
    """Test health monitor with Telegram configured"""
    assert monitor_with_telegram.notifier is not None
    assert monitor_with_telegram.notifier.bot_token == "test_token"
    assert monitor_with_telegram.notifier.chat_id == "test_chat_id"


@patch('socket.socket')
def test_check_port_success(mock_socket_class, monitor):
    """Test port check when port is open"""
    mock_socket = Mock()
    mock_socket.connect_ex.return_value = 0
    mock_socket_class.return_value = mock_socket

    result = monitor.check_port(443)

    assert result is True
    mock_socket.connect_ex.assert_called_once_with(("127.0.0.1", 443))
    mock_socket.close.assert_called_once()


@patch('socket.socket')
def test_check_port_failure(mock_socket_class, monitor):
    """Test port check when port is closed"""
    mock_socket = Mock()
    mock_socket.connect_ex.return_value = 1
    mock_socket_class.return_value = mock_socket

    result = monitor.check_port(443)

    assert result is False


@patch('socket.socket')
def test_check_port_exception(mock_socket_class, monitor):
    """Test port check handles exceptions"""
    mock_socket_class.side_effect = Exception("Network error")

    result = monitor.check_port(443)

    assert result is False


@pytest.mark.integration
@pytest.mark.requires_docker
@patch('subprocess.run')
def test_check_container_running(mock_run, monitor):
    """Test container check when running"""
    mock_run.return_value = Mock(stdout="true\n", returncode=0)

    result = monitor.check_container_status("xray-reality")

    assert result is True


@pytest.mark.integration
@pytest.mark.requires_docker
@patch('subprocess.run')
def test_check_container_stopped(mock_run, monitor):
    """Test container check when stopped"""
    mock_run.return_value = Mock(stdout="false\n", returncode=0)

    result = monitor.check_container_status("xray-reality")

    assert result is False


@pytest.mark.integration
@pytest.mark.requires_docker
@patch('subprocess.run')
def test_check_container_exception(mock_run, monitor):
    """Test container check handles exceptions"""
    mock_run.side_effect = Exception("Docker error")

    result = monitor.check_container_status("xray-reality")

    assert result is False


@pytest.mark.integration
@pytest.mark.requires_docker
@patch('subprocess.run')
def test_restart_service_success(mock_run, monitor):
    """Test service restart success"""
    mock_run.return_value = Mock(returncode=0)

    result = monitor.restart_service("xray", "xray-reality")

    assert result is True
    mock_run.assert_called_once()


@pytest.mark.integration
@pytest.mark.requires_docker
@patch('subprocess.run')
def test_restart_service_failure(mock_run, monitor):
    """Test service restart failure"""
    mock_run.return_value = Mock(returncode=1)

    result = monitor.restart_service("xray", "xray-reality")

    assert result is False


def test_check_service_unknown(monitor):
    """Test checking unknown service"""
    healthy, message = monitor.check_service("unknown")

    assert healthy is False
    assert "Unknown service" in message


@patch.object(HealthMonitor, 'check_port')
@patch.object(HealthMonitor, 'check_container_status')
def test_check_service_healthy(mock_container, mock_port, monitor):
    """Test service check when healthy"""
    mock_port.return_value = True
    mock_container.return_value = True

    healthy, message = monitor.check_service("xray")

    assert healthy is True
    assert "healthy" in message
    assert "443" in message


@patch.object(HealthMonitor, 'check_port')
@patch.object(HealthMonitor, 'check_container_status')
def test_check_service_unhealthy_port(mock_container, mock_port, monitor):
    """Test service check when port is down"""
    mock_port.return_value = False
    mock_container.return_value = True

    healthy, message = monitor.check_service("xray")

    assert healthy is False
    assert "unhealthy" in message
    assert "port 443 not listening" in message


@patch.object(HealthMonitor, 'check_port')
@patch.object(HealthMonitor, 'check_container_status')
def test_check_service_unhealthy_container(mock_container, mock_port, monitor):
    """Test service check when container is down"""
    mock_port.return_value = True
    mock_container.return_value = False

    healthy, message = monitor.check_service("xray")

    assert healthy is False
    assert "unhealthy" in message
    assert "container xray-reality not running" in message


@patch.object(HealthMonitor, 'check_service')
def test_check_all_services(mock_check, monitor, capsys):
    """Test checking all services"""
    mock_check.side_effect = [
        (True, "xray is healthy"),
        (True, "shadowsocks is healthy")
    ]

    results = monitor.check_all_services()

    assert results["xray"] is True
    assert results["shadowsocks"] is True
    assert mock_check.call_count == 2

    captured = capsys.readouterr()
    assert "xray is healthy" in captured.out
    assert "shadowsocks is healthy" in captured.out


@pytest.mark.integration
@pytest.mark.requires_docker
@patch.object(HealthMonitor, 'check_service')
@patch.object(HealthMonitor, 'restart_service')
def test_monitor_and_restart_healthy(mock_restart, mock_check, monitor_with_telegram):
    """Test monitoring when all services are healthy"""
    mock_check.return_value = (True, "xray is healthy")

    with patch.object(monitor_with_telegram.notifier, 'send_service_down_alert'):
        results = monitor_with_telegram.monitor_and_restart()

    assert all(status == "healthy" for status in results.values())
    mock_restart.assert_not_called()


@pytest.mark.integration
@pytest.mark.requires_docker
@patch.object(HealthMonitor, 'check_service')
@patch.object(HealthMonitor, 'restart_service')
@patch('time.sleep')
def test_monitor_and_restart_down(mock_sleep, mock_restart, mock_check, monitor_with_telegram):
    """Test monitoring and restarting a down service"""
    # First check: down, second check after restart: up
    mock_check.side_effect = [
        (False, "xray unhealthy: port 443 not listening"),
        (True, "xray is healthy")
    ]
    mock_restart.return_value = True

    with patch.object(monitor_with_telegram.notifier, 'send_service_down_alert') as mock_down:
        with patch.object(monitor_with_telegram.notifier, 'send_service_restored_alert') as mock_up:
            results = monitor_with_telegram.monitor_and_restart()

    assert results["xray"] == "restarted"
    mock_restart.assert_called_once()
    mock_down.assert_called_once_with("xray", 443)
    mock_up.assert_called_once_with("xray")


@pytest.mark.integration
@pytest.mark.requires_docker
@patch.object(HealthMonitor, 'check_service')
@patch.object(HealthMonitor, 'restart_service')
@patch('time.sleep')
def test_monitor_restart_failed(mock_sleep, mock_restart, mock_check, monitor_with_telegram):
    """Test monitoring when restart fails"""
    mock_check.return_value = (False, "xray unhealthy")
    mock_restart.return_value = False

    with patch.object(monitor_with_telegram.notifier, 'send_service_down_alert'):
        results = monitor_with_telegram.monitor_and_restart()

    assert results["xray"] == "restart_failed"
