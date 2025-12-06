import json
import tempfile
from pathlib import Path
import pytest
from scripts.python.user_manager import User, UserManager


def test_user_creation():
    """Test creating a User object"""
    user = User(username="testuser", uuid="test-uuid-123")

    assert user.username == "testuser"
    assert user.uuid == "test-uuid-123"
    assert user.email == "testuser@vpn"
    assert user.created_at is not None


def test_user_to_dict():
    """Test converting user to dictionary"""
    user = User(username="testuser", uuid="test-uuid-123")
    user_dict = user.to_dict()

    assert user_dict["username"] == "testuser"
    assert user_dict["uuid"] == "test-uuid-123"
    assert user_dict["email"] == "testuser@vpn"
    assert "created_at" in user_dict


def test_user_from_dict():
    """Test creating user from dictionary"""
    user_dict = {
        "username": "testuser",
        "uuid": "test-uuid-123",
        "email": "test@example.com",
        "created_at": "2025-01-01T00:00:00"
    }

    user = User.from_dict(user_dict)

    assert user.username == "testuser"
    assert user.uuid == "test-uuid-123"
    assert user.email == "test@example.com"
    assert user.created_at == "2025-01-01T00:00:00"


def test_user_manager_add_user():
    """Test adding a user"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        user = manager.add_user("alice")

        assert user.username == "alice"
        assert len(user.uuid) > 0
        assert manager.user_count() == 1


def test_user_manager_add_user_with_uuid():
    """Test adding a user with custom UUID"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        user = manager.add_user("bob", uuid="custom-uuid-456")

        assert user.username == "bob"
        assert user.uuid == "custom-uuid-456"


def test_user_manager_add_duplicate_user():
    """Test that adding duplicate user raises error"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("charlie")

        with pytest.raises(ValueError, match="already exists"):
            manager.add_user("charlie")


def test_user_manager_remove_user():
    """Test removing a user"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("dave")
        assert manager.user_count() == 1

        result = manager.remove_user("dave")

        assert result is True
        assert manager.user_count() == 0


def test_user_manager_remove_nonexistent_user():
    """Test removing a user that doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        result = manager.remove_user("nonexistent")

        assert result is False


def test_user_manager_get_user():
    """Test getting a user by username"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("eve", uuid="eve-uuid")

        user = manager.get_user("eve")

        assert user is not None
        assert user.username == "eve"
        assert user.uuid == "eve-uuid"


def test_user_manager_get_nonexistent_user():
    """Test getting a user that doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        user = manager.get_user("nonexistent")

        assert user is None


def test_user_manager_list_users():
    """Test listing all users"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("alice")
        manager.add_user("bob")
        manager.add_user("charlie")

        users = manager.list_users()

        assert len(users) == 3
        usernames = [u.username for u in users]
        assert "alice" in usernames
        assert "bob" in usernames
        assert "charlie" in usernames


def test_user_manager_persistence():
    """Test that users are persisted to file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"

        manager1 = UserManager(users_file)
        manager1.add_user("frank", uuid="frank-uuid")

        manager2 = UserManager(users_file)
        user = manager2.get_user("frank")

        assert user is not None
        assert user.uuid == "frank-uuid"


def test_user_manager_get_users_for_config():
    """Test getting users in config format"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("grace", uuid="grace-uuid")
        manager.add_user("henry", uuid="henry-uuid")

        config_users = manager.get_users_for_config()

        assert len(config_users) == 2
        assert config_users[0]["uuid"] == "grace-uuid"
        assert config_users[0]["email"] == "grace@vpn"
        assert config_users[1]["uuid"] == "henry-uuid"
        assert config_users[1]["email"] == "henry@vpn"


def test_user_manager_json_structure():
    """Test that saved JSON has correct structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = Path(tmpdir) / "users.json"
        manager = UserManager(users_file)

        manager.add_user("iris")

        with open(users_file, 'r') as f:
            data = json.load(f)

        assert "users" in data
        assert "updated_at" in data
        assert len(data["users"]) == 1
        assert data["users"][0]["username"] == "iris"
