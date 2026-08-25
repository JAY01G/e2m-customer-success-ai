import uuid
import pytest
from fastapi.testclient import TestClient


def test_interaction_creation_and_auto_ai_insight(client: TestClient, csm_headers, test_customer):
    payload = {
        "customer_id": str(test_customer.id),
        "type": "MEETING",
        "title": "Strategy Alignment Meeting",
        "notes": "Discussed roadmap expansion. Customer is excited and asked for a follow up proposal by Friday.",
        "duration_minutes": 30,
        "generate_ai_insight": True,
    }
    response = client.post("/api/v1/interactions", json=payload, headers=csm_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "Strategy Alignment Meeting"
    assert data["customer_id"] == str(test_customer.id)

    # Check AI insight attached
    assert data["ai_insight"] is not None
    assert data["ai_insight"]["sentiment"] in ["Positive", "Neutral", "Negative"]
    assert len(data["ai_insight"]["action_items"]) > 0


def test_interaction_invalid_customer_id(client: TestClient, csm_headers):
    fake_id = str(uuid.uuid4())
    payload = {
        "customer_id": fake_id,
        "type": "CALL",
        "title": "Invalid Call",
        "notes": "Testing invalid foreign key lookup",
    }
    response = client.post("/api/v1/interactions", json=payload, headers=csm_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


def test_interaction_filter_by_customer_and_type(
    client: TestClient, csm_headers, test_interaction, test_customer
):
    res = client.get(
        f"/api/v1/interactions?customer_id={test_customer.id}&type=MEETING",
        headers=csm_headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["items"]) >= 1
    assert data["items"][0]["type"] == "MEETING"


def test_interaction_update_and_delete(
    client: TestClient, admin_headers, test_interaction
):
    # Update
    update_res = client.patch(
        f"/api/v1/interactions/{test_interaction.id}",
        json={"title": "Updated Strategy Meeting", "duration_minutes": 60},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Updated Strategy Meeting"
    assert update_res.json()["data"]["duration_minutes"] == 60

    # Delete
    del_res = client.delete(
        f"/api/v1/interactions/{test_interaction.id}", headers=admin_headers
    )
    assert del_res.status_code == 200

    # 404
    get_res = client.get(
        f"/api/v1/interactions/{test_interaction.id}", headers=admin_headers
    )
    assert get_res.status_code == 404
