import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# ensure DB file for AsyncClient
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_brand_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        resp = await client.post('/eom/brands', json={'code': 'BR-001', 'name': 'Brand One'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert resp.status_code == 201
        b = resp.json()
        assert b['code'] == 'BR-001'

        l = await client.get('/eom/brands')
        assert l.status_code == 200
        body = l.json()
        items = body.get('items') if isinstance(body, dict) else body
        assert any(x['code'] == 'BR-001' for x in items)

        gid = b['id']
        g = await client.get(f'/eom/brands/{gid}')
        assert g.status_code == 200

        p = await client.patch(f'/eom/brands/{gid}', json={'name': 'Brand One Updated'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert p.status_code == 200
        assert p.json()['name'] == 'Brand One Updated'

        d = await client.delete(f'/eom/brands/{gid}', headers={'X-User-Roles': 'enterprise.admin'})
        assert d.status_code == 204

        gg = await client.get(f'/eom/brands/{gid}')
        assert gg.status_code == 404
