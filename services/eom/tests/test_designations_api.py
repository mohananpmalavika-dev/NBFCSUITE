import pytest
from starlette.testclient import TestClient

from services.eom.app.main import app

client = TestClient(app)


def test_create_and_fetch_designation():
    payload = {
        "code": "DES-TEST-1",
        "name": "Test Designation 1",
        "status": "active",
        "description": "Designation created by test",
    }

    res = client.post('/eom/designations', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == 'DES-TEST-1'
    assert data['name'] == 'Test Designation 1'
    designation_id = data['id']

    res2 = client.get(f'/eom/designations/{designation_id}')
    assert res2.status_code == 200
    detail = res2.json()
    assert detail['code'] == payload['code']
    assert detail['name'] == payload['name']


def test_list_designations():
    res = client.get('/eom/designations')
    assert res.status_code == 200
    data = res.json()
    assert 'total' in data
    assert 'items' in data
