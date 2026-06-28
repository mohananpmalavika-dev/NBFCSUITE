import os
import tempfile
import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DB_PATH = Path(tempfile.gettempdir()) / "accounting_service_test.db"
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location("accounting_service_main", Path(__file__).resolve().parent / "app" / "main.py")
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)
accounting_main.Base.metadata.create_all(bind=accounting_main.engine)

client = TestClient(accounting_main.app)
tenant_id = "tenant-local-accounting"

cash_response = client.post(
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
assert cash_response.ok, cash_response.text
cash_account = cash_response.json()

expense_response = client.post(
    "/gl-accounts",
    json={
        "tenant_id": tenant_id,
        "account_code": "510000_BRANCH_EXP",
        "account_name": "Branch Operating Expense",
        "account_type": "expense",
        "category": "Expenses",
    },
)
assert expense_response.ok, expense_response.text
expense_account = expense_response.json()

voucher_response = client.post(
    "/vouchers",
    json={
        "tenant_id": tenant_id,
        "voucher_type": "payment",
        "description": "Branch utility payment",
        "reference": "UTIL-001",
        "branch_id": "branch-001",
        "created_by": "tester",
        "lines": [
            {"gl_account_id": expense_account["id"], "debit": 250.0, "credit": 0.0},
            {"gl_account_id": cash_account["id"], "debit": 0.0, "credit": 250.0},
        ],
    },
)
assert voucher_response.ok, voucher_response.text
voucher = voucher_response.json()

receipt_response = client.post(
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
            {"gl_account_id": expense_account["id"], "debit": 250.0, "credit": 0.0},
            {"gl_account_id": cash_account["id"], "debit": 0.0, "credit": 250.0},
        ],
    },
)
assert receipt_response.ok, receipt_response.text
receipt_voucher = receipt_response.json()

for action in ["verify", "approve"]:
    r = client.post(f"/vouchers/{receipt_voucher['id']}/{action}", json={"tenant_id": tenant_id, "performed_by": action})
    print(action, r.status_code, r.json())

post_receipt = client.post(f"/vouchers/{receipt_voucher['id']}/post", json={"tenant_id": tenant_id, "performed_by": "poster"})
print('receipt post', post_receipt.status_code, post_receipt.json())
print('after_receipt_post', client.get('/gl-ledger', params={'tenant_id': tenant_id}).json())

receipt_rev = client.post(f"/vouchers/{receipt_voucher['id']}/reverse", json={"tenant_id": tenant_id, "performed_by": "reverser"})
print('receipt reverse', receipt_rev.status_code, receipt_rev.json())
print('after_receipt_reverse', client.get('/gl-ledger', params={'tenant_id': tenant_id}).json())

for action in ["verify", "approve"]:
    r = client.post(f"/vouchers/{voucher['id']}/{action}", json={"tenant_id": tenant_id, "performed_by": action})
    print(action, r.status_code, r.json())

post_payment = client.post(f"/vouchers/{voucher['id']}/post", json={"tenant_id": tenant_id, "performed_by": "poster"})
print('payment post', post_payment.status_code, post_payment.json())
print('after_payment_post', client.get('/gl-ledger', params={'tenant_id': tenant_id}).json())

payment_rev = client.post(f"/vouchers/{voucher['id']}/reverse", json={"tenant_id": tenant_id, "performed_by": "reverser"})
print('payment reverse', payment_rev.status_code, payment_rev.json())
print('after_payment_reverse', client.get('/gl-ledger', params={'tenant_id': tenant_id}).json())

print('GLBalance rows raw:')
db = accounting_main.SessionLocal()
for b in db.query(accounting_main.GLBalance).order_by(accounting_main.GLBalance.financial_year, accounting_main.GLBalance.branch_id, accounting_main.GLBalance.id):
    acc = db.query(accounting_main.GLAccount).filter_by(id=b.gl_account_id).first()
    print(acc.account_code, b.branch_id, b.currency, b.financial_year, b.total_debit, b.total_credit, b.closing_balance)

print('Journal entries:')
for e in db.query(accounting_main.JournalEntry).all():
    print(e.id, e.posting_status, e.description, e.reference, e.source_event, e.financial_year)

print('Journal lines:')
for l in db.query(accounting_main.JournalLine).all():
    acc = db.query(accounting_main.GLAccount).filter_by(id=l.gl_account_id).first()
    print(l.journal_entry_id, acc.account_code, l.debit, l.credit, l.branch_id, l.currency, l.description)
