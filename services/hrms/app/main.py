from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, JSON, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    employee_number = Column(String, unique=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    designation = Column(String, index=True)
    department = Column(String, index=True)
    employment_type = Column(String, default="full_time")
    status = Column(String, default="active", index=True)
    joining_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    run_name = Column(String)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    status = Column(String, default="draft", index=True)
    gross_pay = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    net_pay = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    finalized_at = Column(DateTime, nullable=True)


class PayrollSlip(Base):
    __tablename__ = "payroll_slips"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    payroll_run_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    employee_number = Column(String)
    employee_name = Column(String)
    basic_pay = Column(Float, default=0.0)
    allowances = Column(JSON, nullable=True)
    deductions = Column(JSON, nullable=True)
    tax_amount = Column(Float, default=0.0)
    gross_pay = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    net_pay = Column(Float, default=0.0)
    status = Column(String, default="draft", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EmployeeCreate(BaseModel):
    tenant_id: str = "default"
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: str
    designation: str
    department: str
    branch_id: Optional[str] = None
    user_id: Optional[str] = None
    employment_type: str = "full_time"
    joining_date: Optional[datetime] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    branch_id: Optional[str] = None
    user_id: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: str
    tenant_id: str
    employee_number: str
    user_id: Optional[str]
    branch_id: Optional[str]
    first_name: str
    last_name: str
    email: str
    phone: str
    designation: str
    department: str
    employment_type: str
    status: str
    joining_date: Optional[datetime]

    class Config:
        from_attributes = True


class PayrollRunCreate(BaseModel):
    tenant_id: str
    run_name: Optional[str] = None
    period_start: datetime
    period_end: datetime


class PayrollRunResponse(BaseModel):
    id: str
    tenant_id: str
    run_name: Optional[str]
    period_start: datetime
    period_end: datetime
    status: str
    gross_pay: float
    total_deductions: float
    net_pay: float
    created_at: datetime
    finalized_at: Optional[datetime]

    class Config:
        from_attributes = True


class PayrollSlipCreate(BaseModel):
    tenant_id: str
    employee_id: str
    basic_pay: float = Field(gt=0)
    allowances: dict = Field(default_factory=dict)
    deductions: dict = Field(default_factory=dict)
    tax_amount: float = Field(default=0.0, ge=0)


class PayrollSlipResponse(BaseModel):
    id: str
    tenant_id: str
    payroll_run_id: str
    employee_id: str
    employee_number: str
    employee_name: str
    basic_pay: float
    allowances: Optional[dict]
    deductions: Optional[dict]
    tax_amount: float
    gross_pay: float
    total_deductions: float
    net_pay: float
    status: str

    class Config:
        from_attributes = True


app = FastAPI(title="hrms-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sum_components(components: dict) -> float:
    return round(sum(float(value or 0.0) for value in components.values()), 2)


def _recalculate_payroll_run(run: PayrollRun, db: Session) -> None:
    slips = db.query(PayrollSlip).filter(PayrollSlip.payroll_run_id == run.id, PayrollSlip.tenant_id == run.tenant_id).all()
    run.gross_pay = round(sum(slip.gross_pay or 0.0 for slip in slips), 2)
    run.total_deductions = round(sum(slip.total_deductions or 0.0 for slip in slips), 2)
    run.net_pay = round(sum(slip.net_pay or 0.0 for slip in slips), 2)


def _payroll_run(run_id: str, tenant_id: str, db: Session) -> PayrollRun:
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id, PayrollRun.tenant_id == tenant_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found for tenant")
    return run


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "hrms"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/employees", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Employee)
        .filter((Employee.employee_number == employee.employee_number) | (Employee.email == employee.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Employee number or email already exists")

    if employee.user_id:
        user_mapping = db.query(Employee).filter(Employee.user_id == employee.user_id).first()
        if user_mapping:
            raise HTTPException(status_code=400, detail="IAM user is already linked to an employee")

    db_employee = Employee(
        id=str(uuid4()),
        tenant_id=employee.tenant_id,
        employee_number=employee.employee_number,
        user_id=employee.user_id,
        branch_id=employee.branch_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        designation=employee.designation,
        department=employee.department,
        employment_type=employee.employment_type,
        joining_date=employee.joining_date or datetime.utcnow(),
        status="active",
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.get("/employees")
async def list_employees(
    tenant_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)
    if tenant_id:
        query = query.filter(Employee.tenant_id == tenant_id)
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    if department:
        query = query.filter(Employee.department == department)
    if status:
        query = query.filter(Employee.status == status)

    total = query.count()
    employees = query.order_by(Employee.created_at.desc()).offset(skip).limit(limit).all()
    return {"items": employees, "skip": skip, "limit": limit, "total": total}


@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post("/payroll/runs", response_model=PayrollRunResponse)
async def create_payroll_run(payload: PayrollRunCreate, db: Session = Depends(get_db)):
    if payload.period_end < payload.period_start:
        raise HTTPException(status_code=400, detail="period_end must be after period_start")
    run = PayrollRun(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        run_name=payload.run_name or f"Payroll {payload.period_start.date()} to {payload.period_end.date()}",
        period_start=payload.period_start,
        period_end=payload.period_end,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@app.get("/payroll/runs", response_model=List[PayrollRunResponse])
async def list_payroll_runs(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PayrollRun).filter(PayrollRun.tenant_id == tenant_id)
    if status:
        query = query.filter(PayrollRun.status == status)
    return query.order_by(PayrollRun.created_at.desc()).all()


@app.post("/payroll/runs/{run_id}/slips", response_model=PayrollSlipResponse)
async def add_payroll_slip(run_id: str, payload: PayrollSlipCreate, db: Session = Depends(get_db)):
    run = _payroll_run(run_id, payload.tenant_id, db)
    if run.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft payroll runs can be edited")
    employee = (
        db.query(Employee)
        .filter(Employee.id == payload.employee_id, Employee.tenant_id == payload.tenant_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for tenant")
    existing = (
        db.query(PayrollSlip)
        .filter(
            PayrollSlip.tenant_id == payload.tenant_id,
            PayrollSlip.payroll_run_id == run_id,
            PayrollSlip.employee_id == payload.employee_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Payroll slip already exists for employee in this run")

    allowance_total = _sum_components(payload.allowances)
    deduction_total = _sum_components(payload.deductions)
    gross_pay = round(payload.basic_pay + allowance_total, 2)
    total_deductions = round(deduction_total + payload.tax_amount, 2)
    slip = PayrollSlip(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        payroll_run_id=run.id,
        employee_id=employee.id,
        employee_number=employee.employee_number,
        employee_name=f"{employee.first_name} {employee.last_name}",
        basic_pay=payload.basic_pay,
        allowances=payload.allowances,
        deductions=payload.deductions,
        tax_amount=payload.tax_amount,
        gross_pay=gross_pay,
        total_deductions=total_deductions,
        net_pay=round(gross_pay - total_deductions, 2),
    )
    db.add(slip)
    db.flush()
    _recalculate_payroll_run(run, db)
    db.commit()
    db.refresh(slip)
    return slip


@app.get("/payroll/runs/{run_id}/slips", response_model=List[PayrollSlipResponse])
async def list_payroll_slips(run_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    _payroll_run(run_id, tenant_id, db)
    return (
        db.query(PayrollSlip)
        .filter(PayrollSlip.payroll_run_id == run_id, PayrollSlip.tenant_id == tenant_id)
        .order_by(PayrollSlip.employee_number.asc())
        .all()
    )


@app.post("/payroll/runs/{run_id}/finalize", response_model=PayrollRunResponse)
async def finalize_payroll_run(run_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    run = _payroll_run(run_id, tenant_id, db)
    if run.status == "finalized":
        return run
    slips = db.query(PayrollSlip).filter(PayrollSlip.payroll_run_id == run.id, PayrollSlip.tenant_id == tenant_id).all()
    if not slips:
        raise HTTPException(status_code=400, detail="Cannot finalize payroll run without slips")
    _recalculate_payroll_run(run, db)
    run.status = "finalized"
    run.finalized_at = datetime.utcnow()
    for slip in slips:
        slip.status = "finalized"
    db.commit()
    db.refresh(run)
    return run


@app.get("/payroll/summary")
async def payroll_summary(
    tenant_id: str = Query(...),
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PayrollRun).filter(PayrollRun.tenant_id == tenant_id)
    if period_start:
        query = query.filter(PayrollRun.period_end >= period_start)
    if period_end:
        query = query.filter(PayrollRun.period_start <= period_end)
    runs = query.all()
    return {
        "tenant_id": tenant_id,
        "run_count": len(runs),
        "gross_pay": round(sum(run.gross_pay or 0.0 for run in runs), 2),
        "total_deductions": round(sum(run.total_deductions or 0.0 for run in runs), 2),
        "net_pay": round(sum(run.net_pay or 0.0 for run in runs), 2),
        "finalized_runs": sum(1 for run in runs if run.status == "finalized"),
    }


@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: str, update: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = update.model_dump(exclude_unset=True)
    if "user_id" in update_data and update_data["user_id"]:
        existing = (
            db.query(Employee)
            .filter(Employee.user_id == update_data["user_id"], Employee.id != employee_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="IAM user is already linked to an employee")

    for key, value in update_data.items():
        setattr(employee, key, value)
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    return employee


@app.post("/employees/{employee_id}/assign-branch", response_model=EmployeeResponse)
async def assign_employee_branch(
    employee_id: str,
    branch_id: str = Query(...),
    db: Session = Depends(get_db),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.branch_id = branch_id
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    return employee


@app.get("/")
async def root():
    return {"service": "hrms", "version": "0.1.0"}
