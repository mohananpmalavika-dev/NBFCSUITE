import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# Use a temporary file-backed sqlite DB so the test server and requests share the same DB file.
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_create_and_list_enterprise():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        payload = {
            'code': 'ENT-001',
            'name': 'Test Enterprise',
            'display_name': 'TestCo',
            'short_name': 'TC',
            'currency_code': 'INR',
        }

        resp = await client.post('/eom/enterprises', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert resp.status_code == 201
        body = resp.json()
        assert body['code'] == 'ENT-001'
        assert body['name'] == 'Test Enterprise'

        list_resp = await client.get('/eom/enterprises')
        assert list_resp.status_code == 200
        body = list_resp.json()
        items = body.get('items') if isinstance(body, dict) else body
        assert any(e['code'] == 'ENT-001' for e in items)


@pytest.mark.asyncio
async def test_update_and_status_and_delete():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        payload = {'code': 'ENT-002', 'name': 'Second Ent'}
        resp = await client.post('/eom/enterprises', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert resp.status_code == 201
        ent = resp.json()
        ent_id = ent['id']

        update = {'name': 'Second Enterprise Updated'}
        up = await client.patch(f'/eom/enterprises/{ent_id}', json=update, headers={'X-User-Roles': 'enterprise.admin'})
        assert up.status_code == 200
        assert up.json()['name'] == 'Second Enterprise Updated'

        st = await client.post(f'/eom/enterprises/{ent_id}/status', json={'status': 'suspended'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert st.status_code == 200
        assert st.json()['status'] == 'suspended'

        h = await client.get(f'/eom/enterprises/{ent_id}/health')
        assert h.status_code == 200

        d = await client.delete(f'/eom/enterprises/{ent_id}', headers={'X-User-Roles': 'enterprise.admin'})
        assert d.status_code == 204

        g = await client.get(f'/eom/enterprises/{ent_id}')
        assert g.status_code == 404
