import os
import tempfile
from fastapi.testclient import TestClient

# ensure DB file for TestClient
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app

client = TestClient(app)


def test_brand_audit_flow():
    # create brand
    res = client.post('/eom/brands', json={'code': 'B-AUD', 'name': 'Audit Brand'}, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code == 201
    bid = res.json()['id']

    # update brand to create another audit entry
    res = client.patch(f'/eom/brands/{bid}', json={'name': 'Audit Brand Renamed'}, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code == 200

    # fetch audit
    res = client.get(f'/eom/brands/{bid}/audit')
    assert res.status_code == 200
    j = res.json()
    assert j['total'] >= 2
    assert any(e['action'] == 'created' for e in j['items'])
    assert any(e['action'] == 'updated' for e in j['items'])
