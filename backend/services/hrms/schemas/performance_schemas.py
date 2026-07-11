"""
Performance Management Schemas
Pydantic models for Goal Setting, Appraisals, 360 Feedback, Ratings & IDP
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class GoalTypeEnum(str, Enum):
    """Goal type"""
    KRA = "kra"
    KPI = "kpi"
    OBJECTIVE = "objective"
    PROJECT = "project"


class GoalStatusEnum(str, Enum):
    """Goal status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalPriorityEnum(str, Enum):
    """Goal priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AppraisalCycleStatusEnum(str, Enum):
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


class AppraisalStatusEnum(str, Enum):
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


class RatingScaleEnum(str, Enum):
    """Performance rating scale"""
    OUTSTANDING = "outstanding"
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"
    MEETS_EXPECTATIONS = "meets_expectations"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNSATISFACTORY = "unsatisfactory"


class FeedbackTypeEnum(str, Enum):
    """360-degree feedback type"""
    SELF = "self"
    MANAGER = "manager"
    PEER = "peer"
    SUBORDINATE = "subordinate"
    CUSTOMER = "customer"
    OTHER = "other"


class FeedbackStatusEnum(str, Enum):
    """Feedback status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"


class IncrementTypeEnum(str, Enum):
    """Increment type"""
    ANNUAL = "annual"
    PROMOTION = "promotion"
    SPECIAL = "special"
    PERFORMANCE_BASED = "performance_based"
    MARKET_CORRECTION = "market_correction"


class IDPStatusEnum(str, Enum):
    """IDP status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DevelopmentActivityTypeEnum(str, Enum):
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
# APPRAISAL CYCLE SCHEMAS
# ============================================================================

class AppraisalCycleBase(BaseModel):
    """Base appraisal cycle schema"""
    cycle_code: str = Field(..., max_length=50, description="Unique cycle code")
    cycle_name: str = Field(..., max_length=200, description="Cycle name")
    cycle_description: Optional[str] = Field(None, description="Cycle description")
    fiscal_year: str = Field(..., max_length=20, description="Fiscal year (e.g., 2024-25)")
    start_date: date = Field(..., description="Cycle start date")
    end_date: date = Field(..., description="Cycle end date")
    
    # Phase deadlines
    goal_setting_start: Optional[date] = None
    goal_setting_end: Optional[date] = None
    self_assessment_start: Optional[date] = None
    self_assessment_end: Optional[date] = None
    manager_review_start: Optional[date] = None
    manager_review_end: Optional[date] = None
    normalization_start: Optional[date] = None
    normalization_end: Optional[date] = None
    hr_review_start: Optional[date] = None
    hr_review_end: Optional[date] = None
    
    # Configuration
    enable_360_feedback: bool = False
    enable_self_assessment: bool = True
    enable_goal_setting: bool = True
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class AppraisalCycleCreate(AppraisalCycleBase):
    """Schema for creating appraisal cycle"""
    pass


class AppraisalCycleUpdate(BaseModel):
    """Schema for updating appraisal cycle"""
    cycle_name: Optional[str] = Field(None, max_length=200)
    cycle_description: Optional[str] = None
    status: Optional[AppraisalCycleStatusEnum] = None
    goal_setting_start: Optional[date] = None
    goal_setting_end: Optional[date] = None
    self_assessment_start: Optional[date] = None
    self_assessment_end: Optional[date] = None
    manager_review_start: Optional[date] = None
    manager_review_end: Optional[date] = None
    normalization_start: Optional[date] = None
    normalization_end: Optional[date] = None
    hr_review_start: Optional[date] = None
    hr_review_end: Optional[date] = None
    enable_360_feedback: Optional[bool] = None
    enable_self_assessment: Optional[bool] = None
    enable_goal_setting: Optional[bool] = None


class AppraisalCycleResponse(AppraisalCycleBase):
    """Schema for appraisal cycle response"""
    id: UUID
    tenant_id: UUID
    status: AppraisalCycleStatusEnum
    total_employees: int = 0
    completed_appraisals: int = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# PERFORMANCE GOAL SCHEMAS (KRA/KPI)
# ============================================================================

class PerformanceGoalBase(BaseModel):
    """Base performance goal schema"""
    goal_code: str = Field(..., max_length=50)
    goal_title: str = Field(..., max_length=200)
    goal_description: Optional[str] = None
    goal_type: GoalTypeEnum = GoalTypeEnum.KPI
    goal_priority: GoalPriorityEnum = GoalPriorityEnum.MEDIUM
    measurement_criteria: Optional[str] = None
    target_value: Optional[str] = Field(None, max_length=100)
    uom: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    weightage: Optional[Decimal] = Field(None, ge=0, le=100, description="Percentage weightage")
    start_date: date
    target_date: date
    
    @validator('target_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('target_date must be after start_date')
        return v


class PerformanceGoalCreate(PerformanceGoalBase):
    """Schema for creating performance goal"""
    employee_id: UUID
    appraisal_cycle_id: UUID


class PerformanceGoalUpdate(BaseModel):
    """Schema for updating performance goal"""
    goal_title: Optional[str] = Field(None, max_length=200)
    goal_description: Optional[str] = None
    goal_priority: Optional[GoalPriorityEnum] = None
    measurement_criteria: Optional[str] = None
    target_value: Optional[str] = None
    achieved_value: Optional[str] = None
    uom: Optional[str] = None
    weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[GoalStatusEnum] = None
    employee_comments: Optional[str] = None
    manager_comments: Optional[str] = None


class PerformanceGoalResponse(PerformanceGoalBase):
    """Schema for performance goal response"""
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    appraisal_cycle_id: UUID
    achieved_value: Optional[str] = None
    completion_date: Optional[date] = None
    progress_percentage: int = 0
    status: GoalStatusEnum
    submitted_date: Optional[datetime] = None
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    employee_comments: Optional[str] = None
    manager_comments: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# EMPLOYEE APPRAISAL SCHEMAS
# ============================================================================

class EmployeeAppraisalBase(BaseModel):
    """Base employee appraisal schema"""
    appraisal_code: str = Field(..., max_length=50)
    employee_id: UUID
    appraisal_cycle_id: UUID
    reviewer_id: Optional[UUID] = None


class EmployeeAppraisalCreate(EmployeeAppraisalBase):
    """Schema for creating employee appraisal"""
    pass


class SelfAssessmentSubmit(BaseModel):
    """Schema for submitting self assessment"""
    self_rating: RatingScaleEnum
    self_rating_numeric: Decimal = Field(..., ge=1.0, le=5.0)
    self_comments: Optional[str] = None
    key_achievements: Optional[str] = None
    areas_of_improvement: Optional[str] = None


class ManagerReviewSubmit(BaseModel):
    """Schema for submitting manager review"""
    manager_rating: RatingScaleEnum
    manager_rating_numeric: Decimal = Field(..., ge=1.0, le=5.0)
    manager_comments: Optional[str] = None
    manager_strengths: Optional[str] = None
    manager_development_areas: Optional[str] = None
    recommended_increment_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    recommended_promotion: bool = False
    recommended_promotion_designation_id: Optional[UUID] = None


class HRReviewSubmit(BaseModel):
    """Schema for submitting HR review"""
    hr_comments: Optional[str] = None
    final_rating: RatingScaleEnum
    final_rating_numeric: Decimal = Field(..., ge=1.0, le=5.0)
    normalized_rating: Optional[RatingScaleEnum] = None
    normalized_rating_numeric: Optional[Decimal] = Field(None, ge=1.0, le=5.0)


class EmployeeAppraisalResponse(EmployeeAppraisalBase):
    """Schema for employee appraisal response"""
    id: UUID
    tenant_id: UUID
    status: AppraisalStatusEnum
    
    # Goal setting
    goals_submitted_date: Optional[datetime] = None
    goals_approved_date: Optional[datetime] = None
    
    # Self assessment
    self_assessment_submitted_date: Optional[datetime] = None
    self_rating: Optional[RatingScaleEnum] = None
    self_rating_numeric: Optional[Decimal] = None
    self_comments: Optional[str] = None
    key_achievements: Optional[str] = None
    areas_of_improvement: Optional[str] = None
    
    # Manager review
    manager_review_submitted_date: Optional[datetime] = None
    manager_rating: Optional[RatingScaleEnum] = None
    manager_rating_numeric: Optional[Decimal] = None
    manager_comments: Optional[str] = None
    manager_strengths: Optional[str] = None
    manager_development_areas: Optional[str] = None
    
    # HR review
    hr_review_submitted_date: Optional[datetime] = None
    hr_comments: Optional[str] = None
    
    # Final rating
    final_rating: Optional[RatingScaleEnum] = None
    final_rating_numeric: Optional[Decimal] = None
    normalized_rating: Optional[RatingScaleEnum] = None
    normalized_rating_numeric: Optional[Decimal] = None
    
    # Overall
    overall_goal_achievement_percentage: Optional[Decimal] = None
    recommended_increment_percentage: Optional[Decimal] = None
    recommended_promotion: bool = False
    recommended_promotion_designation_id: Optional[UUID] = None
    completed_date: Optional[datetime] = None
    
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# 360 FEEDBACK SCHEMAS
# ============================================================================

class FeedbackRequestBase(BaseModel):
    """Base feedback request schema"""
    request_code: str = Field(..., max_length=50)
    employee_id: UUID = Field(..., description="Subject of feedback")
    reviewer_id: UUID = Field(..., description="Person providing feedback")
    appraisal_cycle_id: UUID
    feedback_type: FeedbackTypeEnum
    due_date: Optional[date] = None


class FeedbackRequestCreate(FeedbackRequestBase):
    """Schema for creating feedback request"""
    pass


class FeedbackRequestBulkCreate(BaseModel):
    """Schema for bulk creating feedback requests"""
    employee_id: UUID
    appraisal_cycle_id: UUID
    reviewers: List[dict] = Field(..., description="List of {reviewer_id, feedback_type}")


class FeedbackResponseSubmit(BaseModel):
    """Schema for submitting feedback response"""
    overall_rating: Optional[RatingScaleEnum] = None
    overall_rating_numeric: Optional[Decimal] = Field(None, ge=1.0, le=5.0)
    technical_skills_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_skills_rating: Optional[int] = Field(None, ge=1, le=5)
    teamwork_rating: Optional[int] = Field(None, ge=1, le=5)
    leadership_rating: Optional[int] = Field(None, ge=1, le=5)
    problem_solving_rating: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    additional_comments: Optional[str] = None
    is_anonymous: bool = False


class FeedbackRequestResponse(FeedbackRequestBase):
    """Schema for feedback request response"""
    id: UUID
    tenant_id: UUID
    requested_date: datetime
    status: FeedbackStatusEnum
    reminder_sent_count: int = 0
    last_reminder_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackResponseResponse(BaseModel):
    """Schema for feedback response"""
    id: UUID
    tenant_id: UUID
    feedback_request_id: UUID
    employee_appraisal_id: Optional[UUID] = None
    overall_rating: Optional[RatingScaleEnum] = None
    overall_rating_numeric: Optional[Decimal] = None
    technical_skills_rating: Optional[int] = None
    communication_skills_rating: Optional[int] = None
    teamwork_rating: Optional[int] = None
    leadership_rating: Optional[int] = None
    problem_solving_rating: Optional[int] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    additional_comments: Optional[str] = None
    submitted_date: datetime
    acknowledged_date: Optional[datetime] = None
    is_anonymous: bool = False
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# PERFORMANCE INCREMENT SCHEMAS
# ============================================================================

class PerformanceIncrementBase(BaseModel):
    """Base performance increment schema"""
    increment_code: str = Field(..., max_length=50)
    employee_id: UUID
    increment_type: IncrementTypeEnum = IncrementTypeEnum.ANNUAL
    current_ctc: Decimal = Field(..., gt=0)
    increment_percentage: Decimal = Field(..., ge=0)
    increment_amount: Decimal = Field(..., ge=0)
    revised_ctc: Decimal = Field(..., gt=0)
    effective_from: date
    remarks: Optional[str] = None


class PerformanceIncrementCreate(PerformanceIncrementBase):
    """Schema for creating performance increment"""
    employee_appraisal_id: Optional[UUID] = None
    appraisal_cycle_id: Optional[UUID] = None
    recommended_by_id: Optional[UUID] = None


class PerformanceIncrementUpdate(BaseModel):
    """Schema for updating performance increment"""
    increment_percentage: Optional[Decimal] = Field(None, ge=0)
    increment_amount: Optional[Decimal] = Field(None, ge=0)
    revised_ctc: Optional[Decimal] = Field(None, gt=0)
    effective_from: Optional[date] = None
    remarks: Optional[str] = None
    is_approved: Optional[bool] = None
    is_processed: Optional[bool] = None


class PerformanceIncrementResponse(PerformanceIncrementBase):
    """Schema for performance increment response"""
    id: UUID
    tenant_id: UUID
    employee_appraisal_id: Optional[UUID] = None
    appraisal_cycle_id: Optional[UUID] = None
    recommended_by_id: Optional[UUID] = None
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[datetime] = None
    is_approved: bool = False
    is_processed: bool = False
    processed_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# INDIVIDUAL DEVELOPMENT PLAN (IDP) SCHEMAS
# ============================================================================

class IndividualDevelopmentPlanBase(BaseModel):
    """Base IDP schema"""
    idp_code: str = Field(..., max_length=50)
    idp_title: str = Field(..., max_length=200)
    employee_id: UUID
    career_goal: Optional[str] = None
    target_role: Optional[str] = Field(None, max_length=200)
    target_designation_id: Optional[UUID] = None
    current_skills: Optional[str] = None
    required_skills: Optional[str] = None
    skill_gaps: Optional[str] = None
    plan_start_date: date
    plan_end_date: date
    
    @validator('plan_end_date')
    def validate_dates(cls, v, values):
        if 'plan_start_date' in values and v < values['plan_start_date']:
            raise ValueError('plan_end_date must be after plan_start_date')
        return v


class IndividualDevelopmentPlanCreate(IndividualDevelopmentPlanBase):
    """Schema for creating IDP"""
    appraisal_cycle_id: Optional[UUID] = None


class IndividualDevelopmentPlanUpdate(BaseModel):
    """Schema for updating IDP"""
    idp_title: Optional[str] = Field(None, max_length=200)
    career_goal: Optional[str] = None
    target_role: Optional[str] = None
    target_designation_id: Optional[UUID] = None
    current_skills: Optional[str] = None
    required_skills: Optional[str] = None
    skill_gaps: Optional[str] = None
    plan_end_date: Optional[date] = None
    status: Optional[IDPStatusEnum] = None
    overall_progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    employee_notes: Optional[str] = None
    manager_notes: Optional[str] = None


class IndividualDevelopmentPlanResponse(IndividualDevelopmentPlanBase):
    """Schema for IDP response"""
    id: UUID
    tenant_id: UUID
    appraisal_cycle_id: Optional[UUID] = None
    status: IDPStatusEnum
    submitted_date: Optional[datetime] = None
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[datetime] = None
    overall_progress_percentage: int = 0
    employee_notes: Optional[str] = None
    manager_notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# DEVELOPMENT ACTIVITY SCHEMAS
# ============================================================================

class DevelopmentActivityBase(BaseModel):
    """Base development activity schema"""
    activity_code: str = Field(..., max_length=50)
    activity_title: str = Field(..., max_length=200)
    activity_description: Optional[str] = None
    activity_type: DevelopmentActivityTypeEnum
    provider_name: Optional[str] = Field(None, max_length=200)
    course_name: Optional[str] = Field(None, max_length=200)
    duration_hours: Optional[int] = Field(None, gt=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None


class DevelopmentActivityCreate(DevelopmentActivityBase):
    """Schema for creating development activity"""
    idp_id: UUID


class DevelopmentActivityUpdate(BaseModel):
    """Schema for updating development activity"""
    activity_title: Optional[str] = Field(None, max_length=200)
    activity_description: Optional[str] = None
    provider_name: Optional[str] = None
    course_name: Optional[str] = None
    duration_hours: Optional[int] = None
    cost: Optional[Decimal] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    is_completed: Optional[bool] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    certification_obtained: Optional[str] = None
    certificate_url: Optional[str] = None
    learning_outcome: Optional[str] = None
    employee_feedback: Optional[str] = None
    manager_feedback: Optional[str] = None


class DevelopmentActivityResponse(DevelopmentActivityBase):
    """Schema for development activity response"""
    id: UUID
    tenant_id: UUID
    idp_id: UUID
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    is_completed: bool = False
    completion_percentage: int = 0
    certification_obtained: Optional[str] = None
    certificate_url: Optional[str] = None
    learning_outcome: Optional[str] = None
    employee_feedback: Optional[str] = None
    manager_feedback: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# COMMON RESPONSE SCHEMAS
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
