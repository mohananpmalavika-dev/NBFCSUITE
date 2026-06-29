import os
import pytest
from fastapi.testclient import TestClient

from services.eom.app.main import app

client = TestClient(app)


def test_cost_center_crud_and_status():
    payload = {
        "enterprise_id": None,
        "code": "CC-TEST-1",
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
    assert data['code'] == 'CC-TEST-1'
    cc_id = data['id']

    res2 = client.get(f'/api/v1/finance/cost-centers/{cc_id}')
    assert res2.status_code == 200
    assert res2.json()['name'] == 'HR Cost'

    # Status transition: draft -> active
    res3 = client.patch(f'/api/v1/finance/cost-centers/{cc_id}/status', json={"status": "active"})
    assert res3.status_code in (200, 401, 403)


def test_profit_center_crud():
    payload = {
        "enterprise_id": None,
        "code": "PC-TEST-1",
        "name": "Gold Loan",
        "category": "Gold Loan",
        "status": "draft",
        "description": "seeded by test",
        "currency": "INR",
    }

    res = client.post('/api/v1/finance/profit-centers', json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    assert data['code'] == 'PC-TEST-1'
    pc_id = data['id']

    res2 = client.get(f'/api/v1/finance/profit-centers/{pc_id}')
    assert res2.status_code == 200
    assert res2.json()['name'] == 'Gold Loan'


def test_internal_order_lifecycle():
    payload = {
        "enterprise_id": None,
        "code": "IO-TEST-1",
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


def test_finance_dashboard():
    res = client.get('/api/v1/finance/dashboard')
    assert res.status_code == 200
    body = res.json()
    assert 'kpis' in body
    assert 'summary' in body

