import asyncio
import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/phase1_lending_test.db"
os.environ["FINDNA_BASE_URL"] = "http://127.0.0.1:1"
os.environ["LMS_BASE_URL"] = "http://127.0.0.1:1"
os.environ["LOS_BASE_URL"] = "http://127.0.0.1:1"
os.environ["COLLECTIONS_BASE_URL"] = "http://127.0.0.1:1"

db_path = Path("C:/tmp/phase1_lending_test.db")
if db_path.exists():
    db_path.unlink()

from fastapi import HTTPException
from sqlalchemy import text

from services.los.app.main import (
    Base as LosBase,
    LoanApplicationCreate,
    SessionLocal as LosSessionLocal,
    UnderwritingDecisionRequest,
    create_application,
    decide_application,
    engine as los_engine,
    startup as los_startup,
    submit_application,
    underwrite_application,
)
from services.lms.app.main import (
    Base as LmsBase,
    DisbursementRequest,
    LoanAccountCreate,
    PaymentRequest,
    SessionLocal as LmsSessionLocal,
    create_loan,
    disburse_loan,
    engine as lms_engine,
    record_payment,
)


def run(coro):
    return asyncio.run(coro)


def test_los_application_rules_and_decision_flow():
    LosBase.metadata.drop_all(bind=los_engine)
    run(los_startup())
    db = LosSessionLocal()
    try:
        try:
            run(
                create_application(
                    LoanApplicationCreate(
                        customer_id="customer-1",
                        product_code="PERSONAL_LOAN",
                        applied_amount=9999999,
                        tenure_months=24,
                    ),
                    db,
                )
            )
            assert False, "Expected product limit validation to fail"
        except HTTPException as exc:
            assert exc.status_code == 400

        application = run(
            create_application(
                LoanApplicationCreate(
                    customer_id="customer-1",
                    product_code="PERSONAL_LOAN",
                    applied_amount=200000,
                    tenure_months=24,
                ),
                db,
            )
        )
        assert application.application_status == "draft"

        submit_response = run(submit_application(application.id, db))
        assert submit_response["application_id"] == application.id

        scorecard = run(underwrite_application(application.id, db))
        assert scorecard.recommendation in {"approve", "review"}

        decision = run(
            decide_application(
                application.id,
                UnderwritingDecisionRequest(
                    decision="approved",
                    approved_amount=180000,
                    approved_tenure_months=24,
                    approved_interest_rate=14.5,
                ),
                db,
            )
        )
        assert decision.status == "approved"
        assert decision.sanctioned_amount == 180000
    finally:
        db.close()


def test_lms_booking_disbursement_schedule_and_payment_flow():
    LmsBase.metadata.drop_all(bind=lms_engine)
    LmsBase.metadata.create_all(bind=lms_engine)
    db = LmsSessionLocal()
    try:
        loan = run(
            create_loan(
                LoanAccountCreate(
                    application_id="application-1",
                    customer_id="customer-1",
                    product_id="prod-personal-loan",
                    sanction_amount=120000,
                    tenure_months=12,
                    interest_rate=12,
                ),
                db,
            )
        )
        assert loan.status == "sanctioned"
        assert loan.account_number.startswith("LA-")

        disbursement = run(
            disburse_loan(
                loan.id,
                DisbursementRequest(amount=120000, reference="UTR-1"),
                db,
            )
        )
        assert disbursement["disbursed_amount"] == 120000
        assert disbursement["status"] == "active"

        payment = run(
            record_payment(
                loan.id,
                PaymentRequest(amount=loan.emi_amount, payment_mode="upi", reference="PAY-1"),
                db,
            )
        )
        assert payment["status"] == "success"

        db.refresh(loan)
        assert loan.outstanding_principal < 120000
        first_emi = db.execute(
            text("SELECT status FROM emi_schedule WHERE loan_account_id = :loan_id AND emi_number = 1"),
            {"loan_id": loan.id},
        ).scalar_one()
        assert first_emi == "paid"
    finally:
        db.close()
