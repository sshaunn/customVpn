import boto3
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import subprocess


class S3BackupManager:
    """Manage encrypted backups to S3"""

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        bucket_name: str,
        gpg_passphrase: str
    ):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self.bucket_name = bucket_name
        self.gpg_passphrase = gpg_passphrase

    def create_backup(
        self,
        config_paths: List[Path],
        users_file: Path,
        backup_name: str = None
    ) -> str:
        """Create encrypted backup and upload to S3"""
        if backup_name is None:
            backup_name = f"vpn-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            tar_path = tmp_path / f"{backup_name}.tar.gz"

            with tarfile.open(tar_path, 'w:gz') as tar:
                for config_path in config_paths:
                    if config_path.exists():
                        tar.add(config_path, arcname=config_path.name)

                if users_file.exists():
                    tar.add(users_file, arcname=users_file.name)

            encrypted_path = tmp_path / f"{backup_name}.tar.gz.gpg"

            subprocess.run(
                [
                    'gpg',
                    '--batch',
                    '--yes',
                    '--passphrase', self.gpg_passphrase,
                    '--symmetric',
                    '--cipher-algo', 'AES256',
                    '--output', str(encrypted_path),
                    str(tar_path)
                ],
                check=True,
                capture_output=True
            )

            s3_key = f"backups/{backup_name}.tar.gz.gpg"

            self.s3.upload_file(
                str(encrypted_path),
                self.bucket_name,
                s3_key
            )

            return s3_key

    def list_backups(self) -> List[dict]:
        """List all backups in S3"""
        response = self.s3.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix='backups/'
        )

        backups = []
        if 'Contents' in response:
            for obj in response['Contents']:
                backups.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })

        return sorted(backups, key=lambda x: x['last_modified'], reverse=True)

    def restore_backup(
        self,
        s3_key: str,
        restore_dir: Path
    ) -> List[Path]:
        """Download and decrypt backup from S3"""
        restore_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            encrypted_path = tmp_path / "backup.tar.gz.gpg"

            self.s3.download_file(
                self.bucket_name,
                s3_key,
                str(encrypted_path)
            )

            decrypted_path = tmp_path / "backup.tar.gz"

            subprocess.run(
                [
                    'gpg',
                    '--batch',
                    '--yes',
                    '--passphrase', self.gpg_passphrase,
                    '--decrypt',
                    '--output', str(decrypted_path),
                    str(encrypted_path)
                ],
                check=True,
                capture_output=True
            )

            restored_files = []

            with tarfile.open(decrypted_path, 'r:gz') as tar:
                tar.extractall(restore_dir)

                for member in tar.getmembers():
                    restored_files.append(restore_dir / member.name)

            return restored_files

    def delete_old_backups(self, retention_days: int) -> List[str]:
        """Delete backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        backups = self.list_backups()
        deleted_keys = []

        for backup in backups:
            if backup['last_modified'].replace(tzinfo=None) < cutoff_date:
                self.s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=backup['key']
                )
                deleted_keys.append(backup['key'])

        return deleted_keys
