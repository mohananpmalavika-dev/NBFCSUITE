import asyncio
import os
import tempfile
from pathlib import Path
import importlib.util
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_financial_statements_test_{uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main_financial_statements",
    Path(__file__).resolve().parent / "app" / "main.py",
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)

accounting_main.Base.metadata.create_all(bind=accounting_main.engine)


async def _run_financial_statements_test():
    async with AsyncClient(
        transport=ASGITransport(app=accounting_main.app),
        base_url="http://testserver",
    ) as client:
        tenant_id = "tenant-financial-statements"

        seed_response = await client.post(
            "/api/v1/gl/accounts/seed-defaults",
            json={"tenant_id": tenant_id, "currency": "INR", "financial_year": "2026-27"},
        )
        assert seed_response.status_code == 200

        generate_response = await client.post(
            "/api/v1/financial-statements/generate",
            json={"tenant_id": tenant_id, "statement_type": "balance_sheet", "period": "monthly", "currency": "INR"},
        )
        assert generate_response.status_code == 200
        generated_payload = generate_response.json()
        assert generated_payload["tenant_id"] == tenant_id
        assert generated_payload["statement_type"] == "balance_sheet"
        assert len(generated_payload["lines"]) >= 1

        list_response = await client.get("/api/v1/financial-statements", params={"tenant_id": tenant_id})
        assert list_response.status_code == 200
        list_payload = list_response.json()
        assert list_payload["total"] >= 1

        detail_response = await client.get(
            f"/api/v1/financial-statements/{generated_payload['id']}",
            params={"tenant_id": tenant_id},
        )
        assert detail_response.status_code == 200

        lines_response = await client.get(
            f"/api/v1/financial-statements/{generated_payload['id']}/lines",
            params={"tenant_id": tenant_id},
        )
        assert lines_response.status_code == 200

        ratios_response = await client.get(
            f"/api/v1/financial-statements/{generated_payload['id']}/ratios",
            params={"tenant_id": tenant_id},
        )
        assert ratios_response.status_code == 200

        dashboard_response = await client.get(
            "/api/v1/financial-statements/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert dashboard_response.status_code == 200


def test_financial_statements_endpoints():
    asyncio.run(_run_financial_statements_test())
