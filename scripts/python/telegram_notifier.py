import requests
from typing import Optional
from datetime import datetime


class TelegramNotifier:
    """Send notifications via Telegram bot"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to Telegram"""
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": parse_mode
                },
                timeout=10
            )
            return response.ok
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False

    def send_alert(self, title: str, details: str, severity: str = "INFO") -> bool:
        """Send formatted alert message"""
        emoji_map = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅"
        }

        emoji = emoji_map.get(severity, "📢")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"{emoji} *{severity}: {title}*\n\n{details}\n\n_Time: {timestamp}_"

        return self.send_message(message)

    def send_service_down_alert(self, service_name: str, port: int) -> bool:
        """Send service down alert"""
        return self.send_alert(
            title=f"{service_name} Service Down",
            details=f"Service on port {port} is not responding.\nAttempting restart...",
            severity="ERROR"
        )

    def send_service_restored_alert(self, service_name: str) -> bool:
        """Send service restored alert"""
        return self.send_alert(
            title=f"{service_name} Service Restored",
            details=f"{service_name} is now running normally.",
            severity="SUCCESS"
        )

    def send_backup_alert(self, backup_name: str, size_mb: float, success: bool = True) -> bool:
        """Send backup completion alert"""
        if success:
            return self.send_alert(
                title="Backup Completed",
                details=f"Backup: `{backup_name}`\nSize: {size_mb:.2f} MB\nUploaded to S3 successfully",
                severity="SUCCESS"
            )
        else:
            return self.send_alert(
                title="Backup Failed",
                details=f"Backup: `{backup_name}`\nFailed to create or upload backup",
                severity="ERROR"
            )

    def send_deployment_alert(self, message: str) -> bool:
        """Send deployment notification"""
        return self.send_alert(
            title="VPN Deployment Update",
            details=message,
            severity="INFO"
        )

    def test_connection(self) -> bool:
        """Test if bot can send messages"""
        return self.send_message("✅ Telegram notification system connected!")
