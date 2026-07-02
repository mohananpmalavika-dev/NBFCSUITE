import os
import tempfile
from fastapi.testclient import TestClient
from services.platform.app.main import app


def test_platform_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "platform"}


def test_edp_dashboard_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/edp/dashboard", params={"tenant_id": "tenant-local-accounting"})
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant-local-accounting"
    assert "data_assets" in data
    assert "status" in data
