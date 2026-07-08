"""
HRMS Recruitment & Onboarding Database Models
Job Requisitions, Applicant Tracking, Interviews, Onboarding, Background Verification
"""

from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, Text, ForeignKey, Numeric, Enum as SQLEnum, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from decimal import Decimal
import enum

from backend.shared.database.models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class RequisitionStatus(str, enum.Enum):
    """Job requisition status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class RequisitionPriority(str, enum.Enum):
    """Requisition priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EmploymentType(str, enum.Enum):
    """Employment type"""
    PERMANENT = "permanent"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"


class PostingStatus(str, enum.Enum):
    """Job posting status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class ApplicationSource(str, enum.Enum):
    """Application source"""
    CAREER_PAGE = "career_page"
    REFERRAL = "referral"
    JOB_PORTAL = "job_portal"
    LINKEDIN = "linkedin"
    WALK_IN = "walk_in"
    RECRUITMENT_AGENCY = "recruitment_agency"
    CAMPUS = "campus"
    OTHER = "other"


class ApplicationStatus(str, enum.Enum):
    """Application status"""
    NEW = "new"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ON_HOLD = "on_hold"


class InterviewType(str, enum.Enum):
    """Interview type"""
    PHONE_SCREENING = "phone_screening"
    VIDEO = "video"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"
    HR = "hr"
    PANEL = "panel"
    FINAL = "final"


class InterviewStatus(str, enum.Enum):
    """Interview status"""
    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterviewResult(str, enum.Enum):
    """Interview result"""
    SELECTED = "selected"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    PENDING = "pending"


class OnboardingStatus(str, enum.Enum):
    """Onboarding status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VerificationStatus(str, enum.Enum):
    """Background verification status"""
    NOT_INITIATED = "not_initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED_CLEAR = "completed_clear"
    COMPLETED_WITH_DISCREPANCY = "completed_with_discrepancy"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VerificationType(str, enum.Enum):
    """Verification type"""
    IDENTITY = "identity"
    ADDRESS = "address"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    REFERENCE = "reference"
    CRIMINAL = "criminal"
    CREDIT = "credit"
    DRUG_TEST = "drug_test"


# ============================================================================
# JOB REQUISITION
# ============================================================================

class JobRequisition(BaseModel):
    """
    Job Requisition entity
    Request for new position hiring
    """
    __tablename__ = "recruitment_job_requisitions"
    
    # Basic Information
    requisition_code = Column(String(20), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("hrms_departments.id"), nullable=False)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("hrms_designations.id"), nullable=False)
    
    # Position Details
    number_of_positions = Column(Integer, nullable=False, default=1)
    employment_type = Column(SQLEnum(EmploymentType), nullable=False)
    work_location = Column(String(100), nullable=True)
    
    # Reporting
    reporting_to_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    
    # Job Description
    job_description = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    required_qualifications = Column(Text, nullable=True)
    preferred_qualifications = Column(Text, nullable=True)
    required_experience_years = Column(Integer, nullable=True)
    
    # Compensation
    min_salary = Column(Numeric(15, 2), nullable=True)
    max_salary = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(10), default="INR")
    
    # Priority & Timing
    priority = Column(SQLEnum(RequisitionPriority), nullable=False, default=RequisitionPriority.MEDIUM)
    required_by_date = Column(Date, nullable=True)
    
    # Justification
    justification = Column(Text, nullable=True)
    replacement_for_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    is_replacement = Column(Boolean, default=False)
    
    # Status & Approval
    status = Column(SQLEnum(RequisitionStatus), nullable=False, default=RequisitionStatus.DRAFT)
    requested_by_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=False)
    requested_date = Column(Date, nullable=False, default=date.today)
    approved_by_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    department = relationship("Department", foreign_keys=[department_id])
    designation = relationship("Designation", foreign_keys=[designation_id])
    reporting_to = relationship("Employee", foreign_keys=[reporting_to_employee_id])
    requested_by = relationship("Employee", foreign_keys=[requested_by_employee_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_employee_id])
    replacement_for = relationship("Employee", foreign_keys=[replacement_for_employee_id])
    postings = relationship("JobPosting", back_populates="requisition", lazy="select")
    
    __table_args__ = (
        Index('idx_recruitment_req_tenant', 'tenant_id'),
        Index('idx_recruitment_req_status', 'tenant_id', 'status'),
        Index('idx_recruitment_req_dept', 'tenant_id', 'department_id'),
    )


# ============================================================================
# JOB POSTING
# ============================================================================

class JobPosting(BaseModel):
    """
    Job Posting entity
    Public job advertisement
    """
    __tablename__ = "recruitment_job_postings"
    
    # Link to Requisition
    requisition_id = Column(UUID(as_uuid=True), ForeignKey("recruitment_job_requisitions.id"), nullable=False)
    
    # Posting Details
    posting_code = Column(String(20), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Publishing
    status = Column(SQLEnum(PostingStatus), nullable=False, default=PostingStatus.DRAFT)
    published_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # External Links
    external_job_board_links = Column(JSON, nullable=True)  # URLs to Naukri, LinkedIn, etc.
    
    # Metrics
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    
    # SEO
    slug = Column(String(200), nullable=True, index=True)
    meta_description = Column(String(500), nullable=True)
    
    # Relationships
    requisition = relationship("JobRequisition", back_populates="postings")
    applications = relationship("JobApplication", back_populates="posting", lazy="select")
    
    __table_args__ = (
        Index('idx_recruitment_posting_tenant', 'tenant_id'),
        Index('idx_recruitment_posting_status', 'tenant_id', 'status'),
    )


# ============================================================================
# JOB APPLICATION / APPLICANT
# ============================================================================

class JobApplication(BaseModel):
    """
    Job Application entity
    Applicant tracking
    """
    __tablename__ = "recruitment_job_applications"
    
    # Link to Posting
    posting_id = Column(UUID(as_uuid=True), ForeignKey("recruitment_job_postings.id"), nullable=False)
    
    # Application Details
    application_code = Column(String(20), nullable=False, unique=True, index=True)
    application_date = Column(Date, nullable=False, default=date.today)
    source = Column(SQLEnum(ApplicationSource), nullable=False)
    referrer_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    
    # Applicant Details
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(300), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    mobile = Column(String(20), nullable=False)
    alternate_mobile = Column(String(20), nullable=True)
    
    # Address
    current_city = Column(String(100), nullable=True)
    current_state = Column(String(100), nullable=True)
    
    # Professional Details
    current_designation = Column(String(100), nullable=True)
    current_employer = Column(String(200), nullable=True)
    total_experience_years = Column(Numeric(4, 1), nullable=True)
    relevant_experience_years = Column(Numeric(4, 1), nullable=True)
    
    # Compensation
    current_ctc = Column(Numeric(15, 2), nullable=True)
    expected_ctc = Column(Numeric(15, 2), nullable=True)
    notice_period_days = Column(Integer, nullable=True)
    
    # Education
    highest_qualification = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)
    university = Column(String(200), nullable=True)
    year_of_passing = Column(Integer, nullable=True)
    
    # Documents
    resume_url = Column(String(500), nullable=True)
    cover_letter = Column(Text, nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    
    # Status & Assignment
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW)
    assigned_to_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    
    # Screening
    screening_notes = Column(Text, nullable=True)
    screening_score = Column(Integer, nullable=True)  # 1-10
    
    # Rejection
    rejection_reason = Column(Text, nullable=True)
    rejected_by_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    rejected_date = Column(Date, nullable=True)
    
    # Star Rating
    rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Relationships
    posting = relationship("JobPosting", back_populates="applications")
    referrer = relationship("Employee", foreign_keys=[referrer_employee_id])
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_employee_id])
    rejected_by = relationship("Employee", foreign_keys=[rejected_by_employee_id])
    interviews = relationship("Interview", back_populates="application", lazy="select")
    onboarding = relationship("Onboarding", back_populates="application", uselist=False)
    
    __table_args__ = (
        Index('idx_recruitment_app_tenant', 'tenant_id'),
        Index('idx_recruitment_app_status', 'tenant_id', 'status'),
        Index('idx_recruitment_app_email', 'tenant_id', 'email'),
        Index('idx_recruitment_app_mobile', 'tenant_id', 'mobile'),
    )


# ============================================================================
# INTERVIEW
# ============================================================================

class Interview(BaseModel):
    """
    Interview entity
    Interview scheduling and feedback
    """
    __tablename__ = "recruitment_interviews"
    
    # Link to Application
    application_id = Column(UUID(as_uuid=True), ForeignKey("recruitment_job_applications.id"), nullable=False)
    
    # Interview Details
    interview_code = Column(String(20), nullable=False, unique=True, index=True)
    interview_type = Column(SQLEnum(InterviewType), nullable=False)
    round_number = Column(Integer, nullable=False, default=1)
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    location = Column(String(200), nullable=True)  # Office address or video link
    meeting_link = Column(String(500), nullable=True)
    
    # Interviewers
    interviewer_employee_ids = Column(JSON, nullable=True)  # List of employee IDs
    panel_lead_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    
    # Status
    status = Column(SQLEnum(InterviewStatus), nullable=False, default=InterviewStatus.SCHEDULED)
    
    # Rescheduling
    reschedule_count = Column(Integer, default=0)
    reschedule_reason = Column(Text, nullable=True)
    original_scheduled_date = Column(DateTime(timezone=True), nullable=True)
    
    # Feedback
    feedback = Column(Text, nullable=True)
    technical_rating = Column(Integer, nullable=True)  # 1-10
    communication_rating = Column(Integer, nullable=True)  # 1-10
    cultural_fit_rating = Column(Integer, nullable=True)  # 1-10
    overall_rating = Column(Integer, nullable=True)  # 1-10
    
    result = Column(SQLEnum(InterviewResult), nullable=True)
    result_notes = Column(Text, nullable=True)
    
    # Completed
    completed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    application = relationship("JobApplication", back_populates="interviews")
    panel_lead = relationship("Employee", foreign_keys=[panel_lead_employee_id])
    
    __table_args__ = (
        Index('idx_recruitment_interview_tenant', 'tenant_id'),
        Index('idx_recruitment_interview_app', 'tenant_id', 'application_id'),
        Index('idx_recruitment_interview_date', 'tenant_id', 'scheduled_date'),
    )


# ============================================================================
# ONBOARDING
# ============================================================================

class Onboarding(BaseModel):
    """
    Onboarding entity
    New hire onboarding process
    """
    __tablename__ = "recruitment_onboarding"
    
    # Link to Application & Employee
    application_id = Column(UUID(as_uuid=True), ForeignKey("recruitment_job_applications.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)  # Created after joining
    
    # Onboarding Details
    onboarding_code = Column(String(20), nullable=False, unique=True, index=True)
    
    # Dates
    offer_date = Column(Date, nullable=True)
    offer_accepted_date = Column(Date, nullable=True)
    joining_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(OnboardingStatus), nullable=False, default=OnboardingStatus.NOT_STARTED)
    
    # Checklist (JSON)
    pre_joining_checklist = Column(JSON, nullable=True)  # Tasks before joining
    joining_day_checklist = Column(JSON, nullable=True)  # Tasks on first day
    first_week_checklist = Column(JSON, nullable=True)  # Tasks in first week
    
    # Progress
    pre_joining_completed = Column(Boolean, default=False)
    joining_day_completed = Column(Boolean, default=False)
    first_week_completed = Column(Boolean, default=False)
    
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Mentor/Buddy
    buddy_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id"), nullable=True)
    
    # Welcome Kit
    id_card_issued = Column(Boolean, default=False)
    email_account_created = Column(Boolean, default=False)
    laptop_issued = Column(Boolean, default=False)
    access_cards_issued = Column(Boolean, default=False)
    
    # Training
    induction_completed = Column(Boolean, default=False)
    induction_date = Column(Date, nullable=True)
    
    # Documents
    documents_submitted = Column(Boolean, default=False)
    documents_verified = Column(Boolean, default=False)
    
    # Completion
    onboarding_completed_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    application = relationship("JobApplication", back_populates="onboarding")
    employee = relationship("Employee", foreign_keys=[employee_id])
    buddy = relationship("Employee", foreign_keys=[buddy_employee_id])
    verifications = relationship("BackgroundVerification", back_populates="onboarding", lazy="select")
    
    __table_args__ = (
        Index('idx_recruitment_onboard_tenant', 'tenant_id'),
        Index('idx_recruitment_onboard_status', 'tenant_id', 'status'),
        Index('idx_recruitment_onboard_joining', 'tenant_id', 'joining_date'),
    )


# ============================================================================
# BACKGROUND VERIFICATION
# ============================================================================

class BackgroundVerification(BaseModel):
    """
    Background Verification entity
    Pre-employment verification checks
    """
    __tablename__ = "recruitment_background_verifications"
    
    # Link to Onboarding
    onboarding_id = Column(UUID(as_uuid=True), ForeignKey("recruitment_onboarding.id"), nullable=False)
    
    # Verification Details
    verification_code = Column(String(20), nullable=False, unique=True, index=True)
    verification_type = Column(SQLEnum(VerificationType), nullable=False)
    
    # Agency
    verification_agency = Column(String(200), nullable=True)
    agency_reference_number = Column(String(100), nullable=True)
    
    # Status
    status = Column(SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.NOT_INITIATED)
    
    # Dates
    initiated_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    expected_completion_date = Column(Date, nullable=True)
    
    # Results
    result_summary = Column(Text, nullable=True)
    discrepancy_notes = Column(Text, nullable=True)
    
    # Documents
    report_document_url = Column(String(500), nullable=True)
    
    # Cost
    verification_cost = Column(Numeric(10, 2), nullable=True)
    
    # Relationships
    onboarding = relationship("Onboarding", back_populates="verifications")
    
    __table_args__ = (
        Index('idx_recruitment_verify_tenant', 'tenant_id'),
        Index('idx_recruitment_verify_onboard', 'tenant_id', 'onboarding_id'),
        Index('idx_recruitment_verify_status', 'tenant_id', 'status'),
    )
