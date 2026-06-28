import os
import tempfile
import asyncio

tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"

from services.eom.app.main import app
from httpx import ASGITransport, AsyncClient

print('DATABASE_URL', os.environ['DATABASE_URL'])
print('app routes count', len([route for route in app.routes if hasattr(route, 'path')]))
for route in app.routes:
    if hasattr(route, 'path') and route.path.startswith('/eom/geography'):
        print('ROUTE', route.path)

async def run_test():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        search_resp = await client.get('/eom/geography/search-radius', params={'lat': 10.0, 'lon': 20.0, 'radius_km': 50.0})
        print('search status', search_resp.status_code)
        print('search text', search_resp.text)
        print('search url', search_resp.url)

asyncio.run(run_test())
