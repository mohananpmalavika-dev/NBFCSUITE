import pytest
from starlette.testclient import TestClient

from services.eom.app.main import app

client = TestClient(app)


def create_position(code, title, status='open', reports_to=None):
    payload = {"code": code, "title": title, "status": status}
    if reports_to:
        payload['reports_to_position_id'] = reports_to
    res = client.post('/eom/positions', json=payload, headers={'X-User-Roles': 'enterprise.admin'})
    assert res.status_code in (200, 201)
    return res.json()


def test_position_aux_endpoints():
    # create a small hierarchy: parent -> child1 -> child2
    parent = create_position('PARENT-1', 'Parent Position', status='open')
    child1 = create_position('CHILD-1', 'Child One', status='filled', reports_to=parent['id'])
    child2 = create_position('CHILD-2', 'Child Two', status='open', reports_to=child1['id'])

    # successors non-recursive should return only direct reports of parent
    res = client.get(f"/eom/positions/{parent['id']}/successors")
    assert res.status_code == 200
    body = res.json()
    assert body['position_id'] == parent['id']
    assert isinstance(body['successors'], list)
    assert len(body['successors']) == 1

    # successors recursive should return both descendants
    res2 = client.get(f"/eom/positions/{parent['id']}/successors?recursive=true")
    assert res2.status_code == 200
    body2 = res2.json()
    assert len(body2['successors']) == 2

    # health for parent: total positions 3, filled positions 1
    res3 = client.get(f"/eom/positions/{parent['id']}/health")
    assert res3.status_code == 200
    h = res3.json()
    assert h['total_positions'] == 3
    assert h['filled_positions'] == 1
    assert h['health_score'] == pytest.approx(1/3)

    # budget endpoint returns open_positions count (parent and child2 are open)
    res4 = client.get(f"/eom/positions/{parent['id']}/budget")
    assert res4.status_code == 200
    b = res4.json()
    assert b['open_positions'] == 2
