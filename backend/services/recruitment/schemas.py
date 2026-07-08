"""
HRMS Recruitment & Onboarding Pydantic Schemas
Request/Response models for recruitment API
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS (matching database)
# ============================================================================

class RequisitionStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class RequisitionPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EmploymentTypeEnum(str, Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"


class PostingStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class ApplicationSourceEnum(str, Enum):
    CAREER_PAGE = "career_page"
    REFERRAL = "referral"
    JOB_PORTAL = "job_portal"
    LINKEDIN = "linkedin"
    WALK_IN = "walk_in"
    RECRUITMENT_AGENCY = "recruitment_agency"
    CAMPUS = "campus"
    OTHER = "other"


class ApplicationStatusEnum(str, Enum):
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


class InterviewTypeEnum(str, Enum):
    PHONE_SCREENING = "phone_screening"
    VIDEO = "video"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"
    HR = "hr"
    PANEL = "panel"
    FINAL = "final"


class InterviewStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterviewResultEnum(str, Enum):
    SELECTED = "selected"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    PENDING = "pending"


class OnboardingStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VerificationStatusEnum(str, Enum):
    NOT_INITIATED = "not_initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED_CLEAR = "completed_clear"
    COMPLETED_WITH_DISCREPANCY = "completed_with_discrepancy"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VerificationTypeEnum(str, Enum):
    IDENTITY = "identity"
    ADDRESS = "address"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    REFERENCE = "reference"
    CRIMINAL = "criminal"
    CREDIT = "credit"
    DRUG_TEST = "drug_test"


# ============================================================================
# JOB REQUISITION SCHEMAS
# ============================================================================

class JobRequisitionBase(BaseModel):
    """Base job requisition fields"""
    title: str
    department_id: int
    designation_id: int
    number_of_positions: int = 1
    employment_type: EmploymentTypeEnum
    work_location: Optional[str] = None
    reporting_to_employee_id: Optional[int] = None
    job_description: Optional[str] = None
    responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    required_experience_years: Optional[int] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    priority: RequisitionPriorityEnum = RequisitionPriorityEnum.MEDIUM
    required_by_date: Optional[date] = None
    justification: Optional[str] = None
    is_replacement: bool = False
    replacement_for_employee_id: Optional[int] = None


class JobRequisitionCreate(JobRequisitionBase):
    """Create job requisition"""
    requested_by_employee_id: int


class JobRequisitionUpdate(BaseModel):
    """Update job requisition (all fields optional)"""
    title: Optional[str] = None
    number_of_positions: Optional[int] = None
    work_location: Optional[str] = None
    job_description: Optional[str] = None
    required_by_date: Optional[date] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    priority: Optional[RequisitionPriorityEnum] = None


class JobRequisitionResponse(JobRequisitionBase):
    """Job requisition response"""
    id: int
    requisition_code: str
    status: RequisitionStatusEnum
    requested_by_employee_id: int
    requested_by_name: Optional[str] = None
    requested_date: date
    approved_by_employee_id: Optional[int] = None
    approved_by_name: Optional[str] = None
    approved_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobRequisitionListItem(BaseModel):
    """Simplified requisition for lists"""
    id: int
    requisition_code: str
    title: str
    department_name: Optional[str] = None
    number_of_positions: int
    employment_type: EmploymentTypeEnum
    status: RequisitionStatusEnum
    priority: RequisitionPriorityEnum
    requested_date: date
    requested_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobRequisitionApproval(BaseModel):
    """Approve/reject requisition"""
    approved: bool
    rejection_reason: Optional[str] = None


# ============================================================================
# JOB POSTING SCHEMAS
# ============================================================================

class JobPostingBase(BaseModel):
    """Base job posting fields"""
    requisition_id: int
    title: str
    description: str
    expiry_date: Optional[date] = None
    external_job_board_links: Optional[Dict[str, str]] = None


class JobPostingCreate(JobPostingBase):
    """Create job posting"""
    pass


class JobPostingUpdate(BaseModel):
    """Update job posting"""
    title: Optional[str] = None
    description: Optional[str] = None
    expiry_date: Optional[date] = None
    status: Optional[PostingStatusEnum] = None


class JobPostingResponse(JobPostingBase):
    """Job posting response"""
    id: int
    posting_code: str
    status: PostingStatusEnum
    published_date: Optional[date] = None
    views_count: int = 0
    applications_count: int = 0
    slug: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobPostingListItem(BaseModel):
    """Simplified posting for lists"""
    id: int
    posting_code: str
    title: str
    status: PostingStatusEnum
    published_date: Optional[date] = None
    applications_count: int = 0
    views_count: int = 0
    
    class Config:
        from_attributes = True


# ============================================================================
# JOB APPLICATION SCHEMAS
# ============================================================================

class JobApplicationBase(BaseModel):
    """Base job application fields"""
    posting_id: int
    source: ApplicationSourceEnum
    referrer_employee_id: Optional[int] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    mobile: str
    alternate_mobile: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_designation: Optional[str] = None
    current_employer: Optional[str] = None
    total_experience_years: Optional[Decimal] = None
    relevant_experience_years: Optional[Decimal] = None
    current_ctc: Optional[Decimal] = None
    expected_ctc: Optional[Decimal] = None
    notice_period_days: Optional[int] = None
    highest_qualification: Optional[str] = None
    specialization: Optional[str] = None
    university: Optional[str] = None
    year_of_passing: Optional[int] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    @validator('mobile', 'alternate_mobile')
    def validate_mobile(cls, v):
        if v and len(v) != 10:
            raise ValueError('Mobile must be 10 digits')
        return v


class JobApplicationCreate(JobApplicationBase):
    """Create job application"""
    pass


class JobApplicationUpdate(BaseModel):
    """Update job application"""
    status: Optional[ApplicationStatusEnum] = None
    assigned_to_employee_id: Optional[int] = None
    screening_notes: Optional[str] = None
    screening_score: Optional[int] = None
    rating: Optional[int] = None
    rejection_reason: Optional[str] = None


class JobApplicationResponse(JobApplicationBase):
    """Job application response"""
    id: int
    application_code: str
    full_name: str
    application_date: date
    status: ApplicationStatusEnum
    assigned_to_employee_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    screening_notes: Optional[str] = None
    screening_score: Optional[int] = None
    rating: Optional[int] = None
    rejection_reason: Optional[str] = None
    rejected_by_name: Optional[str] = None
    rejected_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobApplicationListItem(BaseModel):
    """Simplified application for lists"""
    id: int
    application_code: str
    full_name: str
    email: str
    mobile: str
    current_designation: Optional[str] = None
    total_experience_years: Optional[Decimal] = None
    expected_ctc: Optional[Decimal] = None
    status: ApplicationStatusEnum
    rating: Optional[int] = None
    application_date: date
    
    class Config:
        from_attributes = True


# ============================================================================
# INTERVIEW SCHEMAS
# ============================================================================

class InterviewBase(BaseModel):
    """Base interview fields"""
    application_id: int
    interview_type: InterviewTypeEnum
    round_number: int = 1
    scheduled_date: datetime
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewer_employee_ids: Optional[List[int]] = None
    panel_lead_employee_id: Optional[int] = None


class InterviewCreate(InterviewBase):
    """Create interview"""
    pass


class InterviewUpdate(BaseModel):
    """Update interview"""
    scheduled_date: Optional[datetime] = None
    status: Optional[InterviewStatusEnum] = None
    meeting_link: Optional[str] = None


class InterviewFeedback(BaseModel):
    """Interview feedback"""
    feedback: Optional[str] = None
    technical_rating: Optional[int] = Field(None, ge=1, le=10)
    communication_rating: Optional[int] = Field(None, ge=1, le=10)
    cultural_fit_rating: Optional[int] = Field(None, ge=1, le=10)
    overall_rating: Optional[int] = Field(None, ge=1, le=10)
    result: InterviewResultEnum
    result_notes: Optional[str] = None


class InterviewResponse(InterviewBase):
    """Interview response"""
    id: int
    interview_code: str
    status: InterviewStatusEnum
    reschedule_count: int = 0
    feedback: Optional[str] = None
    technical_rating: Optional[int] = None
    communication_rating: Optional[int] = None
    cultural_fit_rating: Optional[int] = None
    overall_rating: Optional[int] = None
    result: Optional[InterviewResultEnum] = None
    result_notes: Optional[str] = None
    completed_date: Optional[datetime] = None
    applicant_name: Optional[str] = None
    panel_lead_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InterviewListItem(BaseModel):
    """Simplified interview for lists"""
    id: int
    interview_code: str
    applicant_name: Optional[str] = None
    interview_type: InterviewTypeEnum
    round_number: int
    scheduled_date: datetime
    status: InterviewStatusEnum
    result: Optional[InterviewResultEnum] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# ONBOARDING SCHEMAS
# ============================================================================

class OnboardingBase(BaseModel):
    """Base onboarding fields"""
    application_id: int
    joining_date: date
    offer_date: Optional[date] = None
    offer_accepted_date: Optional[date] = None
    buddy_employee_id: Optional[int] = None


class OnboardingCreate(OnboardingBase):
    """Create onboarding"""
    pass


class OnboardingUpdate(BaseModel):
    """Update onboarding"""
    status: Optional[OnboardingStatusEnum] = None
    pre_joining_completed: Optional[bool] = None
    joining_day_completed: Optional[bool] = None
    first_week_completed: Optional[bool] = None
    id_card_issued: Optional[bool] = None
    email_account_created: Optional[bool] = None
    laptop_issued: Optional[bool] = None
    access_cards_issued: Optional[bool] = None
    induction_completed: Optional[bool] = None
    documents_submitted: Optional[bool] = None
    documents_verified: Optional[bool] = None


class OnboardingResponse(OnboardingBase):
    """Onboarding response"""
    id: int
    onboarding_code: str
    employee_id: Optional[int] = None
    status: OnboardingStatusEnum
    pre_joining_checklist: Optional[Dict[str, Any]] = None
    joining_day_checklist: Optional[Dict[str, Any]] = None
    first_week_checklist: Optional[Dict[str, Any]] = None
    pre_joining_completed: bool = False
    joining_day_completed: bool = False
    first_week_completed: bool = False
    completion_percentage: int = 0
    id_card_issued: bool = False
    email_account_created: bool = False
    laptop_issued: bool = False
    access_cards_issued: bool = False
    induction_completed: bool = False
    induction_date: Optional[date] = None
    documents_submitted: bool = False
    documents_verified: bool = False
    onboarding_completed_date: Optional[date] = None
    notes: Optional[str] = None
    applicant_name: Optional[str] = None
    buddy_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OnboardingListItem(BaseModel):
    """Simplified onboarding for lists"""
    id: int
    onboarding_code: str
    applicant_name: Optional[str] = None
    joining_date: date
    status: OnboardingStatusEnum
    completion_percentage: int = 0
    
    class Config:
        from_attributes = True


# ============================================================================
# BACKGROUND VERIFICATION SCHEMAS
# ============================================================================

class BackgroundVerificationBase(BaseModel):
    """Base background verification fields"""
    onboarding_id: int
    verification_type: VerificationTypeEnum
    verification_agency: Optional[str] = None
    expected_completion_date: Optional[date] = None


class BackgroundVerificationCreate(BackgroundVerificationBase):
    """Create background verification"""
    pass


class BackgroundVerificationUpdate(BaseModel):
    """Update background verification"""
    status: Optional[VerificationStatusEnum] = None
    agency_reference_number: Optional[str] = None
    result_summary: Optional[str] = None
    discrepancy_notes: Optional[str] = None
    report_document_url: Optional[str] = None
    verification_cost: Optional[Decimal] = None
    completed_date: Optional[date] = None


class BackgroundVerificationResponse(BackgroundVerificationBase):
    """Background verification response"""
    id: int
    verification_code: str
    status: VerificationStatusEnum
    agency_reference_number: Optional[str] = None
    initiated_date: Optional[date] = None
    completed_date: Optional[date] = None
    result_summary: Optional[str] = None
    discrepancy_notes: Optional[str] = None
    report_document_url: Optional[str] = None
    verification_cost: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BackgroundVerificationListItem(BaseModel):
    """Simplified verification for lists"""
    id: int
    verification_code: str
    verification_type: VerificationTypeEnum
    status: VerificationStatusEnum
    verification_agency: Optional[str] = None
    expected_completion_date: Optional[date] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION & FILTERS
# ============================================================================

class PaginatedRequisitionResponse(BaseModel):
    """Paginated requisition response"""
    items: List[JobRequisitionListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedPostingResponse(BaseModel):
    """Paginated posting response"""
    items: List[JobPostingListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedApplicationResponse(BaseModel):
    """Paginated application response"""
    items: List[JobApplicationListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedInterviewResponse(BaseModel):
    """Paginated interview response"""
    items: List[InterviewListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedOnboardingResponse(BaseModel):
    """Paginated onboarding response"""
    items: List[OnboardingListItem]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# DASHBOARD & STATISTICS
# ============================================================================

class RecruitmentDashboardStats(BaseModel):
    """Recruitment dashboard statistics"""
    active_requisitions: int = 0
    open_positions: int = 0
    total_applications: int = 0
    applications_this_month: int = 0
    interviews_scheduled: int = 0
    offers_extended: int = 0
    onboarding_in_progress: int = 0
    avg_time_to_hire_days: Optional[int] = None
    by_status: Dict[str, int] = {}
    by_source: Dict[str, int] = {}
