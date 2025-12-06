import secrets
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Tuple


class KeyGenerator:
    """Generate cryptographic keys and IDs for VPN services"""

    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID v4 for VLESS user"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_reality_keypair() -> Dict[str, str]:
        """Generate x25519 key pair for REALITY protocol using xray binary"""
        try:
            result = subprocess.run(
                ["xray", "x25519"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            private_key = None
            public_key = None

            for line in result.stdout.splitlines():
                if "Private key:" in line:
                    private_key = line.split("Private key:")[1].strip()
                elif "Public key:" in line:
                    public_key = line.split("Public key:")[1].strip()

            if not private_key or not public_key:
                raise ValueError("Failed to parse xray x25519 output")

            return {
                "private_key": private_key,
                "public_key": public_key
            }

        except FileNotFoundError:
            raise RuntimeError("xray binary not found. Install xray-core first.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("xray x25519 command timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"xray x25519 failed: {e.stderr}")

    @staticmethod
    def generate_reality_short_id() -> str:
        """Generate random short ID for REALITY (8 hex chars)"""
        return secrets.token_hex(4)

    @staticmethod
    def generate_shadowsocks_password() -> str:
        """Generate base64 password for Shadowsocks-2022 (32 bytes)"""
        random_bytes = secrets.token_bytes(32)
        import base64
        return base64.b64encode(random_bytes).decode('utf-8')

    @staticmethod
    def generate_all_keys() -> Dict[str, any]:
        """Generate all required keys for VPN setup"""
        reality_keys = KeyGenerator.generate_reality_keypair()

        return {
            "admin_uuid": KeyGenerator.generate_uuid(),
            "reality_private_key": reality_keys["private_key"],
            "reality_public_key": reality_keys["public_key"],
            "reality_short_id": KeyGenerator.generate_reality_short_id(),
            "shadowsocks_password": KeyGenerator.generate_shadowsocks_password()
        }
