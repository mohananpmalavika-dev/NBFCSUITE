import os
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

# Use a temporary file-backed sqlite DB so the test server and requests share the same DB file.
tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
from services.eom.app.main import app


@pytest.mark.asyncio
async def test_geography_crud_and_tree():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        legal_payload = {
            'code': 'LE-GEO-001',
            'name': 'Geography Legal Entity',
        }
        legal_resp = await client.post('/eom/legal-entities', json=legal_payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert legal_resp.status_code == 201, legal_resp.text
        legal_id = legal_resp.json()['id']

        create_payload = {
            'code': 'GEO-001',
            'name': 'Geography Root',
            'node_type': 'region',
            'status': 'active',
            'manager': 'Geo Manager',
            'latitude': '10.0',
            'longitude': '20.0',
            'description': 'Root geography region',
            'legal_entity_id': legal_id,
        }
        create_resp = await client.post('/eom/geography', json=create_payload, headers={'X-User-Roles': 'enterprise.admin'})
        assert create_resp.status_code == 201, create_resp.text
        node = create_resp.json()
        assert node['code'] == 'GEO-001'
        assert node['node_type'] == 'region'
        assert node['manager'] == 'Geo Manager'
        node_id = node['id']

        get_resp = await client.get(f'/eom/geography/{node_id}')
        assert get_resp.status_code == 200
        assert get_resp.json()['name'] == 'Geography Root'

        list_resp = await client.get('/eom/geography')
        assert list_resp.status_code == 200
        list_body = list_resp.json()
        assert list_body['total'] >= 1
        assert any(item['id'] == node_id for item in list_body['items'])

        tree_resp = await client.get('/eom/geography/tree')
        assert tree_resp.status_code == 200
        tree_body = tree_resp.json()
        assert isinstance(tree_body['items'], list)
        assert any(root['id'] == node_id for root in tree_body['items'])

        update_resp = await client.put(f'/eom/geography/{node_id}', json={'manager': 'Updated Manager'}, headers={'X-User-Roles': 'enterprise.admin'})
        assert update_resp.status_code == 200
        assert update_resp.json()['manager'] == 'Updated Manager'

        analytics_resp = await client.get(f'/eom/geography/{node_id}/analytics')
        assert analytics_resp.status_code == 200
        assert analytics_resp.json()['id'] == node_id

        coverage_resp = await client.get(f'/eom/geography/{node_id}/coverage')
        assert coverage_resp.status_code == 200
        assert coverage_resp.json()['id'] == node_id

        search_resp = await client.get('/eom/geography/search-radius', params={'lat': 10.0, 'lon': 20.0, 'radius_km': 50.0})
        assert search_resp.status_code == 200
        assert isinstance(search_resp.json().get('items'), list)
