import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_budget_line_and_commitment_flow():
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/budgets/",
        json={
            "tenant_id": "tenant-1",
            "budget_name": "Q4 Ops",
            "financial_year": "2026",
            "currency": "INR",
            "scope_level": "branch",
            "scope_id": "branch-001",
            "status": "approved",
            "initial_amount": 100000.0,
            "initial_version_name": "Original",
            "initial_period": "Q4",
        },
    )
    assert create_response.status_code == 200
    budget_id = create_response.json()["id"]

    lines_response = client.post(
        f"/api/v1/budgets/{budget_id}/lines",
        json={
            "tenant_id": "tenant-1",
            "line_code": "SALARY",
            "description": "Payroll",
            "amount": 40000.0,
            "gl_account_code": "5000",
            "cost_center": "OPS",
        },
    )
    assert lines_response.status_code == 200
    assert lines_response.json()["line_code"] == "SALARY"

    commitment_response = client.post(
        f"/api/v1/budgets/{budget_id}/commitments",
        json={
            "tenant_id": "tenant-1",
            "reference_type": "purchase_order",
            "reference_id": "PO-1001",
            "amount": 20000.0,
            "status": "active",
        },
    )
    assert commitment_response.status_code == 200
    assert commitment_response.json()["amount"] == 20000.0

    availability_response = client.post(
        "/api/v1/budgets/check-availability",
        json={
            "tenant_id": "tenant-1",
            "scope_level": "branch",
            "scope_id": "branch-001",
            "requested_amount": 15000.0,
        },
    )
    assert availability_response.status_code == 200
    payload = availability_response.json()
    assert payload["status"] == "available"
    assert payload["available_amount"] == 65000.0

    dashboard_response = client.get("/api/v1/budgets/dashboard", params={"tenant_id": "tenant-1"})
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["total_budgets"] == 1
    assert dashboard_payload["total_commitments"] == 20000.0
