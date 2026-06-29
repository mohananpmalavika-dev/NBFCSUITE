import asyncio
import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# Use a temporary file-backed sqlite DB so the test server and requests share the same DB file.
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


def test_branch_crud_and_summary_endpoints():
    async def run_test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
            legal_payload = {
                'code': 'LE-BR-001',
                'name': 'Branch Legal Entity',
            }
            legal_resp = await client.post('/eom/legal-entities', json=legal_payload, headers={'X-User-Roles': 'enterprise.admin'})
            assert legal_resp.status_code == 201, legal_resp.text
            legal_id = legal_resp.json()['id']

            bu_payload = {
                'legal_entity_id': legal_id,
                'business_unit_code': 'BU-BR-001',
                'business_unit_name': 'Branch Business Unit',
            }
            bu_resp = await client.post('/eom/business-units', json=bu_payload, headers={'X-User-Roles': 'enterprise.admin'})
            assert bu_resp.status_code == 201, bu_resp.text
            business_unit_id = bu_resp.json()['id']

            payload = {
                'code': 'BR-001',
                'name': 'Main Branch',
                'branch_type': 'retail',
                'status': 'active',
                'manager': 'Branch Manager',
                'business_unit_id': business_unit_id,
                'legal_entity_id': legal_id,
                'city': 'Mumbai',
                'region': 'West',
                'address': '1 Market Street',
                'phone': '9999999999',
                'email': 'branch@example.com',
                'cash_limit': 1000000,
                'vault_limit': 250000,
                'gold_loan_enabled': True,
                'deposit_enabled': True,
                'forex_enabled': False,
            }
            create_resp = await client.post('/eom/branches', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
            assert create_resp.status_code == 201, create_resp.text
            branch = create_resp.json()
            assert branch['code'] == 'BR-001'
            assert branch['name'] == 'Main Branch'
            branch_id = branch['id']

            get_resp = await client.get(f'/eom/branches/{branch_id}')
            assert get_resp.status_code == 200
            assert get_resp.json()['city'] == 'Mumbai'

            list_resp = await client.get('/eom/branches')
            assert list_resp.status_code == 200
            list_body = list_resp.json()
            assert list_body['total'] >= 1
            assert any(item['id'] == branch_id for item in list_body['items'])

            update_resp = await client.put(f'/eom/branches/{branch_id}', json={'manager': 'Updated Manager'}, headers={'X-User-Roles': 'enterprise.admin'})
            assert update_resp.status_code == 200
            assert update_resp.json()['manager'] == 'Updated Manager'

            status_resp = await client.patch(f'/eom/branches/{branch_id}/status', json={'status': 'inactive'}, headers={'X-User-Roles': 'enterprise.admin'})
            assert status_resp.status_code == 200
            assert status_resp.json()['status'] == 'inactive'

            dashboard_resp = await client.get(f'/eom/branches/{branch_id}/dashboard')
            assert dashboard_resp.status_code == 200
            assert 'health_score' in dashboard_resp.json()

            health_resp = await client.get(f'/eom/branches/{branch_id}/health')
            assert health_resp.status_code == 200
            assert health_resp.json()['id'] == branch_id

            analytics_resp = await client.get(f'/eom/branches/{branch_id}/analytics')
            assert analytics_resp.status_code == 200
            assert analytics_resp.json()['id'] == branch_id

    asyncio.run(run_test())
