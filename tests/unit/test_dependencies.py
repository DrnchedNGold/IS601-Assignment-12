import pytest
from app.auth import dependencies as dep_module
from app.schemas.user import UserResponse
from uuid import uuid4

def test_get_current_user_invalid_token(monkeypatch):
    monkeypatch.setattr(dep_module.User, "verify_token", lambda token: None)
    with pytest.raises(Exception):
        dep_module.get_current_user(token="badtoken")

def test_get_current_user_minimal_payload(monkeypatch):
    # Only 'sub' key
    monkeypatch.setattr(dep_module.User, "verify_token", lambda token: {"sub": str(uuid4())})
    result = dep_module.get_current_user(token="token")
    assert isinstance(result, UserResponse)
    # Direct UUID
    monkeypatch.setattr(dep_module.User, "verify_token", lambda token: uuid4())
    result = dep_module.get_current_user(token="token")
    assert isinstance(result, UserResponse)

def test_get_current_user_invalid_payload(monkeypatch):
    # No 'username' or 'sub'
    monkeypatch.setattr(dep_module.User, "verify_token", lambda token: {"foo": "bar"})
    with pytest.raises(Exception):
        dep_module.get_current_user(token="token")
    # Unsupported type
    monkeypatch.setattr(dep_module.User, "verify_token", lambda token: 123)
    with pytest.raises(Exception):
        dep_module.get_current_user(token="token")

from datetime import datetime

def test_get_current_active_user_inactive():
    user = UserResponse(
        id=uuid4(),
        username="inactive",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        is_active=False,
        is_verified=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    with pytest.raises(Exception):
        dep_module.get_current_active_user(current_user=user)
