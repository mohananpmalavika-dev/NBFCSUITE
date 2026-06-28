import asyncio
import os
import tempfile
import importlib.util
from pathlib import Path
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / 'accounting_service_test.db'
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'

spec = importlib.util.spec_from_file_location('accounting_service_main', Path('c:/NBFCSUITE/services/accounting/app/main.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.Base.metadata.create_all(bind=module.engine)

async def run():
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url='http://testserver') as client:
        tenant_id = 'tenant-local-accounting'
        resp = await client.post('/gl-accounts', json={
            'tenant_id': tenant_id,
            'account_code': '111000_BRANCH_CASH',
            'account_name': 'Branch Cash',
            'account_type': 'asset',
            'category': 'Assets',
            'currency': 'INR',
            'branch_specific': 'true',
            'posting_allowed': 'true',
            'financial_year': '2026-27',
        })
        print('cash status', resp.status_code, resp.text)
        cash_account = resp.json()
        resp = await client.post('/gl-accounts', json={
            'tenant_id': tenant_id,
            'account_code': '510000_BRANCH_EXP',
            'account_name': 'Branch Operating Expense',
            'account_type': 'expense',
            'category': 'Expenses',
        })
        print('expense status', resp.status_code, resp.text)
        expense_account = resp.json()
        # receipt voucher
        resp = await client.post('/vouchers', json={
            'tenant_id': tenant_id,
            'voucher_type': 'receipt',
            'description': 'Customer cash receipt',
            'reference': 'RCPT-001',
            'branch_id': 'branch-001',
            'payment_mode': 'upi',
            'payment_reference': 'UPI-REF-1234',
            'payment_details': {'note': 'Receipt via UPI'},
            'created_by': 'tester',
            'lines': [
                {'gl_account_id': expense_account['id'], 'debit': 250.0, 'credit': 0.0},
                {'gl_account_id': cash_account['id'], 'debit': 0.0, 'credit': 250.0},
            ],
        })
        print('receipt create', resp.status_code, resp.text)
        voucher = resp.json()
        for action in ['verify','approve','post','reverse']:
            resp = await client.post(f"/vouchers/{voucher['id']}/{action}", json={'tenant_id': tenant_id, 'performed_by': action})
            print(action, resp.status_code, resp.text)
        # payment voucher
        resp = await client.post('/vouchers', json={
            'tenant_id': tenant_id,
            'voucher_type': 'payment',
            'description': 'Branch utility payment',
            'reference': 'UTIL-001',
            'branch_id': 'branch-001',
            'created_by': 'tester',
            'lines': [
                {'gl_account_id': expense_account['id'], 'debit': 250.0, 'credit': 0.0},
                {'gl_account_id': cash_account['id'], 'debit': 0.0, 'credit': 250.0},
            ],
        })
        print('payment create', resp.status_code, resp.text)
        voucher2 = resp.json()
        for action in ['verify','approve','post','reverse']:
            resp = await client.post(f"/vouchers/{voucher2['id']}/{action}", json={'tenant_id': tenant_id, 'performed_by': action})
            print(action+'2', resp.status_code, resp.text)
        resp = await client.get('/gl-ledger', params={'tenant_id': tenant_id})
        print('ledger rows', resp.status_code, resp.text)

asyncio.run(run())
