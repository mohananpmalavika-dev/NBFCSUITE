import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.main import app


def test_risk_dashboard_endpoint():
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "risk"}

    dashboard_response = client.get("/api/v1/risk/dashboard", params={"tenant_id": "tenant-test"})
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["tenant_id"] == "tenant-test"
    assert payload["status"] == "operational"
