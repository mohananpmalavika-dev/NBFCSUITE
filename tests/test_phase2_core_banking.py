import asyncio
import os
from datetime import date, datetime
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
    AttendanceRecordCreate,
    Base as HrmsBase,
    DepartmentCreate,
    DesignationCreate,
    EmployeeCreate,
    GradeCreate,
    LeaveDecision,
    LeaveRequestCreate,
    PositionCreate,
    SessionLocal as HrmsSessionLocal,
    create_attendance_record,
    create_department,
    create_designation,
    create_employee,
    create_grade,
    create_leave_request,
    create_position,
    decide_leave_request,
    engine as hrms_engine,
    get_employee,
    list_attendance_records,
    list_employees,
    list_leave_requests,
    list_positions,
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


def test_hrms_organization_setup_position_occupancy_flow():
    HrmsBase.metadata.drop_all(bind=hrms_engine)
    HrmsBase.metadata.create_all(bind=hrms_engine)
    db = HrmsSessionLocal()
    try:
        department = run(
            create_department(
                DepartmentCreate(
                    tenant_id="tenant-a",
                    department_code="COLL",
                    department_name="Collections",
                    cost_center_code="CC-COLL",
                    profit_center_code="PC-COLL",
                    annual_budget=2500000,
                ),
                db,
            )
        )
        grade = run(
            create_grade(
                GradeCreate(
                    tenant_id="tenant-a",
                    grade_code="M1",
                    grade_name="Manager 1",
                    salary_band_min=600000,
                    salary_band_max=1200000,
                    leave_entitlement_days=24,
                    approval_limit=100000,
                    travel_class="Economy",
                ),
                db,
            )
        )
        designation = run(
            create_designation(
                DesignationCreate(
                    tenant_id="tenant-a",
                    designation_code="BR-MGR",
                    designation_name="Branch Manager",
                    grade_id=grade.id,
                    approval_limit=100000,
                    reporting_level=4,
                ),
                db,
            )
        )
        position = run(
            create_position(
                PositionCreate(
                    tenant_id="tenant-a",
                    position_code="POS-BM-001",
                    position_title="Branch Manager",
                    department_id=department.id,
                    designation_id=designation.id,
                    branch_id="branch-1",
                ),
                db,
            )
        )
        assert position.status == "open"

        employee = run(
            create_employee(
                EmployeeCreate(
                    tenant_id="tenant-a",
                    employee_number="EMP-BM-1",
                    first_name="Meera",
                    last_name="Iyer",
                    email="meera.iyer@example.com",
                    phone="9999999010",
                    department_id=department.id,
                    designation_id=designation.id,
                    position_id=position.id,
                    branch_id="branch-1",
                ),
                db,
            )
        )

        assert employee.department == "Collections"
        assert employee.designation == "Branch Manager"
        assert employee.position_id == position.id

        positions = run(
            list_positions(
                tenant_id="tenant-a",
                branch_id="branch-1",
                department_id=department.id,
                status="occupied",
                db=db,
            )
        )
        assert len(positions) == 1
        assert positions[0].occupied_by_employee_id == employee.id
    finally:
        db.close()


def test_hrms_attendance_leave_and_branch_scope_flow():
    HrmsBase.metadata.drop_all(bind=hrms_engine)
    HrmsBase.metadata.create_all(bind=hrms_engine)
    db = HrmsSessionLocal()
    scoped_claims = {"tenant_id": "tenant-a", "branch_id": "branch-1", "area_id": "area-1"}
    try:
        employee = run(
            create_employee(
                EmployeeCreate(
                    tenant_id="tenant-a",
                    employee_number="EMP-SCOPE-1",
                    first_name="Dev",
                    last_name="Nair",
                    email="dev.nair@example.com",
                    phone="9999999011",
                    designation="Operations Officer",
                    department="Operations",
                    area_id="area-1",
                    branch_id="branch-1",
                ),
                db,
                user_claims=scoped_claims,
            )
        )

        attendance = run(
            create_attendance_record(
                AttendanceRecordCreate(
                    tenant_id="tenant-a",
                    employee_id=employee.id,
                    attendance_date=date(2026, 6, 28),
                    check_in_at=datetime(2026, 6, 28, 9, 30),
                    check_out_at=datetime(2026, 6, 28, 18, 0),
                    notes="Branch opening shift",
                ),
                db,
                user_claims=scoped_claims,
            )
        )
        assert attendance.branch_id == "branch-1"
        assert attendance.work_hours == 8.5

        attendance_list = run(
            list_attendance_records(
                tenant_id="tenant-a",
                employee_id=None,
                organization_id=None,
                zone_id=None,
                region_id=None,
                area_id=None,
                branch_id=None,
                status="present",
                start_date=date(2026, 6, 1),
                end_date=date(2026, 6, 30),
                skip=0,
                limit=50,
                db=db,
                user_claims=scoped_claims,
            )
        )
        assert attendance_list["total"] == 1

        leave_request = run(
            create_leave_request(
                LeaveRequestCreate(
                    tenant_id="tenant-a",
                    employee_id=employee.id,
                    leave_type="earned",
                    start_date=date(2026, 7, 1),
                    end_date=date(2026, 7, 3),
                    reason="Family travel",
                ),
                db,
                user_claims=scoped_claims,
            )
        )
        assert leave_request.total_days == 3
        assert leave_request.status == "pending"

        approved = run(
            decide_leave_request(
                leave_request.id,
                LeaveDecision(status="approved", approver_employee_id=employee.id, decision_notes="Approved"),
                tenant_id="tenant-a",
                db=db,
                user_claims=scoped_claims,
            )
        )
        assert approved.status == "approved"

        leave_list = run(
            list_leave_requests(
                tenant_id="tenant-a",
                employee_id=employee.id,
                organization_id=None,
                zone_id=None,
                region_id=None,
                area_id=None,
                branch_id=None,
                status="approved",
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 31),
                skip=0,
                limit=50,
                db=db,
                user_claims=scoped_claims,
            )
        )
        assert leave_list["total"] == 1
    finally:
        db.close()
