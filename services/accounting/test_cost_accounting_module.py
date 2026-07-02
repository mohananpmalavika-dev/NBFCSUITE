import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_cost_center_allocation_and_profitability_flow():
    client = TestClient(app)

    cost_center_response = client.post(
        "/api/v1/cost-centers",
        json={
            "tenant_id": "tenant-1",
            "code": "IT-01",
            "name": "Corporate IT",
            "cost_center_type": "IT",
            "budget_amount": 150000.0,
            "actual_amount": 120000.0,
        },
    )
    assert cost_center_response.status_code == 200
    cost_center_id = cost_center_response.json()["id"]

    profit_center_response = client.post(
        "/api/v1/profit-centers",
        json={
            "tenant_id": "tenant-1",
            "code": "PL-01",
            "name": "Personal Loans",
            "profit_center_type": "loan",
            "manager": "Asha",
        },
    )
    assert profit_center_response.status_code == 200

    allocation_response = client.post(
        "/api/v1/allocations/run",
        json={
            "tenant_id": "tenant-1",
            "source_cost_center_id": cost_center_id,
            "amount": 100000.0,
            "allocation_rule_type": "percentage",
            "receivers": [
                {"receiver_id": "branch-001", "receiver_name": "North Branch", "receiver_type": "branch", "allocation_percentage": 100.0}
            ],
        },
    )
    assert allocation_response.status_code == 200
    assert allocation_response.json()["results"][0]["allocated_amount"] == 100000.0

    products_response = client.get("/api/v1/profitability/products", params={"tenant_id": "tenant-1"})
    assert products_response.status_code == 200
    assert products_response.json()["items"][0]["metric_type"] == "product"

    customers_response = client.get("/api/v1/profitability/customers", params={"tenant_id": "tenant-1"})
    assert customers_response.status_code == 200
    assert customers_response.json()["items"][0]["metric_type"] == "customer"

    branches_response = client.get("/api/v1/profitability/branches", params={"tenant_id": "tenant-1"})
    assert branches_response.status_code == 200
    assert branches_response.json()["items"][0]["metric_type"] == "branch"

    dashboard_response = client.get("/api/v1/cost/dashboard", params={"tenant_id": "tenant-1"})
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["total_cost_centers"] == 1

    simulation_response = client.post(
        "/api/v1/cost/simulate",
        json={"tenant_id": "tenant-1", "adjustment_percent": 10.0},
    )
    assert simulation_response.status_code == 200
    assert simulation_response.json()["projected_total_cost"] >= 100000.0

    reports_response = client.get("/api/v1/cost/reports", params={"tenant_id": "tenant-1"})
    assert reports_response.status_code == 200
    assert reports_response.json()["total_reports"] >= 1
