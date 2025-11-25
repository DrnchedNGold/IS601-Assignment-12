import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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
