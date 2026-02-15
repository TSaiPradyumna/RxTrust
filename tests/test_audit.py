from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_audit_returns_guardian_alert_for_diabetic_profile():
    response = client.post(
        "/audit",
        json={
            "product_name": "Cough Syrup",
            "batch_number": "OLM24120",
            "manufacturer": "Example Pharma",
            "guardian_profile": {"diabetes": True},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_score"] >= 35
    assert payload["verdict"] in {"caution", "alert"}
    assert payload["guardian"]["personalized_flags"]
    assert payload["evidence"]


def test_audit_cache_hit_on_second_call():
    body = {
        "product_name": "Paracetamol",
        "batch_number": "A123",
        "manufacturer": "ABC Labs",
    }
    first = client.post("/audit", json=body)
    second = client.post("/audit", json=body)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["cached"] is True
