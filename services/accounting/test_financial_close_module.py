import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_financial_close_endpoints():
    client = TestClient(app)

    start_response = client.post(
        "/api/v1/close/start",
        json={
            "tenant_id": "tenant-1",
            "cycle_name": "June Close",
            "period": "2026-06",
            "initiated_by": "finance-manager",
        },
    )
    assert start_response.status_code == 200
    payload = start_response.json()
    assert payload["tenant_id"] == "tenant-1"
    assert payload["cycle_name"] == "June Close"
    cycle_id = payload["id"]

    task_response = client.post(
        "/api/v1/close/tasks",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "name": "GL vs AP reconciliation",
            "owner": "recon-team",
            "due_date": "2026-06-30",
            "dependency": "journal-posting",
            "priority": "high",
            "approval_required": True,
        },
    )
    assert task_response.status_code == 200
    task_payload = task_response.json()
    assert task_payload["status"] == "pending"
    assert task_payload["approval_status"] == "pending"

    list_tasks_response = client.get("/api/v1/close/tasks", params={"tenant_id": "tenant-1"})
    assert list_tasks_response.status_code == 200
    assert list_tasks_response.json()["total"] == 1

    reconciliation_response = client.post(
        "/api/v1/close/reconciliation",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "source": "GL",
            "target": "AP",
            "difference_amount": 0.0,
        },
    )
    assert reconciliation_response.status_code == 200
    assert reconciliation_response.json()["status"] == "completed"

    consolidate_response = client.post(
        "/api/v1/close/consolidate",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "entity_from": "Branch A",
            "entity_to": "Region 1",
            "result_summary": "All intercompany flows reconciled",
        },
    )
    assert consolidate_response.status_code == 200
    assert consolidate_response.json()["status"] == "completed"

    eliminate_response = client.post(
        "/api/v1/close/eliminate",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "description": "Intercompany revenue elimination",
            "amount": 25000.0,
        },
    )
    assert eliminate_response.status_code == 200
    assert eliminate_response.json()["status"] == "completed"

    board_response = client.post(
        "/api/v1/close/generate-board-pack",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "report_type": "board_pack",
        },
    )
    assert board_response.status_code == 200
    assert board_response.json()["status"] == "generated"

    rbi_response = client.post(
        "/api/v1/close/generate-rbi-report",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "return_type": "NBS",
        },
    )
    assert rbi_response.status_code == 200
    assert rbi_response.json()["status"] == "generated"

    complete_response = client.post(
        "/api/v1/close/complete",
        json={
            "tenant_id": "tenant-1",
            "cycle_id": cycle_id,
            "completed_by": "cfo",
        },
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "closed"

    dashboard_response = client.get("/api/v1/close/dashboard", params={"tenant_id": "tenant-1"})
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["tenant_id"] == "tenant-1"
