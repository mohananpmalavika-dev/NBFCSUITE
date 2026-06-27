import asyncio
import os
import tempfile
from pathlib import Path
import importlib.util
from httpx import AsyncClient, ASGITransport

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


async def _run_accounting_test():
    async with AsyncClient(
        transport=ASGITransport(app=accounting_main.app),
        base_url="http://testserver",
    ) as client:
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
        assert cash_response.status_code == 200
        cash_account = cash_response.json()
        assert cash_account["category"] == "Assets"
        assert cash_account["posting_allowed"] == "true"

        invalid_parent_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "111500_BAD_PARENT",
                "account_name": "Bad Parent Account",
                "account_type": "asset",
                "parent_account_id": "missing-parent",
            },
        )
        assert invalid_parent_response.status_code == 404

        expense_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "510000_BRANCH_EXP",
                "account_name": "Branch Operating Expense",
                "account_type": "expense",
                "category": "Expenses",
            },
        )
        assert expense_response.status_code == 200
        expense_account = expense_response.json()

        child_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "111100_CASHIER_CASH",
                "account_name": "Cashier Cash",
                "account_type": "asset",
                "category": "Assets",
                "parent_account_id": cash_account["id"],
            },
        )
        assert child_response.status_code == 200

        self_parent_response = await client.put(
            f"/gl-accounts/{cash_account['id']}",
            params={"tenant_id": tenant_id},
            json={"parent_account_id": cash_account["id"]},
        )
        assert self_parent_response.status_code == 400

        hierarchy_response = await client.get("/gl-accounts/hierarchy", params={"tenant_id": tenant_id})
        assert hierarchy_response.status_code == 200
        hierarchy = hierarchy_response.json()["items"]
        cash_node = next(item for item in hierarchy if item["account_code"] == "111000_BRANCH_CASH")
        assert cash_node["children"][0]["account_code"] == "111100_CASHIER_CASH"

        summary_response = await client.get("/gl-accounts/summary", params={"tenant_id": tenant_id})
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert summary["total_accounts"] >= 3
        assert any(row["category"] == "Assets" for row in summary["categories"])

        seed_tenant = "tenant-local-accounting-seed"
        seed_response = await client.post(
            "/gl-accounts/seed-defaults",
            json={"tenant_id": seed_tenant, "currency": "INR", "financial_year": "2026-27"},
        )
        assert seed_response.status_code == 200
        assert seed_response.json()["created_count"] >= 20
        seeded_hierarchy_response = await client.get("/gl-accounts/hierarchy", params={"tenant_id": seed_tenant})
        assert seeded_hierarchy_response.status_code == 200
        seeded_roots = seeded_hierarchy_response.json()["items"]
        assert any(root["account_code"] == "100000" for root in seeded_roots)

        validation_response = await client.post(
            "/posting-engine/validate",
            json={
                "tenant_id": tenant_id,
                "source_module": "deposits",
                "source_event": "deposit",
                "source_reference": "deposit-test-ref",
                "lines": [
                    {"gl_account_id": expense_account["id"], "debit": 250.0, "credit": 0.0},
                    {"gl_account_id": cash_account["id"], "debit": 0.0, "credit": 250.0},
                ],
            },
        )
        assert validation_response.status_code == 200
        validation_payload = validation_response.json()
        assert validation_payload["is_balanced"] is True
        assert validation_payload["pipeline"]["validation"]["is_balanced"] is True
        assert validation_payload["pipeline"]["posting_rule"]["status"] in {"matched", "default_map", "manual"}

        voucher_response = await client.post(
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
        assert voucher_response.status_code == 200
        voucher = voucher_response.json()
        assert voucher["status"] == "draft"

        verify_response = await client.post(
            f"/vouchers/{voucher['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["status"] == "verified"
        approve_response = await client.post(
            f"/vouchers/{voucher['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"
        post_voucher_response = await client.post(
            f"/vouchers/{voucher['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert post_voucher_response.status_code == 200
        assert post_voucher_response.json()["posting_status"] == "posted"

        reverse_response = await client.post(
            f"/vouchers/{voucher['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert reverse_response.status_code == 200
        assert reverse_response.json()["status"] == "reversed"

        rule_payload = {
            "tenant_id": tenant_id,
            "source_module": "deposits",
            "source_event": "deposit",
            "debit_account_code": "1000_CASH",
            "credit_account_code": "2200_CUSTOMER_DEPOSITS",
            "description": "Deposit receipt posting",
        }
        rule_response = await client.post("/posting-rules", json=rule_payload)
        assert rule_response.status_code == 200
        rule_data = rule_response.json()
        assert rule_data["tenant_id"] == tenant_id
        assert rule_data["source_module"] == "deposits"
        assert rule_data["source_event"] == "deposit"
        assert rule_data["debit_account_code"] == "1000_CASH"
        assert rule_data["credit_account_code"] == "2200_CUSTOMER_DEPOSITS"

        multi_line_rule_payload = {
            "tenant_id": tenant_id,
            "source_module": "loans",
            "source_event": "disbursement",
            "description": "Loan disbursement posting",
            "lines": [
                {"account_code": "1200_LOAN_RECEIVABLE", "direction": "debit"},
                {"account_code": "1000_CASH", "direction": "credit"},
            ],
        }
        multi_line_rule_response = await client.post("/posting-rules", json=multi_line_rule_payload)
        assert multi_line_rule_response.status_code == 200
        multi_line_rule_data = multi_line_rule_response.json()
        assert multi_line_rule_data["lines"][0]["account_code"] == "1200_LOAN_RECEIVABLE"
        assert multi_line_rule_data["lines"][0]["direction"] == "debit"

        posting_payload = {
            "tenant_id": tenant_id,
            "idempotency_key": "local-test-001",
            "source_module": "deposits",
            "source_event": "deposit",
            "source_reference": "deposit-test-ref",
            "amount": 1500.0,
            "metadata": {"note": "local deposit posting"},
        }
        posting_response = await client.post("/gl-postings/auto", json=posting_payload)
        assert posting_response.status_code == 200
        posting_data = posting_response.json()
        assert posting_data["posting_status"] == "posted"
        assert posting_data["source_reference"] == "deposit-test-ref"
        assert posting_data["idempotency_key"] == "local-test-001"

        duplicate_response = await client.post("/gl-postings/auto", json=posting_payload)
        assert duplicate_response.status_code == 200
        assert duplicate_response.json()["id"] == posting_data["id"]

        subledger_response = await client.get(
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

        summary_response = await client.get("/sub-ledger-summary", params={"tenant_id": tenant_id})
        assert summary_response.status_code == 200
        summary_rows = summary_response.json()["items"]
        assert any(row["source_module"] == "deposits" and row["ledger_name"] == "Deposit Ledger" for row in summary_rows)

        audit_response = await client.get(
            "/audit-logs",
            params={"tenant_id": tenant_id, "entity": "gl_posting"},
        )
        assert audit_response.status_code == 200
        audit_entries = audit_response.json()
        assert any(entry["action"] == "create" for entry in audit_entries)

        trial_balance_response = await client.get(
            "/reports/trial-balance",
            params={"tenant_id": tenant_id},
        )
        assert trial_balance_response.status_code == 200
        trial_balance = trial_balance_response.json()
        assert trial_balance["is_balanced"] is True
        assert trial_balance["total_debit"] == 1500.0
        assert trial_balance["total_credit"] == 1500.0

        ledger_response = await client.get("/gl-ledger", params={"tenant_id": tenant_id})
        assert ledger_response.status_code == 200
        ledger_rows = ledger_response.json()["items"]
        assert any(row["account_code"] == "111000_BRANCH_CASH" for row in ledger_rows)
        cash_ledger_row = next(row for row in ledger_rows if row["account_code"] == "111000_BRANCH_CASH")
        assert cash_ledger_row["gl_number"] == "111000_BRANCH_CASH"
        assert cash_ledger_row["branch"] == "branch-001"
        assert cash_ledger_row["currency"] == "INR"
        assert cash_ledger_row["opening_balance"] == 0.0
        assert cash_ledger_row["debit"] == 0.0
        assert cash_ledger_row["credit"] == 250.0
        assert cash_ledger_row["balance"] == -250.0
        assert cash_ledger_row["closing_balance"] == -250.0
        assert cash_ledger_row["financial_year"] == "2026-27"

        dashboard_response = await client.get("/dashboard", params={"tenant_id": tenant_id})
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert dashboard["pending_vouchers"] == 0
        assert dashboard["trial_balance"]["is_balanced"] is True

        close_response = await client.post(
            "/day-end/close",
            json={
                "tenant_id": tenant_id,
                "business_date": "2026-06-28T00:00:00",
                "branch_id": "branch-001",
                "closed_by": "tester",
            },
        )
        assert close_response.status_code == 200
        assert close_response.json()["status"] == "closed"


def test_posting_rule_auto_posting_subledger_and_audit():
    asyncio.run(_run_accounting_test())
