import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    payload = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "role": "CUSTOMER_SUCCESS_MANAGER",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "newuser@example.com"
    assert data["data"]["user"]["role"] == "CUSTOMER_SUCCESS_MANAGER"


def test_register_duplicate_email_conflict(client: TestClient, test_admin_user):
    payload = {
        "name": "Another Admin",
        "email": test_admin_user.email,
        "password": "SecurePassword123!",
        "role": "ADMIN",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["message"].lower()


def test_register_weak_password_rejected(client: TestClient):
    payload = {
        "name": "Weak User",
        "email": "weak@example.com",
        "password": "weak",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient, test_csm_user):
    payload = {
        "email": test_csm_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == test_csm_user.email


def test_login_invalid_credentials(client: TestClient, test_csm_user):
    payload = {
        "email": test_csm_user.email,
        "password": "WrongPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


def test_get_me_authenticated(client: TestClient, csm_headers, test_csm_user):
    response = client.get("/api/v1/auth/me", headers=csm_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(test_csm_user.id)
    assert data["data"]["email"] == test_csm_user.email


def test_get_me_unauthenticated(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


def test_refresh_token_via_body(client: TestClient, test_csm_user):
    login_payload = {
        "email": test_csm_user.email,
        "password": "Password123!",
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()["data"]
    refresh_token = login_data["refresh_token"]

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    refresh_data = refresh_resp.json()
    assert refresh_data["success"] is True
    assert "access_token" in refresh_data["data"]
    assert "refresh_token" in refresh_data["data"]
    assert refresh_data["data"]["user"]["email"] == test_csm_user.email


def test_refresh_token_via_cookie(client: TestClient, test_csm_user):
    login_payload = {
        "email": test_csm_user.email,
        "password": "Password123!",
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["data"]["refresh_token"]

    client.cookies.set("refresh_token", refresh_token)
    refresh_resp = client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    refresh_data = refresh_resp.json()
    assert refresh_data["success"] is True
    assert "access_token" in refresh_data["data"]


def test_refresh_token_missing_rejected(client: TestClient):
    client.cookies.clear()
    refresh_resp = client.post("/api/v1/auth/refresh", json={})
    assert refresh_resp.status_code == 401
    refresh_data = refresh_resp.json()
    assert refresh_data["success"] is False
    assert "missing" in refresh_data["message"].lower()

