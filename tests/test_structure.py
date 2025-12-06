import os
from pathlib import Path

def test_directory_structure():
    # Test all required directories exist
    base = Path(__file__).parent.parent

    required_dirs = [
        "scripts/bash",
        "scripts/python",
        "templates",
        "docker/xray",
        "docker/shadowsocks",
        "clients/macos",
        "clients/android",
        "clients/windows",
        "docs",
        "tests",
    ]

    for dir_path in required_dirs:
        full_path = base / dir_path
        assert full_path.exists(), f"Missing directory: {dir_path}"
        assert full_path.is_dir(), f"Not a directory: {dir_path}"

def test_required_files():
    # Test all required config files exist
    base = Path(__file__).parent.parent

    required_files = [
        "README.md",
        "CHANGELOG.md",
        ".gitignore",
        "pyproject.toml",
        "config.env.template",
    ]

    for file_path in required_files:
        full_path = base / file_path
        assert full_path.exists(), f"Missing file: {file_path}"
        assert full_path.is_file(), f"Not a file: {file_path}"

def test_python_packages():
    # Test Python package markers
    base = Path(__file__).parent.parent

    init_files = [
        "scripts/python/__init__.py",
        "tests/__init__.py",
    ]

    for init_path in init_files:
        full_path = base / init_path
        assert full_path.exists(), f"Missing __init__.py: {init_path}"

def test_gitignore_content():
    # Test .gitignore has critical entries
    base = Path(__file__).parent.parent
    gitignore = base / ".gitignore"

    content = gitignore.read_text()

    critical_patterns = [
        "config.env",
        "*.key",
        "*.pem",
        "__pycache__",
        "*.log",
    ]

    for pattern in critical_patterns:
        assert pattern in content, f"Missing in .gitignore: {pattern}"

def test_pyproject_content():
    # Test pyproject.toml has core dependencies
    base = Path(__file__).parent.parent
    pyproject = base / "pyproject.toml"

    content = pyproject.read_text()

    required_packages = [
        "jinja2",
        "boto3",
        "requests",
        "qrcode",
        "click",
        "pytest",
    ]

    for package in required_packages:
        assert package in content, f"Missing in pyproject.toml: {package}"
