from fastapi.testclient import TestClient
from services.ai.app.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "ai"


def test_chat():
    client = TestClient(app)
    r = client.post("/api/v1/ai/chat", json={"tenant_id": "tenant-local", "prompt": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["tenant_id"] == "tenant-local"
    assert "response" in data
