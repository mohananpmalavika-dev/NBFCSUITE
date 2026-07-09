"""
HRMS (Human Resource Management System) Database Models
Employee Management, Organization Structure, Department, Designation, Reporting Hierarchy
"""

from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, Text, ForeignKey, Numeric, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from decimal import Decimal
import enum

from backend.shared.database.models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class EmploymentType(str, enum.Enum):
    """Employment type"""
    PERMANENT = "permanent"
    CONTRACT = "contract"
    PROBATION = "probation"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmploymentStatus(str, enum.Enum):
    """Employment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"
    TERMINATED = "terminated"
    ABSCONDED = "absconded"
    RETIRED = "retired"


class Gender(str, enum.Enum):
    """Gender"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(str, enum.Enum):
    """Blood group"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"


class MaritalStatus(str, enum.Enum):
    """Marital status"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class DepartmentType(str, enum.Enum):
    """Department type"""
    OPERATIONS = "operations"
    FINANCE = "finance"
    IT = "it"
    HR = "hr"
    MARKETING = "marketing"
    SALES = "sales"
    ADMIN = "admin"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    RISK = "risk"
    CREDIT = "credit"
    COLLECTIONS = "collections"
    CUSTOMER_SERVICE = "customer_service"
    OTHER = "other"


# ============================================================================
# ORGANIZATION STRUCTURE
# ============================================================================

class HRMSOrganization(BaseModel):
    """
    Organization/Company entity
    Represents the parent company or holding company
    """
    __tablename__ = "hrms_organizations"
    
    # Basic Information
    organization_code = Column(String(20), nullable=False, index=True)
    organization_name = Column(String(200), nullable=False)
    short_name = Column(String(50), nullable=True)
    legal_name = Column(String(200), nullable=True)
    
    # Registration Details
    pan_number = Column(String(10), nullable=True)
    tan_number = Column(String(10), nullable=True)
    gstin = Column(String(15), nullable=True)
    cin_number = Column(String(21), nullable=True)  # Corporate Identity Number
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Registered Address
    registered_address_line1 = Column(String(200), nullable=True)
    registered_address_line2 = Column(String(200), nullable=True)
    registered_city = Column(String(100), nullable=True)
    registered_state = Column(String(100), nullable=True)
    registered_pincode = Column(String(10), nullable=True)
    registered_country = Column(String(100), default="India")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    established_date = Column(Date, nullable=True)
    
    # Relationships
    departments = relationship("Department", back_populates="organization", lazy="select")
    employees = relationship("Employee", back_populates="organization", lazy="select")
    
    # Unique constraints
    __table_args__ = (
        Index('idx_tenant_org_code', 'tenant_id', 'organization_code', unique=True),
    )
    
    def __repr__(self):
        return f"<Organization(code={self.organization_code}, name={self.organization_name})>"


class Department(BaseModel):
    """
    Department entity
    Represents organizational departments (Finance, HR, IT, Sales, etc.)
    """
    __tablename__ = "hrms_departments"
    
    # Basic Information
    department_code = Column(String(20), nullable=False, index=True)
    department_name = Column(String(100), nullable=False)
    department_type = Column(SQLEnum(DepartmentType), nullable=False, default=DepartmentType.OTHER)
    description = Column(Text, nullable=True)
    
    # Organization Link
    organization_id = Column(UUID(as_uuid=True), ForeignKey("hrms_organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Hierarchy
    parent_department_id = Column(UUID(as_uuid=True), ForeignKey("hrms_departments.id", ondelete="SET NULL"), nullable=True)
    
    # Head of Department
    hod_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    extension = Column(String(10), nullable=True)
    
    # Location
    location = Column(String(100), nullable=True)
    floor = Column(String(50), nullable=True)
    
    # Cost Center
    cost_center_code = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    organization = relationship("HRMSOrganization", back_populates="departments")
    parent_department = relationship("Department", remote_side="Department.id", foreign_keys=[parent_department_id])
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id", lazy="select")
    hod = relationship("Employee", foreign_keys=[hod_employee_id], post_update=True)
    
    # Unique constraints
    __table_args__ = (
        Index('idx_tenant_dept_code', 'tenant_id', 'department_code', unique=True),
    )
    
    def __repr__(self):
        return f"<Department(code={self.department_code}, name={self.department_name})>"


class Designation(BaseModel):
    """
    Designation/Job Title entity
    Represents job titles/positions (Manager, Executive, Clerk, etc.)
    """
    __tablename__ = "hrms_designations"
    
    # Basic Information
    designation_code = Column(String(20), nullable=False, index=True)
    designation_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchy Level
    level = Column(Integer, nullable=True)  # 1=Top Management, 2=Senior, 3=Middle, 4=Junior
    grade = Column(String(10), nullable=True)  # A, B, C, D, etc.
    
    # Salary Range
    min_salary = Column(Numeric(15, 2), nullable=True)
    max_salary = Column(Numeric(15, 2), nullable=True)
    
    # Requirements
    min_experience_years = Column(Integer, nullable=True)
    required_qualification = Column(String(200), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employees = relationship("Employee", back_populates="designation", lazy="select")
    
    # Unique constraints
    __table_args__ = (
        Index('idx_tenant_desig_code', 'tenant_id', 'designation_code', unique=True),
    )
    
    def __repr__(self):
        return f"<Designation(code={self.designation_code}, name={self.designation_name})>"


# ============================================================================
# EMPLOYEE
# ============================================================================

class Employee(BaseModel):
    """
    Employee entity
    Comprehensive employee master with personal, employment, and organizational details
    """
    __tablename__ = "hrms_employees"
    
    # ========================================
    # EMPLOYMENT INFORMATION
    # ========================================
    
    # Employee Identification
    employee_code = Column(String(20), nullable=False, unique=True, index=True)
    employee_id_display = Column(String(50), nullable=True)  # For display on ID cards
    
    # User Account Link (if employee has system access)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Organization & Department
    organization_id = Column(UUID(as_uuid=True), ForeignKey("hrms_organizations.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("hrms_departments.id", ondelete="SET NULL"), nullable=True)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("hrms_designations.id", ondelete="SET NULL"), nullable=True)
    
    # Reporting Hierarchy
    reporting_manager_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    
    # Employment Details
    employment_type = Column(SQLEnum(EmploymentType), nullable=False, default=EmploymentType.PERMANENT)
    employment_status = Column(SQLEnum(EmploymentStatus), nullable=False, default=EmploymentStatus.ACTIVE)
    
    # Important Dates
    date_of_joining = Column(Date, nullable=False)
    date_of_confirmation = Column(Date, nullable=True)
    date_of_resignation = Column(Date, nullable=True)
    date_of_relieving = Column(Date, nullable=True)
    last_working_day = Column(Date, nullable=True)
    
    # Work Location
    work_location = Column(String(100), nullable=True)
    branch_id = Column(UUID(as_uuid=True), nullable=True)  # Link to branch if applicable
    
    # Shift & Work Schedule
    shift_type = Column(String(20), nullable=True)  # day, night, rotational
    work_schedule = Column(String(50), nullable=True)  # 9-6, 10-7, etc.
    
    # ========================================
    # PERSONAL INFORMATION
    # ========================================
    
    # Name
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(300), nullable=False, index=True)
    
    # Basic Details
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    blood_group = Column(SQLEnum(BloodGroup), nullable=True)
    marital_status = Column(SQLEnum(MaritalStatus), nullable=True)
    
    # Family Details
    father_name = Column(String(200), nullable=True)
    mother_name = Column(String(200), nullable=True)
    spouse_name = Column(String(200), nullable=True)
    number_of_children = Column(Integer, default=0)
    
    # Contact Information
    personal_email = Column(String(100), nullable=True)
    official_email = Column(String(100), nullable=True, index=True)
    mobile = Column(String(20), nullable=False)
    alternate_mobile = Column(String(20), nullable=True)
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_number = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)
    
    # ========================================
    # ADDRESS INFORMATION
    # ========================================
    
    # Current Address
    current_address_line1 = Column(String(200), nullable=True)
    current_address_line2 = Column(String(200), nullable=True)
    current_city = Column(String(100), nullable=True)
    current_state = Column(String(100), nullable=True)
    current_pincode = Column(String(10), nullable=True)
    current_country = Column(String(100), default="India")
    
    # Permanent Address
    permanent_address_line1 = Column(String(200), nullable=True)
    permanent_address_line2 = Column(String(200), nullable=True)
    permanent_city = Column(String(100), nullable=True)
    permanent_state = Column(String(100), nullable=True)
    permanent_pincode = Column(String(10), nullable=True)
    permanent_country = Column(String(100), default="India")
    
    # Address Same Flag
    is_permanent_same_as_current = Column(Boolean, default=False)
    
    # ========================================
    # IDENTITY DOCUMENTS
    # ========================================
    
    pan_number = Column(String(10), nullable=True, index=True)
    aadhaar_number = Column(String(12), nullable=True)
    passport_number = Column(String(20), nullable=True)
    driving_license_number = Column(String(20), nullable=True)
    voter_id_number = Column(String(20), nullable=True)
    
    # ========================================
    # BANK & SALARY INFORMATION
    # ========================================
    
    # Salary Account
    salary_bank_name = Column(String(100), nullable=True)
    salary_account_number = Column(String(30), nullable=True)
    salary_ifsc_code = Column(String(11), nullable=True)
    salary_account_holder_name = Column(String(200), nullable=True)
    
    # PF Account
    pf_number = Column(String(30), nullable=True)
    uan_number = Column(String(12), nullable=True)  # Universal Account Number
    pf_join_date = Column(Date, nullable=True)
    
    # ESI Account
    esi_number = Column(String(20), nullable=True)
    
    # Salary Details (Current CTC)
    current_ctc = Column(Numeric(15, 2), nullable=True)
    basic_salary = Column(Numeric(15, 2), nullable=True)
    gross_salary = Column(Numeric(15, 2), nullable=True)
    net_salary = Column(Numeric(15, 2), nullable=True)
    
    # ========================================
    # EDUCATION & EXPERIENCE
    # ========================================
    
    highest_qualification = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)
    university = Column(String(200), nullable=True)
    year_of_passing = Column(Integer, nullable=True)
    
    total_experience_years = Column(Integer, nullable=True)
    previous_employer = Column(String(200), nullable=True)
    previous_designation = Column(String(100), nullable=True)
    
    # ========================================
    # DOCUMENTS & COMPLIANCE
    # ========================================
    
    # Photo & Signature
    photo_url = Column(String(500), nullable=True)
    signature_url = Column(String(500), nullable=True)
    
    # Background Verification
    is_background_verified = Column(Boolean, default=False)
    background_verification_date = Column(Date, nullable=True)
    background_verification_agency = Column(String(200), nullable=True)
    
    # Police Verification
    is_police_verified = Column(Boolean, default=False)
    police_verification_date = Column(Date, nullable=True)
    
    # Medical Examination
    is_medical_done = Column(Boolean, default=False)
    medical_examination_date = Column(Date, nullable=True)
    is_medical_fit = Column(Boolean, default=True)
    
    # ========================================
    # STATUS & FLAGS
    # ========================================
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_on_probation = Column(Boolean, default=False)
    probation_end_date = Column(Date, nullable=True)
    
    # Notice Period (in days)
    notice_period_days = Column(Integer, default=30)
    
    # ========================================
    # ADDITIONAL INFORMATION
    # ========================================
    
    remarks = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # JSON array or comma-separated
    certifications = Column(Text, nullable=True)  # JSON array
    languages_known = Column(Text, nullable=True)  # JSON array
    
    # ========================================
    # RELATIONSHIPS
    # ========================================
    
    organization = relationship("Organization", back_populates="employees")
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    designation = relationship("Designation", back_populates="employees")
    reporting_manager = relationship("Employee", remote_side="Employee.id", foreign_keys=[reporting_manager_id])
    
    # User account relationship
    user = relationship("User", foreign_keys=[user_id])
    
    # ========================================
    # INDEXES & CONSTRAINTS
    # ========================================
    
    __table_args__ = (
        Index('idx_tenant_emp_code', 'tenant_id', 'employee_code', unique=True),
        Index('idx_tenant_official_email', 'tenant_id', 'official_email'),
        Index('idx_tenant_mobile', 'tenant_id', 'mobile'),
        Index('idx_tenant_pan', 'tenant_id', 'pan_number'),
        Index('idx_emp_status', 'tenant_id', 'employment_status', 'is_active'),
        Index('idx_emp_dept', 'tenant_id', 'department_id', 'is_active'),
        Index('idx_emp_manager', 'tenant_id', 'reporting_manager_id'),
    )
    
    def __repr__(self):
        return f"<Employee(code={self.employee_code}, name={self.full_name})>"


# ============================================================================
# REPORTING HIERARCHY
# ============================================================================

class ReportingHierarchy(BaseModel):
    """
    Reporting Hierarchy tracking
    Maintains historical and current reporting relationships
    Supports matrix reporting (multiple managers)
    """
    __tablename__ = "hrms_reporting_hierarchy"
    
    # Employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    
    # Manager
    manager_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    
    # Reporting Type
    reporting_type = Column(String(20), nullable=False, default="direct")  # direct, dotted, functional
    is_primary = Column(Boolean, default=True, nullable=False)
    
    # Effective Period
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_current = Column(Boolean, default=True, nullable=False)
    
    # Reason for Change
    change_reason = Column(String(200), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    manager = relationship("Employee", foreign_keys=[manager_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_emp_current', 'tenant_id', 'employee_id', 'is_current'),
        Index('idx_tenant_manager', 'tenant_id', 'manager_id', 'is_current'),
    )
    
    def __repr__(self):
        return f"<ReportingHierarchy(employee={self.employee_id}, manager={self.manager_id})>"
