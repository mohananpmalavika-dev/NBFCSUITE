import asyncio
import os
from datetime import datetime
from pathlib import Path


os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/phase5_full_suite_test.db"

db_path = Path("C:/tmp/phase5_full_suite_test.db")
if db_path.exists():
    db_path.unlink()

from services.findna.app.main import (
    AIModelFeedbackCreate,
    AIModelVersionCreate,
    AITrainingDatasetCreate,
    AITrainingRunCreate,
    Base as FindnaBase,
    SessionLocal as FindnaSessionLocal,
    capture_model_feedback,
    continuous_improvement_summary,
    create_model_version,
    create_training_dataset,
    create_training_run,
    engine as findna_engine,
    promote_model_version,
)
from services.hrms.app.main import (
    Base as HrmsBase,
    EmployeeCreate,
    PayrollRunCreate,
    PayrollSlipCreate,
    SessionLocal as HrmsSessionLocal,
    add_payroll_slip,
    create_employee,
    create_payroll_run,
    engine as hrms_engine,
    finalize_payroll_run,
    payroll_summary,
)
from services.insurance.app.main import (
    Base as InsuranceBase,
    ClaimCreate,
    ClaimDecision,
    PolicyCreate,
    PremiumPaymentCreate,
    SessionLocal as InsuranceSessionLocal,
    collect_premium,
    create_policy,
    decide_claim,
    engine as insurance_engine,
    submit_claim,
)
from services.procurement.app.main import (
    Base as ProcurementBase,
    GoodsReceiptCreate,
    InvoicePaymentRequest,
    PurchaseOrderCreate,
    PurchaseOrderItem,
    SessionLocal as ProcurementSessionLocal,
    VendorCreate,
    VendorInvoiceCreate,
    approve_purchase_order,
    create_purchase_order,
    create_vendor,
    create_vendor_invoice,
    engine as procurement_engine,
    mark_invoice_paid,
    receive_goods,
)
from services.wealth.app.main import (
    Base as WealthBase,
    InvestmentCreate,
    SIPCreate,
    SchemeCreate,
    SessionLocal as WealthSessionLocal,
    create_investment,
    create_scheme,
    create_sip,
    engine as wealth_engine,
    portfolio,
    run_sip,
)


def run(coro):
    return asyncio.run(coro)


def test_wealth_management_mutual_fund_sip_and_portfolio():
    WealthBase.metadata.drop_all(bind=wealth_engine)
    WealthBase.metadata.create_all(bind=wealth_engine)
    db = WealthSessionLocal()
    try:
        scheme = run(
            create_scheme(
                SchemeCreate(
                    tenant_id="tenant-a",
                    scheme_code="MF-LIQUID",
                    scheme_name="Liquid Fund",
                    fund_house="NBFCSuite AMC",
                    category="debt",
                    nav=25.0,
                ),
                db,
            )
        )
        assert scheme.scheme_code == "MF-LIQUID"

        investment = run(
            create_investment(
                InvestmentCreate(
                    tenant_id="tenant-a",
                    customer_id="customer-1",
                    scheme_code="MF-LIQUID",
                    amount=2500,
                ),
                db,
            )
        )
        assert investment.units == 100

        sip = run(
            create_sip(
                SIPCreate(
                    tenant_id="tenant-a",
                    customer_id="customer-1",
                    scheme_code="MF-LIQUID",
                    amount=1000,
                ),
                db,
            )
        )
        run(run_sip(sip.id, tenant_id="tenant-a", db=db))

        result = run(portfolio("customer-1", tenant_id="tenant-a", db=db))
        assert result["current_value"] == 3500
        assert result["allocation_by_category"]["debt"] == 3500
    finally:
        db.close()


def test_insurance_policy_premium_and_claim_flow():
    InsuranceBase.metadata.drop_all(bind=insurance_engine)
    InsuranceBase.metadata.create_all(bind=insurance_engine)
    db = InsuranceSessionLocal()
    try:
        policy = run(
            create_policy(
                PolicyCreate(
                    tenant_id="tenant-a",
                    customer_id="customer-1",
                    product_type="life",
                    insurer_name="NBFCSuite Insurance",
                    sum_assured=100000,
                    premium_amount=1200,
                ),
                db,
            )
        )
        payment = run(
            collect_premium(
                policy["id"],
                PremiumPaymentCreate(tenant_id="tenant-a", payment_mode="upi"),
                db,
            )
        )
        assert payment.amount == 1200

        claim = run(
            submit_claim(
                policy["id"],
                ClaimCreate(
                    tenant_id="tenant-a",
                    claim_type="life",
                    claim_amount=50000,
                    incident_date=datetime(2026, 6, 1),
                ),
                db,
            )
        )
        decided = run(
            decide_claim(
                claim.id,
                ClaimDecision(status="approved", approved_amount=45000),
                tenant_id="tenant-a",
                db=db,
            )
        )
        assert decided.status == "approved"
        assert decided.approved_amount == 45000
    finally:
        db.close()


def test_procurement_vendor_po_receipt_invoice_flow():
    ProcurementBase.metadata.drop_all(bind=procurement_engine)
    ProcurementBase.metadata.create_all(bind=procurement_engine)
    db = ProcurementSessionLocal()
    try:
        vendor = run(
            create_vendor(
                VendorCreate(
                    tenant_id="tenant-a",
                    vendor_code="VEND-IT",
                    vendor_name="IT Supplies",
                ),
                db,
            )
        )
        assert vendor["vendor_code"] == "VEND-IT"

        po = run(
            create_purchase_order(
                PurchaseOrderCreate(
                    tenant_id="tenant-a",
                    vendor_code="VEND-IT",
                    department="IT",
                    items=[
                        PurchaseOrderItem(
                            description="Laptop",
                            quantity=2,
                            unit_price=50000,
                            tax_rate_percent=18,
                        )
                    ],
                ),
                db,
            )
        )
        assert po.total_amount == 118000

        approved = run(approve_purchase_order(po.id, tenant_id="tenant-a", db=db))
        assert approved.status == "approved"
        receipt = run(
            receive_goods(
                po.id,
                GoodsReceiptCreate(
                    tenant_id="tenant-a",
                    received_by="employee-1",
                    received_items=[{"description": "Laptop", "quantity": 2}],
                ),
                db,
            )
        )
        assert receipt.status == "received"

        invoice = run(
            create_vendor_invoice(
                VendorInvoiceCreate(
                    tenant_id="tenant-a",
                    vendor_code="VEND-IT",
                    invoice_number="INV-IT-1",
                    amount=100000,
                    tax_amount=18000,
                    po_id=po.id,
                ),
                db,
            )
        )
        paid = run(
            mark_invoice_paid(
                invoice.id,
                InvoicePaymentRequest(tenant_id="tenant-a", payment_reference="PAY-1"),
                db,
            )
        )
        assert paid.status == "paid"
    finally:
        db.close()


def test_hrms_payroll_run_slip_finalize_and_summary():
    HrmsBase.metadata.drop_all(bind=hrms_engine)
    HrmsBase.metadata.create_all(bind=hrms_engine)
    db = HrmsSessionLocal()
    try:
        employee = run(
            create_employee(
                EmployeeCreate(
                    tenant_id="tenant-a",
                    employee_number="EMP-1",
                    first_name="Asha",
                    last_name="Rao",
                    email="asha@example.com",
                    phone="9999999999",
                    designation="Manager",
                    department="Operations",
                ),
                db,
            )
        )
        payroll_run = run(
            create_payroll_run(
                PayrollRunCreate(
                    tenant_id="tenant-a",
                    period_start=datetime(2026, 6, 1),
                    period_end=datetime(2026, 6, 30),
                ),
                db,
            )
        )
        slip = run(
            add_payroll_slip(
                payroll_run.id,
                PayrollSlipCreate(
                    tenant_id="tenant-a",
                    employee_id=employee.id,
                    basic_pay=50000,
                    allowances={"hra": 10000},
                    deductions={"pf": 5000},
                    tax_amount=3000,
                ),
                db,
            )
        )
        assert slip.net_pay == 52000
        finalized = run(finalize_payroll_run(payroll_run.id, tenant_id="tenant-a", db=db))
        assert finalized.status == "finalized"
        summary = run(payroll_summary(tenant_id="tenant-a", period_start=None, period_end=None, db=db))
        assert summary["net_pay"] == 52000
    finally:
        db.close()


def test_findna_ai_feedback_training_and_model_promotion_loop():
    FindnaBase.metadata.drop_all(bind=findna_engine)
    FindnaBase.metadata.create_all(bind=findna_engine)
    db = FindnaSessionLocal()
    try:
        dataset = run(
            create_training_dataset(
                AITrainingDatasetCreate(
                    dataset_name="credit-risk-june",
                    row_count=1000,
                    feature_schema={"features": ["behavior_score", "statement_score"]},
                    label_schema={"label": "default_90d"},
                ),
                db,
            )
        )
        model = run(
            create_model_version(
                AIModelVersionCreate(
                    model_name="credit-risk",
                    version="v2",
                    model_type="risk",
                    training_dataset_id=dataset.id,
                    metrics={"auc": 0.82},
                ),
                db,
            )
        )
        run(
            capture_model_feedback(
                AIModelFeedbackCreate(
                    model_name="credit-risk",
                    model_version="v2",
                    subject_type="loan_application",
                    subject_id="app-1",
                    prediction={"recommendation": "approve"},
                    actual_outcome={"default_90d": False},
                    feedback_source="lms",
                ),
                db,
            )
        )
        training_run = run(
            create_training_run(
                AITrainingRunCreate(
                    model_name="credit-risk",
                    dataset_id=dataset.id,
                    base_model_version="v1",
                    candidate_model_version="v2",
                    metrics={"auc": 0.82, "ks": 0.41},
                ),
                db,
            )
        )
        assert training_run.status == "completed"
        promoted = run(promote_model_version(model.id, db))
        assert promoted.status == "active"
        summary = run(continuous_improvement_summary(db))
        assert summary["feedback_count"] == 1
        assert summary["active_models"][0]["version"] == "v2"
    finally:
        db.close()
