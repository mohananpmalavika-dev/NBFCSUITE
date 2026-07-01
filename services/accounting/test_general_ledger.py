import asyncio
import os
import tempfile
from pathlib import Path
import importlib.util
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_general_ledger_test_{uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path(__file__).resolve().parent / "app" / "main.py",
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)

accounting_main.Base.metadata.create_all(bind=accounting_main.engine)


async def _run_general_ledger_test():
    async with AsyncClient(
        transport=ASGITransport(app=accounting_main.app),
        base_url="http://testserver",
    ) as client:
        tenant_id = "tenant-general-ledger"

        seed_response = await client.post(
            "/api/v1/gl/accounts/seed-defaults",
            json={"tenant_id": tenant_id, "currency": "INR", "financial_year": "2026-27"},
        )
        assert seed_response.status_code == 200

        dashboard_response = await client.get("/api/v1/gl/ledger/dashboard", params={"tenant_id": tenant_id})
        assert dashboard_response.status_code == 200
        dashboard_payload = dashboard_response.json()
        assert "kpis" in dashboard_payload
        assert "summary" in dashboard_payload
        assert dashboard_payload["kpis"]["total_accounts"] >= 20

        balances_response = await client.get("/api/v1/gl/ledger/balances", params={"tenant_id": tenant_id})
        assert balances_response.status_code == 200
        balances_payload = balances_response.json()
        assert "items" in balances_payload

        entries_response = await client.get("/api/v1/gl/ledger/entries", params={"tenant_id": tenant_id})
        assert entries_response.status_code == 200
        entries_payload = entries_response.json()
        assert "items" in entries_payload

        health_response = await client.get("/api/v1/gl/ledger/health", params={"tenant_id": tenant_id})
        assert health_response.status_code == 200
        assert health_response.json()["tenant_id"] == tenant_id


def test_general_ledger_endpoints():
    asyncio.run(_run_general_ledger_test())
