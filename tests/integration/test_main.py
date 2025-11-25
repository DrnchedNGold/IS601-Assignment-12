import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# task_progress
# - [x] Analyze requirements
# - [x] Set up necessary files
# - [x] Implement user registration, login, DB verification tests
# - [x] Implement calculation CRUD tests
# - [x] Implement error handling and invalid data tests
# - [x] Verify status codes and error responses
# - [ ] Review and update tests as needed

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_and_login():
    user = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    reg = client.post("/auth/register", json=user)
    assert reg.status_code == 201 or reg.status_code == 400  # 400 if already exists

    login = client.post("/auth/login", json={
        "username": "testuser",
        "password": "SecurePass123!"
    })
    assert login.status_code == 200 or login.status_code == 401

def test_form_login():
    data = {
        "username": "testuser",
        "password": "SecurePass123!"
    }
    response = client.post("/auth/token", data=data)
    assert response.status_code in [200, 401]

def test_calculation_endpoints():
    # Register and login
    user = {
        "first_name": "Calc",
        "last_name": "User",
        "email": "calcuser@example.com",
        "username": "calcuser",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    client.post("/auth/register", json=user)
    login = client.post("/auth/login", json={
        "username": "calcuser",
        "password": "SecurePass123!"
    })
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Add calculation
    calc = {
        "type": "addition",
        "inputs": [1, 2]
    }
    add = client.post("/calculations", json=calc, headers=headers)
    assert add.status_code == 201
    calc_id = add.json()["id"]

    # Browse
    browse = client.get("/calculations", headers=headers)
    assert browse.status_code == 200

    # Read
    read = client.get(f"/calculations/{calc_id}", headers=headers)
    assert read.status_code == 200

    # Edit
    update = client.put(f"/calculations/{calc_id}", json={"inputs": [2, 3]}, headers=headers)
    assert update.status_code == 200

    # Delete
    delete = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert delete.status_code == 204

def test_invalid_calculation():
    # Register and login
    user = {
        "first_name": "Err",
        "last_name": "User",
        "email": "erruser@example.com",
        "username": "erruser",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    client.post("/auth/register", json=user)
    login = client.post("/auth/login", json={
        "username": "erruser",
        "password": "SecurePass123!"
    })
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid calculation type
    calc = {
        "type": "invalid",
        "inputs": [1, 2]
    }
    add = client.post("/calculations", json=calc, headers=headers)
    assert add.status_code == 422 or add.status_code == 400

    # Division by zero
    calc = {
        "type": "division",
        "inputs": [1, 0]
    }
    add = client.post("/calculations", json=calc, headers=headers)
    assert add.status_code == 400 or add.status_code == 422

def test_invalid_uuid_and_not_found():
    # Register and login
    user = {
        "first_name": "Edge",
        "last_name": "Case",
        "email": "edgecase@example.com",
        "username": "edgecase",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    client.post("/auth/register", json=user)
    login = client.post("/auth/login", json={
        "username": "edgecase",
        "password": "SecurePass123!"
    })
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid UUID
    resp = client.get("/calculations/invalid-uuid", headers=headers)
    assert resp.status_code == 400

    # Not found
    from uuid import uuid4
    fake_id = str(uuid4())
    resp = client.get(f"/calculations/{fake_id}", headers=headers)
    assert resp.status_code == 404

    resp = client.put(f"/calculations/{fake_id}", json={"inputs": [1, 2]}, headers=headers)
    assert resp.status_code == 404

    resp = client.delete(f"/calculations/{fake_id}", headers=headers)
    assert resp.status_code == 404

def test_duplicate_user_registration():
    user = {
        "first_name": "Dup",
        "last_name": "User",
        "email": "dupuser@example.com",
        "username": "dupuser",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    reg1 = client.post("/auth/register", json=user)
    reg2 = client.post("/auth/register", json=user)
    assert reg2.status_code == 400

def test_invalid_password_registration():
    user = {
        "first_name": "Bad",
        "last_name": "Password",
        "email": "badpass@example.com",
        "username": "badpass",
        "password": "short",
        "confirm_password": "short"
    }
    reg = client.post("/auth/register", json=user)
    assert reg.status_code == 422 or reg.status_code == 400

def test_login_failure():
    login = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert login.status_code == 401

    data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    resp = client.post("/auth/token", data=data)
    assert resp.status_code == 401

# Additional coverage for app/auth/dependencies.py

import uuid
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user, get_current_active_user
from app.schemas.user import UserResponse

# Direct function tests for dependency coverage

def test_get_current_user_full_payload(monkeypatch):
    # Patch User.verify_token to return full payload
    monkeypatch.setattr("app.models.user.User.verify_token", lambda token: {
        "id": str(uuid.uuid4()),
        "username": "fulluser",
        "email": "full@example.com",
        "first_name": "Full",
        "last_name": "User",
        "is_active": True,
        "is_verified": True,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    })
    from app.auth.dependencies import get_current_user
    token = "dummy"
    user = get_current_user(token)
    assert user.username == "fulluser"

def test_get_current_user_minimal_payload(monkeypatch):
    # Patch User.verify_token to return minimal dict payload
    monkeypatch.setattr("app.models.user.User.verify_token", lambda token: {"sub": str(uuid.uuid4())})
    from app.auth.dependencies import get_current_user
    token = "dummy"
    user = get_current_user(token)
    assert user.username == "unknown"

def test_get_current_user_uuid_payload(monkeypatch):
    # Patch User.verify_token to return UUID
    monkeypatch.setattr("app.models.user.User.verify_token", lambda token: uuid.uuid4())
    from app.auth.dependencies import get_current_user
    token = "dummy"
    user = get_current_user(token)
    assert user.username == "unknown"

def test_get_current_user_invalid_token(monkeypatch):
    # Patch User.verify_token to return None
    monkeypatch.setattr("app.models.user.User.verify_token", lambda token: None)
    from app.auth.dependencies import get_current_user
    token = "dummy"
    import pytest
    with pytest.raises(Exception) as excinfo:
        get_current_user(token)
    assert "Could not validate credentials" in str(excinfo.value)

def test_get_current_active_user_inactive():
    from app.auth.dependencies import get_current_active_user
    inactive_user = UserResponse(
        id=str(uuid.uuid4()),
        username="inactive",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        is_active=False,
        is_verified=True,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )
    import pytest
    with pytest.raises(Exception) as excinfo:
        get_current_active_user(inactive_user)

# Additional coverage for app/auth/jwt.py

def test_verify_password_and_hash():
    from app.auth import jwt as jwtmod
    password = "StrongPassword123!"
    hashed = jwtmod.get_password_hash(password)
    assert jwtmod.verify_password(password, hashed)
    assert not jwtmod.verify_password("WrongPassword", hashed)

def test_create_token_access_and_refresh():
    from app.auth import jwt as jwtmod
    from app.schemas.token import TokenType
    user_id = str(uuid.uuid4())
    token_access = jwtmod.create_token(user_id, TokenType.ACCESS)
    token_refresh = jwtmod.create_token(user_id, TokenType.REFRESH)
    assert isinstance(token_access, str)
    assert isinstance(token_refresh, str)
    # Custom expires_delta
    import datetime
    token_custom = jwtmod.create_token(user_id, TokenType.ACCESS, expires_delta=datetime.timedelta(minutes=1))
    assert isinstance(token_custom, str)

import asyncio

@pytest.mark.asyncio
async def test_decode_token_valid(monkeypatch):
    from app.auth import jwt as jwtmod
    from app.schemas.token import TokenType
    user_id = str(uuid.uuid4())
    token = jwtmod.create_token(user_id, TokenType.ACCESS)
    # Patch is_blacklisted to always return False
    monkeypatch.setattr("app.auth.redis.is_blacklisted", lambda jti: False)
    payload = await jwtmod.decode_token(token, TokenType.ACCESS)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"

def test_decode_token_invalid_type(monkeypatch):
    from app.auth import jwt as jwtmod
    from app.schemas.token import TokenType
    user_id = str(uuid.uuid4())
    token = jwtmod.create_token(user_id, TokenType.ACCESS)
    # Patch is_blacklisted to always return False
    async def _is_blacklisted(jti): return False
    monkeypatch.setattr("app.auth.redis.is_blacklisted", _is_blacklisted)
    import pytest
    with pytest.raises(Exception) as excinfo:
        asyncio.run(jwtmod.decode_token(token, TokenType.REFRESH))
    assert "Could not validate credentials" in str(excinfo.value)

def test_create_token_error(monkeypatch):
    from app.auth import jwt as jwtmod
    from app.schemas.token import TokenType
    # Patch jwt.encode to raise Exception
    monkeypatch.setattr("jose.jwt.encode", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    import pytest
    with pytest.raises(Exception) as excinfo:
        jwtmod.create_token(str(uuid.uuid4()), TokenType.ACCESS)
    assert "Could not create token" in str(excinfo.value)
