from datetime import datetime
from typing import Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True)
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


class EmployeeCreate(BaseModel):
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


app = FastAPI(title="hrms-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    branch_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)
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
