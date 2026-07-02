import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.main import app


def test_grc_health_and_dashboard():
    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok", "service": "grc"}

    dashboard_response = client.get("/api/v1/grc/dashboard", params={"tenant_id": "tenant-test"})
    assert dashboard_response.status_code == 200
    payload = dashboard_response.json()
    assert payload["tenant_id"] == "tenant-test"
    assert payload["status"] == "operational"
