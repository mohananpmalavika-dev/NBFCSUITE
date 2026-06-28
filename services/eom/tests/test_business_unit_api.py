import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# Use a temporary file-backed sqlite DB so the test server and requests share the same DB file.
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_business_unit_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        legal_payload = {
            'code': 'LE-100',
            'name': 'Legal Entity for BU',
        }
        legal_resp = await client.post('/eom/legal-entities', json=legal_payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert legal_resp.status_code == 201, legal_resp.text
        legal_body = legal_resp.json()
        legal_id = legal_body['id']

        bu_payload = {
            'legal_entity_id': legal_id,
            'business_unit_code': 'BU-001',
            'business_unit_name': 'Business Unit One',
            'head': 'BU Head',
        }
        bu_resp = await client.post('/eom/business-units', json=bu_payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert bu_resp.status_code == 201, bu_resp.text
        business_unit = bu_resp.json()
        assert business_unit['business_unit_code'] == 'BU-001'
        assert business_unit['business_unit_name'] == 'Business Unit One'

        bu_id = business_unit['id']

        get_resp = await client.get(f'/eom/business-units/{bu_id}')
        assert get_resp.status_code == 200
        assert get_resp.json()['legal_entity_id'] == legal_id

        list_resp = await client.get('/eom/business-units')
        assert list_resp.status_code == 200
        list_body = list_resp.json()
        assert list_body['total'] >= 1
        assert any(item['id'] == bu_id for item in list_body['items'])

        patch_resp = await client.patch(f'/eom/business-units/{bu_id}', json={'business_unit_name': 'BU One Updated'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert patch_resp.status_code == 200
        assert patch_resp.json()['business_unit_name'] == 'BU One Updated'

        status_resp = await client.patch(f'/eom/business-units/{bu_id}/status', json={'status': 'inactive'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert status_resp.status_code == 200
        assert status_resp.json()['status'] == 'inactive'

        health_resp = await client.get(f'/eom/business-units/{bu_id}/health')
        assert health_resp.status_code == 200
        assert 'health_score' in health_resp.json()

        analytics_resp = await client.get(f'/eom/business-units/{bu_id}/analytics')
        assert analytics_resp.status_code == 200
        assert analytics_resp.json()['id'] == bu_id

        kpis_resp = await client.get(f'/eom/business-units/{bu_id}/kpis')
        assert kpis_resp.status_code == 200
        assert 'kpis' in kpis_resp.json()
