import pytest
from fastapi.testclient import TestClient

from services.eom.app.main import app

client = TestClient(app)


def test_create_and_fetch_position():
    payload = {
        "code": "POS-TEST-1",
        "title": "Test Position 1",
        "status": "open",
        "description": "Position created by test",
    }

    res = client.post('/eom/positions', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == 'POS-TEST-1'
    assert data['title'] == 'Test Position 1'
    position_id = data['id']

    res2 = client.get(f'/eom/positions/{position_id}')
    assert res2.status_code == 200
    detail = res2.json()
    assert detail['code'] == payload['code']
    assert detail['title'] == payload['title']


def test_list_positions():
    res = client.get('/eom/positions')
    assert res.status_code == 200
    data = res.json()
    assert 'total' in data
    assert 'items' in data
