"""
HRMS Training & Development Pydantic Schemas
Request/Response models for Training API
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS (matching database)
# ============================================================================

class TrainingTypeEnum(str, Enum):
    CLASSROOM = "classroom"
    ONLINE = "online"
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    CONFERENCE = "conference"
    ON_THE_JOB = "on_the_job"
    MENTORING = "mentoring"
    SELF_PACED = "self_paced"
    BLENDED = "blended"


class TrainingCategoryEnum(str, Enum):
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    LEADERSHIP = "leadership"
    COMPLIANCE = "compliance"
    PRODUCT = "product"
    SALES = "sales"
    CUSTOMER_SERVICE = "customer_service"
    SAFETY = "safety"
    INDUCTION = "induction"
    PROFESSIONAL = "professional"


class TrainingStatusEnum(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class ParticipantStatusEnum(str, Enum):
    NOMINATED = "nominated"
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    ABSENT = "absent"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"


class AssessmentTypeEnum(str, Enum):
    PRE_TEST = "pre_test"
    POST_TEST = "post_test"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PRACTICAL = "practical"
    PROJECT = "project"
    VIVA = "viva"
    CASE_STUDY = "case_study"


class CertificationStatusEnum(str, Enum):
    PENDING = "pending"
    ISSUED = "issued"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RENEWED = "renewed"


class SkillLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TrainingDeliveryModeEnum(str, Enum):
    INSTRUCTOR_LED = "instructor_led"
    SELF_PACED = "self_paced"
    BLENDED = "blended"
    VIRTUAL = "virtual"


# ============================================================================
# TRAINING COURSE SCHEMAS
# ============================================================================

class TrainingCourseBase(BaseModel):
    """Base training course fields"""
    course_name: str
    course_description: Optional[str] = None
    training_type: TrainingTypeEnum
    training_category: TrainingCategoryEnum
    delivery_mode: TrainingDeliveryModeEnum = TrainingDeliveryModeEnum.INSTRUCTOR_LED
    duration_hours: Decimal
    duration_days: Optional[int] = None
    max_participants: Optional[int] = None
    min_participants: Optional[int] = None
    target_designation_ids: Optional[List[str]] = None
    target_department_ids: Optional[List[str]] = None
    experience_level_required: Optional[str] = None
    prerequisites: Optional[str] = None
    prerequisite_course_ids: Optional[List[str]] = None
    learning_objectives: Optional[str] = None
    syllabus: Optional[str] = None
    internal_trainer_id: Optional[str] = None
    external_trainer_name: Optional[str] = None
    external_trainer_organization: Optional[str] = None
    lms_course_id: Optional[str] = None
    lms_course_url: Optional[str] = None
    cost_per_participant: Optional[Decimal] = None
    currency: str = "INR"
    provides_certificate: bool = False
    certificate_validity_months: Optional[int] = None
    is_mandatory: bool = False
    is_compliance_training: bool = False
    is_active: bool = True
    is_published: bool = False


class TrainingCourseCreate(TrainingCourseBase):
    """Create training course"""
    pass


class TrainingCourseUpdate(BaseModel):
    """Update training course (all fields optional)"""
    course_name: Optional[str] = None
    course_description: Optional[str] = None
    duration_hours: Optional[Decimal] = None
    max_participants: Optional[int] = None
    internal_trainer_id: Optional[str] = None
    external_trainer_name: Optional[str] = None
    cost_per_participant: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None


class TrainingCourseResponse(TrainingCourseBase):
    """Training course response"""
    id: str
    course_code: str
    average_rating: Optional[Decimal] = None
    total_ratings: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TrainingCourseListItem(BaseModel):
    """Simplified training course for lists"""
    id: str
    course_code: str
    course_name: str
    training_type: TrainingTypeEnum
    training_category: TrainingCategoryEnum
    duration_hours: Decimal
    is_active: bool
    is_published: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# TRAINING SESSION SCHEMAS
# ============================================================================

class TrainingSessionBase(BaseModel):
    """Base training session fields"""
    session_name: str
    course_id: str
    start_date: date
    end_date: date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location_type: str = "physical"
    venue: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    virtual_meeting_link: Optional[str] = None
    trainer_id: Optional[str] = None
    external_trainer_name: Optional[str] = None
    max_participants: int
    budget_allocated: Optional[Decimal] = None
    status: TrainingStatusEnum = TrainingStatusEnum.SCHEDULED


class TrainingSessionCreate(TrainingSessionBase):
    """Create training session"""
    pass


class TrainingSessionUpdate(BaseModel):
    """Update training session"""
    session_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    venue: Optional[str] = None
    trainer_id: Optional[str] = None
    status: Optional[TrainingStatusEnum] = None
    cancellation_reason: Optional[str] = None


class TrainingSessionResponse(TrainingSessionBase):
    """Training session response"""
    id: str
    session_code: str
    enrolled_count: int = 0
    confirmed_count: int = 0
    attended_count: int = 0
    average_feedback_rating: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrainingSessionListItem(BaseModel):
    """Simplified training session for lists"""
    id: str
    session_code: str
    session_name: str
    course_name: str
    start_date: date
    end_date: date
    status: TrainingStatusEnum
    enrolled_count: int
    max_participants: int
    
    class Config:
        from_attributes = True


# ============================================================================
# TRAINING PARTICIPANT SCHEMAS
# ============================================================================

class TrainingParticipantBase(BaseModel):
    """Base participant fields"""
    session_id: str
    employee_id: str
    nominated_by_id: Optional[str] = None
    nomination_reason: Optional[str] = None
    status: ParticipantStatusEnum = ParticipantStatusEnum.NOMINATED


class TrainingParticipantCreate(TrainingParticipantBase):
    """Create participant"""
    pass


class TrainingParticipantUpdate(BaseModel):
    """Update participant"""
    status: Optional[ParticipantStatusEnum] = None
    attended: Optional[bool] = None
    attendance_percentage: Optional[Decimal] = None
    feedback_rating: Optional[int] = None
    feedback_comments: Optional[str] = None


class TrainingParticipantResponse(TrainingParticipantBase):
    """Participant response"""
    id: str
    employee_name: str
    employee_code: str
    attended: bool = False
    final_score: Optional[Decimal] = None
    passed: bool = False
    certificate_issued: bool = False
    
    class Config:
        from_attributes = True


# ============================================================================
# ASSESSMENT SCHEMAS
# ============================================================================

class TrainingAssessmentBase(BaseModel):
    """Base assessment fields"""
    assessment_name: str
    assessment_description: Optional[str] = None
    course_id: Optional[str] = None
    session_id: Optional[str] = None
    assessment_type: AssessmentTypeEnum
    total_marks: int = 100
    passing_marks: int
    duration_minutes: Optional[int] = None
    scheduled_date: Optional[date] = None


class TrainingAssessmentCreate(TrainingAssessmentBase):
    """Create assessment"""
    pass


class TrainingAssessmentResponse(TrainingAssessmentBase):
    """Assessment response"""
    id: str
    assessment_code: str
    question_count: Optional[int] = None
    is_published: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CERTIFICATION SCHEMAS
# ============================================================================

class TrainingCertificationBase(BaseModel):
    """Base certification fields"""
    certificate_name: str
    course_id: Optional[str] = None
    session_id: Optional[str] = None
    employee_id: str
    issue_date: date
    expiry_date: Optional[date] = None
    status: CertificationStatusEnum = CertificationStatusEnum.ISSUED


class TrainingCertificationCreate(TrainingCertificationBase):
    """Create certification"""
    pass


class TrainingCertificationResponse(TrainingCertificationBase):
    """Certification response"""
    id: str
    certificate_number: str
    employee_name: str
    course_name: Optional[str] = None
    certificate_url: Optional[str] = None
    verification_code: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# SKILL SCHEMAS
# ============================================================================

class SkillBase(BaseModel):
    """Base skill fields"""
    skill_name: str
    skill_description: Optional[str] = None
    skill_category: Optional[str] = None
    skill_type: Optional[str] = None
    parent_skill_id: Optional[str] = None
    is_active: bool = True


class SkillCreate(SkillBase):
    """Create skill"""
    pass


class SkillResponse(SkillBase):
    """Skill response"""
    id: str
    skill_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeSkillBase(BaseModel):
    """Base employee skill fields"""
    employee_id: str
    skill_id: str
    proficiency_level: SkillLevelEnum
    proficiency_percentage: Optional[int] = None
    is_certified: bool = False
    certification_name: Optional[str] = None
    years_of_experience: Optional[Decimal] = None


class EmployeeSkillCreate(EmployeeSkillBase):
    """Create employee skill"""
    pass


class EmployeeSkillResponse(EmployeeSkillBase):
    """Employee skill response"""
    id: str
    skill_name: str
    skill_category: Optional[str] = None
    is_verified: bool = False
    
    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD & STATISTICS
# ============================================================================

class TrainingDashboardStats(BaseModel):
    """Training dashboard statistics"""
    total_courses: int = 0
    active_courses: int = 0
    total_sessions: int = 0
    upcoming_sessions: int = 0
    ongoing_sessions: int = 0
    completed_sessions: int = 0
    total_participants: int = 0
    certifications_issued: int = 0
    average_training_rating: Optional[Decimal] = None
    compliance_completion_rate: Optional[Decimal] = None
    by_category: Optional[Dict[str, int]] = None
    by_type: Optional[Dict[str, int]] = None


class TrainingCalendarItem(BaseModel):
    """Training calendar item"""
    id: str
    session_code: str
    session_name: str
    course_name: str
    start_date: date
    end_date: date
    start_time: Optional[str] = None
    venue: Optional[str] = None
    trainer_name: Optional[str] = None
    enrolled_count: int
    max_participants: int
    status: TrainingStatusEnum
    
    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION
# ============================================================================

class PaginatedTrainingCourseResponse(BaseModel):
    """Paginated training course response"""
    items: List[TrainingCourseResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedTrainingSessionResponse(BaseModel):
    """Paginated training session response"""
    items: List[TrainingSessionResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedParticipantResponse(BaseModel):
    """Paginated participant response"""
    items: List[TrainingParticipantResponse]
    total: int
    page: int
    page_size: int
    pages: int
