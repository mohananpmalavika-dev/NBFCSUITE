import os
import tempfile
import uuid
import importlib.util
from pathlib import Path
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_fixed_assets_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path("app/main.py").resolve(),
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)
accounting_main.Base.metadata.create_all(bind=accounting_main.engine)

async def main():
    async with AsyncClient(transport=ASGITransport(app=accounting_main.app), base_url="http://testserver") as client:
        tenant_id = "tenant-local-assets"

        def print_resp(name, resp):
            print(f"{name}: status={resp.status_code}")
            try:
                print(resp.json())
            except Exception:
                print(resp.text)
            print("---")

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
        print_resp('create', create_response)
        asset = create_response.json()

        get_response = await client.get(f"/api/v1/assets/{asset['id']}", params={"tenant_id": tenant_id})
        print_resp('get', get_response)

        capitalize_response = await client.post(
            f"/api/v1/assets/{asset['id']}/capitalize",
            params={"tenant_id": tenant_id},
            json={"capitalization_date": "2026-08-01T00:00:00"},
        )
        print_resp('capitalize', capitalize_response)
        if capitalize_response.status_code != 200:
            return

        depreciate_response = await client.post(
            f"/api/v1/assets/{asset['id']}/depreciate",
            params={"tenant_id": tenant_id},
            json={"depreciation_amount": 15000.0, "depreciation_method": "straight_line", "period": "2026-27"},
        )
        print_resp('depreciate', depreciate_response)
        if depreciate_response.status_code != 200:
            return

        transfer_response = await client.post(
            f"/api/v1/assets/{asset['id']}/transfer",
            params={"tenant_id": tenant_id},
            json={"to_location": "BR102", "to_department_id": "branch_ops", "reason": "branch relocation"},
        )
        print_resp('transfer', transfer_response)
        if transfer_response.status_code != 200:
            return

        verify_response = await client.post(
            f"/api/v1/assets/{asset['id']}/verify",
            params={"tenant_id": tenant_id},
            json={"verified_by": "inspector", "remarks": "Asset inspected and approved"},
        )
        print_resp('verify', verify_response)
        if verify_response.status_code != 200:
            return

        dispose_response = await client.post(
            f"/api/v1/assets/{asset['id']}/dispose",
            params={"tenant_id": tenant_id},
            json={"disposal_reason": "end of useful life", "disposal_value": 10000.0},
        )
        print_resp('dispose', dispose_response)
        if dispose_response.status_code != 200:
            return

        dashboard_response = await client.get("/api/v1/assets/dashboard", params={"tenant_id": tenant_id})
        print_resp('dashboard', dashboard_response)

import asyncio
asyncio.run(main())
