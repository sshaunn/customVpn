import json
from pathlib import Path
from typing import Any, Dict, List
from jinja2 import Environment, FileSystemLoader, Template


class ConfigGenerator:
    """Generate VPN configuration files from templates"""

    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "templates"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render_xray_config(
        self,
        users: List[Dict[str, str]],
        xray_port: int,
        reality_sni: str,
        reality_private_key: str,
        reality_short_id: str
    ) -> str:
        """Render Xray VLESS+REALITY configuration"""
        template = self.env.get_template("xray-config.json.j2")

        config = template.render(
            users=users,
            xray_port=xray_port,
            reality_sni=reality_sni,
            reality_private_key=reality_private_key,
            reality_short_id=reality_short_id
        )

        return config

    def render_shadowsocks_config(
        self,
        ss_port: int,
        ss_password: str
    ) -> str:
        """Render Shadowsocks configuration"""
        template = self.env.get_template("shadowsocks-config.json.j2")

        config = template.render(
            ss_port=ss_port,
            ss_password=ss_password
        )

        return config

    def save_config(self, config: str, output_path: Path) -> None:
        """Save configuration to file and validate JSON"""
        json.loads(config)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(config)

    def generate_all_configs(
        self,
        users: List[Dict[str, str]],
        xray_port: int,
        reality_sni: str,
        reality_private_key: str,
        reality_short_id: str,
        ss_port: int,
        ss_password: str,
        output_dir: Path
    ) -> Dict[str, Path]:
        """Generate all VPN configurations"""
        xray_config = self.render_xray_config(
            users=users,
            xray_port=xray_port,
            reality_sni=reality_sni,
            reality_private_key=reality_private_key,
            reality_short_id=reality_short_id
        )

        ss_config = self.render_shadowsocks_config(
            ss_port=ss_port,
            ss_password=ss_password
        )

        xray_path = output_dir / "xray" / "config.json"
        ss_path = output_dir / "shadowsocks" / "config.json"

        self.save_config(xray_config, xray_path)
        self.save_config(ss_config, ss_path)

        return {
            "xray": xray_path,
            "shadowsocks": ss_path
        }
