import asyncio
import os
import tempfile
from pathlib import Path
import importlib.util
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

# Configure local SQLite database before importing the accounting app.
TEST_DB_PATH = Path(tempfile.gettempdir()) / f"accounting_service_test_{uuid4().hex}.db"
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

        receipt_response = await client.post(
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
        assert receipt_response.status_code == 200
        receipt_voucher = receipt_response.json()
        assert receipt_voucher["voucher_type"] == "receipt"
        assert receipt_voucher["payment_mode"] == "upi"
        assert receipt_voucher["payment_reference"] == "UPI-REF-1234"
        assert receipt_voucher["payment_details"]["note"] == "Receipt via UPI"

        customer_receipt_response = await client.post(
            "/receipt-vouchers",
            json={
                "tenant_id": tenant_id,
                "receipt_category": "customer_payments",
                "amount": 800.0,
                "payer_name": "Asha Customer",
                "customer_id": "customer-001",
                "description": "Loan repayment received",
                "reference": "RCPT-CUST-001",
                "branch_id": "branch-001",
                "payment_mode": "upi",
                "payment_reference": "UPI-CUST-001",
                "payment_details": {"upi_id": "asha@upi"},
                "created_by": "tester",
            },
        )
        assert customer_receipt_response.status_code == 200
        customer_receipt = customer_receipt_response.json()
        assert customer_receipt["voucher_type"] == "receipt"
        assert customer_receipt["receipt_category"] == "customer_payments"
        assert customer_receipt["payer_name"] == "Asha Customer"
        assert customer_receipt["customer_id"] == "customer-001"
        assert customer_receipt["amount"] == 800.0
        assert customer_receipt["payment_mode"] == "upi"
        assert len(customer_receipt["lines"]) == 2

        receipt_options_response = await client.get("/receipt-vouchers/options")
        assert receipt_options_response.status_code == 200
        receipt_options = receipt_options_response.json()
        assert receipt_options["categories"][0]["key"] == "customer_payments"
        assert {"cash", "cheque", "upi", "rtgs", "neft", "imps"}.issubset(set(receipt_options["payment_modes"]))

        customer_receipt_verify_response = await client.post(
            f"/vouchers/{customer_receipt['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert customer_receipt_verify_response.status_code == 200
        customer_receipt_approve_response = await client.post(
            f"/vouchers/{customer_receipt['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert customer_receipt_approve_response.status_code == 200
        customer_receipt_post_response = await client.post(
            f"/vouchers/{customer_receipt['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert customer_receipt_post_response.status_code == 200
        assert customer_receipt_post_response.json()["posting_status"] == "posted"
        customer_receipt_reverse_response = await client.post(
            f"/vouchers/{customer_receipt['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert customer_receipt_reverse_response.status_code == 200
        assert customer_receipt_reverse_response.json()["status"] == "reversed"

        salary_payment_response = await client.post(
            "/payment-vouchers",
            json={
                "tenant_id": tenant_id,
                "payment_category": "salary",
                "amount": 1200.0,
                "payee_name": "Operations team",
                "description": "June salary payout",
                "reference": "SAL-JUN",
                "branch_id": "branch-001",
                "payment_mode": "neft",
                "payment_reference": "NEFT-SAL-JUN",
                "payment_details": {"bank": "Primary bank"},
                "created_by": "tester",
            },
        )
        assert salary_payment_response.status_code == 200
        salary_payment = salary_payment_response.json()
        assert salary_payment["voucher_type"] == "payment"
        assert salary_payment["payment_category"] == "salary"
        assert salary_payment["payee_name"] == "Operations team"
        assert salary_payment["amount"] == 1200.0
        assert salary_payment["payment_mode"] == "neft"
        assert len(salary_payment["lines"]) == 2

        category_response = await client.get("/payment-vouchers/categories")
        assert category_response.status_code == 200
        category_keys = {item["key"] for item in category_response.json()["items"]}
        assert {"vendor_payments", "salary", "rent", "electricity", "tax", "insurance"}.issubset(category_keys)

        salary_verify_response = await client.post(
            f"/vouchers/{salary_payment['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert salary_verify_response.status_code == 200
        salary_approve_response = await client.post(
            f"/vouchers/{salary_payment['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert salary_approve_response.status_code == 200
        salary_post_response = await client.post(
            f"/vouchers/{salary_payment['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert salary_post_response.status_code == 200
        assert salary_post_response.json()["posting_status"] == "posted"
        salary_reverse_response = await client.post(
            f"/vouchers/{salary_payment['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert salary_reverse_response.status_code == 200
        assert salary_reverse_response.json()["status"] == "reversed"

        contra_response = await client.post(
            "/contra-vouchers",
            json={
                "tenant_id": tenant_id,
                "transfer_type": "cash_to_bank",
                "amount": 600.0,
                "description": "Deposit branch cash to bank",
                "reference": "CONTRA-CASH-BANK",
                "transfer_reference": "DEP-001",
                "branch_id": "branch-001",
                "source_location": "Main cash counter",
                "destination_location": "Primary bank",
                "transfer_details": {"deposit_slip": "SLIP-001"},
                "created_by": "tester",
            },
        )
        assert contra_response.status_code == 200
        contra_voucher = contra_response.json()
        assert contra_voucher["voucher_type"] == "contra"
        assert contra_voucher["contra_transfer_type"] == "cash_to_bank"
        assert contra_voucher["source_location"] == "Main cash counter"
        assert contra_voucher["destination_location"] == "Primary bank"
        assert contra_voucher["transfer_reference"] == "DEP-001"
        assert contra_voucher["amount"] == 600.0
        assert len(contra_voucher["lines"]) == 2

        contra_options_response = await client.get("/contra-vouchers/options")
        assert contra_options_response.status_code == 200
        transfer_keys = {item["key"] for item in contra_options_response.json()["transfer_types"]}
        assert {"cash_to_bank", "bank_to_cash", "vault_to_branch", "branch_to_treasury"}.issubset(transfer_keys)

        contra_verify_response = await client.post(
            f"/vouchers/{contra_voucher['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert contra_verify_response.status_code == 200
        contra_approve_response = await client.post(
            f"/vouchers/{contra_voucher['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert contra_approve_response.status_code == 200
        contra_post_response = await client.post(
            f"/vouchers/{contra_voucher['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert contra_post_response.status_code == 200
        assert contra_post_response.json()["posting_status"] == "posted"
        contra_reverse_response = await client.post(
            f"/vouchers/{contra_voucher['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert contra_reverse_response.status_code == 200
        assert contra_reverse_response.json()["status"] == "reversed"

        credit_note_response = await client.post(
            "/credit-notes",
            json={
                "tenant_id": tenant_id,
                "credit_note_type": "discount",
                "amount": 450.0,
                "customer_name": "Asha Customer",
                "customer_id": "customer-001",
                "description": "Campaign discount credit note",
                "reference": "CN-DISC-001",
                "credit_note_reference": "DISC-001",
                "branch_id": "branch-001",
                "credit_note_details": {"reason": "Campaign discount"},
                "created_by": "tester",
            },
        )
        assert credit_note_response.status_code == 200
        credit_note = credit_note_response.json()
        assert credit_note["voucher_type"] == "credit_note"
        assert credit_note["credit_note_type"] == "discount"
        assert credit_note["customer_name"] == "Asha Customer"
        assert credit_note["customer_id"] == "customer-001"
        assert credit_note["credit_note_reference"] == "DISC-001"
        assert credit_note["amount"] == 450.0
        assert len(credit_note["lines"]) == 2

        credit_note_options_response = await client.get("/credit-notes/options")
        assert credit_note_options_response.status_code == 200
        credit_note_type_keys = {item["key"] for item in credit_note_options_response.json()["credit_note_types"]}
        assert {"interest_reversal", "refund", "adjustment", "discount"}.issubset(credit_note_type_keys)

        credit_note_filter_response = await client.get(
            "/vouchers",
            params={"tenant_id": tenant_id, "voucher_type": "credit_note", "credit_note_type": "discount"},
        )
        assert credit_note_filter_response.status_code == 200
        assert any(item["id"] == credit_note["id"] for item in credit_note_filter_response.json()["items"])

        credit_note_verify_response = await client.post(
            f"/vouchers/{credit_note['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert credit_note_verify_response.status_code == 200
        credit_note_approve_response = await client.post(
            f"/vouchers/{credit_note['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert credit_note_approve_response.status_code == 200
        credit_note_post_response = await client.post(
            f"/vouchers/{credit_note['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert credit_note_post_response.status_code == 200
        assert credit_note_post_response.json()["posting_status"] == "posted"
        credit_note_reverse_response = await client.post(
            f"/vouchers/{credit_note['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert credit_note_reverse_response.status_code == 200
        assert credit_note_reverse_response.json()["status"] == "reversed"

        debit_note_response = await client.post(
            "/debit-notes",
            json={
                "tenant_id": tenant_id,
                "debit_note_type": "penalty",
                "amount": 375.0,
                "customer_name": "Asha Customer",
                "customer_id": "customer-001",
                "description": "Late payment penalty debit note",
                "reference": "DN-PEN-001",
                "debit_note_reference": "PEN-001",
                "branch_id": "branch-001",
                "debit_note_details": {"reason": "Late payment penalty"},
                "created_by": "tester",
            },
        )
        assert debit_note_response.status_code == 200
        debit_note = debit_note_response.json()
        assert debit_note["voucher_type"] == "debit_note"
        assert debit_note["debit_note_type"] == "penalty"
        assert debit_note["customer_name"] == "Asha Customer"
        assert debit_note["customer_id"] == "customer-001"
        assert debit_note["debit_note_reference"] == "PEN-001"
        assert debit_note["amount"] == 375.0
        assert len(debit_note["lines"]) == 2

        debit_note_options_response = await client.get("/debit-notes/options")
        assert debit_note_options_response.status_code == 200
        debit_note_type_keys = {item["key"] for item in debit_note_options_response.json()["debit_note_types"]}
        assert {"penalty", "charges", "recovery", "tax_adjustment"}.issubset(debit_note_type_keys)

        debit_note_filter_response = await client.get(
            "/vouchers",
            params={"tenant_id": tenant_id, "voucher_type": "debit_note", "debit_note_type": "penalty"},
        )
        assert debit_note_filter_response.status_code == 200
        assert any(item["id"] == debit_note["id"] for item in debit_note_filter_response.json()["items"])

        debit_note_verify_response = await client.post(
            f"/vouchers/{debit_note['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert debit_note_verify_response.status_code == 200
        debit_note_approve_response = await client.post(
            f"/vouchers/{debit_note['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert debit_note_approve_response.status_code == 200
        debit_note_post_response = await client.post(
            f"/vouchers/{debit_note['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert debit_note_post_response.status_code == 200
        assert debit_note_post_response.json()["posting_status"] == "posted"
        debit_note_reverse_response = await client.post(
            f"/vouchers/{debit_note['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert debit_note_reverse_response.status_code == 200
        assert debit_note_reverse_response.json()["status"] == "reversed"

        receipt_verify_response = await client.post(
            f"/vouchers/{receipt_voucher['id']}/verify",
            json={"tenant_id": tenant_id, "performed_by": "verifier"},
        )
        assert receipt_verify_response.status_code == 200
        assert receipt_verify_response.json()["status"] == "verified"
        receipt_approve_response = await client.post(
            f"/vouchers/{receipt_voucher['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "approver"},
        )
        assert receipt_approve_response.status_code == 200
        assert receipt_approve_response.json()["status"] == "approved"
        receipt_post_response = await client.post(
            f"/vouchers/{receipt_voucher['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "poster"},
        )
        assert receipt_post_response.status_code == 200
        assert receipt_post_response.json()["posting_status"] == "posted"
        receipt_reverse_response = await client.post(
            f"/vouchers/{receipt_voucher['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "reverser"},
        )
        assert receipt_reverse_response.status_code == 200
        assert receipt_reverse_response.json()["status"] == "reversed"

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
        assert cash_ledger_row["debit"] == 500.0
        assert cash_ledger_row["credit"] == 500.0
        assert cash_ledger_row["balance"] == 0.0
        assert cash_ledger_row["closing_balance"] == 0.0
        assert cash_ledger_row["financial_year"] == "2026-27"
        bank_ledger_row = next(row for row in ledger_rows if row["account_code"] == "1120_BANK")
        assert bank_ledger_row["debit"] == 2600.0
        assert bank_ledger_row["credit"] == 2600.0
        assert bank_ledger_row["balance"] == 0.0
        cash_transfer_row = next(
            row
            for row in ledger_rows
            if row["account_code"] == "1000_CASH" and row["branch"] == "branch-001"
        )
        assert cash_transfer_row["debit"] == 600.0
        assert cash_transfer_row["credit"] == 600.0
        assert cash_transfer_row["balance"] == 0.0
        discount_row = next(row for row in ledger_rows if row["account_code"] == "5500_DISCOUNT_ALLOWED")
        assert discount_row["debit"] == 450.0
        assert discount_row["credit"] == 450.0
        assert discount_row["balance"] == 0.0
        penalty_row = next(row for row in ledger_rows if row["account_code"] == "4120_PENALTY_INCOME")
        assert penalty_row["debit"] == 375.0
        assert penalty_row["credit"] == 375.0
        assert penalty_row["balance"] == 0.0

        dashboard_response = await client.get("/dashboard", params={"tenant_id": tenant_id})
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert dashboard["pending_vouchers"] == 0
        assert dashboard["trial_balance"]["is_balanced"] is True

        accounting_360_response = await client.get("/accounting-360/dashboard", params={"tenant_id": tenant_id})
        assert accounting_360_response.status_code == 200
        accounting_360 = accounting_360_response.json()
        assert accounting_360["trial_balance"]["is_balanced"] is True
        assert any(metric["key"] == "assets" for metric in accounting_360["metrics"])
        assert accounting_360["posting_health"]["journal_entries"] >= 1
        assert accounting_360["gl_tree"]

        accounting_360_search_response = await client.get(
            "/accounting-360/search",
            params={"tenant_id": tenant_id, "q": "cash"},
        )
        assert accounting_360_search_response.status_code == 200
        assert any("Cash" in item["account_name"] for item in accounting_360_search_response.json()["items"])

        accounting_360_gl_response = await client.get(
            f"/accounting-360/gl/{cash_account['id']}",
            params={"tenant_id": tenant_id},
        )
        assert accounting_360_gl_response.status_code == 200
        accounting_360_gl = accounting_360_gl_response.json()
        assert accounting_360_gl["account"]["account_code"] == "111000_BRANCH_CASH"
        assert "ai_summary" in accounting_360_gl["summary"]

        quick_action_response = await client.post(
            "/accounting-360/quick-action",
            json={
                "tenant_id": tenant_id,
                "action_type": "expense_paid",
                "amount": 99.0,
                "party_name": "Power utility",
                "description": "Branch electricity",
                "source_reference": "A360-UTIL-001",
                "branch_id": "branch-001",
                "performed_by": "tester",
            },
        )
        assert quick_action_response.status_code == 200
        quick_action = quick_action_response.json()
        assert quick_action["journal_entry"]["posting_status"] == "posted"
        assert quick_action["pipeline"]["posting_rule"]["status"] == "accounting_360_template"
        assert quick_action["inferred_lines"][0]["direction"] == "debit"

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
