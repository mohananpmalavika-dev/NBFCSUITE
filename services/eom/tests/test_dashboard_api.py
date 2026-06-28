import os
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient

tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_eom_dashboard_hierarchy_search_and_reports():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True) as client:
        enterprise_resp = await client.post(
            "/eom/enterprises",
            json={"code": "ENT-DASH", "name": "Dashboard Enterprise"},
            headers={"X-User-Roles": "enterprise.admin"},
        )
        assert enterprise_resp.status_code == 201, enterprise_resp.text

        legal_resp = await client.post(
            "/eom/legal-entities",
            json={"code": "LE-DASH", "name": "Dashboard Legal Entity"},
            headers={"X-User-Roles": "enterprise.admin"},
        )
        assert legal_resp.status_code == 201, legal_resp.text
        legal_id = legal_resp.json()["id"]

        unit_resp = await client.post(
            "/eom/business-units",
            json={
                "legal_entity_id": legal_id,
                "business_unit_code": "BU-DASH",
                "business_unit_name": "Dashboard Business Unit",
                "head": "Ops Head",
            },
            headers={"X-User-Roles": "enterprise.admin"},
        )
        assert unit_resp.status_code == 201, unit_resp.text

        dashboard_resp = await client.get("/eom/dashboard")
        assert dashboard_resp.status_code == 200
        dashboard = dashboard_resp.json()
        assert dashboard["summary"]["enterprises"] >= 1
        assert dashboard["summary"]["legal_entities"] >= 1
        assert dashboard["summary"]["business_units"] >= 1
        assert any(section["label"] == "Hierarchy explorer" for section in dashboard["workspace"])

        hierarchy_resp = await client.get("/eom/hierarchy")
        assert hierarchy_resp.status_code == 200
        assert isinstance(hierarchy_resp.json()["items"], list)

        search_resp = await client.get("/eom/search", params={"q": "Dashboard"})
        assert search_resp.status_code == 200
        search_items = search_resp.json()["items"]
        assert any(item["type"] == "enterprise" for item in search_items)
        assert any(item["type"] == "business_unit" for item in search_items)

        reports_resp = await client.get("/eom/reports")
        assert reports_resp.status_code == 200
        assert "Organization tree" in reports_resp.json()["items"]
