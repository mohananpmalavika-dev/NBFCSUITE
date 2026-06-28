import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.db as db_module
from app.routers import eom as eom_router
from app.main import app as customer_app


@pytest.fixture()
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    db_module.engine = engine
    db_module.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db_module.Base.metadata.drop_all(bind=engine)
    db_module.Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = db_module.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    customer_app.dependency_overrides[eom_router.get_db] = override_get_db
    with TestClient(customer_app) as test_client:
        yield test_client

    customer_app.dependency_overrides.clear()


def test_eom_dashboard_returns_summary_and_recent_enterprises(client):
    response = client.post(
        "/eom/enterprises",
        json={
            "tenant_id": "tenant-001",
            "enterprise_code": "ARTH",
            "enterprise_name": "ARTH.OS",
            "country": "India",
            "currency": "INR",
            "timezone": "Asia/Kolkata",
        },
    )
    assert response.status_code == 200

    dashboard = client.get("/eom/dashboard")
    assert dashboard.status_code == 200

    body = dashboard.json()
    assert body["summary"]["enterprises"] == 1
    assert body["recent_enterprises"][0]["enterprise_code"] == "ARTH"
    assert body["workspace"]["title"] == "Enterprise Organization Management"
