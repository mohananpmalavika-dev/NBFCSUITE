import os
import tempfile
from pathlib import Path
import importlib.util
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_fixed_assets_test_{uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path(__file__).resolve().parent / "app" / "main.py",
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)

accounting_main.Base.metadata.create_all(bind=accounting_main.engine)


async def _asset_lifecycle():
    async with AsyncClient(
        transport=ASGITransport(app=accounting_main.app),
        base_url="http://testserver",
    ) as client:
        tenant_id = "tenant-local-assets"

        create_response = await client.post(
            "/api/v1/assets/",
            json={
                "tenant_id": tenant_id,
                "asset_code": "AST-2026-BR101-000001",
                "asset_name": "Branch ATM Machine",
                "asset_category": "atm",
                "asset_class": "equipment",
                "asset_type": "hardware",
                "location": "BR101",
                "branch_id": "BR101",
                "department_id": "operations",
                "acquisition_cost": 150000.0,
                "book_value": 150000.0,
                "currency": "INR",
                "lifecycle_stage": "planning",
                "created_by": "tester",
            },
        )
        assert create_response.status_code == 200
        asset = create_response.json()
        assert asset["asset_code"] == "AST-2026-BR101-000001"
        assert asset["status"] == "draft"

        get_response = await client.get(f"/api/v1/assets/{asset['id']}", params={"tenant_id": tenant_id})
        assert get_response.status_code == 200
        assert get_response.json()["asset_name"] == "Branch ATM Machine"

        capitalize_response = await client.post(
            f"/api/v1/assets/{asset['id']}/capitalize",
            params={"tenant_id": tenant_id},
            json={"capitalization_date": "2026-08-01T00:00:00"},
        )
        assert capitalize_response.status_code == 200
        funded = capitalize_response.json()
        assert funded["status"] == "capitalized"
        assert funded["net_book_value"] == 150000.0

        depreciate_response = await client.post(
            f"/api/v1/assets/{asset['id']}/depreciate",
            params={"tenant_id": tenant_id},
            json={"depreciation_amount": 15000.0, "depreciation_method": "straight_line", "period": "2026-27"},
        )
        assert depreciate_response.status_code == 200
        depreciated = depreciate_response.json()
        assert depreciated["accumulated_depreciation"] == 15000.0
        assert depreciated["net_book_value"] == 135000.0

        transfer_response = await client.post(
            f"/api/v1/assets/{asset['id']}/transfer",
            params={"tenant_id": tenant_id},
            json={"to_location": "BR102", "to_department_id": "branch_ops", "reason": "branch relocation"},
        )
        assert transfer_response.status_code == 200
        transferred = transfer_response.json()
        assert transferred["location"] == "BR102"
        assert transferred["department_id"] == "branch_ops"

        verify_response = await client.post(
            f"/api/v1/assets/{asset['id']}/verify",
            params={"tenant_id": tenant_id},
            json={"verified_by": "inspector", "remarks": "Asset inspected and approved"},
        )
        assert verify_response.status_code == 200
        verified = verify_response.json()
        assert verified["status"] == "verified"

        dispose_response = await client.post(
            f"/api/v1/assets/{asset['id']}/dispose",
            params={"tenant_id": tenant_id},
            json={"disposal_reason": "end of useful life", "disposal_value": 10000.0},
        )
        assert dispose_response.status_code == 200
        disposed = dispose_response.json()
        assert disposed["status"] == "disposed"

        dashboard_response = await client.get("/api/v1/assets/dashboard", params={"tenant_id": tenant_id})
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert dashboard["total_assets"] == 1
        assert dashboard["total_net_book_value"] == 135000.0
        assert dashboard["assets_by_status"]["disposed"] == 1


def test_asset_lifecycle():
    import asyncio

    asyncio.run(_asset_lifecycle())
