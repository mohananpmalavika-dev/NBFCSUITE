import os
import tempfile
import asyncio
from services.eom.app.main import app
from httpx import ASGITransport, AsyncClient

print('DATABASE_URL', os.environ.get('DATABASE_URL'))
print('app routes:')
for route in app.routes:
    if hasattr(route, 'path'):
        print(route.path)

async def run_test():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        legal_payload = {'code': 'LE-GEO-001', 'name': 'Geography Legal Entity'}
        legal_resp = await client.post('/eom/legal-entities', json=legal_payload, headers={'X-User-Roles': 'enterprise.admin'})
        print('legal status', legal_resp.status_code, legal_resp.text)
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
        print('create status', create_resp.status_code, create_resp.text)
        node_id = create_resp.json()['id']

        search_resp = await client.get('/eom/geography/search-radius', params={'lat': 10.0, 'lon': 20.0, 'radius_km': 50.0})
        print('search status', search_resp.status_code, search_resp.text)
        print('search url', search_resp.url)

asyncio.run(run_test())
