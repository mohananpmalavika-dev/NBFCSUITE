import pytest
from starlette.testclient import TestClient

from services.eom.app.main import app

client = TestClient(app)


def test_create_and_fetch_team():
    # create a section first to attach to team
    sec_payload = {"code": "SEC-FOR-TEAM-1", "name": "Section for Team", "department": "Ops", "status": "active"}
    res_sec = client.post('/eom/sections', json=sec_payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert res_sec.status_code in (200, 201)
    section_id = res_sec.json()['id']

    payload = {
        "code": "TEAM-TEST-1",
        "name": "Test Team 1",
        "section_id": section_id,
        "team_type": "Permanent Team",
        "status": "active",
    }

    res = client.post('/eom/teams', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == payload['code']
    assert data['name'] == payload['name']
    team_id = data['id']

    res2 = client.get(f'/eom/teams/{team_id}')
    assert res2.status_code == 200
    detail = res2.json()
    assert detail['code'] == payload['code']
    assert detail['name'] == payload['name']


def test_list_teams():
    res = client.get('/eom/teams')
    assert res.status_code == 200
    data = res.json()
    assert 'total' in data
    assert 'items' in data
