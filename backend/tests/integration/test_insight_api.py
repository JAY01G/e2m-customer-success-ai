import uuid
import pytest
from fastapi.testclient import TestClient


def test_generate_and_retrieve_insight(client: TestClient, csm_headers, test_interaction):
    # Generate Insight
    gen_res = client.post(
        f"/api/v1/interactions/{test_interaction.id}/insights",
        json={"regenerate": True},
        headers=csm_headers,
    )
    assert gen_res.status_code == 200
    gen_data = gen_res.json()["data"]
    assert gen_data["interaction_id"] == str(test_interaction.id)
    assert gen_data["sentiment"] in ["Positive", "Neutral", "Negative"]

    # Retrieve Insight
    get_res = client.get(
        f"/api/v1/interactions/{test_interaction.id}/insights",
        headers=csm_headers,
    )
    assert get_res.status_code == 200
    get_data = get_res.json()["data"]
    assert get_data["id"] == gen_data["id"]


def test_generate_insight_nonexistent_interaction(client: TestClient, csm_headers):
    fake_id = str(uuid.uuid4())
    res = client.post(
        f"/api/v1/interactions/{fake_id}/insights",
        json={"regenerate": False},
        headers=csm_headers,
    )
    assert res.status_code == 404
