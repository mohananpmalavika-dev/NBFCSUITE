import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# ensure DB file for TestClient
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"

from services.eom.app.main import app


@pytest.mark.asyncio
async def test_legal_entity_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        payload = {
            'code': 'LE-001',
            'name': 'Legal One',
            'display_name': 'Legal One Pvt Ltd',
        }
        # create (needs role header)
        res = await client.post('/eom/legal-entities', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert res.status_code == 201, res.text
        body = res.json()
        assert body['code'] == 'LE-001'

        le_id = body['id']

        # get
        res = await client.get(f'/eom/legal-entities/{le_id}', headers={'X-User-Roles': 'enterprise.admin'})
        assert res.status_code == 200
        assert res.json()['name'] == 'Legal One'

        # list
        res = await client.get('/eom/legal-entities')
        assert res.status_code == 200
        js = res.json()
        assert js['total'] >= 1

        # patch
        res = await client.patch(f'/eom/legal-entities/{le_id}', json={'name': 'Legal One Renamed'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert res.status_code == 200
        assert res.json()['name'] == 'Legal One Renamed'

        # delete
        res = await client.delete(f'/eom/legal-entities/{le_id}', headers={'X-User-Roles': 'enterprise.admin'})
        assert res.status_code == 204
