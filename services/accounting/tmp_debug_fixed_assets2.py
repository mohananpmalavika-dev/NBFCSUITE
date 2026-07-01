import os
import tempfile
import uuid
import importlib.util
import logging
from pathlib import Path
from httpx import AsyncClient, ASGITransport

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_fixed_assets_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path("app/main.py").resolve(),
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)
accounting_main.engine.echo = False
accounting_main.Base.metadata.create_all(bind=accounting_main.engine)

async def main():
    async with AsyncClient(transport=ASGITransport(app=accounting_main.app), base_url="http://testserver") as client:
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
        print('create_status', create_response.status_code)
        print('create_json', create_response.json())
        if create_response.status_code == 200:
            asset = create_response.json()
            get_response = await client.get(f"/api/v1/assets/{asset['id']}", params={"tenant_id": tenant_id})
            print('get_status', get_response.status_code)
            print('get_json', get_response.text)

import asyncio
asyncio.run(main())
