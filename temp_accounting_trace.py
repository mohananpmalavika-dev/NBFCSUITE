import asyncio
import os
import tempfile
import importlib.util
from pathlib import Path
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = Path(tempfile.gettempdir()) / 'accounting_trace.db'
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'

spec = importlib.util.spec_from_file_location('accounting_service_main', Path('c:/NBFCSUITE/services/accounting/app/main.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.Base.metadata.create_all(bind=module.engine)

async def dump_ledger(client, tenant_id, label):
    resp = await client.get('/gl-ledger', params={'tenant_id': tenant_id})
    print('---', label, resp.status_code, resp.json())

async def run():
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url='http://testserver') as client:
        tenant_id='tenant-local-accounting'
        cash_account = (await client.post('/gl-accounts', json={'tenant_id': tenant_id,'account_code': '111000_BRANCH_CASH','account_name': 'Branch Cash','account_type': 'asset','category': 'Assets','currency': 'INR','branch_specific': 'true','posting_allowed': 'true','financial_year': '2026-27'})).json()
        expense_account = (await client.post('/gl-accounts', json={'tenant_id': tenant_id,'account_code': '510000_BRANCH_EXP','account_name': 'Branch Operating Expense','account_type': 'expense','category': 'Expenses'})).json()
        # receipt
        receipt = (await client.post('/vouchers', json={'tenant_id': tenant_id,'voucher_type': 'receipt','description': 'Customer cash receipt','reference': 'RCPT-001','branch_id': 'branch-001','payment_mode': 'upi','payment_reference': 'UPI-REF-1234','payment_details': {'note': 'Receipt via UPI'},'created_by': 'tester','lines': [{'gl_account_id': expense_account['id'], 'debit': 250.0, 'credit': 0.0},{'gl_account_id': cash_account['id'], 'debit': 0.0, 'credit': 250.0}]})).json()
        for action in ['verify','approve','post']:
            resp = await client.post(f"/vouchers/{receipt['id']}/{action}", json={'tenant_id': tenant_id,'performed_by': action})
            print('receipt',action,resp.status_code,resp.text)
        await dump_ledger(client, tenant_id, 'after_receipt_post')
        resp = await client.post(f"/vouchers/{receipt['id']}/reverse", json={'tenant_id': tenant_id,'performed_by':'reverser'})
        print('receipt reverse',resp.status_code,resp.text)
        await dump_ledger(client, tenant_id, 'after_receipt_reverse')
        # payment
        payment = (await client.post('/vouchers', json={'tenant_id': tenant_id,'voucher_type': 'payment','description': 'Branch utility payment','reference': 'UTIL-001','branch_id': 'branch-001','created_by': 'tester','lines': [{'gl_account_id': expense_account['id'], 'debit': 250.0, 'credit': 0.0},{'gl_account_id': cash_account['id'], 'debit': 0.0, 'credit': 250.0}]})).json()
        for action in ['verify','approve','post']:
            resp = await client.post(f"/vouchers/{payment['id']}/{action}", json={'tenant_id': tenant_id,'performed_by': action})
            print('payment',action,resp.status_code,resp.text)
        await dump_ledger(client, tenant_id, 'after_payment_post')
        resp = await client.post(f"/vouchers/{payment['id']}/reverse", json={'tenant_id': tenant_id,'performed_by':'reverser'})
        print('payment reverse',resp.status_code,resp.text)
        await dump_ledger(client, tenant_id, 'after_payment_reverse')

asyncio.run(run())
