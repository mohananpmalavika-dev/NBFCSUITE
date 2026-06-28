import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# ensure DB file for AsyncClient
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_brand_audit_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        res = await client.post('/eom/brands', json={'code': 'B-AUD', 'name': 'Audit Brand'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert res.status_code == 201
        bid = res.json()['id']

        res = await client.patch(f'/eom/brands/{bid}', json={'name': 'Audit Brand Renamed'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert res.status_code == 200

        res = await client.get(f'/eom/brands/{bid}/audit')
        assert res.status_code == 200
        j = res.json()
        assert j['total'] >= 2
        assert any(e['action'] == 'created' for e in j['items'])
        assert any(e['action'] == 'updated' for e in j['items'])
