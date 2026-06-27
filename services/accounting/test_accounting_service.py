import os
import tempfile
from pathlib import Path
import importlib.util
from fastapi.testclient import TestClient

# Configure local SQLite database before importing the accounting app.
TEST_DB_PATH = Path(tempfile.gettempdir()) / "accounting_service_test.db"
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

spec = importlib.util.spec_from_file_location(
    "accounting_service_main",
    Path(__file__).resolve().parent / "app" / "main.py",
)
accounting_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting_main)

accounting_main.Base.metadata.create_all(bind=accounting_main.engine)
client = TestClient(accounting_main.app)


def teardown_module(module):
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_posting_rule_auto_posting_subledger_and_audit():
    tenant_id = "tenant-local-accounting"

    rule_payload = {
        "tenant_id": tenant_id,
        "source_module": "deposits",
        "source_event": "deposit",
        "debit_account_code": "1000_CASH",
        "credit_account_code": "2200_CUSTOMER_DEPOSITS",
        "description": "Deposit receipt posting",
    }
    rule_response = client.post("/posting-rules", json=rule_payload)
    assert rule_response.status_code == 200
    rule_data = rule_response.json()
    assert rule_data["tenant_id"] == tenant_id
    assert rule_data["source_module"] == "deposits"
    assert rule_data["source_event"] == "deposit"
    assert rule_data["debit_account_code"] == "1000_CASH"
    assert rule_data["credit_account_code"] == "2200_CUSTOMER_DEPOSITS"

    posting_payload = {
        "tenant_id": tenant_id,
        "idempotency_key": "local-test-001",
        "source_module": "deposits",
        "source_event": "deposit",
        "source_reference": "deposit-test-ref",
        "amount": 1500.0,
        "metadata": {"note": "local deposit posting"},
    }
    posting_response = client.post("/gl-postings/auto", json=posting_payload)
    assert posting_response.status_code == 200
    posting_data = posting_response.json()
    assert posting_data["posting_status"] == "posted"
    assert posting_data["source_reference"] == "deposit-test-ref"
    assert posting_data["idempotency_key"] == "local-test-001"

    duplicate_response = client.post("/gl-postings/auto", json=posting_payload)
    assert duplicate_response.status_code == 200
    assert duplicate_response.json()["id"] == posting_data["id"]

    subledger_response = client.get(
        "/sub-ledger-entries",
        params={
            "tenant_id": tenant_id,
            "source_module": "deposits",
            "source_event": "deposit",
            "source_reference": "deposit-test-ref",
        },
    )
    assert subledger_response.status_code == 200
    subledger_entries = subledger_response.json()
    assert len(subledger_entries) == 1
    assert subledger_entries[0]["amount"] == 1500.0
    assert subledger_entries[0]["journal_entry_id"] == posting_data["id"]

    audit_response = client.get(
        "/audit-logs",
        params={"tenant_id": tenant_id, "entity": "gl_posting"},
    )
    assert audit_response.status_code == 200
    audit_entries = audit_response.json()
    assert any(entry["action"] == "create" for entry in audit_entries)

    trial_balance_response = client.get(
        "/reports/trial-balance",
        params={"tenant_id": tenant_id},
    )
    assert trial_balance_response.status_code == 200
    trial_balance = trial_balance_response.json()
    assert trial_balance["is_balanced"] is True
    assert trial_balance["total_debit"] == 1500.0
    assert trial_balance["total_credit"] == 1500.0
