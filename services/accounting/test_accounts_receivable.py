import os
import tempfile
from pathlib import Path
import importlib.util
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_ar_service_test_{uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path(__file__).resolve().parent / "services" / "accounting" / "app" / "main.py",
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)

accounting_main.Base.metadata.create_all(bind=accounting_main.engine)


async def test_ar_receivable_lifecycle():
    async with AsyncClient(
        transport=ASGITransport(app=accounting_main.app),
        base_url="http://testserver",
    ) as client:
        tenant_id = "tenant-local-ar"

        receivable_response = await client.post(
            "/api/v1/ar/receivables",
            json={
                "tenant_id": tenant_id,
                "customer_id": "customer-001",
                "receivable_number": "RCV-001",
                "product_type": "loan",
                "amount": 1000.0,
                "currency": "INR",
                "due_date": "2026-07-31T00:00:00",
                "metadata": {"loan_id": "loan-123"},
                "created_by": "tester",
            },
        )
        assert receivable_response.status_code == 200
        receivable = receivable_response.json()
        assert receivable["receivable_number"] == "RCV-001"
        assert receivable["status"] == "pending"

        receipt_response = await client.post(
            "/api/v1/ar/receipts",
            json={
                "tenant_id": tenant_id,
                "customer_id": "customer-001",
                "receipt_number": "RCT-001",
                "payment_method": "upi",
                "amount": 500.0,
                "currency": "INR",
                "metadata": {"payment_reference": "UPI-123"},
                "created_by": "tester",
            },
        )
        assert receipt_response.status_code == 200
        receipt = receipt_response.json()
        assert receipt["amount"] == 500.0

        allocate_response = await client.post(
            "/api/v1/ar/allocate",
            json={
                "tenant_id": tenant_id,
                "items": [
                    {
                        "receipt_id": receipt["id"],
                        "receivable_id": receivable["id"],
                        "amount": 500.0,
                    }
                ],
            },
        )
        assert allocate_response.status_code == 200
        allocation = allocate_response.json()
        assert allocation["allocations_created"] == 1
        assert allocation["allocated_amount"] == 500.0

        ledger_response = await client.get(
            "/api/v1/ar/ledger",
            params={"tenant_id": tenant_id, "customer_id": "customer-001"},
        )
        assert ledger_response.status_code == 200
        ledger = ledger_response.json()
        assert ledger["outstanding_balance"] == 500.0

        dashboard_response = await client.get(
            "/api/v1/ar/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert dashboard["total_receivables"] == 1
        assert dashboard["total_receipts"] == 500.0
