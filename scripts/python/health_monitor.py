import socket
import subprocess
import os
from typing import Dict, List, Tuple
from datetime import datetime
from scripts.python.telegram_notifier import TelegramNotifier


class HealthMonitor:
    """Monitor VPN services health and restart on failure"""

    def __init__(self, telegram_bot_token: str = None, telegram_chat_id: str = None):
        self.services = {
            "xray": {"port": 443, "container": "xray-reality"},
            "shadowsocks": {"port": 8388, "container": "shadowsocks-fallback"}
        }
        self.notifier = None
        if telegram_bot_token and telegram_chat_id:
            self.notifier = TelegramNotifier(telegram_bot_token, telegram_chat_id)

    def check_port(self, port: int, host: str = "127.0.0.1", timeout: int = 3) -> bool:
        """Check if a port is listening"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def check_container_status(self, container_name: str) -> bool:
        """Check if a Docker container is running"""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() == "true"
        except Exception:
            return False

    def restart_service(self, service_name: str, container_name: str) -> bool:
        """Restart a Docker service"""
        try:
            result = subprocess.run(
                ["docker", "restart", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_service(self, service_name: str) -> Tuple[bool, str]:
        """Check service health (port and container)"""
        service = self.services.get(service_name)
        if not service:
            return False, f"Unknown service: {service_name}"

        port = service["port"]
        container = service["container"]

        port_ok = self.check_port(port)
        container_ok = self.check_container_status(container)

        if port_ok and container_ok:
            return True, f"{service_name} is healthy (port {port} listening, container running)"

        issues = []
        if not port_ok:
            issues.append(f"port {port} not listening")
        if not container_ok:
            issues.append(f"container {container} not running")

        return False, f"{service_name} unhealthy: {', '.join(issues)}"

    def check_all_services(self) -> Dict[str, bool]:
        """Check all services and return status"""
        results = {}
        for service_name in self.services.keys():
            healthy, message = self.check_service(service_name)
            results[service_name] = healthy
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
        return results

    def monitor_and_restart(self) -> Dict[str, str]:
        """Monitor all services and restart if needed"""
        results = {}

        for service_name, config in self.services.items():
            healthy, message = self.check_service(service_name)

            if healthy:
                results[service_name] = "healthy"
                continue

            # Service is down, attempt restart
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attempting to restart {service_name}...")

            if self.notifier:
                self.notifier.send_service_down_alert(service_name, config["port"])

            restart_success = self.restart_service(service_name, config["container"])

            if restart_success:
                # Wait and verify restart
                import time
                time.sleep(5)
                healthy_after, _ = self.check_service(service_name)

                if healthy_after:
                    results[service_name] = "restarted"
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {service_name} successfully restarted")
                    if self.notifier:
                        self.notifier.send_service_restored_alert(service_name)
                else:
                    results[service_name] = "restart_failed"
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {service_name} restart failed verification")
            else:
                results[service_name] = "restart_failed"
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to restart {service_name}")

        return results


def main():
    """CLI entry point"""
    import sys
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv("config.env")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    monitor = HealthMonitor(bot_token, chat_id)

    if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
        # Just check status, don't restart
        monitor.check_all_services()
    else:
        # Monitor and restart if needed
        results = monitor.monitor_and_restart()

        # Exit with error if any service failed
        if any(status in ["restart_failed"] for status in results.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
