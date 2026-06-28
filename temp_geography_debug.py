import asyncio
from services.eom.app.main import app
from httpx import ASGITransport, AsyncClient

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver', follow_redirects=True) as client:
        r = await client.get('/eom/geography/search-radius', params={'lat': 10.0, 'lon': 20.0, 'radius_km': 50.0})
        print('status', r.status_code)
        print('url', r.url)
        print('text', r.text)
        print('headers', list(r.headers.items()))

asyncio.run(main())
