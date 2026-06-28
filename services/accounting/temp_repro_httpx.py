import os
import tempfile
import uuid
import importlib.util
from pathlib import Path
from httpx import AsyncClient, ASGITransport
import asyncio

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_service_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path(__file__).resolve().parent / "app" / "main.py",
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)
accounting_main.Base.metadata.create_all(bind=accounting_main.engine)

async def main():
    async with AsyncClient(transport=ASGITransport(app=accounting_main.app), base_url="http://testserver") as client:
        tenant_id = "tenant-local-accounting"
        cash_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "111000_BRANCH_CASH",
                "account_name": "Branch Cash",
                "account_type": "asset",
                "category": "Assets",
                "currency": "INR",
                "branch_specific": "true",
                "posting_allowed": "true",
                "financial_year": "2026-27",
            },
        )
        cash = cash_response.json()
        exp_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "510000_BRANCH_EXP",
                "account_name": "Branch Operating Expense",
                "account_type": "expense",
                "category": "Expenses",
            },
        )
        exp = exp_response.json()
        voucher_response = await client.post(
            "/vouchers",
            json={
                "tenant_id": tenant_id,
                "voucher_type": "receipt",
                "description": "Customer cash receipt",
                "reference": "RCPT-001",
                "branch_id": "branch-001",
                "payment_mode": "upi",
                "payment_reference": "UPI-REF-1234",
                "payment_details": {"note": "Receipt via UPI"},
                "created_by": "tester",
                "lines": [
                    {"gl_account_id": exp["id"], "debit": 250.0, "credit": 0.0},
                    {"gl_account_id": cash["id"], "debit": 0.0, "credit": 250.0},
                ],
            },
        )
        voucher = voucher_response.json()
        for action in ["verify", "approve"]:
            r = await client.post(f"/vouchers/{voucher['id']}/{action}", json={"tenant_id": tenant_id, "performed_by": action})
            print(action, r.status_code, r.json())
        rpost = await client.post(f"/vouchers/{voucher['id']}/post", json={"tenant_id": tenant_id, "performed_by": "poster"})
        print('post', rpost.status_code, rpost.json())
        ledger1 = await client.get("/gl-ledger", params={"tenant_id": tenant_id})
        print('ledger after post', ledger1.json())
        rrev = await client.post(f"/vouchers/{voucher['id']}/reverse", json={"tenant_id": tenant_id, "performed_by": "reverser"})
        print('reverse', rrev.status_code, rrev.json())
        ledger2 = await client.get("/gl-ledger", params={"tenant_id": tenant_id})
        print('ledger after reverse', ledger2.json())
        db = accounting_main.SessionLocal()
        for b in db.query(accounting_main.GLBalance).all():
            acc = db.query(accounting_main.GLAccount).filter(accounting_main.GLAccount.id == b.gl_account_id).first()
            print('balance row', acc.account_code, b.branch_id, b.total_debit, b.total_credit, b.closing_balance)
        for e in db.query(accounting_main.JournalEntry).all():
            print('entry', e.id, e.posting_status, e.description, e.reference, e.source_event)
        for l in db.query(accounting_main.JournalLine).all():
            acc = db.query(accounting_main.GLAccount).filter(accounting_main.GLAccount.id == l.gl_account_id).first()
            print('line', l.journal_entry_id, acc.account_code, l.debit, l.credit, l.description)

if __name__ == '__main__':
    asyncio.run(main())
