import asyncio
import os
from datetime import datetime
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/phase2_core_banking_test.db"
os.environ["FINDNA_BASE_URL"] = "http://127.0.0.1:1"

db_path = Path("C:/tmp/phase2_core_banking_test.db")
if db_path.exists():
    db_path.unlink()

from services.collections.app.main import (
    Base as CollectionsBase,
    CollectionActivityCreate,
    CollectionAssignmentCreate,
    SessionLocal as CollectionsSessionLocal,
    create_assignment,
    engine as collections_engine,
    get_collection_status,
    list_assignments,
    log_activity,
    startup as collections_startup,
)
from services.deposits.app.main import (
    Base as DepositsBase,
    DepositAccountCreate,
    DepositTransactionCreate,
    SessionLocal as DepositsSessionLocal,
    create_deposit_account,
    create_deposit_transaction,
    engine as deposits_engine,
    get_account_statement,
    get_interest_schedule,
    startup as deposits_startup,
)
from services.hrms.app.main import (
    Base as HrmsBase,
    EmployeeCreate,
    SessionLocal as HrmsSessionLocal,
    create_employee,
    engine as hrms_engine,
    get_employee,
    list_employees,
)


def run(coro):
    return asyncio.run(coro)


def test_deposit_account_transactions_interest_and_statement_flow():
    DepositsBase.metadata.drop_all(bind=deposits_engine)
    run(deposits_startup())
    db = DepositsSessionLocal()
    try:
        account = run(
            create_deposit_account(
                DepositAccountCreate(
                    customer_id="customer-1",
                    deposit_type_code="FD",
                    principal_amount=100000,
                    start_date=datetime(2026, 1, 1),
                ),
                db,
            )
        )
        assert account.account_number.startswith("DA-")
        assert account.current_balance == 100000

        credit = run(
            create_deposit_transaction(
                account.id,
                DepositTransactionCreate(
                    transaction_type="credit",
                    amount=5000,
                    description="Top-up",
                    reference="DEP-1",
                    transaction_date=datetime(2026, 2, 1),
                ),
                db,
            )
        )
        assert credit.running_balance == 105000

        debit = run(
            create_deposit_transaction(
                account.id,
                DepositTransactionCreate(
                    transaction_type="debit",
                    amount=2500,
                    description="Premature withdrawal charge",
                    reference="WDL-1",
                    transaction_date=datetime(2026, 2, 5),
                ),
                db,
            )
        )
        assert debit.running_balance == 102500

        statement = run(
            get_account_statement(
                account.id,
                datetime(2026, 1, 1),
                datetime(2026, 2, 28),
                db,
            )
        )
        assert statement["opening_balance"] == 100000
        assert statement["closing_balance"] == 102500
        assert len(statement["transactions"]) == 2

        schedule = run(get_interest_schedule(account.id, db))
        assert schedule.total_interest > 0
        assert schedule.maturity_amount > account.principal_amount
    finally:
        db.close()


def test_collections_auto_bucket_assignment_and_activity_flow():
    CollectionsBase.metadata.drop_all(bind=collections_engine)
    run(collections_startup())
    db = CollectionsSessionLocal()
    try:
        assignment = run(
            create_assignment(
                CollectionAssignmentCreate(
                    loan_account_id="loan-1",
                    customer_id="customer-1",
                    collector_user_id="collector-1",
                    branch_id="branch-1",
                    days_past_due=45,
                    outstanding_amount=25000,
                    priority="high",
                ),
                db,
            )
        )
        assert assignment.bucket_name == "30-60 DPD"
        assert assignment.branch_id == "branch-1"

        activity = run(
            log_activity(
                "loan-1",
                CollectionActivityCreate(
                    activity_type="call",
                    notes="Customer promised to pay next week",
                    promised_amount=5000,
                    promised_date=datetime(2026, 3, 15),
                    customer_response="committed",
                ),
                db,
            )
        )
        assert activity["message"] == "Activity logged successfully"

        status = run(get_collection_status("loan-1", db))
        assert status["bucket_name"] == "30-60 DPD"
        assert status["latest_activity"].customer_response == "committed"

        scoped = run(
            list_assignments(
                collector_id=None,
                branch_id="branch-1",
                status="active",
                skip=0,
                limit=10,
                db=db,
            )
        )
        assert scoped["total"] == 1
    finally:
        db.close()


def test_hrms_employee_master_branch_and_user_mapping():
    HrmsBase.metadata.drop_all(bind=hrms_engine)
    HrmsBase.metadata.create_all(bind=hrms_engine)
    db = HrmsSessionLocal()
    try:
        employee = run(
            create_employee(
                EmployeeCreate(
                    employee_number="EMP-001",
                    first_name="Anika",
                    last_name="Rao",
                    email="anika.rao@example.com",
                    phone="9999999002",
                    designation="Collection Officer",
                    department="Collections",
                    branch_id="branch-1",
                    user_id="collector-1",
                    joining_date=datetime(2026, 1, 10),
                ),
                db,
            )
        )
        assert employee.status == "active"
        assert employee.branch_id == "branch-1"
        assert employee.user_id == "collector-1"

        fetched = run(get_employee(employee.id, db))
        assert fetched.employee_number == "EMP-001"

        employees = run(
            list_employees(
                branch_id="branch-1",
                department="Collections",
                status="active",
                skip=0,
                limit=50,
                db=db,
            )
        )
        assert employees["total"] == 1
    finally:
        db.close()
