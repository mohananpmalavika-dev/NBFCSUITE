import os
import tempfile
import importlib.util
from pathlib import Path
import asyncio
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / 'accounting_debug.db'
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'

spec = importlib.util.spec_from_file_location('accounting_service_main', Path('app/main.py'))
appmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(appmod)
appmod.Base.metadata.create_all(bind=appmod.engine)

async def main():
    async with AsyncClient(transport=ASGITransport(app=appmod.app), base_url='http://testserver') as client:
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
        print('payment create', voucher_response.status_code, voucher_response.text)
        voucher = voucher_response.json()
        verify_response = await client.post(f"/vouchers/{voucher['id']}/verify", json={'tenant_id': tenant_id, 'performed_by': 'verifier'})
        print('verify', verify_response.status_code, verify_response.text)
        approve_response = await client.post(f"/vouchers/{voucher['id']}/approve", json={'tenant_id': tenant_id, 'performed_by': 'approver'})
        print('approve', approve_response.status_code, approve_response.text)
        post_response = await client.post(f"/vouchers/{voucher['id']}/post", json={'tenant_id': tenant_id, 'performed_by': 'poster'})
        print('payment post', post_response.status_code, post_response.text)

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
        print('receipt create', receipt_response.status_code, receipt_response.text)
        receipt_voucher = receipt_response.json()
        verify_response = await client.post(f"/vouchers/{receipt_voucher['id']}/verify", json={'tenant_id': tenant_id, 'performed_by': 'verifier'})
        approve_response = await client.post(f"/vouchers/{receipt_voucher['id']}/approve", json={'tenant_id': tenant_id, 'performed_by': 'approver'})
        post_response = await client.post(f"/vouchers/{receipt_voucher['id']}/post", json={'tenant_id': tenant_id, 'performed_by': 'poster'})
        print('receipt post', post_response.status_code, post_response.text)
        reverse_response = await client.post(f"/vouchers/{receipt_voucher['id']}/reverse", json={'tenant_id': tenant_id, 'performed_by': 'reverser'})
        print('receipt reverse', reverse_response.status_code, reverse_response.text)

        payment_reverse_response = await client.post(f"/vouchers/{voucher['id']}/reverse", json={'tenant_id': tenant_id, 'performed_by': 'reverser'})
        print('payment reverse', payment_reverse_response.status_code, payment_reverse_response.text)

        ledger_response = await client.get('/gl-ledger', params={'tenant_id': tenant_id})
        print('ledger', ledger_response.status_code, ledger_response.json())

if __name__ == '__main__':
    asyncio.run(main())
