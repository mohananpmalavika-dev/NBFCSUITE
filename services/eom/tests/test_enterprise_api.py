import os
import tempfile
# Use a temporary file-backed sqlite DB so the test server and requests share the same DB file.
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from fastapi.testclient import TestClient
from services.eom.app.main import app

client = TestClient(app)


def test_create_and_list_enterprise():
    payload = {
        'code': 'ENT-001',
        'name': 'Test Enterprise',
        'display_name': 'TestCo',
        'short_name': 'TC',
        'currency_code': 'INR',
    }

    resp = client.post('/eom/enterprises', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert resp.status_code == 201
    body = resp.json()
    assert body['code'] == 'ENT-001'
    assert body['name'] == 'Test Enterprise'

    list_resp = client.get('/eom/enterprises')
    assert list_resp.status_code == 200
    body = list_resp.json()
    items = body.get('items') if isinstance(body, dict) else body
    assert any(e['code'] == 'ENT-001' for e in items)


def test_update_and_status_and_delete():
    # create
    payload = {'code': 'ENT-002', 'name': 'Second Ent'}
    resp = client.post('/eom/enterprises', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert resp.status_code == 201
    ent = resp.json()
    ent_id = ent['id']

    # patch
    update = {'name': 'Second Enterprise Updated'}
    up = client.patch(f'/eom/enterprises/{ent_id}', json=update, headers={'X-User-Roles': 'enterprise.admin'})
    assert up.status_code == 200
    assert up.json()['name'] == 'Second Enterprise Updated'

    # set status
    st = client.post(f'/eom/enterprises/{ent_id}/status', json={'status': 'suspended'}, headers={'X-User-Roles': 'enterprise.admin'})
    assert st.status_code == 200
    assert st.json()['status'] == 'suspended'

    # health
    h = client.get(f'/eom/enterprises/{ent_id}/health')
    assert h.status_code == 200

    # delete
    d = client.delete(f'/eom/enterprises/{ent_id}', headers={'X-User-Roles': 'enterprise.admin'})
    assert d.status_code == 204
    # ensure gone
    g = client.get(f'/eom/enterprises/{ent_id}')
    assert g.status_code == 404
