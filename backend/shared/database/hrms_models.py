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
    
    organization = relationship("HRMSOrganization", back_populates="employees")
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


# ============================================================================
# PERFORMANCE MANAGEMENT ENUMS
# ============================================================================

class GoalType(str, enum.Enum):
    """Goal type"""
    KRA = "kra"  # Key Result Area
    KPI = "kpi"  # Key Performance Indicator
    OBJECTIVE = "objective"
    PROJECT = "project"


class GoalStatus(str, enum.Enum):
    """Goal status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalPriority(str, enum.Enum):
    """Goal priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AppraisalCycleStatus(str, enum.Enum):
    """Appraisal cycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    GOAL_SETTING = "goal_setting"
    SELF_ASSESSMENT = "self_assessment"
    MANAGER_REVIEW = "manager_review"
    NORMALIZATION = "normalization"
    HR_REVIEW = "hr_review"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class AppraisalStatus(str, enum.Enum):
    """Individual appraisal status"""
    NOT_STARTED = "not_started"
    GOAL_SETTING_PENDING = "goal_setting_pending"
    GOAL_SETTING_SUBMITTED = "goal_setting_submitted"
    GOALS_APPROVED = "goals_approved"
    SELF_ASSESSMENT_PENDING = "self_assessment_pending"
    SELF_ASSESSMENT_SUBMITTED = "self_assessment_submitted"
    MANAGER_REVIEW_PENDING = "manager_review_pending"
    MANAGER_REVIEW_SUBMITTED = "manager_review_submitted"
    HR_REVIEW_PENDING = "hr_review_pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RatingScale(str, enum.Enum):
    """Performance rating scale"""
    OUTSTANDING = "outstanding"  # 5
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"  # 4
    MEETS_EXPECTATIONS = "meets_expectations"  # 3
    NEEDS_IMPROVEMENT = "needs_improvement"  # 2
    UNSATISFACTORY = "unsatisfactory"  # 1


class FeedbackType(str, enum.Enum):
    """360-degree feedback type"""
    SELF = "self"
    MANAGER = "manager"
    PEER = "peer"
    SUBORDINATE = "subordinate"
    CUSTOMER = "customer"
    OTHER = "other"


class FeedbackStatus(str, enum.Enum):
    """Feedback status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"


class IncrementType(str, enum.Enum):
    """Increment type"""
    ANNUAL = "annual"
    PROMOTION = "promotion"
    SPECIAL = "special"
    PERFORMANCE_BASED = "performance_based"
    MARKET_CORRECTION = "market_correction"


class IDPStatus(str, enum.Enum):
    """Individual Development Plan status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DevelopmentActivityType(str, enum.Enum):
    """Development activity type"""
    TRAINING = "training"
    CERTIFICATION = "certification"
    WORKSHOP = "workshop"
    MENTORING = "mentoring"
    JOB_ROTATION = "job_rotation"
    SELF_LEARNING = "self_learning"
    CONFERENCE = "conference"
    PROJECT = "project"


# ============================================================================
# PERFORMANCE MANAGEMENT - GOAL SETTING (KRA/KPI)
# ============================================================================

class PerformanceGoal(BaseModel):
    """
    Performance Goals (KRA/KPI)
    Individual goals set for employees during appraisal cycles
    """
    __tablename__ = "hrms_performance_goals"
    
    # Goal Identification
    goal_code = Column(String(50), nullable=False, index=True)
    goal_title = Column(String(200), nullable=False)
    goal_description = Column(Text, nullable=True)
    
    # Goal Type
    goal_type = Column(SQLEnum(GoalType), nullable=False, default=GoalType.KPI)
    goal_priority = Column(SQLEnum(GoalPriority), nullable=False, default=GoalPriority.MEDIUM)
    
    # Ownership
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    appraisal_cycle_id = Column(UUID(as_uuid=True), ForeignKey("hrms_appraisal_cycles.id", ondelete="CASCADE"), nullable=False)
    
    # Measurement
    measurement_criteria = Column(Text, nullable=True)
    target_value = Column(String(100), nullable=True)
    achieved_value = Column(String(100), nullable=True)
    uom = Column(String(50), nullable=True)  # Unit of Measurement
    weightage = Column(Numeric(5, 2), nullable=True)  # Percentage weightage
    
    # Timeline
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    
    # Progress Tracking
    progress_percentage = Column(Integer, default=0)
    status = Column(SQLEnum(GoalStatus), nullable=False, default=GoalStatus.DRAFT)
    
    # Approval
    submitted_date = Column(DateTime, nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Comments
    employee_comments = Column(Text, nullable=True)
    manager_comments = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performance_goals")
    appraisal_cycle = relationship("AppraisalCycle", back_populates="goals")
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_goal_emp', 'tenant_id', 'employee_id', 'appraisal_cycle_id'),
        Index('idx_tenant_goal_code', 'tenant_id', 'goal_code'),
        Index('idx_tenant_goal_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<PerformanceGoal(code={self.goal_code}, title={self.goal_title})>"


# ============================================================================
# PERFORMANCE MANAGEMENT - APPRAISAL CYCLES
# ============================================================================

class AppraisalCycle(BaseModel):
    """
    Appraisal Cycles
    Annual or periodic performance appraisal cycles
    """
    __tablename__ = "hrms_appraisal_cycles"
    
    # Cycle Identification
    cycle_code = Column(String(50), nullable=False, unique=True, index=True)
    cycle_name = Column(String(200), nullable=False)
    cycle_description = Column(Text, nullable=True)
    
    # Fiscal Year
    fiscal_year = Column(String(20), nullable=False)  # e.g., "2024-25"
    
    # Timeline
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Phase Deadlines
    goal_setting_start = Column(Date, nullable=True)
    goal_setting_end = Column(Date, nullable=True)
    
    self_assessment_start = Column(Date, nullable=True)
    self_assessment_end = Column(Date, nullable=True)
    
    manager_review_start = Column(Date, nullable=True)
    manager_review_end = Column(Date, nullable=True)
    
    normalization_start = Column(Date, nullable=True)
    normalization_end = Column(Date, nullable=True)
    
    hr_review_start = Column(Date, nullable=True)
    hr_review_end = Column(Date, nullable=True)
    
    # Status
    status = Column(SQLEnum(AppraisalCycleStatus), nullable=False, default=AppraisalCycleStatus.DRAFT)
    
    # Configuration
    enable_360_feedback = Column(Boolean, default=False)
    enable_self_assessment = Column(Boolean, default=True)
    enable_goal_setting = Column(Boolean, default=True)
    
    # Statistics
    total_employees = Column(Integer, default=0)
    completed_appraisals = Column(Integer, default=0)
    
    # Relationships
    appraisals = relationship("EmployeeAppraisal", back_populates="appraisal_cycle", lazy="select")
    goals = relationship("PerformanceGoal", back_populates="appraisal_cycle", lazy="select")
    feedback_requests = relationship("FeedbackRequest", back_populates="appraisal_cycle", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_cycle_code', 'tenant_id', 'cycle_code', unique=True),
        Index('idx_tenant_cycle_status', 'tenant_id', 'status'),
        Index('idx_tenant_cycle_year', 'tenant_id', 'fiscal_year'),
    )
    
    def __repr__(self):
        return f"<AppraisalCycle(code={self.cycle_code}, name={self.cycle_name})>"


# ============================================================================
# PERFORMANCE MANAGEMENT - EMPLOYEE APPRAISAL
# ============================================================================

class EmployeeAppraisal(BaseModel):
    """
    Employee Appraisal
    Individual employee appraisal records for each cycle
    """
    __tablename__ = "hrms_employee_appraisals"
    
    # Identification
    appraisal_code = Column(String(50), nullable=False, index=True)
    
    # Links
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    appraisal_cycle_id = Column(UUID(as_uuid=True), ForeignKey("hrms_appraisal_cycles.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    
    # Status
    status = Column(SQLEnum(AppraisalStatus), nullable=False, default=AppraisalStatus.NOT_STARTED)
    
    # Goal Setting
    goals_submitted_date = Column(DateTime, nullable=True)
    goals_approved_date = Column(DateTime, nullable=True)
    
    # Self Assessment
    self_assessment_submitted_date = Column(DateTime, nullable=True)
    self_rating = Column(SQLEnum(RatingScale), nullable=True)
    self_rating_numeric = Column(Numeric(3, 2), nullable=True)  # 1.00 to 5.00
    self_comments = Column(Text, nullable=True)
    key_achievements = Column(Text, nullable=True)
    areas_of_improvement = Column(Text, nullable=True)
    
    # Manager Review
    manager_review_submitted_date = Column(DateTime, nullable=True)
    manager_rating = Column(SQLEnum(RatingScale), nullable=True)
    manager_rating_numeric = Column(Numeric(3, 2), nullable=True)
    manager_comments = Column(Text, nullable=True)
    manager_strengths = Column(Text, nullable=True)
    manager_development_areas = Column(Text, nullable=True)
    
    # HR Review
    hr_review_submitted_date = Column(DateTime, nullable=True)
    hr_comments = Column(Text, nullable=True)
    
    # Final Rating
    final_rating = Column(SQLEnum(RatingScale), nullable=True)
    final_rating_numeric = Column(Numeric(3, 2), nullable=True)
    normalized_rating = Column(SQLEnum(RatingScale), nullable=True)
    normalized_rating_numeric = Column(Numeric(3, 2), nullable=True)
    
    # Overall Goal Achievement
    overall_goal_achievement_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Increment & Promotion
    recommended_increment_percentage = Column(Numeric(5, 2), nullable=True)
    recommended_promotion = Column(Boolean, default=False)
    recommended_promotion_designation_id = Column(UUID(as_uuid=True), ForeignKey("hrms_designations.id", ondelete="SET NULL"), nullable=True)
    
    # Completion
    completed_date = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="appraisals")
    appraisal_cycle = relationship("AppraisalCycle", back_populates="appraisals")
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    recommended_promotion_designation = relationship("Designation", foreign_keys=[recommended_promotion_designation_id])
    feedback_received = relationship("FeedbackResponse", back_populates="appraisal", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_appraisal_emp_cycle', 'tenant_id', 'employee_id', 'appraisal_cycle_id', unique=True),
        Index('idx_tenant_appraisal_code', 'tenant_id', 'appraisal_code'),
        Index('idx_tenant_appraisal_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<EmployeeAppraisal(code={self.appraisal_code}, employee_id={self.employee_id})>"


# ============================================================================
# PERFORMANCE MANAGEMENT - 360 DEGREE FEEDBACK
# ============================================================================

class FeedbackRequest(BaseModel):
    """
    360-Degree Feedback Requests
    Requests sent to various stakeholders for feedback
    """
    __tablename__ = "hrms_feedback_requests"
    
    # Request Identification
    request_code = Column(String(50), nullable=False, index=True)
    
    # Subject & Reviewer
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)  # Subject
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)  # Reviewer
    appraisal_cycle_id = Column(UUID(as_uuid=True), ForeignKey("hrms_appraisal_cycles.id", ondelete="CASCADE"), nullable=False)
    
    # Feedback Type
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    
    # Request Details
    requested_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(Date, nullable=True)
    
    # Status
    status = Column(SQLEnum(FeedbackStatus), nullable=False, default=FeedbackStatus.PENDING)
    
    # Reminders
    reminder_sent_count = Column(Integer, default=0)
    last_reminder_date = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])  # Subject
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])  # Reviewer
    appraisal_cycle = relationship("AppraisalCycle", back_populates="feedback_requests")
    response = relationship("FeedbackResponse", back_populates="feedback_request", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_feedback_req_emp', 'tenant_id', 'employee_id', 'appraisal_cycle_id'),
        Index('idx_tenant_feedback_req_reviewer', 'tenant_id', 'reviewer_id', 'status'),
        Index('idx_tenant_feedback_req_code', 'tenant_id', 'request_code'),
    )
    
    def __repr__(self):
        return f"<FeedbackRequest(code={self.request_code}, type={self.feedback_type})>"


class FeedbackResponse(BaseModel):
    """
    360-Degree Feedback Responses
    Actual feedback submitted by reviewers
    """
    __tablename__ = "hrms_feedback_responses"
    
    # Response Link
    feedback_request_id = Column(UUID(as_uuid=True), ForeignKey("hrms_feedback_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    employee_appraisal_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employee_appraisals.id", ondelete="CASCADE"), nullable=True)
    
    # Rating
    overall_rating = Column(SQLEnum(RatingScale), nullable=True)
    overall_rating_numeric = Column(Numeric(3, 2), nullable=True)
    
    # Competency Ratings (JSON or separate table)
    technical_skills_rating = Column(Integer, nullable=True)  # 1-5
    communication_skills_rating = Column(Integer, nullable=True)
    teamwork_rating = Column(Integer, nullable=True)
    leadership_rating = Column(Integer, nullable=True)
    problem_solving_rating = Column(Integer, nullable=True)
    
    # Feedback Text
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    additional_comments = Column(Text, nullable=True)
    
    # Submission
    submitted_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    acknowledged_date = Column(DateTime, nullable=True)
    
    # Confidentiality
    is_anonymous = Column(Boolean, default=False)
    
    # Relationships
    feedback_request = relationship("FeedbackRequest", back_populates="response")
    appraisal = relationship("EmployeeAppraisal", back_populates="feedback_received")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_feedback_resp_request', 'tenant_id', 'feedback_request_id', unique=True),
        Index('idx_tenant_feedback_resp_appraisal', 'tenant_id', 'employee_appraisal_id'),
    )
    
    def __repr__(self):
        return f"<FeedbackResponse(request_id={self.feedback_request_id})>"


# ============================================================================
# PERFORMANCE MANAGEMENT - RATINGS & INCREMENT
# ============================================================================

class PerformanceIncrement(BaseModel):
    """
    Performance-based Increments
    Salary increments based on performance ratings
    """
    __tablename__ = "hrms_performance_increments"
    
    # Increment Identification
    increment_code = Column(String(50), nullable=False, index=True)
    
    # Employee & Appraisal
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    employee_appraisal_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employee_appraisals.id", ondelete="SET NULL"), nullable=True)
    appraisal_cycle_id = Column(UUID(as_uuid=True), ForeignKey("hrms_appraisal_cycles.id", ondelete="SET NULL"), nullable=True)
    
    # Increment Type
    increment_type = Column(SQLEnum(IncrementType), nullable=False, default=IncrementType.ANNUAL)
    
    # Salary Details
    current_ctc = Column(Numeric(15, 2), nullable=False)
    increment_percentage = Column(Numeric(5, 2), nullable=False)
    increment_amount = Column(Numeric(15, 2), nullable=False)
    revised_ctc = Column(Numeric(15, 2), nullable=False)
    
    # Effective Date
    effective_from = Column(Date, nullable=False)
    
    # Approval
    recommended_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Status
    is_approved = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    processed_date = Column(DateTime, nullable=True)
    
    # Comments
    remarks = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    employee_appraisal = relationship("EmployeeAppraisal", foreign_keys=[employee_appraisal_id])
    appraisal_cycle = relationship("AppraisalCycle", foreign_keys=[appraisal_cycle_id])
    recommended_by = relationship("Employee", foreign_keys=[recommended_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_increment_emp', 'tenant_id', 'employee_id'),
        Index('idx_tenant_increment_code', 'tenant_id', 'increment_code'),
        Index('idx_tenant_increment_cycle', 'tenant_id', 'appraisal_cycle_id'),
    )
    
    def __repr__(self):
        return f"<PerformanceIncrement(code={self.increment_code}, employee_id={self.employee_id})>"


# ============================================================================
# PERFORMANCE MANAGEMENT - INDIVIDUAL DEVELOPMENT PLAN (IDP)
# ============================================================================

class IndividualDevelopmentPlan(BaseModel):
    """
    Individual Development Plans (IDP)
    Career development and skill enhancement plans
    """
    __tablename__ = "hrms_individual_development_plans"
    
    # IDP Identification
    idp_code = Column(String(50), nullable=False, index=True)
    idp_title = Column(String(200), nullable=False)
    
    # Employee & Period
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    appraisal_cycle_id = Column(UUID(as_uuid=True), ForeignKey("hrms_appraisal_cycles.id", ondelete="SET NULL"), nullable=True)
    
    # Career Aspirations
    career_goal = Column(Text, nullable=True)
    target_role = Column(String(200), nullable=True)
    target_designation_id = Column(UUID(as_uuid=True), ForeignKey("hrms_designations.id", ondelete="SET NULL"), nullable=True)
    
    # Skill Gaps
    current_skills = Column(Text, nullable=True)  # JSON or text
    required_skills = Column(Text, nullable=True)  # JSON or text
    skill_gaps = Column(Text, nullable=True)  # JSON or text
    
    # Timeline
    plan_start_date = Column(Date, nullable=False)
    plan_end_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(IDPStatus), nullable=False, default=IDPStatus.DRAFT)
    
    # Approval
    submitted_date = Column(DateTime, nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Progress
    overall_progress_percentage = Column(Integer, default=0)
    
    # Comments
    employee_notes = Column(Text, nullable=True)
    manager_notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="development_plans")
    appraisal_cycle = relationship("AppraisalCycle", foreign_keys=[appraisal_cycle_id])
    target_designation = relationship("Designation", foreign_keys=[target_designation_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    activities = relationship("DevelopmentActivity", back_populates="idp", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_idp_emp', 'tenant_id', 'employee_id'),
        Index('idx_tenant_idp_code', 'tenant_id', 'idp_code'),
        Index('idx_tenant_idp_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<IndividualDevelopmentPlan(code={self.idp_code}, title={self.idp_title})>"


class DevelopmentActivity(BaseModel):
    """
    Development Activities
    Individual learning/development activities within an IDP
    """
    __tablename__ = "hrms_development_activities"
    
    # Activity Identification
    activity_code = Column(String(50), nullable=False, index=True)
    activity_title = Column(String(200), nullable=False)
    activity_description = Column(Text, nullable=True)
    
    # IDP Link
    idp_id = Column(UUID(as_uuid=True), ForeignKey("hrms_individual_development_plans.id", ondelete="CASCADE"), nullable=False)
    
    # Activity Type
    activity_type = Column(SQLEnum(DevelopmentActivityType), nullable=False)
    
    # Details
    provider_name = Column(String(200), nullable=True)  # Training provider, mentor name, etc.
    course_name = Column(String(200), nullable=True)
    duration_hours = Column(Integer, nullable=True)
    cost = Column(Numeric(15, 2), nullable=True)
    
    # Timeline
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    actual_start_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)
    
    # Outcome
    certification_obtained = Column(String(200), nullable=True)
    certificate_url = Column(String(500), nullable=True)
    learning_outcome = Column(Text, nullable=True)
    
    # Comments
    employee_feedback = Column(Text, nullable=True)
    manager_feedback = Column(Text, nullable=True)
    
    # Relationships
    idp = relationship("IndividualDevelopmentPlan", back_populates="activities")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_activity_idp', 'tenant_id', 'idp_id'),
        Index('idx_tenant_activity_code', 'tenant_id', 'activity_code'),
    )
    
    def __repr__(self):
        return f"<DevelopmentActivity(code={self.activity_code}, title={self.activity_title})>"


# ============================================================================
# EMPLOYEE SELF-SERVICE ENUMS
# ============================================================================

class LeaveType(str, enum.Enum):
    """Leave type"""
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    COMPENSATORY_OFF = "compensatory_off"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    MARRIAGE = "marriage"
    UNPAID = "unpaid"
    SABBATICAL = "sabbatical"
    WORK_FROM_HOME = "work_from_home"


class LeaveStatus(str, enum.Enum):
    """Leave application status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"


class InvestmentSection(str, enum.Enum):
    """Tax investment sections"""
    SECTION_80C = "80C"  # PPF, LIC, ELSS, etc.
    SECTION_80D = "80D"  # Medical Insurance
    SECTION_80E = "80E"  # Education Loan Interest
    SECTION_80G = "80G"  # Donations
    SECTION_24 = "24"    # Home Loan Interest
    SECTION_80CCD = "80CCD"  # NPS
    HRA = "HRA"  # House Rent Allowance
    LTA = "LTA"  # Leave Travel Allowance
    OTHER = "OTHER"


class InvestmentStatus(str, enum.Enum):
    """Investment declaration status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    APPROVED = "approved"


class ReimbursementType(str, enum.Enum):
    """Reimbursement type"""
    TRAVEL = "travel"
    MEDICAL = "medical"
    TELEPHONE = "telephone"
    INTERNET = "internet"
    FUEL = "fuel"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    TRAINING = "training"
    UNIFORM = "uniform"
    RELOCATION = "relocation"
    OTHER = "other"


class ReimbursementStatus(str, enum.Enum):
    """Reimbursement claim status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"
    PAID = "paid"


# ============================================================================
# LEAVE MANAGEMENT
# ============================================================================

class LeaveBalance(BaseModel):
    """
    Leave Balance
    Tracks available leave balance for each employee by leave type
    """
    __tablename__ = "hrms_leave_balances"
    
    # Employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    
    # Leave Type
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    
    # Financial Year
    financial_year = Column(String(20), nullable=False)  # e.g., "2024-25"
    
    # Balance
    opening_balance = Column(Numeric(5, 2), default=0, nullable=False)
    accrued = Column(Numeric(5, 2), default=0, nullable=False)
    used = Column(Numeric(5, 2), default=0, nullable=False)
    lapsed = Column(Numeric(5, 2), default=0, nullable=False)
    carried_forward = Column(Numeric(5, 2), default=0, nullable=False)
    current_balance = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Policy
    max_carry_forward = Column(Numeric(5, 2), nullable=True)
    max_encashment = Column(Numeric(5, 2), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_balances")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_leave_bal_emp', 'tenant_id', 'employee_id', 'financial_year', 'leave_type', unique=True),
        Index('idx_leave_bal_year', 'tenant_id', 'financial_year'),
    )
    
    def __repr__(self):
        return f"<LeaveBalance(employee_id={self.employee_id}, type={self.leave_type}, balance={self.current_balance})>"


class LeaveApplication(BaseModel):
    """
    Leave Application
    Employee leave requests and applications
    """
    __tablename__ = "hrms_leave_applications"
    
    # Application Identification
    application_code = Column(String(50), nullable=False, index=True)
    
    # Employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    
    # Leave Details
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    number_of_days = Column(Numeric(5, 2), nullable=False)
    
    # Half Day Options
    is_half_day = Column(Boolean, default=False)
    half_day_session = Column(String(20), nullable=True)  # first_half, second_half
    
    # Reason
    reason = Column(Text, nullable=False)
    contact_number_during_leave = Column(String(20), nullable=True)
    contact_address_during_leave = Column(Text, nullable=True)
    
    # Approval Workflow
    status = Column(SQLEnum(LeaveStatus), nullable=False, default=LeaveStatus.DRAFT)
    submitted_date = Column(DateTime, nullable=True)
    
    # First Level Approval (Reporting Manager)
    approver1_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approver1_status = Column(String(20), nullable=True)  # pending, approved, rejected
    approver1_date = Column(DateTime, nullable=True)
    approver1_comments = Column(Text, nullable=True)
    
    # Second Level Approval (Department Head)
    approver2_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approver2_status = Column(String(20), nullable=True)
    approver2_date = Column(DateTime, nullable=True)
    approver2_comments = Column(Text, nullable=True)
    
    # HR Approval
    hr_approver_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    hr_status = Column(String(20), nullable=True)
    hr_date = Column(DateTime, nullable=True)
    hr_comments = Column(Text, nullable=True)
    
    # Final Status
    approved_date = Column(DateTime, nullable=True)
    rejected_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Cancellation
    is_cancelled = Column(Boolean, default=False)
    cancelled_date = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Attachments
    attachment_urls = Column(Text, nullable=True)  # JSON array of URLs
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_applications")
    approver1 = relationship("Employee", foreign_keys=[approver1_id])
    approver2 = relationship("Employee", foreign_keys=[approver2_id])
    hr_approver = relationship("Employee", foreign_keys=[hr_approver_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_leave_app_code', 'tenant_id', 'application_code', unique=True),
        Index('idx_tenant_leave_app_emp', 'tenant_id', 'employee_id', 'status'),
        Index('idx_leave_app_dates', 'tenant_id', 'from_date', 'to_date'),
        Index('idx_leave_app_approver', 'tenant_id', 'approver1_id', 'approver1_status'),
    )
    
    def __repr__(self):
        return f"<LeaveApplication(code={self.application_code}, employee_id={self.employee_id})>"


# ============================================================================
# INVESTMENT DECLARATION (TAX SAVING)
# ============================================================================

class InvestmentDeclaration(BaseModel):
    """
    Investment Declaration
    Annual tax saving investment declarations by employees
    """
    __tablename__ = "hrms_investment_declarations"
    
    # Declaration Identification
    declaration_code = Column(String(50), nullable=False, index=True)
    
    # Employee & Period
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    financial_year = Column(String(20), nullable=False)  # e.g., "2024-25"
    
    # Tax Regime
    tax_regime = Column(String(20), nullable=False, default="old")  # old, new
    
    # Status
    status = Column(SQLEnum(InvestmentStatus), nullable=False, default=InvestmentStatus.DRAFT)
    
    # Submission
    submitted_date = Column(DateTime, nullable=True)
    submitted_by_employee = Column(Boolean, default=False)
    
    # Verification
    verified_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    verification_comments = Column(Text, nullable=True)
    
    # Approval
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    
    # Rejection
    rejected_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Lock Status
    is_locked = Column(Boolean, default=False)
    locked_date = Column(DateTime, nullable=True)
    
    # Totals (calculated from line items)
    total_declared_amount = Column(Numeric(15, 2), default=0)
    total_approved_amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="investment_declarations")
    verified_by = relationship("Employee", foreign_keys=[verified_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    line_items = relationship("InvestmentDeclarationItem", back_populates="declaration", lazy="select", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_inv_decl_code', 'tenant_id', 'declaration_code', unique=True),
        Index('idx_tenant_inv_decl_emp', 'tenant_id', 'employee_id', 'financial_year'),
        Index('idx_inv_decl_year', 'tenant_id', 'financial_year'),
        Index('idx_inv_decl_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<InvestmentDeclaration(code={self.declaration_code}, employee_id={self.employee_id})>"


class InvestmentDeclarationItem(BaseModel):
    """
    Investment Declaration Line Items
    Individual investment items under each declaration
    """
    __tablename__ = "hrms_investment_declaration_items"
    
    # Declaration Link
    declaration_id = Column(UUID(as_uuid=True), ForeignKey("hrms_investment_declarations.id", ondelete="CASCADE"), nullable=False)
    
    # Investment Details
    section = Column(SQLEnum(InvestmentSection), nullable=False)
    investment_type = Column(String(100), nullable=False)  # PPF, LIC, ELSS, Medical Insurance, etc.
    description = Column(Text, nullable=True)
    
    # Amount
    declared_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2), nullable=True)
    
    # Proof Details
    proof_document_name = Column(String(200), nullable=True)
    proof_document_url = Column(String(500), nullable=True)
    policy_number = Column(String(100), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_remarks = Column(Text, nullable=True)
    
    # Relationships
    declaration = relationship("InvestmentDeclaration", back_populates="line_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_inv_item_decl', 'tenant_id', 'declaration_id'),
        Index('idx_inv_item_section', 'tenant_id', 'section'),
    )
    
    def __repr__(self):
        return f"<InvestmentDeclarationItem(declaration_id={self.declaration_id}, section={self.section})>"


# ============================================================================
# REIMBURSEMENT CLAIMS
# ============================================================================

class ReimbursementClaim(BaseModel):
    """
    Reimbursement Claims
    Employee expense reimbursement claims
    """
    __tablename__ = "hrms_reimbursement_claims"
    
    # Claim Identification
    claim_code = Column(String(50), nullable=False, index=True)
    claim_title = Column(String(200), nullable=False)
    
    # Employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    
    # Claim Type
    reimbursement_type = Column(SQLEnum(ReimbursementType), nullable=False)
    
    # Claim Details
    claim_description = Column(Text, nullable=False)
    expense_date = Column(Date, nullable=False)
    claim_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2), nullable=True)
    
    # Bill/Receipt Details
    bill_number = Column(String(100), nullable=True)
    vendor_name = Column(String(200), nullable=True)
    
    # Attachments
    attachment_urls = Column(Text, nullable=True)  # JSON array of bill/receipt URLs
    
    # Status
    status = Column(SQLEnum(ReimbursementStatus), nullable=False, default=ReimbursementStatus.DRAFT)
    submitted_date = Column(DateTime, nullable=True)
    
    # Approval Workflow
    approver_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approver_status = Column(String(20), nullable=True)  # pending, approved, rejected
    approved_date = Column(DateTime, nullable=True)
    approver_comments = Column(Text, nullable=True)
    
    # HR Processing
    hr_processor_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    hr_processed_date = Column(DateTime, nullable=True)
    hr_comments = Column(Text, nullable=True)
    
    # Rejection
    rejected_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Payment
    is_paid = Column(Boolean, default=False)
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    payment_mode = Column(String(50), nullable=True)  # bank_transfer, cash, cheque
    
    # Accounting
    expense_account_code = Column(String(50), nullable=True)
    cost_center_code = Column(String(50), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="reimbursement_claims")
    approver = relationship("Employee", foreign_keys=[approver_id])
    hr_processor = relationship("Employee", foreign_keys=[hr_processor_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_reimb_claim_code', 'tenant_id', 'claim_code', unique=True),
        Index('idx_tenant_reimb_claim_emp', 'tenant_id', 'employee_id', 'status'),
        Index('idx_reimb_claim_type', 'tenant_id', 'reimbursement_type'),
        Index('idx_reimb_claim_approver', 'tenant_id', 'approver_id', 'approver_status'),
        Index('idx_reimb_claim_payment', 'tenant_id', 'is_paid'),
    )
    
    def __repr__(self):
        return f"<ReimbursementClaim(code={self.claim_code}, employee_id={self.employee_id})>"


# ============================================================================
# UPDATE EMPLOYEE MODEL WITH ESS RELATIONSHIPS
# ============================================================================

# Add these relationships to Employee model
Employee.performance_goals = relationship("PerformanceGoal", foreign_keys="PerformanceGoal.employee_id", back_populates="employee", lazy="select")
Employee.appraisals = relationship("EmployeeAppraisal", foreign_keys="EmployeeAppraisal.employee_id", back_populates="employee", lazy="select")
Employee.development_plans = relationship("IndividualDevelopmentPlan", foreign_keys="IndividualDevelopmentPlan.employee_id", back_populates="employee", lazy="select")

# Employee Self-Service Relationships
Employee.leave_balances = relationship("LeaveBalance", foreign_keys="LeaveBalance.employee_id", back_populates="employee", lazy="select")
Employee.leave_applications = relationship("LeaveApplication", foreign_keys="LeaveApplication.employee_id", back_populates="employee", lazy="select")
Employee.investment_declarations = relationship("InvestmentDeclaration", foreign_keys="InvestmentDeclaration.employee_id", back_populates="employee", lazy="select")
Employee.reimbursement_claims = relationship("ReimbursementClaim", foreign_keys="ReimbursementClaim.employee_id", back_populates="employee", lazy="select")


# ============================================================================
# EXIT MANAGEMENT
# ============================================================================

class ResignationType(str, enum.Enum):
    """Type of resignation"""
    VOLUNTARY = "voluntary"
    INVOLUNTARY = "involuntary"
    RETIREMENT = "retirement"
    ABSCONDING = "absconding"
    END_OF_CONTRACT = "end_of_contract"
    MUTUAL_CONSENT = "mutual_consent"


class ResignationStatus(str, enum.Enum):
    """Resignation status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClearanceStatus(str, enum.Enum):
    """Clearance status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_APPLICABLE = "not_applicable"
    WAIVED = "waived"


class SettlementStatus(str, enum.Enum):
    """Settlement status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PROCESSING = "processing"
    PAID = "paid"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"


class SettlementComponentType(str, enum.Enum):
    """Settlement component type"""
    SALARY = "salary"  # Pending salary
    LEAVE_ENCASHMENT = "leave_encashment"  # Unused leave encashment
    NOTICE_PAY = "notice_pay"  # Notice period payment
    BONUS = "bonus"  # Pending bonus
    GRATUITY = "gratuity"  # Gratuity payment
    REIMBURSEMENT = "reimbursement"  # Pending reimbursements
    RECOVERY = "recovery"  # Amount to be recovered
    OTHER = "other"  # Other components


class ExitDocumentType(str, enum.Enum):
    """Exit document type"""
    RESIGNATION_LETTER = "resignation_letter"
    ACCEPTANCE_LETTER = "acceptance_letter"
    EXPERIENCE_LETTER = "experience_letter"
    RELIEVING_LETTER = "relieving_letter"
    SERVICE_CERTIFICATE = "service_certificate"
    NOC = "noc"  # No Objection Certificate
    CLEARANCE_FORM = "clearance_form"
    FNF_STATEMENT = "fnf_statement"  # Full and Final Settlement
    FORM_16 = "form_16"
    PF_WITHDRAWAL = "pf_withdrawal"
    GRATUITY_FORM = "gratuity_form"
    OTHER = "other"


class Resignation(BaseModel):
    """
    Resignation/Exit Request entity
    Manages employee resignation and exit process
    """
    __tablename__ = "exit_resignations"
    
    # Basic Information
    resignation_code = Column(String(50), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Resignation Details
    resignation_type = Column(SQLEnum(ResignationType), nullable=False, default=ResignationType.VOLUNTARY)
    resignation_date = Column(Date, nullable=False)  # Date of submission
    last_working_date = Column(Date, nullable=False)  # Intended last working date
    actual_last_working_date = Column(Date, nullable=True)  # Actual last working date
    
    # Notice Period
    notice_period_days = Column(Integer, nullable=False, default=30)  # As per policy
    notice_period_served = Column(Integer, nullable=True)  # Actual days served
    is_notice_period_waived = Column(Boolean, default=False)
    notice_waiver_reason = Column(Text, nullable=True)
    
    # Reason for Leaving
    reason_category = Column(String(100), nullable=True)  # career_growth, higher_studies, relocation, etc.
    reason_details = Column(Text, nullable=False)
    feedback = Column(Text, nullable=True)  # Exit interview feedback
    
    # Status and Workflow
    status = Column(SQLEnum(ResignationStatus), nullable=False, default=ResignationStatus.SUBMITTED, index=True)
    
    # Reporting Manager Review
    reporting_manager_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    manager_reviewed_date = Column(DateTime, nullable=True)
    manager_comments = Column(Text, nullable=True)
    manager_recommendation = Column(String(50), nullable=True)  # approve, reject, counter_offer
    
    # HR Review
    hr_reviewer_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    hr_reviewed_date = Column(DateTime, nullable=True)
    hr_comments = Column(Text, nullable=True)
    
    # Approval
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    
    # Rejection/Withdrawal
    rejected_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    withdrawn_date = Column(DateTime, nullable=True)
    withdrawal_reason = Column(Text, nullable=True)
    
    # Counter Offer
    counter_offer_made = Column(Boolean, default=False)
    counter_offer_details = Column(Text, nullable=True)
    counter_offer_accepted = Column(Boolean, nullable=True)
    
    # Exit Interview
    exit_interview_scheduled = Column(Boolean, default=False)
    exit_interview_date = Column(DateTime, nullable=True)
    exit_interview_conducted_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    exit_interview_notes = Column(Text, nullable=True)
    
    # Handover
    handover_completed = Column(Boolean, default=False)
    handover_to_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    handover_notes = Column(Text, nullable=True)
    handover_document_path = Column(String(500), nullable=True)
    
    # Additional Info
    re_employment_eligible = Column(Boolean, default=True)
    blacklist_flag = Column(Boolean, default=False)
    blacklist_reason = Column(Text, nullable=True)
    
    # Attachments
    resignation_letter_path = Column(String(500), nullable=True)
    supporting_documents = Column(Text, nullable=True)  # JSON array of document paths
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="resignations")
    reporting_manager = relationship("Employee", foreign_keys=[reporting_manager_id])
    hr_reviewer = relationship("Employee", foreign_keys=[hr_reviewer_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    exit_interviewer = relationship("Employee", foreign_keys=[exit_interview_conducted_by_id])
    handover_to = relationship("Employee", foreign_keys=[handover_to_employee_id])
    clearances = relationship("ExitClearance", back_populates="resignation", cascade="all, delete-orphan", lazy="select")
    settlement = relationship("ExitSettlement", back_populates="resignation", uselist=False, cascade="all, delete-orphan", lazy="select")
    documents = relationship("ExitDocument", back_populates="resignation", cascade="all, delete-orphan", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_resignation_code', 'tenant_id', 'resignation_code', unique=True),
        Index('idx_tenant_resignation_emp', 'tenant_id', 'employee_id', 'status'),
        Index('idx_resignation_dates', 'tenant_id', 'resignation_date', 'last_working_date'),
        Index('idx_resignation_manager', 'tenant_id', 'reporting_manager_id'),
    )
    
    def __repr__(self):
        return f"<Resignation(code={self.resignation_code}, employee_id={self.employee_id}, status={self.status})>"


class ExitClearance(BaseModel):
    """
    Exit Clearance entity
    Manages clearance from different departments/functions
    """
    __tablename__ = "exit_clearances"
    
    # Basic Information
    resignation_id = Column(UUID(as_uuid=True), ForeignKey("exit_resignations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Clearance Details
    clearance_from = Column(String(100), nullable=False)  # Department/Function name (IT, Admin, Finance, etc.)
    clearance_type = Column(String(100), nullable=False)  # asset_return, document_submission, accounts_clearance, etc.
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(SQLEnum(ClearanceStatus), nullable=False, default=ClearanceStatus.PENDING, index=True)
    
    # Assigned To
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    assigned_date = Column(DateTime, nullable=True)
    
    # Clearance Items/Checklist
    checklist_items = Column(Text, nullable=True)  # JSON array of items to be cleared
    pending_items = Column(Text, nullable=True)  # JSON array of pending items
    
    # Completion
    cleared_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    cleared_date = Column(DateTime, nullable=True)
    clearance_remarks = Column(Text, nullable=True)
    
    # Attachments
    supporting_documents = Column(Text, nullable=True)  # JSON array of document paths
    
    # Dependencies
    is_mandatory = Column(Boolean, default=True)
    depends_on_clearance_id = Column(UUID(as_uuid=True), ForeignKey("exit_clearances.id", ondelete="SET NULL"), nullable=True)
    
    # Escalation
    due_date = Column(Date, nullable=True)
    is_overdue = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)
    
    # Relationships
    resignation = relationship("Resignation", back_populates="clearances")
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])
    cleared_by = relationship("Employee", foreign_keys=[cleared_by_id])
    depends_on = relationship("ExitClearance", remote_side="ExitClearance.id", foreign_keys=[depends_on_clearance_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_clearance_resignation', 'tenant_id', 'resignation_id'),
        Index('idx_clearance_status', 'tenant_id', 'status'),
        Index('idx_clearance_assigned', 'tenant_id', 'assigned_to_id', 'status'),
    )
    
    def __repr__(self):
        return f"<ExitClearance(resignation_id={self.resignation_id}, clearance_from={self.clearance_from}, status={self.status})>"


class ExitSettlement(BaseModel):
    """
    Exit Settlement (Full & Final Settlement) entity
    Manages financial settlement calculations and payments
    """
    __tablename__ = "exit_settlements"
    
    # Basic Information
    settlement_code = Column(String(50), nullable=False, index=True)
    resignation_id = Column(UUID(as_uuid=True), ForeignKey("exit_resignations.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Settlement Period
    settlement_from_date = Column(Date, nullable=False)
    settlement_to_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(SettlementStatus), nullable=False, default=SettlementStatus.PENDING, index=True)
    
    # Calculation Details
    # Salary Components
    basic_salary_days = Column(Integer, nullable=True)
    basic_salary_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Leave Encashment
    total_leave_balance = Column(Numeric(10, 2), nullable=True, default=Decimal('0.00'))
    encashable_leaves = Column(Numeric(10, 2), nullable=True, default=Decimal('0.00'))
    leave_encashment_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Notice Period
    notice_period_shortfall_days = Column(Integer, nullable=True, default=0)
    notice_pay_recovery = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Gratuity
    years_of_service = Column(Numeric(5, 2), nullable=True)
    gratuity_eligible = Column(Boolean, default=False)
    gratuity_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Bonus/Incentives
    bonus_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    incentive_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Reimbursements
    pending_reimbursement_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Recoveries/Deductions
    loan_recovery = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    advance_recovery = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    asset_loss_recovery = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    other_recovery = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    recovery_remarks = Column(Text, nullable=True)
    
    # Totals
    gross_payable = Column(Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    total_deductions = Column(Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    net_payable = Column(Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    
    # Tax
    tds_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    professional_tax = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Calculated By
    calculated_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    calculated_date = Column(DateTime, nullable=True)
    calculation_remarks = Column(Text, nullable=True)
    
    # Approval
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    approval_remarks = Column(Text, nullable=True)
    
    # Finance Processing
    finance_processor_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    finance_processed_date = Column(DateTime, nullable=True)
    finance_remarks = Column(Text, nullable=True)
    
    # Payment Details
    payment_date = Column(Date, nullable=True)
    payment_mode = Column(String(50), nullable=True)  # bank_transfer, cheque, cash
    payment_reference = Column(String(100), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_name = Column(String(200), nullable=True)
    bank_ifsc_code = Column(String(20), nullable=True)
    
    # Hold/Rejection
    hold_reason = Column(Text, nullable=True)
    hold_until_date = Column(Date, nullable=True)
    rejected_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Attachments
    fnf_statement_path = Column(String(500), nullable=True)
    supporting_documents = Column(Text, nullable=True)  # JSON array
    
    # Relationships
    resignation = relationship("Resignation", back_populates="settlement")
    employee = relationship("Employee", foreign_keys=[employee_id])
    calculated_by = relationship("Employee", foreign_keys=[calculated_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    finance_processor = relationship("Employee", foreign_keys=[finance_processor_id])
    components = relationship("SettlementComponent", back_populates="settlement", cascade="all, delete-orphan", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_settlement_code', 'tenant_id', 'settlement_code', unique=True),
        Index('idx_tenant_settlement_emp', 'tenant_id', 'employee_id'),
        Index('idx_settlement_status', 'tenant_id', 'status'),
        Index('idx_settlement_payment', 'tenant_id', 'payment_date'),
    )
    
    def __repr__(self):
        return f"<ExitSettlement(code={self.settlement_code}, employee_id={self.employee_id}, net_payable={self.net_payable})>"


class SettlementComponent(BaseModel):
    """
    Settlement Component entity
    Detailed breakdown of settlement components
    """
    __tablename__ = "exit_settlement_components"
    
    # Basic Information
    settlement_id = Column(UUID(as_uuid=True), ForeignKey("exit_settlements.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Component Details
    component_type = Column(SQLEnum(SettlementComponentType), nullable=False)
    component_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    is_deduction = Column(Boolean, default=False)  # True for recoveries/deductions
    
    # Calculation Details
    calculation_basis = Column(Text, nullable=True)
    quantity = Column(Numeric(10, 2), nullable=True)  # e.g., number of days, number of leaves
    rate = Column(Numeric(15, 2), nullable=True)  # e.g., per day rate
    
    # Tax
    is_taxable = Column(Boolean, default=True)
    tax_amount = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Relationships
    settlement = relationship("ExitSettlement", back_populates="components")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_settlement_comp', 'tenant_id', 'settlement_id'),
        Index('idx_settlement_comp_type', 'tenant_id', 'component_type'),
    )
    
    def __repr__(self):
        return f"<SettlementComponent(settlement_id={self.settlement_id}, type={self.component_type}, amount={self.amount})>"


class ExitDocument(BaseModel):
    """
    Exit Document entity
    Manages all exit-related documents (experience letter, relieving letter, etc.)
    """
    __tablename__ = "exit_documents"
    
    # Basic Information
    document_code = Column(String(50), nullable=False, index=True)
    resignation_id = Column(UUID(as_uuid=True), ForeignKey("exit_resignations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document Details
    document_type = Column(SQLEnum(ExitDocumentType), nullable=False, index=True)
    document_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template
    template_name = Column(String(200), nullable=True)
    template_version = Column(String(20), nullable=True)
    
    # Content
    document_content = Column(Text, nullable=True)  # For system-generated documents
    document_path = Column(String(500), nullable=True)  # For uploaded/stored documents
    document_url = Column(String(500), nullable=True)  # For external links
    
    # Status
    is_generated = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_issued = Column(Boolean, default=False)
    
    # Generation
    generated_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    generated_date = Column(DateTime, nullable=True)
    
    # Approval
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    approval_remarks = Column(Text, nullable=True)
    
    # Issuance
    issued_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    issued_date = Column(DateTime, nullable=True)
    issue_remarks = Column(Text, nullable=True)
    
    # Document Metadata
    document_number = Column(String(100), nullable=True)  # Reference number on the document
    issue_place = Column(String(200), nullable=True)
    validity_date = Column(Date, nullable=True)
    
    # Digital Signature
    is_digitally_signed = Column(Boolean, default=False)
    digital_signature_info = Column(Text, nullable=True)
    
    # Delivery
    delivery_mode = Column(String(50), nullable=True)  # email, hard_copy, courier, portal
    delivered_date = Column(DateTime, nullable=True)
    recipient_email = Column(String(100), nullable=True)
    recipient_address = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    
    # Employee Acknowledgment
    acknowledged_by_employee = Column(Boolean, default=False)
    acknowledgment_date = Column(DateTime, nullable=True)
    
    # Relationships
    resignation = relationship("Resignation", back_populates="documents")
    employee = relationship("Employee", foreign_keys=[employee_id])
    generated_by = relationship("Employee", foreign_keys=[generated_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    issued_by = relationship("Employee", foreign_keys=[issued_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_exit_doc_code', 'tenant_id', 'document_code', unique=True),
        Index('idx_tenant_exit_doc_resignation', 'tenant_id', 'resignation_id'),
        Index('idx_exit_doc_type', 'tenant_id', 'document_type'),
        Index('idx_exit_doc_employee', 'tenant_id', 'employee_id'),
    )
    
    def __repr__(self):
        return f"<ExitDocument(code={self.document_code}, type={self.document_type}, employee_id={self.employee_id})>"


# ============================================================================
# UPDATE EMPLOYEE MODEL WITH EXIT MANAGEMENT RELATIONSHIPS
# ============================================================================

# Add these relationships to Employee model
Employee.resignations = relationship("Resignation", foreign_keys="Resignation.employee_id", back_populates="employee", lazy="select")
