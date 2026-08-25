import pytest
from fastapi.testclient import TestClient


def test_dashboard_summary_metrics(
    client: TestClient, csm_headers, test_customer, test_interaction
):
    # Ensure insight is generated
    client.post(
        f"/api/v1/interactions/{test_interaction.id}/insights",
        json={"regenerate": True},
        headers=csm_headers,
    )

    response = client.get("/api/v1/dashboard/summary", headers=csm_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["total_customers"] >= 1
    assert data["active_customers"] >= 1
    assert data["average_health_score"] > 0
    assert data["total_interactions"] >= 1
    assert "sentiment_distribution" in data
    assert "health_distribution" in data
    assert "status_distribution" in data
    assert "recent_interactions" in data
    assert "at_risk_customers_list" in data


def test_dashboard_unauthenticated(client: TestClient):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401
