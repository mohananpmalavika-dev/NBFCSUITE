import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path for test execution
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.eom.app.main import app


client = TestClient(app)


def test_cost_center_crud_and_status():
    code = f"CC-TEST-{uuid.uuid4().hex[:8]}"
    payload = {
        "enterprise_id": None,
        "code": code,
        "name": "HR Cost",
        "category": "HR",
        "status": "draft",
        "description": "seeded by test",
        "budget_owner": "finance",
        "currency": "INR",
    }

    res = client.post('/api/v1/finance/cost-centers', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == code
    cc_id = data['id']

    list_res = client.get('/api/v1/finance/cost-centers')
    assert list_res.status_code == 200
    assert any(item['id'] == cc_id for item in list_res.json()['items'])

    res2 = client.get(f'/api/v1/finance/cost-centers/{cc_id}')
    assert res2.status_code == 200
    assert res2.json()['name'] == 'HR Cost'

    # Status transition: draft -> active
    res3 = client.patch(f'/api/v1/finance/cost-centers/{cc_id}/status', json={"status": "active"})
    assert res3.status_code in (200, 401, 403)


def test_profit_center_crud():
    code = f"PC-TEST-{uuid.uuid4().hex[:8]}"
    payload = {
        "enterprise_id": None,
        "code": code,
        "name": "Gold Loan",
        "category": "Gold Loan",
        "status": "draft",
        "description": "seeded by test",
        "currency": "INR",
    }

    res = client.post('/api/v1/finance/profit-centers', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == code
    pc_id = data['id']

    list_res = client.get('/api/v1/finance/profit-centers')
    assert list_res.status_code == 200
    assert any(item['id'] == pc_id for item in list_res.json()['items'])

    res2 = client.get(f'/api/v1/finance/profit-centers/{pc_id}')
    assert res2.status_code == 200
    assert res2.json()['name'] == 'Gold Loan'


def test_internal_order_lifecycle():
    code = f"IO-TEST-{uuid.uuid4().hex[:8]}"
    payload = {
        "enterprise_id": None,
        "code": code,
        "name": "ERP Implementation",
        "description": "seeded by test",
        "status": "draft",
    }

    res = client.post('/api/v1/finance/internal-orders', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    io_id = data['id']
    assert data['status'] == 'draft'

    res2 = client.patch(f'/api/v1/finance/internal-orders/{io_id}/status', json={"status": "approved"})
    assert res2.status_code in (200, 401, 403)


def test_budget_crud():
    payload = {
        "enterprise_id": None,
        "year": 2026,
        "status": "original",
        "original_total": 1200000,
        "revised_total": 1250000,
        "committed_total": 250000,
        "actual_total": 175000,
        "forecast_total": 1180000,
        "currency": "INR",
    }

    res = client.post('/api/v1/finance/budgets', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    budget_id = data['id']
    assert data['year'] == 2026

    list_res = client.get('/api/v1/finance/budgets?year=2026')
    assert list_res.status_code == 200
    assert any(item['id'] == budget_id for item in list_res.json()['items'])

    get_res = client.get(f'/api/v1/finance/budgets/{budget_id}')
    assert get_res.status_code == 200
    assert get_res.json()['original_total'] == 1200000


def test_finance_dashboard():
    res = client.get('/api/v1/finance/dashboard')
    assert res.status_code == 200
    body = res.json()
    assert 'kpis' in body
    assert 'summary' in body

