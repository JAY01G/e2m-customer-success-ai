import pytest
from fastapi.testclient import TestClient


def test_admin_can_access_user_list(client: TestClient, admin_headers):
    response = client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]


def test_csm_cannot_access_user_list(client: TestClient, csm_headers):
    response = client.get("/api/v1/users", headers=csm_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert "requires" in data["message"].lower() or "permission" in data["message"].lower()


def test_viewer_cannot_access_user_list(client: TestClient, viewer_headers):
    response = client.get("/api/v1/users", headers=viewer_headers)
    assert response.status_code == 403


def test_csm_can_create_customer(client: TestClient, csm_headers):
    payload = {
        "name": "Acme User",
        "company_name": "Acme Corp",
        "email": "acme@example.com",
        "health_score": 90,
    }
    response = client.post("/api/v1/customers", json=payload, headers=csm_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["company_name"] == "Acme Corp"


def test_viewer_cannot_create_customer(client: TestClient, viewer_headers):
    payload = {
        "name": "Acme User",
        "company_name": "Acme Corp",
        "email": "acme@example.com",
        "health_score": 90,
    }
    response = client.post("/api/v1/customers", json=payload, headers=viewer_headers)
    assert response.status_code == 403


def test_viewer_can_view_customers(client: TestClient, viewer_headers, test_customer):
    response = client.get("/api/v1/customers", headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) >= 1


def test_viewer_cannot_delete_customer(client: TestClient, viewer_headers, test_customer):
    response = client.delete(f"/api/v1/customers/{test_customer.id}", headers=viewer_headers)
    assert response.status_code == 403


def test_csm_cannot_delete_customer(client: TestClient, csm_headers, test_customer):
    # Customer deletion is restricted to ADMIN
    response = client.delete(f"/api/v1/customers/{test_customer.id}", headers=csm_headers)
    assert response.status_code == 403


def test_admin_can_delete_customer(client: TestClient, admin_headers, test_customer):
    response = client.delete(f"/api/v1/customers/{test_customer.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
