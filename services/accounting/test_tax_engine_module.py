import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_tax_engine_endpoints():
    client = TestClient(app)

    calculate_response = client.post(
        "/api/v1/tax/calculate",
        json={"tenant_id": "tenant-1", "tax_type": "CGST", "base_amount": 1000.0},
    )
    assert calculate_response.status_code == 200
    calculate_payload = calculate_response.json()
    assert calculate_payload["tax_type"] == "CGST"
    assert calculate_payload["tax_amount"] == 90.0

    gst_return_response = client.post(
        "/api/v1/tax/gst/returns",
        json={
            "tenant_id": "tenant-1",
            "return_type": "GSTR-3B",
            "period": "2026-04",
            "details": {"sales": 100000.0, "tax": 18000.0},
        },
    )
    assert gst_return_response.status_code == 200
    assert gst_return_response.json()["return_type"] == "GSTR-3B"
    assert gst_return_response.json()["status"] == "filed"

    tds_return_response = client.post(
        "/api/v1/tax/tds/returns",
        json={
            "tenant_id": "tenant-1",
            "return_type": "24Q",
            "period": "2026-Q1",
            "details": {"tax_deducted": 2500.0},
        },
    )
    assert tds_return_response.status_code == 200
    assert tds_return_response.json()["return_type"] == "24Q"
    assert tds_return_response.json()["status"] == "filed"

    ledger_response = client.get("/api/v1/tax/ledger", params={"tenant_id": "tenant-1"})
    assert ledger_response.status_code == 200
    assert ledger_response.json()["entries"] == []

    reconciliation_response = client.post(
        "/api/v1/tax/reconciliation",
        json={
            "tenant_id": "tenant-1",
            "reference_id": "inv-001",
            "reported_amount": 1000.0,
            "recorded_amount": 980.0,
        },
    )
    assert reconciliation_response.status_code == 200
    assert reconciliation_response.json()["difference_amount"] == 20.0

    einvoice_response = client.post(
        "/api/v1/tax/einvoice",
        json={
            "tenant_id": "tenant-1",
            "invoice_id": "INV-001",
            "invoice_date": "2026-05-01T00:00:00",
            "amount": 50000.0,
        },
    )
    assert einvoice_response.status_code == 200
    assert einvoice_response.json()["status"] == "generated"
    assert einvoice_response.json()["irn"].startswith("IRN-")

    ewaybill_response = client.post(
        "/api/v1/tax/ewaybill",
        json={
            "tenant_id": "tenant-1",
            "invoice_id": "INV-001",
            "vehicle_number": "TN01AB1234",
            "transporter_name": "TransCo",
            "from_place": "Chennai",
            "to_place": "Bengaluru",
            "distance_km": 330.0,
        },
    )
    assert ewaybill_response.status_code == 200
    assert ewaybill_response.json()["ewaybill_number"].startswith("EWB-")

    compliance_response = client.get("/api/v1/tax/compliance", params={"tenant_id": "tenant-1"})
    assert compliance_response.status_code == 200
    assert compliance_response.json()["gst_compliance"] == "98%"

    dashboard_response = client.get("/api/v1/tax/dashboard", params={"tenant_id": "tenant-1"})
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["total_gst_transactions"] == 0
