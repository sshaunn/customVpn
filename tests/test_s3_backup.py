import json
import tempfile
from pathlib import Path
import pytest
from scripts.python.s3_backup import S3BackupManager


@pytest.fixture
def backup_manager():
    """Create backup manager with test credentials from config.env"""
    config_file = Path(__file__).parent.parent / "config.env"

    env = {}
    if config_file.exists():
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value

    if not all(k in env for k in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'S3_BUCKET_NAME', 'GPG_PASSPHRASE']):
        pytest.skip("AWS credentials not configured in config.env")

    return S3BackupManager(
        aws_access_key_id=env['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=env['AWS_SECRET_ACCESS_KEY'],
        aws_region=env['AWS_REGION'],
        bucket_name=env['S3_BUCKET_NAME'],
        gpg_passphrase=env['GPG_PASSPHRASE']
    )


@pytest.fixture
def test_files():
    """Create test configuration files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        xray_config = tmp_path / "xray_config.json"
        xray_config.write_text(json.dumps({"test": "xray"}))

        ss_config = tmp_path / "ss_config.json"
        ss_config.write_text(json.dumps({"test": "shadowsocks"}))

        users_file = tmp_path / "users.json"
        users_file.write_text(json.dumps({"users": [{"username": "test"}]}))

        yield {
            "configs": [xray_config, ss_config],
            "users": users_file
        }


@pytest.mark.skipif(True, reason="Requires GPG installed and AWS credentials")
def test_create_backup(backup_manager, test_files):
    """Test creating encrypted backup and uploading to S3"""
    s3_key = backup_manager.create_backup(
        config_paths=test_files["configs"],
        users_file=test_files["users"],
        backup_name="test-backup"
    )

    assert s3_key.startswith("backups/")
    assert "test-backup" in s3_key
    assert s3_key.endswith(".tar.gz.gpg")


@pytest.mark.skipif(True, reason="Requires GPG installed and AWS credentials")
def test_list_backups(backup_manager):
    """Test listing backups from S3"""
    backups = backup_manager.list_backups()

    assert isinstance(backups, list)

    if len(backups) > 0:
        assert 'key' in backups[0]
        assert 'size' in backups[0]
        assert 'last_modified' in backups[0]


@pytest.mark.skipif(True, reason="Requires GPG installed and AWS credentials")
def test_restore_backup(backup_manager, test_files):
    """Test restoring backup from S3"""
    s3_key = backup_manager.create_backup(
        config_paths=test_files["configs"],
        users_file=test_files["users"],
        backup_name="test-restore"
    )

    with tempfile.TemporaryDirectory() as restore_dir:
        restore_path = Path(restore_dir)

        restored_files = backup_manager.restore_backup(s3_key, restore_path)

        assert len(restored_files) == 3

        file_names = [f.name for f in restored_files]
        assert "xray_config.json" in file_names
        assert "ss_config.json" in file_names
        assert "users.json" in file_names


@pytest.mark.skipif(True, reason="Requires GPG installed and AWS credentials")
def test_delete_old_backups(backup_manager):
    """Test deleting old backups"""
    deleted = backup_manager.delete_old_backups(retention_days=365)

    assert isinstance(deleted, list)


def test_backup_manager_initialization():
    """Test that BackupManager can be initialized"""
    manager = S3BackupManager(
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret",
        aws_region="ap-southeast-2",
        bucket_name="test-bucket",
        gpg_passphrase="test_passphrase"
    )

    assert manager.bucket_name == "test-bucket"
    assert manager.gpg_passphrase == "test_passphrase"
