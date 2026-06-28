import os
import tempfile
from fastapi.testclient import TestClient
from services.eom.app.main import app

# ensure DB file for TestClient
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"

client = TestClient(app)


def test_legal_entity_crud():
    payload = {
        'code': 'LE-001',
        'name': 'Legal One',
        'display_name': 'Legal One Pvt Ltd',
    }
    # create (needs role header)
    res = client.post('/eom/legal-entities', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code == 201, res.text
    body = res.json()
    assert body['code'] == 'LE-001'

    le_id = body['id']

    # get
    res = client.get(f'/eom/legal-entities/{le_id}', headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code == 200
    assert res.json()['name'] == 'Legal One'

    # list
    res = client.get('/eom/legal-entities')
    assert res.status_code == 200
    js = res.json()
    assert js['total'] >= 1

    # patch
    res = client.patch(f'/eom/legal-entities/{le_id}', json={'name': 'Legal One Renamed'}, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code == 200
    assert res.json()['name'] == 'Legal One Renamed'

    # delete
    res = client.delete(f'/eom/legal-entities/{le_id}', headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code == 204
