import os
from pathlib import Path
import tempfile
import importlib.util
import asyncio
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / 'accounting_service_test.db'
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'

spec = importlib.util.spec_from_file_location('accounting_service_main', Path('app/main.py'))
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)
accounting_main.Base.metadata.create_all(bind=accounting_main.engine)

async def debug():
    async with AsyncClient(transport=ASGITransport(app=accounting_main.app), base_url='http://testserver') as client:
        tenant_id = 'tenant-local-accounting'
        cash_response = await client.post('/gl-accounts', json={
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
        cash_account = cash_response.json()
        expense_response = await client.post('/gl-accounts', json={
            'tenant_id': tenant_id,
            'account_code': '510000_BRANCH_EXP',
            'account_name': 'Branch Operating Expense',
            'account_type': 'expense',
            'category': 'Expenses',
        })
        expense_account = expense_response.json()
        voucher_response = await client.post('/vouchers', json={
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
        assert voucher_response.status_code == 200
        voucher = voucher_response.json()
        await client.post(f"/vouchers/{voucher['id']}/verify", json={'tenant_id': tenant_id, 'performed_by': 'verifier'})
        await client.post(f"/vouchers/{voucher['id']}/approve", json={'tenant_id': tenant_id, 'performed_by': 'approver'})
        await client.post(f"/vouchers/{voucher['id']}/post", json={'tenant_id': tenant_id, 'performed_by': 'poster'})

        receipt_response = await client.post('/vouchers', json={
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
        assert receipt_response.status_code == 200
        receipt_voucher = receipt_response.json()
        await client.post(f"/vouchers/{receipt_voucher['id']}/verify", json={'tenant_id': tenant_id, 'performed_by': 'verifier'})
        await client.post(f"/vouchers/{receipt_voucher['id']}/approve", json={'tenant_id': tenant_id, 'performed_by': 'approver'})
        await client.post(f"/vouchers/{receipt_voucher['id']}/post", json={'tenant_id': tenant_id, 'performed_by': 'poster'})
        await client.post(f"/vouchers/{receipt_voucher['id']}/reverse", json={'tenant_id': tenant_id, 'performed_by': 'reverser'})

        ledger_response = await client.get('/gl-ledger', params={'tenant_id': tenant_id})
        print('ledger', ledger_response.json())

asyncio.run(debug())
