import base64
import json
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader
import qrcode


class ClientConfigGenerator:
    """Generate client configuration files for various platforms"""

    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "templates"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_vless_share_link(
        self,
        username: str,
        uuid: str,
        server_ip: str,
        port: int,
        reality_sni: str,
        reality_public_key: str,
        reality_short_id: str
    ) -> str:
        """Generate VLESS share link for import"""
        template = self.env.get_template("client-vless-share.j2")

        link = template.render(
            username=username,
            uuid=uuid,
            server_ip=server_ip,
            port=port,
            reality_sni=reality_sni,
            reality_public_key=reality_public_key,
            reality_short_id=reality_short_id
        )

        return link.strip()

    def generate_shadowsocks_share_link(
        self,
        username: str,
        server_ip: str,
        ss_port: int,
        ss_password: str,
        ss_method: str = "2022-blake3-aes-256-gcm"
    ) -> str:
        """Generate Shadowsocks share link"""
        method_password = f"{ss_method}:{ss_password}"
        method_password_base64 = base64.b64encode(method_password.encode()).decode()

        template = self.env.get_template("client-shadowsocks-share.j2")

        link = template.render(
            username=username,
            server_ip=server_ip,
            ss_port=ss_port,
            ss_method_password_base64=method_password_base64
        )

        return link.strip()

    def generate_client_json_config(
        self,
        username: str,
        uuid: str,
        server_ip: str,
        port: int,
        reality_sni: str,
        reality_public_key: str,
        reality_short_id: str
    ) -> str:
        """Generate JSON config for desktop clients (v2rayN, v2rayU, Qv2ray)"""
        template = self.env.get_template("client-config.json.j2")

        config = template.render(
            username=username,
            uuid=uuid,
            server_ip=server_ip,
            port=port,
            reality_sni=reality_sni,
            reality_public_key=reality_public_key,
            reality_short_id=reality_short_id
        )

        return config

    def generate_qr_code(self, content: str, output_path: Path) -> None:
        """Generate QR code image from content"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)

    def generate_all_client_configs(
        self,
        username: str,
        uuid: str,
        server_ip: str,
        xray_port: int,
        reality_sni: str,
        reality_public_key: str,
        reality_short_id: str,
        ss_port: int,
        ss_password: str,
        output_dir: Path
    ) -> Dict[str, Path]:
        """Generate all client configs for a user"""
        output_dir = output_dir / username
        output_dir.mkdir(parents=True, exist_ok=True)

        vless_link = self.generate_vless_share_link(
            username=username,
            uuid=uuid,
            server_ip=server_ip,
            port=xray_port,
            reality_sni=reality_sni,
            reality_public_key=reality_public_key,
            reality_short_id=reality_short_id
        )

        ss_link = self.generate_shadowsocks_share_link(
            username=username,
            server_ip=server_ip,
            ss_port=ss_port,
            ss_password=ss_password
        )

        json_config = self.generate_client_json_config(
            username=username,
            uuid=uuid,
            server_ip=server_ip,
            port=xray_port,
            reality_sni=reality_sni,
            reality_public_key=reality_public_key,
            reality_short_id=reality_short_id
        )

        vless_link_path = output_dir / "vless-link.txt"
        vless_link_path.write_text(vless_link)

        ss_link_path = output_dir / "shadowsocks-link.txt"
        ss_link_path.write_text(ss_link)

        json_config_path = output_dir / "config.json"
        json_config_path.write_text(json_config)

        vless_qr_path = output_dir / "vless-qr.png"
        self.generate_qr_code(vless_link, vless_qr_path)

        ss_qr_path = output_dir / "shadowsocks-qr.png"
        self.generate_qr_code(ss_link, ss_qr_path)

        return {
            "vless_link": vless_link_path,
            "vless_qr": vless_qr_path,
            "shadowsocks_link": ss_link_path,
            "shadowsocks_qr": ss_qr_path,
            "json_config": json_config_path
        }
