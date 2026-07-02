from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_list_products():
    r = client.get("/api/v1/gold/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
