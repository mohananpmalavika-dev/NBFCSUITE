"""
Project Management Pydantic Schemas
Request/Response models for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from backend.shared.database.project_management_models import (
    ProjectStatus, ProjectPriority, ProjectType,
    TaskStatus, TaskPriority, TaskType,
    TimeEntryStatus, BudgetStatus, ExpenseCategory, ExpenseStatus,
    ResourceAllocationStatus
)


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================

class ProjectBase(BaseModel):
    """Base project schema"""
    project_name: str = Field(..., min_length=1, max_length=200)
    project_description: Optional[str] = None
    project_type: ProjectType = ProjectType.INTERNAL
    project_priority: ProjectPriority = ProjectPriority.MEDIUM
    status: ProjectStatus = ProjectStatus.PLANNING
    planned_start_date: date
    planned_end_date: date
    project_manager_id: Optional[UUID] = None
    sponsor_name: Optional[str] = None
    sponsor_email: Optional[str] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    estimated_budget: Optional[Decimal] = Decimal('0.00')
    approved_budget: Optional[Decimal] = Decimal('0.00')
    currency: str = "INR"
    objectives: Optional[str] = None
    success_criteria: Optional[str] = None
    deliverables: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_billable: bool = False
    is_confidential: bool = False


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    project_description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    project_priority: Optional[ProjectPriority] = None
    status: Optional[ProjectStatus] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    project_manager_id: Optional[UUID] = None
    sponsor_name: Optional[str] = None
    sponsor_email: Optional[str] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    department_id: Optional[UUID] = None
    estimated_budget: Optional[Decimal] = None
    approved_budget: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    health_status: Optional[str] = None
    objectives: Optional[str] = None
    success_criteria: Optional[str] = None
    deliverables: Optional[List[str]] = None
    key_risks: Optional[str] = None
    current_issues: Optional[str] = None
    tags: Optional[List[str]] = None
    is_billable: Optional[bool] = None
    is_confidential: Optional[bool] = None
    is_archived: Optional[bool] = None


class ProjectListItem(BaseModel):
    """Schema for project list item"""
    id: UUID
    project_code: str
    project_name: str
    project_type: ProjectType
    project_priority: ProjectPriority
    status: ProjectStatus
    planned_start_date: date
    planned_end_date: date
    project_manager_id: Optional[UUID]
    project_manager_name: Optional[str]
    approved_budget: Optional[Decimal]
    actual_cost: Optional[Decimal]
    progress_percentage: int
    health_status: str
    is_billable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetail(BaseModel):
    """Schema for detailed project view"""
    id: UUID
    project_code: str
    project_name: str
    project_description: Optional[str]
    project_type: ProjectType
    project_priority: ProjectPriority
    status: ProjectStatus
    planned_start_date: date
    planned_end_date: date
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    project_manager_id: Optional[UUID]
    project_manager_name: Optional[str]
    sponsor_name: Optional[str]
    sponsor_email: Optional[str]
    client_name: Optional[str]
    client_contact: Optional[str]
    department_id: Optional[UUID]
    department_name: Optional[str]
    estimated_budget: Optional[Decimal]
    approved_budget: Optional[Decimal]
    actual_cost: Optional[Decimal]
    currency: str
    progress_percentage: int
    health_status: str
    objectives: Optional[str]
    success_criteria: Optional[str]
    deliverables: Optional[List[str]]
    key_risks: Optional[str]
    current_issues: Optional[str]
    tags: Optional[List[str]]
    is_billable: bool
    is_confidential: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    """Project statistics"""
    total_projects: int
    active_projects: int
    completed_projects: int
    on_hold_projects: int
    total_budget: Decimal
    total_spent: Decimal
    budget_utilization_percentage: float


# ============================================================================
# TASK SCHEMAS
# ============================================================================

class TaskBase(BaseModel):
    """Base task schema"""
    task_title: str = Field(..., min_length=1, max_length=300)
    task_description: Optional[str] = None
    project_id: UUID
    parent_task_id: Optional[UUID] = None
    task_type: TaskType = TaskType.FEATURE
    task_priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    assigned_to_id: Optional[UUID] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = Decimal('0.00')
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_billable: bool = True


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    task_title: Optional[str] = Field(None, min_length=1, max_length=300)
    task_description: Optional[str] = None
    parent_task_id: Optional[UUID] = None
    task_type: Optional[TaskType] = None
    task_priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assigned_to_id: Optional[UUID] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    remaining_hours: Optional[Decimal] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_blocked: Optional[bool] = None
    blocked_reason: Optional[str] = None
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_billable: Optional[bool] = None


class TaskListItem(BaseModel):
    """Schema for task list item"""
    id: UUID
    task_code: str
    task_title: str
    task_type: TaskType
    task_priority: TaskPriority
    status: TaskStatus
    project_id: UUID
    project_name: str
    assigned_to_id: Optional[UUID]
    assigned_to_name: Optional[str]
    due_date: Optional[date]
    estimated_hours: Optional[Decimal]
    actual_hours: Optional[Decimal]
    progress_percentage: int
    is_blocked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskDetail(BaseModel):
    """Schema for detailed task view"""
    id: UUID
    task_code: str
    task_title: str
    task_description: Optional[str]
    project_id: UUID
    project_name: str
    parent_task_id: Optional[UUID]
    task_type: TaskType
    task_priority: TaskPriority
    status: TaskStatus
    assigned_to_id: Optional[UUID]
    assigned_to_name: Optional[str]
    assigned_by_id: Optional[UUID]
    assigned_date: Optional[datetime]
    planned_start_date: Optional[date]
    planned_end_date: Optional[date]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    due_date: Optional[date]
    estimated_hours: Optional[Decimal]
    actual_hours: Optional[Decimal]
    remaining_hours: Optional[Decimal]
    progress_percentage: int
    is_blocked: bool
    blocked_reason: Optional[str]
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    is_billable: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskCommentCreate(BaseModel):
    """Schema for creating a task comment"""
    task_id: UUID
    comment_text: str = Field(..., min_length=1)
    parent_comment_id: Optional[UUID] = None
    is_internal: bool = False


class TaskCommentResponse(BaseModel):
    """Schema for task comment response"""
    id: UUID
    task_id: UUID
    comment_text: str
    commented_by_id: Optional[UUID]
    commented_by_name: Optional[str]
    parent_comment_id: Optional[UUID]
    is_internal: bool
    is_pinned: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# TIME ENTRY SCHEMAS
# ============================================================================

class TimeEntryBase(BaseModel):
    """Base time entry schema"""
    project_id: UUID
    task_id: Optional[UUID] = None
    entry_date: date
    hours: Decimal = Field(..., gt=0, le=24)
    description: str = Field(..., min_length=1)
    work_type: Optional[str] = None
    is_billable: bool = True


class TimeEntryCreate(TimeEntryBase):
    """Schema for creating a time entry"""
    pass


class TimeEntryUpdate(BaseModel):
    """Schema for updating a time entry"""
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    entry_date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    hours: Optional[Decimal] = Field(None, gt=0, le=24)
    description: Optional[str] = None
    work_type: Optional[str] = None
    is_billable: Optional[bool] = None


class TimeEntryListItem(BaseModel):
    """Schema for time entry list item"""
    id: UUID
    entry_code: str
    employee_id: UUID
    employee_name: str
    project_id: UUID
    project_name: str
    task_id: Optional[UUID]
    task_title: Optional[str]
    entry_date: date
    hours: Decimal
    description: str
    work_type: Optional[str]
    status: TimeEntryStatus
    is_billable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TimeEntryDetail(BaseModel):
    """Schema for detailed time entry view"""
    id: UUID
    entry_code: str
    employee_id: UUID
    employee_name: str
    project_id: UUID
    project_name: str
    task_id: Optional[UUID]
    task_title: Optional[str]
    entry_date: date
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    hours: Decimal
    description: str
    work_type: Optional[str]
    status: TimeEntryStatus
    submitted_date: Optional[datetime]
    approved_by_id: Optional[UUID]
    approved_date: Optional[datetime]
    rejection_reason: Optional[str]
    is_billable: bool
    hourly_rate: Optional[Decimal]
    billing_amount: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TimeEntryApproval(BaseModel):
    """Schema for approving/rejecting time entries"""
    time_entry_ids: List[UUID]
    action: str = Field(..., pattern="^(approve|reject)$")
    rejection_reason: Optional[str] = None


# ============================================================================
# BUDGET SCHEMAS
# ============================================================================

class ProjectBudgetBase(BaseModel):
    """Base project budget schema"""
    project_id: UUID
    budget_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    fiscal_year: str
    start_date: date
    end_date: date
    planned_budget: Decimal = Field(..., ge=0)
    currency: str = "INR"
    alert_threshold_percentage: int = Field(80, ge=0, le=100)


class ProjectBudgetCreate(ProjectBudgetBase):
    """Schema for creating a project budget"""
    pass


class ProjectBudgetUpdate(BaseModel):
    """Schema for updating a project budget"""
    budget_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_budget: Optional[Decimal] = None
    approved_budget: Optional[Decimal] = None
    revised_budget: Optional[Decimal] = None
    alert_threshold_percentage: Optional[int] = Field(None, ge=0, le=100)


class BudgetExpenseLineCreate(BaseModel):
    """Schema for creating a budget expense line"""
    expense_category: ExpenseCategory
    description: Optional[str] = None
    planned_amount: Decimal = Field(..., ge=0)
    expense_month: Optional[str] = None  # YYYY-MM
    reference_number: Optional[str] = None
    vendor_name: Optional[str] = None


class BudgetExpenseLineUpdate(BaseModel):
    """Schema for updating a budget expense line"""
    planned_amount: Optional[Decimal] = None
    committed_amount: Optional[Decimal] = None
    actual_amount: Optional[Decimal] = None
    status: Optional[ExpenseStatus] = None
    description: Optional[str] = None


class BudgetExpenseLineResponse(BaseModel):
    """Schema for budget expense line response"""
    id: UUID
    budget_id: UUID
    expense_category: ExpenseCategory
    description: Optional[str]
    planned_amount: Decimal
    committed_amount: Decimal
    actual_amount: Decimal
    variance: Decimal
    status: ExpenseStatus
    expense_month: Optional[str]
    
    class Config:
        from_attributes = True


class ProjectBudgetDetail(BaseModel):
    """Schema for detailed project budget view"""
    id: UUID
    budget_code: str
    project_id: UUID
    project_name: str
    budget_name: str
    description: Optional[str]
    fiscal_year: str
    start_date: date
    end_date: date
    planned_budget: Decimal
    approved_budget: Optional[Decimal]
    revised_budget: Optional[Decimal]
    committed_cost: Decimal
    actual_cost: Decimal
    available_budget: Decimal
    budget_variance: Decimal
    variance_percentage: Decimal
    status: BudgetStatus
    currency: str
    alert_threshold_percentage: int
    is_threshold_exceeded: bool
    expense_lines: List[BudgetExpenseLineResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# RESOURCE ALLOCATION SCHEMAS
# ============================================================================

class ResourceAllocationBase(BaseModel):
    """Base resource allocation schema"""
    project_id: UUID
    employee_id: UUID
    role_in_project: str = Field(..., min_length=1, max_length=100)
    responsibilities: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    allocation_percentage: int = Field(100, ge=0, le=100)
    hours_per_week: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    is_billable: bool = True


class ResourceAllocationCreate(ResourceAllocationBase):
    """Schema for creating a resource allocation"""
    pass


class ResourceAllocationUpdate(BaseModel):
    """Schema for updating a resource allocation"""
    role_in_project: Optional[str] = None
    responsibilities: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    allocation_percentage: Optional[int] = Field(None, ge=0, le=100)
    hours_per_week: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    is_billable: Optional[bool] = None
    status: Optional[ResourceAllocationStatus] = None
    notes: Optional[str] = None


class ResourceAllocationResponse(BaseModel):
    """Schema for resource allocation response"""
    id: UUID
    allocation_code: str
    project_id: UUID
    project_name: str
    employee_id: UUID
    employee_name: str
    role_in_project: str
    responsibilities: Optional[str]
    start_date: date
    end_date: Optional[date]
    allocation_percentage: int
    hours_per_week: Optional[Decimal]
    hourly_rate: Optional[Decimal]
    is_billable: bool
    status: ResourceAllocationStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# MILESTONE SCHEMAS
# ============================================================================

class MilestoneCreate(BaseModel):
    """Schema for creating a milestone"""
    project_id: UUID
    milestone_name: str = Field(..., min_length=1, max_length=200)
    milestone_description: Optional[str] = None
    planned_date: date
    deliverables: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    sequence_number: int = 1


class MilestoneUpdate(BaseModel):
    """Schema for updating a milestone"""
    milestone_name: Optional[str] = None
    milestone_description: Optional[str] = None
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    is_completed: Optional[bool] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    deliverables: Optional[str] = None
    acceptance_criteria: Optional[str] = None


class MilestoneResponse(BaseModel):
    """Schema for milestone response"""
    id: UUID
    project_id: UUID
    milestone_name: str
    milestone_description: Optional[str]
    planned_date: date
    actual_date: Optional[date]
    is_completed: bool
    completion_percentage: int
    sequence_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION & FILTER SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ProjectFilters(BaseModel):
    """Project filter parameters"""
    status: Optional[List[ProjectStatus]] = None
    priority: Optional[List[ProjectPriority]] = None
    project_type: Optional[List[ProjectType]] = None
    project_manager_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    search: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None


class TaskFilters(BaseModel):
    """Task filter parameters"""
    project_id: Optional[UUID] = None
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    task_type: Optional[List[TaskType]] = None
    assigned_to_id: Optional[UUID] = None
    search: Optional[str] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
