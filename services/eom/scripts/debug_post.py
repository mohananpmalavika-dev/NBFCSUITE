import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from fastapi.testclient import TestClient
from services.eom.app.main import app

client = TestClient(app)

payload = {
    'code': 'ENT-001',
    'name': 'Test Enterprise',
    'display_name': 'TestCo',
    'short_name': 'TC',
    'currency_code': 'INR',
}
resp = client.post('/eom/enterprises', json=payload)
print('status', resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('resp.text:', resp.text)
