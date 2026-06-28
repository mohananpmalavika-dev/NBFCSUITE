import os
import tempfile
# ensure DB file for TestClient
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from fastapi.testclient import TestClient
from services.eom.app.main import app

client = TestClient(app)


def test_brand_crud():
    # create
    resp = client.post('/eom/brands', json={'code': 'BR-001', 'name': 'Brand One'}, headers={'X-User-Roles': 'enterprise.admin'})
    assert resp.status_code == 201
    b = resp.json()
    assert b['code'] == 'BR-001'

    # list
    l = client.get('/eom/brands')
    assert l.status_code == 200
    body = l.json()
    items = body.get('items') if isinstance(body, dict) else body
    assert any(x['code'] == 'BR-001' for x in items)

    # get
    gid = b['id']
    g = client.get(f'/eom/brands/{gid}')
    assert g.status_code == 200

    # patch
    p = client.patch(f'/eom/brands/{gid}', json={'name': 'Brand One Updated'}, headers={'X-User-Roles': 'enterprise.admin'})
    assert p.status_code == 200
    assert p.json()['name'] == 'Brand One Updated'

    # delete
    d = client.delete(f'/eom/brands/{gid}', headers={'X-User-Roles': 'enterprise.admin'})
    assert d.status_code == 204
    # ensure gone
    gg = client.get(f'/eom/brands/{gid}')
    assert gg.status_code == 404
