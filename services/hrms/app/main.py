from datetime import date, datetime
from typing import List, Optional, Type
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, Date, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.organization.models.organization_unit import OrganizationUnit
from app.organization.models.organization_unit_audit import OrganizationUnitAudit
from app.organization.models.organization_unit_closure import OrganizationUnitClosure
from app.organization.routers.organization_unit import router as organization_router


class HRDepartment(Base):
    __tablename__ = "hr_departments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    department_code = Column(String, index=True, nullable=False)
    department_name = Column(String, nullable=False)
    parent_department_id = Column(String, index=True, nullable=True)
    department_head_employee_id = Column(String, index=True, nullable=True)
    cost_center_code = Column(String, index=True, nullable=True)
    profit_center_code = Column(String, index=True, nullable=True)
    budget_owner_employee_id = Column(String, index=True, nullable=True)
    annual_budget = Column(Float, default=0.0)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HRGrade(Base):
    __tablename__ = "hr_grades"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    grade_code = Column(String, index=True, nullable=False)
    grade_name = Column(String, nullable=False)
    salary_band_min = Column(Float, default=0.0)
    salary_band_max = Column(Float, default=0.0)
    leave_entitlement_days = Column(Integer, default=0)
    benefits = Column(JSON, nullable=True)
    approval_limit = Column(Float, default=0.0)
    travel_class = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HRDesignation(Base):
    __tablename__ = "hr_designations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    designation_code = Column(String, index=True, nullable=False)
    designation_name = Column(String, nullable=False)
    grade_id = Column(String, index=True, nullable=True)
    salary_band_min = Column(Float, default=0.0)
    salary_band_max = Column(Float, default=0.0)
    approval_limit = Column(Float, default=0.0)
    reporting_level = Column(Integer, default=0)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HRPosition(Base):
    __tablename__ = "hr_positions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    position_code = Column(String, index=True, nullable=False)
    position_title = Column(String, nullable=False)
    department_id = Column(String, index=True, nullable=True)
    designation_id = Column(String, index=True, nullable=True)
    grade_id = Column(String, index=True, nullable=True)
    job_role_id = Column(String, index=True, nullable=True)
    organization_unit_id = Column(String, index=True, nullable=True)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    reports_to_position_id = Column(String, index=True, nullable=True)
    occupied_by_employee_id = Column(String, index=True, nullable=True)
    approval_limit = Column(Float, default=0.0)
    budgeted_salary = Column(Float, default=0.0)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    status = Column(String, default="open", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobFamily(Base):
    __tablename__ = "hr_job_families"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    family_code = Column(String, index=True, nullable=False)
    family_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobRole(Base):
    __tablename__ = "hr_job_roles"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    role_code = Column(String, index=True, nullable=False)
    role_name = Column(String, nullable=False)
    job_family_id = Column(String, index=True, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeAssignment(Base):
    __tablename__ = "hr_employee_assignments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    employee_id = Column(String, index=True, nullable=False)
    position_id = Column(String, index=True, nullable=False)
    assignment_type = Column(String, default="primary", index=True)
    status = Column(String, default="active", index=True)
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=True)
    assigned_by = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeTimeline(Base):
    __tablename__ = "hr_employee_timelines"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    employee_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    event_title = Column(String, nullable=True)
    event_details = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    event_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    employee_number = Column(String, unique=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=True)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    designation = Column(String, index=True)
    department = Column(String, index=True)
    department_id = Column(String, index=True, nullable=True)
    designation_id = Column(String, index=True, nullable=True)
    grade_id = Column(String, index=True, nullable=True)
    position_id = Column(String, index=True, nullable=True)
    manager_employee_id = Column(String, index=True, nullable=True)
    official_email = Column(String, unique=True, index=True, nullable=True)
    employment_type = Column(String, default="full_time")
    status = Column(String, default="active", index=True)
    joining_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
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
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
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


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    employee_number = Column(String)
    employee_name = Column(String)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    attendance_date = Column(Date, index=True, nullable=False)
    check_in_at = Column(DateTime, nullable=True)
    check_out_at = Column(DateTime, nullable=True)
    status = Column(String, default="present", index=True)
    work_hours = Column(Float, default=0.0)


class HRShift(Base):
    __tablename__ = "hr_shifts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    shift_code = Column(String, index=True, nullable=False)
    shift_name = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    break_minutes = Column(Integer, default=0)
    grace_in = Column(Integer, default=0)
    grace_out = Column(Integer, default=0)
    weekly_off = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeShift(Base):
    __tablename__ = "hr_employee_shifts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    employee_id = Column(String, index=True, nullable=False)
    shift_id = Column(String, index=True, nullable=False)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Attendance(Base):
    __tablename__ = "hr_attendance"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    attendance_date = Column(Date, index=True, nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    working_hours = Column(Float, default=0.0)
    late_minutes = Column(Integer, default=0)
    early_exit_minutes = Column(Integer, default=0)
    overtime_minutes = Column(Integer, default=0)
    attendance_status = Column(String, default="present", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AttendanceLog(Base):
    __tablename__ = "hr_attendance_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    attendance_id = Column(String, index=True, nullable=True)
    device_ip = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow)


class LeaveType(Base):
    __tablename__ = "hr_leave_types"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    code = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_paid = Column(String, default="yes")
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class LeaveBalance(Base):
    __tablename__ = "hr_leave_balances"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    leave_type_id = Column(String, index=True, nullable=False)
    opening = Column(Float, default=0.0)
    credited = Column(Float, default=0.0)
    availed = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeaveApplication(Base):
    __tablename__ = "hr_leave_applications"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    leave_type_id = Column(String, index=True, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HolidayCalendar(Base):
    __tablename__ = "hr_holidays"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    holiday_name = Column(String, nullable=False)
    holiday_date = Column(Date, nullable=False)
    branch = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    employee_id = Column(String, index=True, nullable=False)
    employee_number = Column(String)
    employee_name = Column(String)
    organization_id = Column(String, index=True, nullable=True)
    zone_id = Column(String, index=True, nullable=True)
    region_id = Column(String, index=True, nullable=True)
    area_id = Column(String, index=True, nullable=True)
    branch_id = Column(String, index=True, nullable=True)
    leave_type = Column(String, index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Float, default=0.0)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    approver_employee_id = Column(String, index=True, nullable=True)
    decision_notes = Column(String, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)


class DepartmentCreate(BaseModel):
    tenant_id: str = "default"
    department_code: str
    department_name: str
    parent_department_id: Optional[str] = None
    department_head_employee_id: Optional[str] = None
    cost_center_code: Optional[str] = None
    profit_center_code: Optional[str] = None
    budget_owner_employee_id: Optional[str] = None
    annual_budget: float = Field(default=0.0, ge=0)


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = None
    parent_department_id: Optional[str] = None
    department_head_employee_id: Optional[str] = None
    cost_center_code: Optional[str] = None
    profit_center_code: Optional[str] = None
    budget_owner_employee_id: Optional[str] = None
    annual_budget: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = None


class DepartmentResponse(DepartmentCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentTreeResponse(DepartmentResponse):
    children: List["DepartmentTreeResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DepartmentBudgetResponse(BaseModel):
    department_id: str
    department_name: str
    tenant_id: str
    annual_budget: float
    cost_center_code: Optional[str] = None
    profit_center_code: Optional[str] = None
    budget_owner_employee_id: Optional[str] = None
    department_head_employee_id: Optional[str] = None
    department_head_name: Optional[str] = None
    total_positions: int
    open_positions: int
    occupied_positions: int
    total_employees: int


class DepartmentAnalyticsResponse(DepartmentBudgetResponse):
    active_employees: int
    status: str

    class Config:
        from_attributes = True


DepartmentTreeResponse.update_forward_refs()


class GradeCreate(BaseModel):
    tenant_id: str = "default"
    grade_code: str
    grade_name: str
    salary_band_min: float = Field(default=0.0, ge=0)
    salary_band_max: float = Field(default=0.0, ge=0)
    leave_entitlement_days: int = Field(default=0, ge=0)
    benefits: dict = Field(default_factory=dict)
    approval_limit: float = Field(default=0.0, ge=0)
    travel_class: Optional[str] = None


class GradeUpdate(BaseModel):
    grade_name: Optional[str] = None
    salary_band_min: Optional[float] = Field(default=None, ge=0)
    salary_band_max: Optional[float] = Field(default=None, ge=0)
    leave_entitlement_days: Optional[int] = Field(default=None, ge=0)
    benefits: Optional[dict] = None
    approval_limit: Optional[float] = Field(default=None, ge=0)
    travel_class: Optional[str] = None
    status: Optional[str] = None


class GradeResponse(GradeCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DesignationCreate(BaseModel):
    tenant_id: str = "default"
    designation_code: str
    designation_name: str
    grade_id: Optional[str] = None
    salary_band_min: float = Field(default=0.0, ge=0)
    salary_band_max: float = Field(default=0.0, ge=0)
    approval_limit: float = Field(default=0.0, ge=0)
    reporting_level: int = Field(default=0, ge=0)


class DesignationUpdate(BaseModel):
    designation_name: Optional[str] = None
    grade_id: Optional[str] = None
    salary_band_min: Optional[float] = Field(default=None, ge=0)
    salary_band_max: Optional[float] = Field(default=None, ge=0)
    approval_limit: Optional[float] = Field(default=None, ge=0)
    reporting_level: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = None


class DesignationResponse(DesignationCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    tenant_id: str = "default"
    position_code: str
    position_title: str
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    grade_id: Optional[str] = None
    job_role_id: Optional[str] = None
    organization_unit_id: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None
    reports_to_position_id: Optional[str] = None
    approval_limit: float = Field(default=0.0, ge=0)
    budgeted_salary: Optional[float] = Field(default=None, ge=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class PositionUpdate(BaseModel):
    position_title: Optional[str] = None
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    grade_id: Optional[str] = None
    job_role_id: Optional[str] = None
    organization_unit_id: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None
    reports_to_position_id: Optional[str] = None
    occupied_by_employee_id: Optional[str] = None
    approval_limit: Optional[float] = Field(default=None, ge=0)
    budgeted_salary: Optional[float] = Field(default=None, ge=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    status: Optional[str] = None


class PositionResponse(PositionCreate):
    id: str
    occupied_by_employee_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeCreate(BaseModel):
    tenant_id: str = "default"
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: str
    designation: str = ""
    department: str = ""
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    grade_id: Optional[str] = None
    position_id: Optional[str] = None
    manager_employee_id: Optional[str] = None
    official_email: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
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
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    grade_id: Optional[str] = None
    position_id: Optional[str] = None
    manager_employee_id: Optional[str] = None
    official_email: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None
    user_id: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: str
    tenant_id: str
    employee_number: str
    user_id: Optional[str]
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
    first_name: str
    last_name: str
    email: str
    phone: str
    designation: str
    department: str
    department_id: Optional[str]
    designation_id: Optional[str]
    grade_id: Optional[str]
    position_id: Optional[str]
    manager_employee_id: Optional[str]
    official_email: Optional[str]
    employment_type: str
    status: str
    joining_date: Optional[datetime]

    class Config:
        from_attributes = True


class JobFamilyCreate(BaseModel):
    tenant_id: str = "default"
    family_code: str
    family_name: str
    description: Optional[str] = None


class JobFamilyUpdate(BaseModel):
    family_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobFamilyResponse(JobFamilyCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobRoleCreate(BaseModel):
    tenant_id: str = "default"
    role_code: str
    role_name: str
    job_family_id: Optional[str] = None
    description: Optional[str] = None


class JobRoleUpdate(BaseModel):
    role_name: Optional[str] = None
    job_family_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobRoleResponse(JobRoleCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeAssignmentCreate(BaseModel):
    tenant_id: str = "default"
    employee_id: str
    position_id: str
    assignment_type: str = "primary"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_by: Optional[str] = None
    notes: Optional[str] = None


class EmployeeAssignmentResponse(EmployeeAssignmentCreate):
    id: str
    status: str
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeTimelineCreate(BaseModel):
    event_type: str
    event_title: Optional[str] = None
    event_details: Optional[dict] = None
    notes: Optional[str] = None
    event_timestamp: Optional[datetime] = None


class EmployeeTimelineResponse(EmployeeTimelineCreate):
    id: str
    tenant_id: str
    employee_id: str
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PayrollRunCreate(BaseModel):
    tenant_id: str
    run_name: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None
    period_start: datetime
    period_end: datetime


class PayrollRunResponse(BaseModel):
    id: str
    tenant_id: str
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
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
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
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


class AttendanceRecordCreate(BaseModel):
    tenant_id: str = "default"
    employee_id: str
    attendance_date: date
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    status: str = "present"
    work_hours: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None


class AttendanceRecordUpdate(BaseModel):
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    status: Optional[str] = None
    work_hours: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None


class AttendanceRecordResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    employee_number: str
    employee_name: str
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
    attendance_date: date
    check_in_at: Optional[datetime]
    check_out_at: Optional[datetime]
    status: str
    work_hours: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    tenant_id: str = "default"
    employee_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveDecision(BaseModel):
    status: str
    approver_employee_id: Optional[str] = None
    decision_notes: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    employee_number: str
    employee_name: str
    organization_id: Optional[str]
    zone_id: Optional[str]
    region_id: Optional[str]
    area_id: Optional[str]
    branch_id: Optional[str]
    leave_type: str
    start_date: date
    end_date: date
    total_days: float
    reason: Optional[str]
    status: str
    approver_employee_id: Optional[str]
    decision_notes: Optional[str]
    requested_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True


try:
    from app.security import get_current_user_claims, scope_filter_columns
except ModuleNotFoundError:
    from .security import get_current_user_claims, scope_filter_columns

app = FastAPI(title="hrms-service", version="0.1.0")
app.include_router(organization_router)

SCOPE_FIELDS = ("organization_id", "zone_id", "region_id", "area_id", "branch_id")


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


def _claims(user_claims: dict | None) -> dict:
    return user_claims if isinstance(user_claims, dict) else {}


def _payroll_run(run_id: str, tenant_id: str, db: Session) -> PayrollRun:
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id, PayrollRun.tenant_id == tenant_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found for tenant")
    return run


def _resolve_tenant_id(tenant_id: str | None, user_claims: dict) -> str:
    claims = _claims(user_claims)
    claim_tenant_id = claims.get("tenant_id")
    if not claim_tenant_id:
        return tenant_id or "default"
    if tenant_id and tenant_id != claim_tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    return claim_tenant_id


def _resolve_branch_id(branch_id: str | None, user_claims: dict) -> str | None:
    claims = _claims(user_claims)
    claim_branch_id = claims.get("branch_id")
    if claim_branch_id and branch_id and branch_id != claim_branch_id:
        raise HTTPException(status_code=403, detail="Branch is outside the caller's scope")
    return branch_id or claim_branch_id


def _resolve_scope_values(requested: dict | None, user_claims: dict) -> dict:
    requested = requested or {}
    claims = _claims(user_claims)
    scope_values = {}
    for field in SCOPE_FIELDS:
        requested_value = requested.get(field)
        if requested_value is not None and not isinstance(requested_value, str):
            requested_value = None
        claim_value = claims.get(field)
        if claim_value is not None and not isinstance(claim_value, str):
            claim_value = None
        if claim_value and requested_value and requested_value != claim_value:
            label = field.removesuffix("_id").replace("_", " ").title()
            raise HTTPException(status_code=403, detail=f"{label} is outside the caller's scope")
        scope_values[field] = requested_value or claim_value
    return scope_values


def _apply_scope_values(entity, scope_values: dict) -> None:
    for field in SCOPE_FIELDS:
        if hasattr(entity, field):
            setattr(entity, field, scope_values.get(field))


def _copy_scope_values(source, target, overwrite: bool = False) -> None:
    for field in SCOPE_FIELDS:
        if not hasattr(source, field) or not hasattr(target, field):
            continue
        source_value = getattr(source, field)
        target_value = getattr(target, field)
        if source_value and target_value and source_value != target_value:
            label = field.removesuffix("_id").replace("_", " ").title()
            raise HTTPException(status_code=400, detail=f"{label} mismatch")
        if overwrite or not target_value:
            setattr(target, field, source_value)


def _assert_record_in_scope(entity, user_claims: dict) -> None:
    claims = _claims(user_claims)
    for field in SCOPE_FIELDS:
        claim_value = claims.get(field)
        if claim_value and hasattr(entity, field) and getattr(entity, field) != claim_value:
            raise HTTPException(status_code=403, detail="Record is outside the caller's scope")


def _apply_scope_filters(query, model: Type[Base], requested: dict | None, user_claims: dict):
    scope_values = _resolve_scope_values(requested, user_claims)
    for field, value in scope_values.items():
        if value and hasattr(model, field):
            query = query.filter(getattr(model, field) == value)
    return query


def _employee_display_name(employee: Employee) -> str:
    return f"{employee.first_name or ''} {employee.last_name or ''}".strip()


def _calculate_work_hours(check_in_at: datetime | None, check_out_at: datetime | None, provided: float | None = None) -> float:
    if provided is not None:
        return round(provided, 2)
    if not check_in_at or not check_out_at or check_out_at < check_in_at:
        return 0.0
    return round((check_out_at - check_in_at).total_seconds() / 3600, 2)


def _workflow_employee(employee_id: str, tenant_id: str, db: Session, user_claims: dict) -> Employee:
    employee = _get_tenant_record(db, Employee, employee_id, tenant_id, "Employee")
    _assert_record_in_scope(employee, user_claims)
    return employee


def _get_tenant_record(db: Session, model: Type[Base], record_id: str | None, tenant_id: str, label: str):
    if not record_id:
        return None
    record = db.query(model).filter(model.id == record_id, model.tenant_id == tenant_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"{label} not found for tenant")
    return record


def _ensure_unique_code(db: Session, model: Type[Base], tenant_id: str, column_name: str, code: str, label: str) -> None:
    existing = (
        db.query(model)
        .filter(model.tenant_id == tenant_id, getattr(model, column_name) == code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail=f"{label} code already exists for tenant")


def _apply_update(entity, payload: BaseModel) -> None:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, key, value)
    entity.updated_at = datetime.utcnow()


def _build_department_tree(departments: list[HRDepartment]) -> list[DepartmentTreeResponse]:
    nodes: dict[str, DepartmentTreeResponse] = {
        department.id: DepartmentTreeResponse.model_validate(department)
        for department in departments
    }
    tree: list[DepartmentTreeResponse] = []
    for node in nodes.values():
        parent_id = node.parent_department_id
        if parent_id and parent_id in nodes:
            nodes[parent_id].children.append(node)
        else:
            tree.append(node)
    return sorted(tree, key=lambda item: item.department_name.lower())


def _department_summary(department: HRDepartment, db: Session, user_claims: dict) -> dict:
    tenant_id = department.tenant_id
    employee_query = db.query(Employee).filter(Employee.tenant_id == tenant_id, Employee.department_id == department.id)
    employee_query = _apply_scope_filters(employee_query, Employee, None, user_claims)
    total_employees = employee_query.count()
    active_employees = employee_query.filter(Employee.status == "active").count()

    position_query = db.query(HRPosition).filter(HRPosition.tenant_id == tenant_id, HRPosition.department_id == department.id)
    position_query = _apply_scope_filters(position_query, HRPosition, None, user_claims)
    total_positions = position_query.count()
    open_positions = position_query.filter(HRPosition.status == "open").count()
    occupied_positions = position_query.filter(HRPosition.status != "open").count()

    head_name = None
    if department.department_head_employee_id:
        head = db.query(Employee).filter(Employee.id == department.department_head_employee_id, Employee.tenant_id == tenant_id).first()
        if head:
            head_name = _employee_display_name(head)

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_positions": total_positions,
        "open_positions": open_positions,
        "occupied_positions": occupied_positions,
        "department_head_name": head_name,
    }


def _validate_grade_band(min_value: float | None, max_value: float | None) -> None:
    if min_value is not None and max_value is not None and max_value and min_value > max_value:
        raise HTTPException(status_code=400, detail="salary_band_min cannot exceed salary_band_max")


def _sync_position_status(position: HRPosition) -> None:
    position.status = "occupied" if position.occupied_by_employee_id else "open"
    position.updated_at = datetime.utcnow()


def _release_employee_position(db: Session, employee: Employee) -> None:
    if not employee.position_id:
        return
    position = (
        db.query(HRPosition)
        .filter(
            HRPosition.id == employee.position_id,
            HRPosition.tenant_id == employee.tenant_id,
            HRPosition.occupied_by_employee_id == employee.id,
        )
        .first()
    )
    if position:
        position.occupied_by_employee_id = None
        _sync_position_status(position)


def _assign_position_to_employee(db: Session, employee: Employee, position_id: str | None, tenant_id: str) -> HRPosition | None:
    if not position_id:
        return None
    position = _get_tenant_record(db, HRPosition, position_id, tenant_id, "Position")
    if position.occupied_by_employee_id and position.occupied_by_employee_id != employee.id:
        raise HTTPException(status_code=400, detail="Position is already occupied")
    _copy_scope_values(position, employee)
    position.occupied_by_employee_id = employee.id
    _sync_position_status(position)
    employee.position_id = position.id
    return position


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "hrms"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/departments", response_model=DepartmentResponse)
async def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    _ensure_unique_code(db, HRDepartment, tenant_id, "department_code", payload.department_code, "Department")
    _get_tenant_record(db, HRDepartment, payload.parent_department_id, tenant_id, "Parent department")

    department = HRDepartment(
        id=str(uuid4()),
        tenant_id=tenant_id,
        department_code=payload.department_code,
        department_name=payload.department_name,
        parent_department_id=payload.parent_department_id,
        department_head_employee_id=payload.department_head_employee_id,
        cost_center_code=payload.cost_center_code,
        profit_center_code=payload.profit_center_code,
        budget_owner_employee_id=payload.budget_owner_employee_id,
        annual_budget=payload.annual_budget,
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@app.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRDepartment).filter(HRDepartment.tenant_id == tenant_id)
    if status:
        query = query.filter(HRDepartment.status == status)
    return query.order_by(HRDepartment.department_name.asc()).all()


@app.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    department = _get_tenant_record(db, HRDepartment, department_id, tenant_id, "Department")
    _get_tenant_record(db, HRDepartment, payload.parent_department_id, tenant_id, "Parent department")
    _apply_update(department, payload)
    db.commit()
    db.refresh(department)
    return department


@app.get("/departments/tree", response_model=List[DepartmentTreeResponse])
async def get_department_tree(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRDepartment).filter(HRDepartment.tenant_id == tenant_id)
    if status:
        query = query.filter(HRDepartment.status == status)
    departments = query.order_by(HRDepartment.department_name.asc()).all()
    return _build_department_tree(departments)


@app.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    department = _get_tenant_record(db, HRDepartment, department_id, tenant_id, "Department")
    _assert_record_in_scope(department, user_claims)
    return department


@app.get("/departments/{department_id}/employees", response_model=List[EmployeeResponse])
async def get_department_employees(
    department_id: str,
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    department = _get_tenant_record(db, HRDepartment, department_id, tenant_id, "Department")
    _assert_record_in_scope(department, user_claims)
    query = db.query(Employee).filter(Employee.tenant_id == tenant_id, Employee.department_id == department.id)
    query = _apply_scope_filters(query, Employee, None, user_claims)
    if status:
        query = query.filter(Employee.status == status)
    return query.order_by(Employee.last_name.asc(), Employee.first_name.asc()).offset(skip).limit(limit).all()


@app.get("/departments/{department_id}/positions", response_model=List[PositionResponse])
async def get_department_positions(
    department_id: str,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    department = _get_tenant_record(db, HRDepartment, department_id, tenant_id, "Department")
    _assert_record_in_scope(department, user_claims)
    query = db.query(HRPosition).filter(HRPosition.tenant_id == tenant_id, HRPosition.department_id == department.id)
    query = _apply_scope_filters(query, HRPosition, None, user_claims)
    if status:
        query = query.filter(HRPosition.status == status)
    return query.order_by(HRPosition.position_code.asc()).all()


@app.get("/departments/{department_id}/budget", response_model=DepartmentBudgetResponse)
async def get_department_budget(
    department_id: str,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    department = _get_tenant_record(db, HRDepartment, department_id, tenant_id, "Department")
    _assert_record_in_scope(department, user_claims)
    summary = _department_summary(department, db, user_claims)
    return DepartmentBudgetResponse(
        department_id=department.id,
        department_name=department.department_name,
        tenant_id=department.tenant_id,
        annual_budget=department.annual_budget,
        cost_center_code=department.cost_center_code,
        profit_center_code=department.profit_center_code,
        budget_owner_employee_id=department.budget_owner_employee_id,
        department_head_employee_id=department.department_head_employee_id,
        department_head_name=summary["department_head_name"],
        total_positions=summary["total_positions"],
        open_positions=summary["open_positions"],
        occupied_positions=summary["occupied_positions"],
        total_employees=summary["total_employees"],
    )


@app.get("/departments/{department_id}/analytics", response_model=DepartmentAnalyticsResponse)
async def get_department_analytics(
    department_id: str,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    department = _get_tenant_record(db, HRDepartment, department_id, tenant_id, "Department")
    _assert_record_in_scope(department, user_claims)
    summary = _department_summary(department, db, user_claims)
    return DepartmentAnalyticsResponse(
        department_id=department.id,
        department_name=department.department_name,
        tenant_id=department.tenant_id,
        annual_budget=department.annual_budget,
        cost_center_code=department.cost_center_code,
        profit_center_code=department.profit_center_code,
        budget_owner_employee_id=department.budget_owner_employee_id,
        department_head_employee_id=department.department_head_employee_id,
        department_head_name=summary["department_head_name"],
        total_positions=summary["total_positions"],
        open_positions=summary["open_positions"],
        occupied_positions=summary["occupied_positions"],
        total_employees=summary["total_employees"],
        active_employees=summary["active_employees"],
        status=department.status,
    )


@app.post("/grades", response_model=GradeResponse)
async def create_grade(
    payload: GradeCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    _validate_grade_band(payload.salary_band_min, payload.salary_band_max)
    _ensure_unique_code(db, HRGrade, tenant_id, "grade_code", payload.grade_code, "Grade")

    grade = HRGrade(
        id=str(uuid4()),
        tenant_id=tenant_id,
        grade_code=payload.grade_code,
        grade_name=payload.grade_name,
        salary_band_min=payload.salary_band_min,
        salary_band_max=payload.salary_band_max,
        leave_entitlement_days=payload.leave_entitlement_days,
        benefits=payload.benefits,
        approval_limit=payload.approval_limit,
        travel_class=payload.travel_class,
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@app.get("/grades", response_model=List[GradeResponse])
async def list_grades(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRGrade).filter(HRGrade.tenant_id == tenant_id)
    if status:
        query = query.filter(HRGrade.status == status)
    return query.order_by(HRGrade.grade_code.asc()).all()


@app.put("/grades/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: str,
    payload: GradeUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    grade = _get_tenant_record(db, HRGrade, grade_id, tenant_id, "Grade")
    next_min = payload.salary_band_min if payload.salary_band_min is not None else grade.salary_band_min
    next_max = payload.salary_band_max if payload.salary_band_max is not None else grade.salary_band_max
    _validate_grade_band(next_min, next_max)
    _apply_update(grade, payload)
    db.commit()
    db.refresh(grade)
    return grade


@app.post("/designations", response_model=DesignationResponse)
async def create_designation(
    payload: DesignationCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    _validate_grade_band(payload.salary_band_min, payload.salary_band_max)
    _ensure_unique_code(db, HRDesignation, tenant_id, "designation_code", payload.designation_code, "Designation")
    _get_tenant_record(db, HRGrade, payload.grade_id, tenant_id, "Grade")

    designation = HRDesignation(
        id=str(uuid4()),
        tenant_id=tenant_id,
        designation_code=payload.designation_code,
        designation_name=payload.designation_name,
        grade_id=payload.grade_id,
        salary_band_min=payload.salary_band_min,
        salary_band_max=payload.salary_band_max,
        approval_limit=payload.approval_limit,
        reporting_level=payload.reporting_level,
    )
    db.add(designation)
    db.commit()
    db.refresh(designation)
    return designation


@app.get("/designations", response_model=List[DesignationResponse])
async def list_designations(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRDesignation).filter(HRDesignation.tenant_id == tenant_id)
    if status:
        query = query.filter(HRDesignation.status == status)
    return query.order_by(HRDesignation.reporting_level.asc(), HRDesignation.designation_name.asc()).all()


@app.put("/designations/{designation_id}", response_model=DesignationResponse)
async def update_designation(
    designation_id: str,
    payload: DesignationUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    designation = _get_tenant_record(db, HRDesignation, designation_id, tenant_id, "Designation")
    _get_tenant_record(db, HRGrade, payload.grade_id, tenant_id, "Grade")
    next_min = payload.salary_band_min if payload.salary_band_min is not None else designation.salary_band_min
    next_max = payload.salary_band_max if payload.salary_band_max is not None else designation.salary_band_max
    _validate_grade_band(next_min, next_max)
    _apply_update(designation, payload)
    db.commit()
    db.refresh(designation)
    return designation


@app.post("/positions", response_model=PositionResponse)
async def create_position(
    payload: PositionCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    scope_values = _resolve_scope_values(payload.model_dump(include=set(SCOPE_FIELDS)), user_claims)
    _ensure_unique_code(db, HRPosition, tenant_id, "position_code", payload.position_code, "Position")
    department = _get_tenant_record(db, HRDepartment, payload.department_id, tenant_id, "Department")
    designation = _get_tenant_record(db, HRDesignation, payload.designation_id, tenant_id, "Designation")
    grade = _get_tenant_record(db, HRGrade, payload.grade_id or (designation.grade_id if designation else None), tenant_id, "Grade")
    job_role = _get_tenant_record(db, JobRole, payload.job_role_id, tenant_id, "Job role")
    organization_unit = _get_tenant_record(db, OrganizationUnit, payload.organization_unit_id, tenant_id, "Organization unit")
    _get_tenant_record(db, HRPosition, payload.reports_to_position_id, tenant_id, "Reporting position")

    position = HRPosition(
        id=str(uuid4()),
        tenant_id=tenant_id,
        position_code=payload.position_code,
        position_title=payload.position_title,
        department_id=department.id if department else None,
        designation_id=designation.id if designation else None,
        grade_id=grade.id if grade else None,
        job_role_id=job_role.id if job_role else None,
        organization_unit_id=organization_unit.id if organization_unit else None,
        organization_id=scope_values["organization_id"],
        zone_id=scope_values["zone_id"],
        region_id=scope_values["region_id"],
        area_id=scope_values["area_id"],
        branch_id=scope_values["branch_id"],
        reports_to_position_id=payload.reports_to_position_id,
        approval_limit=payload.approval_limit,
        budgeted_salary=payload.budgeted_salary,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        status="open",
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


@app.get("/positions", response_model=List[PositionResponse])
async def list_positions(
    tenant_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    department_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRPosition).filter(HRPosition.tenant_id == tenant_id)
    query = _apply_scope_filters(
        query,
        HRPosition,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    if department_id:
        query = query.filter(HRPosition.department_id == department_id)
    if status:
        query = query.filter(HRPosition.status == status)
    return query.order_by(HRPosition.position_code.asc()).all()


@app.put("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: str,
    payload: PositionUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    position = _get_tenant_record(db, HRPosition, position_id, tenant_id, "Position")
    _assert_record_in_scope(position, user_claims)
    update_data = payload.model_dump(exclude_unset=True)
    scope_update = {field: update_data.pop(field) for field in list(update_data.keys()) if field in SCOPE_FIELDS}
    scope_values = _resolve_scope_values(scope_update, user_claims) if scope_update else {}
    _get_tenant_record(db, HRDepartment, update_data.get("department_id"), tenant_id, "Department")
    designation = _get_tenant_record(db, HRDesignation, update_data.get("designation_id"), tenant_id, "Designation")
    grade_id = update_data.get("grade_id") or (designation.grade_id if designation else None)
    _get_tenant_record(db, HRGrade, grade_id, tenant_id, "Grade")
    _get_tenant_record(db, JobRole, update_data.get("job_role_id"), tenant_id, "Job role")
    _get_tenant_record(db, OrganizationUnit, update_data.get("organization_unit_id"), tenant_id, "Organization unit")
    _get_tenant_record(db, HRPosition, update_data.get("reports_to_position_id"), tenant_id, "Reporting position")

    occupant_id = update_data.pop("occupied_by_employee_id", None)
    for key, value in update_data.items():
        setattr(position, key, value)
    if scope_values:
        _apply_scope_values(position, scope_values)
    if occupant_id is not None:
        employee = _get_tenant_record(db, Employee, occupant_id, tenant_id, "Employee") if occupant_id else None
        if employee:
            _copy_scope_values(position, employee)
            existing_position = (
                db.query(HRPosition)
                .filter(
                    HRPosition.tenant_id == tenant_id,
                    HRPosition.occupied_by_employee_id == employee.id,
                    HRPosition.id != position.id,
                )
                .first()
            )
            if existing_position:
                raise HTTPException(status_code=400, detail="Employee is already assigned to another position")
            employee.position_id = position.id
        position.occupied_by_employee_id = employee.id if employee else None
    _sync_position_status(position)
    db.commit()
    db.refresh(position)
    return position


@app.post("/positions/{position_id}/vacate", response_model=PositionResponse)
async def vacate_position(
    position_id: str,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    position = _get_tenant_record(db, HRPosition, position_id, tenant_id, "Position")
    _assert_record_in_scope(position, user_claims)
    if position.occupied_by_employee_id:
        employee = db.query(Employee).filter(Employee.id == position.occupied_by_employee_id, Employee.tenant_id == tenant_id).first()
        if employee and employee.position_id == position.id:
            employee.position_id = None
    position.occupied_by_employee_id = None
    _sync_position_status(position)
    db.commit()
    db.refresh(position)
    return position


@app.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(employee.tenant_id, user_claims)
    scope_values = _resolve_scope_values(employee.model_dump(include=set(SCOPE_FIELDS)), user_claims)
    existing = (
        db.query(Employee)
        .filter(
            Employee.tenant_id == tenant_id,
            (Employee.employee_number == employee.employee_number) | (Employee.email == employee.email),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Employee number or email already exists")

    if employee.user_id:
        user_mapping = db.query(Employee).filter(Employee.user_id == employee.user_id, Employee.tenant_id == tenant_id).first()
        if user_mapping:
            raise HTTPException(status_code=400, detail="IAM user is already linked to an employee")

    department = _get_tenant_record(db, HRDepartment, employee.department_id, tenant_id, "Department")
    designation = _get_tenant_record(db, HRDesignation, employee.designation_id, tenant_id, "Designation")
    grade = _get_tenant_record(
        db,
        HRGrade,
        employee.grade_id or (designation.grade_id if designation else None),
        tenant_id,
        "Grade",
    )
    _get_tenant_record(db, Employee, employee.manager_employee_id, tenant_id, "Manager")

    db_employee = Employee(
        id=str(uuid4()),
        tenant_id=tenant_id,
        employee_number=employee.employee_number,
        user_id=employee.user_id,
        organization_id=scope_values["organization_id"],
        zone_id=scope_values["zone_id"],
        region_id=scope_values["region_id"],
        area_id=scope_values["area_id"],
        branch_id=scope_values["branch_id"],
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        designation=employee.designation or (designation.designation_name if designation else ""),
        department=employee.department or (department.department_name if department else ""),
        department_id=department.id if department else employee.department_id,
        designation_id=designation.id if designation else employee.designation_id,
        grade_id=grade.id if grade else employee.grade_id,
        manager_employee_id=employee.manager_employee_id,
        official_email=employee.official_email,
        employment_type=employee.employment_type,
        joining_date=employee.joining_date or datetime.utcnow(),
        status="active",
    )
    db.add(db_employee)
    db.flush()
    _assign_position_to_employee(db, db_employee, employee.position_id, tenant_id)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.get("/employees")
async def list_employees(
    tenant_id: Optional[str] = None,
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(Employee).filter(Employee.tenant_id == tenant_id)
    query = _apply_scope_filters(
        query,
        Employee,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    if department:
        query = query.filter(Employee.department == department)
    if status:
        query = query.filter(Employee.status == status)

    total = query.count()
    employees = query.order_by(Employee.created_at.desc()).offset(skip).limit(limit).all()
    return {"items": employees, "skip": skip, "limit": limit, "total": total}


@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.tenant_id == tenant_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    _assert_record_in_scope(employee, user_claims)
    return employee


@app.post("/payroll/runs", response_model=PayrollRunResponse)
async def create_payroll_run(
    payload: PayrollRunCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    if payload.period_end < payload.period_start:
        raise HTTPException(status_code=400, detail="period_end must be after period_start")
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    scope_values = _resolve_scope_values(payload.model_dump(include=set(SCOPE_FIELDS)), user_claims)
    run = PayrollRun(
        id=str(uuid4()),
        tenant_id=tenant_id,
        organization_id=scope_values["organization_id"],
        zone_id=scope_values["zone_id"],
        region_id=scope_values["region_id"],
        area_id=scope_values["area_id"],
        branch_id=scope_values["branch_id"],
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
    tenant_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(PayrollRun).filter(PayrollRun.tenant_id == tenant_id)
    query = _apply_scope_filters(
        query,
        PayrollRun,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    if status:
        query = query.filter(PayrollRun.status == status)
    return query.order_by(PayrollRun.created_at.desc()).all()


@app.post("/payroll/runs/{run_id}/slips", response_model=PayrollSlipResponse)
async def add_payroll_slip(
    run_id: str,
    payload: PayrollSlipCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    run = _payroll_run(run_id, tenant_id, db)
    _assert_record_in_scope(run, user_claims)
    if run.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft payroll runs can be edited")
    employee = (
        db.query(Employee)
        .filter(Employee.id == payload.employee_id, Employee.tenant_id == tenant_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for tenant")
    _assert_record_in_scope(employee, user_claims)
    _copy_scope_values(run, employee)
    existing = (
        db.query(PayrollSlip)
        .filter(
            PayrollSlip.tenant_id == tenant_id,
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
        tenant_id=tenant_id,
        payroll_run_id=run.id,
        employee_id=employee.id,
        organization_id=employee.organization_id,
        zone_id=employee.zone_id,
        region_id=employee.region_id,
        area_id=employee.area_id,
        branch_id=employee.branch_id,
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
async def list_payroll_slips(
    run_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    run = _payroll_run(run_id, tenant_id, db)
    _assert_record_in_scope(run, user_claims)
    return (
        db.query(PayrollSlip)
        .filter(PayrollSlip.payroll_run_id == run_id, PayrollSlip.tenant_id == tenant_id)
        .order_by(PayrollSlip.employee_number.asc())
        .all()
    )


@app.post("/payroll/runs/{run_id}/finalize", response_model=PayrollRunResponse)
async def finalize_payroll_run(
    run_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    run = _payroll_run(run_id, tenant_id, db)
    _assert_record_in_scope(run, user_claims)
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
    tenant_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(PayrollRun).filter(PayrollRun.tenant_id == tenant_id)
    query = _apply_scope_filters(
        query,
        PayrollRun,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
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


@app.post("/attendance/records", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    payload: AttendanceRecordCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    employee = _workflow_employee(payload.employee_id, tenant_id, db, user_claims)
    existing = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.employee_id == employee.id,
            AttendanceRecord.attendance_date == payload.attendance_date,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Attendance already captured for employee on this date")

    record = AttendanceRecord(
        id=str(uuid4()),
        tenant_id=tenant_id,
        employee_id=employee.id,
        employee_number=employee.employee_number,
        employee_name=_employee_display_name(employee),
        organization_id=employee.organization_id,
        zone_id=employee.zone_id,
        region_id=employee.region_id,
        area_id=employee.area_id,
        branch_id=employee.branch_id,
        attendance_date=payload.attendance_date,
        check_in_at=payload.check_in_at,
        check_out_at=payload.check_out_at,
        status=payload.status,
        work_hours=_calculate_work_hours(payload.check_in_at, payload.check_out_at, payload.work_hours),
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/attendance/records")
async def list_attendance_records(
    tenant_id: Optional[str] = Query(None),
    employee_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(AttendanceRecord).filter(AttendanceRecord.tenant_id == tenant_id)
    query = _apply_scope_filters(
        query,
        AttendanceRecord,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    if employee_id:
        query = query.filter(AttendanceRecord.employee_id == employee_id)
    if status:
        query = query.filter(AttendanceRecord.status == status)
    if start_date:
        query = query.filter(AttendanceRecord.attendance_date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.attendance_date <= end_date)
    total = query.count()
    records = query.order_by(AttendanceRecord.attendance_date.desc(), AttendanceRecord.employee_number.asc()).offset(skip).limit(limit).all()
    return {"items": records, "skip": skip, "limit": limit, "total": total}


@app.put("/attendance/records/{record_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    record_id: str,
    payload: AttendanceRecordUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id, AttendanceRecord.tenant_id == tenant_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    _assert_record_in_scope(record, user_claims)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    record.work_hours = _calculate_work_hours(record.check_in_at, record.check_out_at, update_data.get("work_hours"))
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


@app.post("/leave/requests", response_model=LeaveRequestResponse)
async def create_leave_request(
    payload: LeaveRequestCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date must be on or after start_date")
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    employee = _workflow_employee(payload.employee_id, tenant_id, db, user_claims)
    request = LeaveRequest(
        id=str(uuid4()),
        tenant_id=tenant_id,
        employee_id=employee.id,
        employee_number=employee.employee_number,
        employee_name=_employee_display_name(employee),
        organization_id=employee.organization_id,
        zone_id=employee.zone_id,
        region_id=employee.region_id,
        area_id=employee.area_id,
        branch_id=employee.branch_id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_days=float((payload.end_date - payload.start_date).days + 1),
        reason=payload.reason,
        status="pending",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@app.get("/leave/requests")
async def list_leave_requests(
    tenant_id: Optional[str] = Query(None),
    employee_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(LeaveRequest).filter(LeaveRequest.tenant_id == tenant_id)
    query = _apply_scope_filters(
        query,
        LeaveRequest,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    if start_date:
        query = query.filter(LeaveRequest.end_date >= start_date)
    if end_date:
        query = query.filter(LeaveRequest.start_date <= end_date)
    total = query.count()
    requests = query.order_by(LeaveRequest.requested_at.desc()).offset(skip).limit(limit).all()
    return {"items": requests, "skip": skip, "limit": limit, "total": total}


@app.post("/leave/requests/{request_id}/decision", response_model=LeaveRequestResponse)
async def decide_leave_request(
    request_id: str,
    payload: LeaveDecision,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id, LeaveRequest.tenant_id == tenant_id).first()
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    _assert_record_in_scope(leave_request, user_claims)
    next_status = payload.status.lower()
    if next_status not in {"approved", "rejected", "cancelled"}:
        raise HTTPException(status_code=400, detail="status must be approved, rejected, or cancelled")
    if leave_request.status != "pending" and leave_request.status != next_status:
        raise HTTPException(status_code=400, detail="Only pending leave requests can be decided")
    if payload.approver_employee_id:
        approver = _workflow_employee(payload.approver_employee_id, tenant_id, db, user_claims)
        leave_request.approver_employee_id = approver.id
    leave_request.status = next_status
    leave_request.decision_notes = payload.decision_notes
    leave_request.decided_at = datetime.utcnow()
    db.commit()
    db.refresh(leave_request)
    return leave_request


@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    update: EmployeeUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.tenant_id == tenant_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    _assert_record_in_scope(employee, user_claims)

    update_data = update.model_dump(exclude_unset=True)
    if "user_id" in update_data and update_data["user_id"]:
        existing = (
            db.query(Employee)
            .filter(Employee.user_id == update_data["user_id"], Employee.id != employee_id, Employee.tenant_id == tenant_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="IAM user is already linked to an employee")

    scope_update = {field: update_data.pop(field) for field in list(update_data.keys()) if field in SCOPE_FIELDS}
    if scope_update:
        _apply_scope_values(employee, _resolve_scope_values(scope_update, user_claims))
    if "department_id" in update_data and update_data["department_id"]:
        department = _get_tenant_record(db, HRDepartment, update_data["department_id"], tenant_id, "Department")
        update_data.setdefault("department", department.department_name)
    if "designation_id" in update_data and update_data["designation_id"]:
        designation = _get_tenant_record(db, HRDesignation, update_data["designation_id"], tenant_id, "Designation")
        update_data.setdefault("designation", designation.designation_name)
        update_data.setdefault("grade_id", designation.grade_id)
    if "grade_id" in update_data and update_data["grade_id"]:
        _get_tenant_record(db, HRGrade, update_data["grade_id"], tenant_id, "Grade")
    if "manager_employee_id" in update_data and update_data["manager_employee_id"]:
        _get_tenant_record(db, Employee, update_data["manager_employee_id"], tenant_id, "Manager")
    if "position_id" in update_data:
        next_position_id = update_data.pop("position_id")
        if next_position_id != employee.position_id:
            _release_employee_position(db, employee)
            _assign_position_to_employee(db, employee, next_position_id, tenant_id)

    for key, value in update_data.items():
        setattr(employee, key, value)
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    return employee


@app.post("/job-families", response_model=JobFamilyResponse)
async def create_job_family(
    payload: JobFamilyCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    _ensure_unique_code(db, JobFamily, tenant_id, "family_code", payload.family_code, "Job family")
    family = JobFamily(
        id=str(uuid4()),
        tenant_id=tenant_id,
        family_code=payload.family_code,
        family_name=payload.family_name,
        description=payload.description,
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


@app.get("/job-families", response_model=List[JobFamilyResponse])
async def list_job_families(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(JobFamily).filter(JobFamily.tenant_id == tenant_id)
    if status:
        query = query.filter(JobFamily.status == status)
    return query.order_by(JobFamily.family_name.asc()).all()


@app.put("/job-families/{job_family_id}", response_model=JobFamilyResponse)
async def update_job_family(
    job_family_id: str,
    payload: JobFamilyUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    family = _get_tenant_record(db, JobFamily, job_family_id, tenant_id, "Job family")
    _apply_update(family, payload)
    db.commit()
    db.refresh(family)
    return family


@app.post("/job-roles", response_model=JobRoleResponse)
async def create_job_role(
    payload: JobRoleCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    _ensure_unique_code(db, JobRole, tenant_id, "role_code", payload.role_code, "Job role")
    _get_tenant_record(db, JobFamily, payload.job_family_id, tenant_id, "Job family")
    role = JobRole(
        id=str(uuid4()),
        tenant_id=tenant_id,
        role_code=payload.role_code,
        role_name=payload.role_name,
        job_family_id=payload.job_family_id,
        description=payload.description,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@app.get("/job-roles", response_model=List[JobRoleResponse])
async def list_job_roles(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(JobRole).filter(JobRole.tenant_id == tenant_id)
    if status:
        query = query.filter(JobRole.status == status)
    return query.order_by(JobRole.role_name.asc()).all()


@app.put("/job-roles/{job_role_id}", response_model=JobRoleResponse)
async def update_job_role(
    job_role_id: str,
    payload: JobRoleUpdate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    role = _get_tenant_record(db, JobRole, job_role_id, tenant_id, "Job role")
    if payload.job_family_id:
        _get_tenant_record(db, JobFamily, payload.job_family_id, tenant_id, "Job family")
    _apply_update(role, payload)
    db.commit()
    db.refresh(role)
    return role


@app.post("/employee-assignments", response_model=EmployeeAssignmentResponse)
async def create_employee_assignment(
    payload: EmployeeAssignmentCreate,
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(payload.tenant_id, user_claims)
    employee = _workflow_employee(payload.employee_id, tenant_id, db, user_claims)
    position = _get_tenant_record(db, HRPosition, payload.position_id, tenant_id, "Position")
    if position.occupied_by_employee_id and position.occupied_by_employee_id != employee.id:
        raise HTTPException(status_code=400, detail="Position is already occupied")
    if payload.assignment_type == "primary" and employee.position_id and employee.position_id != position.id:
        _release_employee_position(db, employee)
    _assign_position_to_employee(db, employee, position.id, tenant_id)
    assignment = EmployeeAssignment(
        id=str(uuid4()),
        tenant_id=tenant_id,
        employee_id=employee.id,
        position_id=position.id,
        assignment_type=payload.assignment_type,
        status="active",
        start_date=payload.start_date or date.today(),
        end_date=payload.end_date,
        assigned_by=payload.assigned_by,
        notes=payload.notes,
        organization_id=employee.organization_id,
        zone_id=employee.zone_id,
        region_id=employee.region_id,
        area_id=employee.area_id,
        branch_id=employee.branch_id,
    )
    db.add(assignment)
    timeline_event = EmployeeTimeline(
        id=str(uuid4()),
        tenant_id=tenant_id,
        employee_id=employee.id,
        event_type="position_assigned",
        event_title="Position Assigned",
        event_details={
            "position_id": position.id,
            "position_title": position.position_title,
            "assignment_type": payload.assignment_type,
        },
        notes=payload.notes,
        organization_id=employee.organization_id,
        zone_id=employee.zone_id,
        region_id=employee.region_id,
        area_id=employee.area_id,
        branch_id=employee.branch_id,
        event_timestamp=payload.start_date or datetime.utcnow(),
    )
    db.add(timeline_event)
    db.commit()
    db.refresh(assignment)
    return assignment


@app.get("/positions/vacant", response_model=List[PositionResponse])
async def get_vacant_positions(
    tenant_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRPosition).filter(HRPosition.tenant_id == tenant_id, HRPosition.status == "open")
    query = _apply_scope_filters(
        query,
        HRPosition,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    return query.order_by(HRPosition.position_code.asc()).all()


@app.get("/positions/occupied", response_model=List[PositionResponse])
async def get_occupied_positions(
    tenant_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    region_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    query = db.query(HRPosition).filter(HRPosition.tenant_id == tenant_id, HRPosition.status != "open")
    query = _apply_scope_filters(
        query,
        HRPosition,
        {
            "organization_id": organization_id,
            "zone_id": zone_id,
            "region_id": region_id,
            "area_id": area_id,
            "branch_id": branch_id,
        },
        user_claims,
    )
    return query.order_by(HRPosition.position_code.asc()).all()


@app.get("/organization/{organization_unit_id}/positions", response_model=List[PositionResponse])
async def get_organization_positions(
    organization_unit_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    _get_tenant_record(db, OrganizationUnit, organization_unit_id, tenant_id, "Organization unit")
    descendant_ids = [organization_unit_id]
    rows = (
        db.query(OrganizationUnitClosure.descendant_id)
        .filter(
            OrganizationUnitClosure.tenant_id == tenant_id,
            OrganizationUnitClosure.ancestor_id == organization_unit_id,
        )
        .all()
    )
    descendant_ids += [row.descendant_id for row in rows if row.descendant_id != organization_unit_id]
    query = db.query(HRPosition).filter(HRPosition.tenant_id == tenant_id, HRPosition.organization_unit_id.in_(descendant_ids))
    return query.order_by(HRPosition.position_code.asc()).all()


@app.get("/employees/{employee_id}/timeline", response_model=List[EmployeeTimelineResponse])
async def get_employee_timeline(
    employee_id: str,
    tenant_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    _workflow_employee(employee_id, tenant_id, db, user_claims)
    timeline = (
        db.query(EmployeeTimeline)
        .filter(EmployeeTimeline.tenant_id == tenant_id, EmployeeTimeline.employee_id == employee_id)
        .order_by(EmployeeTimeline.event_timestamp.desc())
        .limit(limit)
        .all()
    )
    return timeline


@app.post("/employees/{employee_id}/timeline", response_model=EmployeeTimelineResponse)
async def add_employee_timeline_event(
    employee_id: str,
    payload: EmployeeTimelineCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(tenant_id, user_claims)
    employee = _workflow_employee(employee_id, tenant_id, db, user_claims)
    entry = EmployeeTimeline(
        id=str(uuid4()),
        tenant_id=tenant_id,
        employee_id=employee.id,
        event_type=payload.event_type,
        event_title=payload.event_title,
        event_details=payload.event_details,
        notes=payload.notes,
        organization_id=employee.organization_id,
        zone_id=employee.zone_id,
        region_id=employee.region_id,
        area_id=employee.area_id,
        branch_id=employee.branch_id,
        event_timestamp=payload.event_timestamp or datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.post("/employees/{employee_id}/assign-branch", response_model=EmployeeResponse)
async def assign_employee_branch(
    employee_id: str,
    branch_id: str = Query(...),
    db: Session = Depends(get_db),
    user_claims: dict = Depends(get_current_user_claims),
):
    tenant_id = _resolve_tenant_id(None, user_claims)
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.tenant_id == tenant_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    _assert_record_in_scope(employee, user_claims)
    employee.branch_id = _resolve_scope_values({"branch_id": branch_id}, user_claims)["branch_id"]
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    return employee


@app.get("/")
async def root():
    return {"service": "hrms", "version": "0.1.0"}
