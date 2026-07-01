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

        afc_dashboard_response = await client.get("/api/v1/gl/dashboard", params={"tenant_id": tenant_id})
        assert afc_dashboard_response.status_code == 200
        afc_dashboard = afc_dashboard_response.json()
        assert afc_dashboard["kpis"]["total_accounts"] >= 3
        assert "accounts_by_type" in afc_dashboard["charts"]

        afc_list_response = await client.get("/api/v1/gl/accounts", params={"tenant_id": tenant_id, "q": "Cash"})
        assert afc_list_response.status_code == 200
        afc_accounts = afc_list_response.json()
        assert afc_accounts["total"] >= 2
        assert any(item["gl_code"] == "111000_BRANCH_CASH" for item in afc_accounts["items"])

        afc_tree_response = await client.get("/api/v1/gl/accounts/tree", params={"tenant_id": tenant_id})
        assert afc_tree_response.status_code == 200
        assert any(item["account_code"] == "111000_BRANCH_CASH" for item in afc_tree_response.json()["items"])

        afc_search_response = await client.get("/api/v1/gl/accounts/search", params={"tenant_id": tenant_id, "q": "cash"})
        assert afc_search_response.status_code == 200
        assert any(item["account_code"] == "111000_BRANCH_CASH" for item in afc_search_response.json()["items"])

        afc_detail_response = await client.get(
            f"/api/v1/gl/accounts/{cash_account['id']}",
            params={"tenant_id": tenant_id},
        )
        assert afc_detail_response.status_code == 200
        assert afc_detail_response.json()["gl_code"] == "111000_BRANCH_CASH"

        afc_usage_response = await client.get(
            f"/api/v1/gl/accounts/{cash_account['id']}/usage",
            params={"tenant_id": tenant_id},
        )
        assert afc_usage_response.status_code == 200
        assert "summary" in afc_usage_response.json()

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

        vendor_response = await client.post(
            "/api/v1/ap/vendors",
            json={
                "tenant_id": tenant_id,
                "vendor_code": "VEND-001",
                "vendor_name": "Acme Supplies",
                "vendor_type": "supplier",
                "status": "active",
                "payment_terms": "45 days",
                "credit_limit": 50000.0,
                "gst_number": "GSTIN12345",
                "currency": "INR",
                "branch_id": "branch-001",
                "metadata": {"preferred_contact": "ap@acme.com"},
                "created_by": "tester",
            },
        )
        assert vendor_response.status_code == 200
        vendor = vendor_response.json()
        assert vendor["vendor_name"] == "Acme Supplies"
        assert vendor["vendor_code"] == "VEND-001"

        invoice_response = await client.post(
            "/api/v1/ap/invoices",
            json={
                "tenant_id": tenant_id,
                "vendor_id": vendor["id"],
                "invoice_number": "INV-2026-001",
                "invoice_date": "2026-06-20T00:00:00",
                "due_date": "2026-07-20T00:00:00",
                "currency": "INR",
                "total_amount": 15000.0,
                "status": "pending",
                "branch_id": "branch-001",
                "reference": "PO-1234",
                "description": "Office supplies procurement",
                "metadata": {"cost_center": "ops"},
                "created_by": "tester",
            },
        )
        assert invoice_response.status_code == 200
        ap_invoice = invoice_response.json()
        assert ap_invoice["vendor_id"] == vendor["id"]
        assert ap_invoice["invoice_number"] == "INV-2026-001"
        assert ap_invoice["total_amount"] == 15000.0

        list_invoices_response = await client.get(
            "/api/v1/ap/invoices",
            params={"tenant_id": tenant_id},
        )
        assert list_invoices_response.status_code == 200
        assert any(item["id"] == ap_invoice["id"] for item in list_invoices_response.json())

        vendor_ledger_response = await client.get(
            f"/api/v1/ap/vendors/{vendor['id']}/ledger",
            params={"tenant_id": tenant_id},
        )
        assert vendor_ledger_response.status_code == 200
        vendor_ledger = vendor_ledger_response.json()
        assert vendor_ledger["vendor"]["id"] == vendor["id"]
        assert vendor_ledger["total_invoices"] == 1
        assert vendor_ledger["outstanding_balance"] == 15000.0

        ap_dashboard_response = await client.get(
            "/api/v1/ap/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert ap_dashboard_response.status_code == 200
        ap_dashboard = ap_dashboard_response.json()
        assert ap_dashboard["total_vendors"] >= 1
        assert ap_dashboard["total_invoices"] >= 1

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

        formula_rule_payload = {
            "tenant_id": tenant_id,
            "source_module": "collections",
            "source_event": "emi_split",
            "rule_name": "Gold loan EMI split",
            "priority": 10,
            "status": "draft",
            "description": "Split EMI into principal, interest, and penalty",
            "conditions": [
                {"field": "product", "operator": "eq", "value": "gold_loan"},
                {"field": "emi_amount", "operator": "gt", "value": 0},
            ],
            "lines": [
                {"account_code": "1120_BANK", "direction": "debit", "amount_source": "emi_amount", "description": "EMI cash received"},
                {"account_code": "1200_LOAN_RECEIVABLE", "direction": "credit", "formula": "principal", "description": "Principal recovery"},
                {"account_code": "410000", "direction": "credit", "formula": "interest + penalty", "description": "Income recovery"},
            ],
            "created_by": "tester",
        }
        formula_rule_response = await client.post("/posting-rules", json=formula_rule_payload)
        assert formula_rule_response.status_code == 200
        formula_rule = formula_rule_response.json()
        assert formula_rule["status"] == "draft"
        assert formula_rule["conditions"][0]["field"] == "product"
        assert formula_rule["lines"][2]["formula"] == "interest + penalty"

        formula_validation_response = await client.post("/posting-rules/validate", json=formula_rule_payload)
        assert formula_validation_response.status_code == 200
        assert formula_validation_response.json()["formula_count"] == 2

        formula_simulation_response = await client.post(
            "/posting-rules/simulate",
            json={
                "tenant_id": tenant_id,
                "source_module": "collections",
                "source_event": "emi_split",
                "source_reference": "SIM-EMI-001",
                "amount": 1000.0,
                "event_data": {
                    "product": "gold_loan",
                    "emi_amount": 1000.0,
                    "principal": 700.0,
                    "interest": 250.0,
                    "penalty": 50.0,
                },
            },
        )
        assert formula_simulation_response.status_code == 200
        formula_simulation = formula_simulation_response.json()
        assert formula_simulation["is_balanced"] is True
        assert formula_simulation["total_debit"] == 1000.0
        assert formula_simulation["total_credit"] == 1000.0

        afc_rule_dashboard_response = await client.get(
            "/api/v1/accounting/posting-rules/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert afc_rule_dashboard_response.status_code == 200
        assert afc_rule_dashboard_response.json()["kpis"]["posting_rules"] >= 3

        afc_rule_list_response = await client.get(
            "/api/v1/accounting/posting-rules",
            params={"tenant_id": tenant_id, "source_module": "collections"},
        )
        assert afc_rule_list_response.status_code == 200
        assert any(item["id"] == formula_rule["id"] for item in afc_rule_list_response.json()["items"])

        afc_rule_detail_response = await client.get(
            f"/api/v1/accounting/posting-rules/{formula_rule['id']}",
            params={"tenant_id": tenant_id},
        )
        assert afc_rule_detail_response.status_code == 200
        afc_rule_detail = afc_rule_detail_response.json()
        assert afc_rule_detail["accounting_view"]["debit_lines"][0]["account_code"] == "1120_BANK"
        assert afc_rule_detail["operations_view"]["execution_count"] >= 1

        afc_rule_simulation_response = await client.post(
            f"/api/v1/accounting/posting-rules/{formula_rule['id']}/simulate",
            json={
                "tenant_id": tenant_id,
                "source_reference": "AFC-SIM-001",
                "amount": 1000.0,
                "event_data": {
                    "product": "gold_loan",
                    "emi_amount": 1000.0,
                    "principal": 700.0,
                    "interest": 250.0,
                    "penalty": 50.0,
                },
            },
        )
        assert afc_rule_simulation_response.status_code == 200
        assert afc_rule_simulation_response.json()["is_balanced"] is True

        formula_publish_response = await client.post(
            f"/posting-rules/{formula_rule['id']}/publish",
            json={"tenant_id": tenant_id, "performed_by": "tester"},
        )
        assert formula_publish_response.status_code == 400

        submit_rule_response = await client.post(
            f"/posting-rules/{formula_rule['id']}/submit",
            json={"tenant_id": tenant_id, "performed_by": "maker"},
        )
        assert submit_rule_response.status_code == 200
        assert submit_rule_response.json()["approval_status"] == "maker_submitted"
        checker_rule_response = await client.post(
            f"/posting-rules/{formula_rule['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "checker", "stage": "checker"},
        )
        assert checker_rule_response.status_code == 200
        assert checker_rule_response.json()["approval_status"] == "checker_approved"
        finance_rule_response = await client.post(
            f"/posting-rules/{formula_rule['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "finance-head", "stage": "finance_head"},
        )
        assert finance_rule_response.status_code == 200
        assert finance_rule_response.json()["approval_status"] == "finance_head_approved"

        formula_publish_response = await client.post(
            f"/posting-rules/{formula_rule['id']}/publish",
            json={"tenant_id": tenant_id, "performed_by": "tester"},
        )
        assert formula_publish_response.status_code == 200
        assert formula_publish_response.json()["status"] == "active"
        assert formula_publish_response.json()["approval_status"] == "published"

        immutable_update_response = await client.put(
            f"/posting-rules/{formula_rule['id']}",
            params={"tenant_id": tenant_id},
            json={"description": "Attempt to overwrite published rule", "performed_by": "tester"},
        )
        assert immutable_update_response.status_code == 400

        new_version_response = await client.post(
            f"/posting-rules/{formula_rule['id']}/new-version",
            json={
                "tenant_id": tenant_id,
                "description": "Next FY EMI split",
                "effective_from": "2026-07-01T00:00:00",
                "performed_by": "tester",
            },
        )
        assert new_version_response.status_code == 200
        assert new_version_response.json()["version"] == 2.0
        assert new_version_response.json()["supersedes_rule_id"] == formula_rule["id"]
        assert new_version_response.json()["status"] == "draft"

        afc_rule_versions_response = await client.get(
            f"/api/v1/accounting/posting-rules/{formula_rule['id']}/versions",
            params={"tenant_id": tenant_id},
        )
        assert afc_rule_versions_response.status_code == 200
        assert len(afc_rule_versions_response.json()["items"]) >= 2

        formula_history_response = await client.get(
            f"/posting-rules/{formula_rule['id']}/history",
            params={"tenant_id": tenant_id},
        )
        assert formula_history_response.status_code == 200
        assert any(item["action"] == "publish" for item in formula_history_response.json())
        assert any(item["action"] == "approve_finance_head" for item in formula_history_response.json())

        formula_executions_response = await client.get(
            f"/posting-rules/{formula_rule['id']}/executions",
            params={"tenant_id": tenant_id},
        )
        assert formula_executions_response.status_code == 200
        assert formula_executions_response.json()["total"] >= 1

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

        multi_currency_journal_response = await client.post(
            "/journal-entries",
            json={
                "tenant_id": tenant_id,
                "description": "FX dimension smoke journal",
                "reference": "FX-DIM-001",
                "branch_id": "branch-001",
                "business_date": "2026-06-28T00:00:00",
                "lines": [
                    {
                        "gl_account_id": expense_account["id"],
                        "debit": 10.0,
                        "credit": 0.0,
                        "currency": "INR",
                        "transaction_currency": "USD",
                        "transaction_amount": 0.12,
                        "exchange_rate": 83.33,
                        "department_id": "ops",
                        "cost_center": "cc-ops",
                        "profit_center": "pc-branch",
                        "project_id": "proj-001",
                        "employee_id": "emp-001",
                        "product_id": "gold-loan",
                        "business_unit_id": "bu-lending",
                    },
                    {
                        "gl_account_id": cash_account["id"],
                        "debit": 0.0,
                        "credit": 10.0,
                        "currency": "INR",
                        "department_id": "ops",
                        "cost_center": "cc-ops",
                        "profit_center": "pc-branch",
                    },
                ],
            },
        )
        assert multi_currency_journal_response.status_code == 200
        db = accounting_main.SessionLocal()
        try:
            fx_line = (
                db.query(accounting_main.JournalLine)
                .join(accounting_main.JournalEntry)
                .filter(
                    accounting_main.JournalEntry.tenant_id == tenant_id,
                    accounting_main.JournalEntry.reference == "FX-DIM-001",
                    accounting_main.JournalLine.debit == 10.0,
                )
                .first()
            )
            assert fx_line is not None
            assert fx_line.transaction_currency == "USD"
            assert fx_line.department_id == "ops"
            assert fx_line.business_unit_id == "bu-lending"
        finally:
            db.close()

        freeze_response = await client.put(
            f"/gl-accounts/{expense_account['id']}",
            params={"tenant_id": tenant_id},
            json={"freeze_status": "freeze_debit"},
        )
        assert freeze_response.status_code == 200
        freeze_block_response = await client.post(
            "/posting-engine/validate",
            json={
                "tenant_id": tenant_id,
                "lines": [
                    {"gl_account_id": expense_account["id"], "debit": 5.0, "credit": 0.0},
                    {"gl_account_id": cash_account["id"], "debit": 0.0, "credit": 5.0},
                ],
            },
        )
        assert freeze_block_response.status_code == 400
        unfreeze_response = await client.put(
            f"/gl-accounts/{expense_account['id']}",
            params={"tenant_id": tenant_id},
            json={"freeze_status": "open"},
        )
        assert unfreeze_response.status_code == 200

        rollback_post_response = await client.post(
            "/gl-postings/auto",
            json={
                "tenant_id": tenant_id,
                "source_module": "deposits",
                "source_event": "deposit",
                "source_reference": "rollback-test-ref",
                "amount": 77.0,
                "metadata": {"note": "rollback smoke"},
            },
        )
        assert rollback_post_response.status_code == 200
        db = accounting_main.SessionLocal()
        try:
            execution = (
                db.query(accounting_main.PostingExecutionLog)
                .filter(
                    accounting_main.PostingExecutionLog.tenant_id == tenant_id,
                    accounting_main.PostingExecutionLog.source_reference == "rollback-test-ref",
                    accounting_main.PostingExecutionLog.status == "posted",
                )
                .first()
            )
            assert execution is not None
            rollback_execution_id = execution.id
        finally:
            db.close()
        rollback_response = await client.post(
            f"/posting-executions/{rollback_execution_id}/rollback",
            json={"tenant_id": tenant_id, "performed_by": "tester", "reason": "test rollback"},
        )
        assert rollback_response.status_code == 200
        assert rollback_response.json()["status"] == "rolled_back"
        assert len(rollback_response.json()["reversed_subledger_ids"]) == 1
        rollback_subledger_response = await client.get(
            "/sub-ledger-entries",
            params={"tenant_id": tenant_id, "source_reference": "rollback-test-ref"},
        )
        assert rollback_subledger_response.status_code == 200
        rollback_subledger_rows = rollback_subledger_response.json()
        assert {row["status"] for row in rollback_subledger_rows} == {"reversed", "reversal"}
        assert round(sum(row["amount"] for row in rollback_subledger_rows), 2) == 0.0

        period_response = await client.post(
            "/accounting-periods",
            json={
                "tenant_id": tenant_id,
                "financial_year": "2026-27",
                "period_name": "July 2026",
                "period_start": "2026-07-01T00:00:00",
                "period_end": "2026-07-31T23:59:59",
                "performed_by": "tester",
            },
        )
        assert period_response.status_code == 200
        period = period_response.json()
        lock_period_response = await client.post(
            f"/accounting-periods/{period['id']}/lock",
            json={"tenant_id": tenant_id, "performed_by": "finance", "reason": "month close"},
        )
        assert lock_period_response.status_code == 200
        locked_post_response = await client.post(
            "/journal-entries",
            json={
                "tenant_id": tenant_id,
                "description": "Blocked locked-period journal",
                "business_date": "2026-07-15T00:00:00",
                "lines": [
                    {"gl_account_id": expense_account["id"], "debit": 1.0, "credit": 0.0},
                    {"gl_account_id": cash_account["id"], "debit": 0.0, "credit": 1.0},
                ],
            },
        )
        assert locked_post_response.status_code == 400
        request_unlock_response = await client.post(
            f"/accounting-periods/{period['id']}/request-unlock",
            json={"tenant_id": tenant_id, "performed_by": "maker", "reason": "correction"},
        )
        assert request_unlock_response.status_code == 200
        assert request_unlock_response.json()["status"] == "pending_unlock"
        approve_unlock_response = await client.post(
            f"/accounting-periods/{period['id']}/approve-unlock",
            json={"tenant_id": tenant_id, "performed_by": "finance-head"},
        )
        assert approve_unlock_response.status_code == 200
        assert approve_unlock_response.json()["status"] == "open"

        event_response = await client.post(
            "/api/v1/accounting/events",
            json={
                "tenant_id": tenant_id,
                "event_type": "LOAN_DISBURSED",
                "source_module": "Loan",
                "reference_id": "LN-9001",
                "reference_number": "LD-9001",
                "business_date": "2026-07-16T00:00:00",
                "currency": "INR",
                "amount": 250000,
                "priority": "high",
                "dimensions": {"branch_id": "branch-001", "product_id": "gold-loan", "customer_id": "cust-001"},
                "payload": {"loan_id": "LN-9001", "customer_id": "cust-001", "amount": 250000},
                "created_by": "loan-service",
            },
        )
        assert event_response.status_code == 200
        accounting_event = event_response.json()
        assert accounting_event["status"] == "created"
        assert accounting_event["queue_status"] == "priority_queue"

        validate_event_response = await client.post(
            f"/api/v1/accounting/events/{accounting_event['id']}/validate",
            json={"tenant_id": tenant_id, "performed_by": "event-engine"},
        )
        assert validate_event_response.status_code == 200
        validated_event = validate_event_response.json()
        assert validated_event["validation_status"] == "passed"
        assert validated_event["status"] == "queued"
        assert validated_event["business_view"]["source_module"] == "Loan"

        event_list_response = await client.get(
            "/api/v1/accounting/events",
            params={"tenant_id": tenant_id, "source_module": "Loan"},
        )
        assert event_list_response.status_code == 200
        assert event_list_response.json()["total"] >= 1

        event_dashboard_response = await client.get(
            "/api/v1/accounting/events/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert event_dashboard_response.status_code == 200
        assert event_dashboard_response.json()["kpis"]["pending"] >= 1

        event_queue_response = await client.get(
            "/api/v1/accounting/events/queue",
            params={"tenant_id": tenant_id},
        )
        assert event_queue_response.status_code == 200
        assert any(item["id"] == accounting_event["id"] for item in event_queue_response.json()["items"])

        failed_event_response = await client.post(
            "/api/v1/accounting/events",
            json={
                "tenant_id": tenant_id,
                "event_type": "PURCHASE_ORDER_APPROVED",
                "source_module": "Procurement",
                "reference_id": "PO-FAIL-1",
                "business_date": "2026-07-17T00:00:00",
                "currency": "INR",
                "amount": 1000,
            },
        )
        assert failed_event_response.status_code == 200
        failed_event = failed_event_response.json()
        failed_validate_response = await client.post(
            f"/api/v1/accounting/events/{failed_event['id']}/validate",
            json={"tenant_id": tenant_id, "performed_by": "event-engine"},
        )
        assert failed_validate_response.status_code == 200
        assert failed_validate_response.json()["queue_status"] == "dead_letter_queue"

        retry_response = await client.post(
            f"/api/v1/accounting/events/{failed_event['id']}/retry",
            json={"tenant_id": tenant_id, "performed_by": "finance", "reason": "rule fix pending"},
        )
        assert retry_response.status_code == 200
        assert retry_response.json()["queue_status"] == "retry_queue"
        assert retry_response.json()["retry_count"] == 1

        replay_response = await client.post(
            f"/api/v1/accounting/events/{failed_event['id']}/replay",
            json={"tenant_id": tenant_id, "performed_by": "finance", "reason": "manual replay"},
        )
        assert replay_response.status_code == 200
        assert replay_response.json()["version"] == 2

        financial_year_response = await client.post(
            "/api/v1/accounting/calendar/years",
            json={
                "tenant_id": tenant_id,
                "year_code": "2028-29",
                "description": "Fiscal year 2028-29",
                "start_date": "2028-04-01T00:00:00",
                "end_date": "2029-03-31T23:59:59",
                "calendar_type": "fiscal",
                "status": "active",
                "calendars": ["Corporate", "Tax", "Treasury"],
                "performed_by": "tester",
            },
        )
        assert financial_year_response.status_code == 200
        financial_year = financial_year_response.json()
        assert financial_year["financial_year"]["year_code"] == "2028-29"
        assert financial_year["generated_count"] == 12

        calendar_dashboard_response = await client.get(
            "/api/v1/accounting/calendar/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert calendar_dashboard_response.status_code == 200
        assert calendar_dashboard_response.json()["kpis"]["open_periods"] >= 1

        years_response = await client.get(
            "/api/v1/accounting/calendar/years",
            params={"tenant_id": tenant_id},
        )
        assert years_response.status_code == 200
        assert any(item["year_code"] == "2028-29" for item in years_response.json()["items"])

        periods_response = await client.get(
            "/api/v1/accounting/calendar/periods",
            params={"tenant_id": tenant_id, "financial_year": "2028-29"},
        )
        assert periods_response.status_code == 200
        generated_period = periods_response.json()["items"][0]
        assert generated_period["posting_window"]["late_adjustments_allowed"] is False

        open_response = await client.post(
            f"/api/v1/accounting/calendar/periods/{generated_period['id']}/open",
            json={"tenant_id": tenant_id, "performed_by": "finance"},
        )
        assert open_response.status_code == 200
        assert open_response.json()["status"] == "open"

        soft_close_response = await client.post(
            f"/api/v1/accounting/calendar/periods/{generated_period['id']}/soft-close",
            json={"tenant_id": tenant_id, "performed_by": "finance"},
        )
        assert soft_close_response.status_code == 200
        assert soft_close_response.json()["status"] == "soft_close"

        eom_response = await client.post(
            "/api/v1/accounting/calendar/eom/execute",
            json={"tenant_id": tenant_id, "period_id": generated_period["id"], "performed_by": "finance-head"},
        )
        assert eom_response.status_code == 200
        assert eom_response.json()["event"] == "EOM_COMPLETED"
        assert eom_response.json()["period"]["status"] == "hard_close"

        reopen_response = await client.post(
            f"/api/v1/accounting/calendar/periods/{generated_period['id']}/reopen",
            json={"tenant_id": tenant_id, "performed_by": "cfo", "reason": "late adjustment"},
        )
        assert reopen_response.status_code == 200
        assert reopen_response.json()["status"] == "open"

        eod_response = await client.post(
            "/api/v1/accounting/calendar/eod/execute",
            json={
                "tenant_id": tenant_id,
                "business_date": "2026-06-27T00:00:00",
                "branch_id": "branch-fcpm",
                "performed_by": "tester",
            },
        )
        assert eod_response.status_code == 200
        assert eod_response.json()["event"] == "EOD_COMPLETED"

        eoy_response = await client.post(
            "/api/v1/accounting/calendar/eoy/execute",
            json={"tenant_id": tenant_id, "financial_year": "2028-29", "performed_by": "cfo"},
        )
        assert eoy_response.status_code == 200
        assert eoy_response.json()["event"] == "EOY_COMPLETED"
        assert eoy_response.json()["periods_archived"] == 12

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


async def _run_journal_engine_test():
    async with AsyncClient(
        transport=ASGITransport(app=accounting_main.app),
        base_url="http://testserver",
    ) as client:
        tenant_id = f"tenant-journal-{uuid4().hex[:8]}"

        expense_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "5100_SALARY_EXPENSE",
                "account_name": "Salary Expense",
                "account_type": "expense",
                "category": "Expenses",
            },
        )
        bank_response = await client.post(
            "/gl-accounts",
            json={
                "tenant_id": tenant_id,
                "account_code": "1120_BANK",
                "account_name": "Operating Bank",
                "account_type": "asset",
                "category": "Assets",
            },
        )
        assert expense_response.status_code == 200
        assert bank_response.status_code == 200
        expense_account = expense_response.json()
        bank_account = bank_response.json()

        for dimension_type, code, name in [
            ("branch", "BR-001", "Main Branch"),
            ("cost_center", "CC-HR", "Human Resources"),
        ]:
            dimension_response = await client.post(
                "/accounting-dimensions",
                json={
                    "tenant_id": tenant_id,
                    "dimension_type": dimension_type,
                    "code": code,
                    "name": name,
                },
            )
            assert dimension_response.status_code == 200

        batch_response = await client.post(
            "/journal-batches",
            json={
                "tenant_id": tenant_id,
                "posting_date": "2026-06-28T00:00:00",
                "financial_year": "2026-27",
                "created_by": "journal-maker",
            },
        )
        assert batch_response.status_code == 200
        batch = batch_response.json()
        assert batch["batch_no"] == "JBT-2026-000001"

        template_response = await client.post(
            "/journal-templates",
            json={
                "tenant_id": tenant_id,
                "template_name": "Monthly Salary",
                "description": "Salary expense paid from bank",
                "created_by": "journal-maker",
                "lines": [
                    {"account_code": "5100_SALARY_EXPENSE", "direction": "debit", "description": "Salary expense"},
                    {"account_code": "1120_BANK", "direction": "credit", "description": "Bank payment"},
                ],
            },
        )
        assert template_response.status_code == 200
        template = template_response.json()

        simulation_response = await client.post(
            "/journals/simulate",
            json={
                "tenant_id": tenant_id,
                "template_id": template["id"],
                "amount": 125000,
                "posting_date": "2026-06-28T00:00:00",
                "branch_id": "BR-001",
            },
        )
        assert simulation_response.status_code == 200
        simulation = simulation_response.json()
        assert simulation["valid"] is True
        assert simulation["total_debit"] == 125000
        assert simulation["impact"]["trial_balance"]["remains_balanced"] is True

        invalid_validation_response = await client.post(
            "/journals/validate",
            json={
                "tenant_id": tenant_id,
                "posting_date": "2026-06-28T00:00:00",
                "lines": [
                    {"gl_account_id": expense_account["id"], "debit": 100, "credit": 0},
                    {"gl_account_id": bank_account["id"], "debit": 0, "credit": 90},
                ],
            },
        )
        assert invalid_validation_response.status_code == 200
        assert invalid_validation_response.json()["valid"] is False

        journal_response = await client.post(
            "/journals",
            json={
                "tenant_id": tenant_id,
                "batch_id": batch["id"],
                "posting_date": "2026-06-28T00:00:00",
                "financial_year": "2026-27",
                "description": "June salary posting",
                "reference": "PAYROLL-2026-06",
                "branch_id": "BR-001",
                "created_by": "journal-maker",
                "template_id": template["id"],
                "attachments": [
                    {"document_id": "doc-payroll-001", "file_name": "payroll-june.pdf", "uploaded_by": "journal-maker"}
                ],
                "lines": [
                    {
                        "gl_account_id": expense_account["id"],
                        "debit": 125000,
                        "credit": 0,
                        "branch_id": "BR-001",
                        "cost_center": "CC-HR",
                        "description": "Salary expense",
                    },
                    {
                        "gl_account_id": bank_account["id"],
                        "debit": 0,
                        "credit": 125000,
                        "branch_id": "BR-001",
                        "cost_center": "CC-HR",
                        "description": "Bank payment",
                    },
                ],
            },
        )
        assert journal_response.status_code == 200
        journal = journal_response.json()
        assert journal["journal_no"] == "JRN-2026-00000001"
        assert journal["status"] == "draft"
        assert journal["validation_result"]["valid"] is True
        assert journal["attachments"][0]["file_name"] == "payroll-june.pdf"

        afc_dashboard_response = await client.get(
            "/api/v1/accounting/journals/dashboard",
            params={"tenant_id": tenant_id},
        )
        assert afc_dashboard_response.status_code == 200
        assert afc_dashboard_response.json()["kpis"]["draft"] == 1
        assert afc_dashboard_response.json()["kpis"]["journal_health"] >= 90

        afc_detail_response = await client.get(
            f"/api/v1/accounting/journals/{journal['id']}",
            params={"tenant_id": tenant_id},
        )
        assert afc_detail_response.status_code == 200
        assert afc_detail_response.json()["journal_number"] == "JRN-2026-00000001"
        assert afc_detail_response.json()["business_view"]["business_event"] == "manual_journal"
        assert afc_detail_response.json()["validation_summary"]["is_balanced"] is True

        afc_update_response = await client.put(
            f"/api/v1/accounting/journals/{journal['id']}",
            params={"tenant_id": tenant_id},
            json={
                "description": "June salary posting - reviewed",
                "performed_by": "journal-maker",
            },
        )
        assert afc_update_response.status_code == 200
        assert afc_update_response.json()["description"] == "June salary posting - reviewed"

        afc_search_response = await client.get(
            "/api/v1/accounting/journals/search",
            params={"tenant_id": tenant_id, "q": "PAYROLL", "min_amount": 100000},
        )
        assert afc_search_response.status_code == 200
        assert afc_search_response.json()["total"] == 1

        submit_response = await client.post(
            f"/journals/{journal['id']}/submit",
            json={"tenant_id": tenant_id, "performed_by": "journal-maker", "remarks": "Ready for review"},
        )
        assert submit_response.status_code == 200
        assert submit_response.json()["status"] == "pending"

        self_approval_response = await client.post(
            f"/journals/{journal['id']}/approve",
            json={"tenant_id": tenant_id, "performed_by": "journal-maker", "decision": "approved"},
        )
        assert self_approval_response.status_code == 400

        approval_response = await client.post(
            f"/api/v1/accounting/journals/{journal['id']}/approve",
            json={
                "tenant_id": tenant_id,
                "performed_by": "journal-checker",
                "decision": "approved",
                "remarks": "Payroll control totals checked",
            },
        )
        assert approval_response.status_code == 200
        assert approval_response.json()["status"] == "approved"
        assert approval_response.json()["approved_by"] == "journal-checker"

        post_response = await client.post(
            f"/api/v1/accounting/journals/{journal['id']}/post",
            json={"tenant_id": tenant_id, "performed_by": "finance-head"},
        )
        assert post_response.status_code == 200
        posted = post_response.json()
        assert posted["status"] == "posted"
        assert posted["voucher_id"]

        db = accounting_main.SessionLocal()
        try:
            voucher = db.query(accounting_main.Voucher).filter(
                accounting_main.Voucher.id == posted["voucher_id"]
            ).first()
            assert voucher is not None
            assert voucher.posted_journal_entry_id == journal["id"]
            assert voucher.status == "posted"
        finally:
            db.close()

        history_response = await client.get(
            "/journals/history",
            params={"tenant_id": tenant_id, "journal_id": journal["id"]},
        )
        assert history_response.status_code == 200
        history_actions = {item["action"] for item in history_response.json()["items"]}
        assert {"create", "submit", "approved", "post"}.issubset(history_actions)

        reverse_response = await client.post(
            f"/api/v1/accounting/journals/{journal['id']}/reverse",
            json={"tenant_id": tenant_id, "performed_by": "finance-head", "remarks": "Controlled reversal test"},
        )
        assert reverse_response.status_code == 200
        reversal_result = reverse_response.json()
        assert reversal_result["journal"]["status"] == "reversed"
        assert reversal_result["reversal"]["status"] == "posted"
        assert reversal_result["reversal"]["reversal_of"] == journal["id"]
        assert reversal_result["reversal"]["journal_no"] == "JRN-2026-00000002"

        db = accounting_main.SessionLocal()
        try:
            refreshed_expense = db.query(accounting_main.GLAccount).filter(
                accounting_main.GLAccount.id == expense_account["id"]
            ).first()
            refreshed_bank = db.query(accounting_main.GLAccount).filter(
                accounting_main.GLAccount.id == bank_account["id"]
            ).first()
            assert refreshed_expense.balance == 0
            assert refreshed_bank.balance == 0
        finally:
            db.close()

        cancellable_response = await client.post(
            "/journals",
            json={
                "tenant_id": tenant_id,
                "posting_date": "2026-06-28T00:00:00",
                "description": "Journal to cancel",
                "created_by": "journal-maker",
                "lines": [
                    {"gl_account_id": expense_account["id"], "debit": 1, "credit": 0},
                    {"gl_account_id": bank_account["id"], "debit": 0, "credit": 1},
                ],
            },
        )
        assert cancellable_response.status_code == 200
        cancellable = cancellable_response.json()
        cancel_response = await client.post(
            f"/journals/{cancellable['id']}/cancel",
            json={"tenant_id": tenant_id, "performed_by": "journal-maker", "remarks": "Duplicate draft"},
        )
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "cancelled"

        journal_list_response = await client.get("/journals", params={"tenant_id": tenant_id})
        assert journal_list_response.status_code == 200
        journal_list = journal_list_response.json()
        assert journal_list["total"] == 3
        assert journal_list["status_counts"]["reversed"] == 1
        assert journal_list["status_counts"]["posted"] == 1
        assert journal_list["status_counts"]["cancelled"] == 1

        afc_list_response = await client.get("/api/v1/accounting/journals", params={"tenant_id": tenant_id})
        assert afc_list_response.status_code == 200
        assert afc_list_response.json()["total"] == 3
        assert afc_list_response.json()["status_counts"]["reversed"] == 1

        batches_response = await client.get("/journal-batches", params={"tenant_id": tenant_id})
        assert batches_response.status_code == 200
        assert batches_response.json()["items"][0]["total_amount"] == 125000


def test_enterprise_journal_engine_lifecycle():
    asyncio.run(_run_journal_engine_test())
