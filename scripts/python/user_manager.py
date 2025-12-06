import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from scripts.python.key_generator import KeyGenerator


class User:
    """Represents a VPN user"""

    def __init__(self, username: str, uuid: str, email: str = None, created_at: str = None):
        self.username = username
        self.uuid = uuid
        self.email = email or f"{username}@vpn"
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, str]:
        """Convert user to dictionary"""
        return {
            "username": self.username,
            "uuid": self.uuid,
            "email": self.email,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'User':
        """Create user from dictionary"""
        return cls(
            username=data["username"],
            uuid=data["uuid"],
            email=data.get("email"),
            created_at=data.get("created_at")
        )


class UserManager:
    """Manage VPN users"""

    def __init__(self, users_file: Path = None):
        if users_file is None:
            users_file = Path(__file__).parent.parent.parent / "users.json"

        self.users_file = users_file
        self.users: List[User] = []
        self._load_users()

    def _load_users(self) -> None:
        """Load users from file"""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                self.users = [User.from_dict(u) for u in data.get("users", [])]

    def _save_users(self) -> None:
        """Save users to file"""
        self.users_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "users": [u.to_dict() for u in self.users],
            "updated_at": datetime.now().isoformat()
        }

        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_user(self, username: str, uuid: str = None) -> User:
        """Add a new user"""
        if self.get_user(username):
            raise ValueError(f"User '{username}' already exists")

        if uuid is None:
            uuid = KeyGenerator.generate_uuid()

        user = User(username=username, uuid=uuid)
        self.users.append(user)
        self._save_users()

        return user

    def remove_user(self, username: str) -> bool:
        """Remove a user by username"""
        user = self.get_user(username)
        if not user:
            return False

        self.users = [u for u in self.users if u.username != username]
        self._save_users()

        return True

    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users:
            if user.username == username:
                return user
        return None

    def list_users(self) -> List[User]:
        """List all users"""
        return self.users.copy()

    def get_users_for_config(self) -> List[Dict[str, str]]:
        """Get users in format for config generator"""
        return [{"uuid": u.uuid, "email": u.email} for u in self.users]

    def user_count(self) -> int:
        """Get total number of users"""
        return len(self.users)
