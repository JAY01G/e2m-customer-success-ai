import uuid
import pytest
from fastapi.testclient import TestClient


def test_customer_crud_lifecycle(client: TestClient, admin_headers):
    # 1. Create
    payload = {
        "name": "Sarah Connor",
        "company_name": "Cyberdyne Systems",
        "email": "sarah@cyberdyne.io",
        "phone": "+1 555 123 4567",
        "industry": "Robotics & AI",
        "status": "ACTIVE",
        "health_score": 95,
        "notes": "Fast growing account",
    }
    create_res = client.post("/api/v1/customers", json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    created_data = create_res.json()["data"]
    customer_id = created_data["id"]
    assert created_data["company_name"] == "Cyberdyne Systems"
    assert created_data["health_score"] == 95

    # 2. Get Detail
    get_res = client.get(f"/api/v1/customers/{customer_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == customer_id

    # 3. Update
    update_payload = {
        "health_score": 88,
        "status": "AT_RISK",
        "notes": "Updated account notes",
    }
    update_res = client.patch(
        f"/api/v1/customers/{customer_id}", json=update_payload, headers=admin_headers
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()["data"]
    assert updated_data["health_score"] == 88
    assert updated_data["status"] == "AT_RISK"

    # 4. Delete
    del_res = client.delete(f"/api/v1/customers/{customer_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # 5. Verify 404
    get_after_del = client.get(f"/api/v1/customers/{customer_id}", headers=admin_headers)
    assert get_after_del.status_code == 404


def test_customer_health_score_validation(client: TestClient, admin_headers):
    # Health score > 100
    payload = {
        "name": "Invalid User",
        "company_name": "Test Co",
        "email": "test@test.com",
        "health_score": 150,
    }
    res = client.post("/api/v1/customers", json=payload, headers=admin_headers)
    assert res.status_code == 422


def test_customer_filtering_and_search(client: TestClient, admin_headers, test_customer):
    # Search by company name
    res = client.get("/api/v1/customers?search=Acme", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["items"]) >= 1

    # Search with no match
    res_empty = client.get("/api/v1/customers?search=NonExistentCorpXYZ", headers=admin_headers)
    assert res_empty.status_code == 200
    assert len(res_empty.json()["data"]["items"]) == 0

    # Status filter
    res_status = client.get("/api/v1/customers?status=ACTIVE", headers=admin_headers)
    assert res_status.status_code == 200
    assert len(res_status.json()["data"]["items"]) >= 1


def test_customer_pagination(client: TestClient, admin_headers, test_customer):
    res = client.get("/api/v1/customers?page=1&page_size=5", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert "total" in data
    assert "total_pages" in data
