import pytest
from starlette.testclient import TestClient

from services.eom.app.main import app

client = TestClient(app)


def test_create_and_fetch_section():
    payload = {
        "code": "SEC-TEST-1",
        "name": "Test Section 1",
        "department": "Test Dept",
        "status": "active",
    }

    res = client.post('/eom/sections', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == payload['code']
    assert data['name'] == payload['name']
    section_id = data['id']

    res2 = client.get(f'/eom/sections/{section_id}')
    assert res2.status_code == 200
    detail = res2.json()
    assert detail['code'] == payload['code']
    assert detail['name'] == payload['name']


def test_list_sections():
    res = client.get('/eom/sections')
    assert res.status_code == 200
    data = res.json()
    assert 'total' in data
    assert 'items' in data
