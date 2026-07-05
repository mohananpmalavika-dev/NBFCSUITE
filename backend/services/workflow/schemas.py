"""
Workflow Engine Pydantic Schemas

Comprehensive schemas for all workflow operations including:
- Workflow templates
- Workflow instances
- Workflow steps
- Workflow tasks
- SLA tracking
- Analytics
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


# ==================== ENUMS ====================

class WorkflowType(str, Enum):
    """Workflow types"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class WorkflowStatus(str, Enum):
    """Workflow template status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class InstanceStatus(str, Enum):
    """Workflow instance status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Workflow step status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Workflow step types"""
    START = "start"
    END = "end"
    HUMAN_TASK = "human_task"
    SYSTEM_TASK = "system_task"
    DECISION = "decision"
    TIMER = "timer"


class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Task types"""
    APPROVAL = "approval"
    REVIEW = "review"
    DATA_ENTRY = "data_entry"
    DOCUMENT_UPLOAD = "document_upload"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AssignmentType(str, Enum):
    """Task assignment types"""
    DIRECT = "direct"
    ROLE_BASED = "role_based"
    POOL = "pool"


# ==================== WORKFLOW TEMPLATE SCHEMAS ====================

class WorkflowStepDefinition(BaseModel):
    """Workflow step definition in template"""
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    type: StepType
    description: Optional[str] = None
    
    # Navigation
    next: Optional[str] = None
    transitions: Optional[List[Dict[str, Any]]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    
    # Configuration
    task_type: Optional[str] = None
    assigned_role: Optional[str] = None
    sla_hours: Optional[int] = Field(None, ge=1)
    
    # System task config
    action: Optional[str] = None
    
    # Result
    result: Optional[str] = None


class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    steps: List[WorkflowStepDefinition] = Field(..., min_items=1)
    variables: Optional[List[Dict[str, Any]]] = None
    sla: Optional[Dict[str, Any]] = None


class WorkflowTemplateCreate(BaseModel):
    """Schema for creating workflow template"""
    template_code: str = Field(..., min_length=2, max_length=50)
    template_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    
    workflow_type: WorkflowType
    trigger_event: Optional[str] = Field(None, max_length=100)
    
    workflow_definition: Dict[str, Any] = Field(..., description="Complete workflow graph")
    default_variables: Optional[Dict[str, Any]] = None
    
    default_sla_hours: Optional[int] = Field(None, ge=1)
    escalation_enabled: bool = False
    escalation_rules: Optional[Dict[str, Any]] = None
    
    is_active: bool = False


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating workflow template"""
    template_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    
    workflow_type: Optional[WorkflowType] = None
    trigger_event: Optional[str] = Field(None, max_length=100)
    
    workflow_definition: Optional[Dict[str, Any]] = None
    default_variables: Optional[Dict[str, Any]] = None
    
    default_sla_hours: Optional[int] = Field(None, ge=1)
    escalation_enabled: Optional[bool] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    
    status: Optional[WorkflowStatus] = None
    is_active: Optional[bool] = None


class WorkflowTemplateResponse(BaseModel):
    """Schema for workflow template response"""
    id: int
    tenant_id: int
    template_code: str
    template_name: str
    description: Optional[str]
    category: Optional[str]
    workflow_type: str
    trigger_event: Optional[str]
    workflow_definition: Dict[str, Any]
    default_variables: Optional[Dict[str, Any]]
    version: int
    is_latest: bool
    status: str
    is_active: bool
    default_sla_hours: Optional[int]
    escalation_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateValidationResponse(BaseModel):
    """Validation result for workflow definition"""
    valid: bool
    errors: List[str]
    warnings: List[str]


class TemplateStatistics(BaseModel):
    """Template usage statistics"""
    template: Dict[str, Any]
    statistics: Dict[str, Any]
    status_breakdown: Dict[str, int]


# ==================== WORKFLOW INSTANCE SCHEMAS ====================

class WorkflowInstanceCreate(BaseModel):
    """Schema for starting workflow instance"""
    template_code: str = Field(..., min_length=2)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[int] = Field(None, gt=0)
    variables: Optional[Dict[str, Any]] = None
    priority: Priority = Priority.NORMAL
    instance_name: Optional[str] = Field(None, max_length=200)


class WorkflowInstanceResponse(BaseModel):
    """Schema for workflow instance response"""
    id: int
    tenant_id: int
    workflow_template_id: int
    instance_number: str
    instance_name: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[int]
    initiated_by: int
    status: str
    current_step_id: Optional[int]
    workflow_variables: Optional[Dict[str, Any]]
    priority: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    deadline: Optional[datetime]
    is_escalated: bool
    result: Optional[str]
    result_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowInstanceDetails(BaseModel):
    """Detailed workflow instance with related data"""
    instance: WorkflowInstanceResponse
    template: Dict[str, Any]
    current_step: Optional[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    pending_tasks: List[Dict[str, Any]]


class CancelWorkflowRequest(BaseModel):
    """Request to cancel workflow"""
    reason: Optional[str] = Field(None, max_length=500)


# ==================== WORKFLOW STEP SCHEMAS ====================

class WorkflowStepResponse(BaseModel):
    """Schema for workflow step response"""
    id: int
    workflow_instance_id: int
    step_key: str
    step_name: str
    step_type: str
    status: str
    assigned_to: Optional[int]
    assigned_role: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    deadline: Optional[datetime]
    actual_duration: Optional[int]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    action_taken: Optional[str]
    comments: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== WORKFLOW HISTORY SCHEMAS ====================

class WorkflowHistoryResponse(BaseModel):
    """Schema for workflow history response"""
    id: int
    workflow_instance_id: int
    workflow_step_id: Optional[int]
    event_type: str
    event_timestamp: datetime
    actor_id: Optional[int]
    actor_type: Optional[str]
    from_step: Optional[str]
    to_step: Optional[str]
    action: Optional[str]
    event_data: Optional[Dict[str, Any]]
    comments: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== WORKFLOW TASK SCHEMAS ====================

class WorkflowTaskResponse(BaseModel):
    """Schema for workflow task response"""
    id: int
    workflow_instance_id: int
    workflow_step_id: int
    task_title: str
    task_description: Optional[str]
    task_type: str
    assigned_to: Optional[int]
    assigned_role: Optional[str]
    assignment_type: Optional[str]
    status: str
    claimed_at: Optional[datetime]
    claimed_by: Optional[int]
    priority: str
    created_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    form_data: Optional[Dict[str, Any]]
    result: Optional[str]
    comments: Optional[str]
    
    class Config:
        from_attributes = True


class TaskDetailsResponse(BaseModel):
    """Comprehensive task details"""
    task: Dict[str, Any]
    assignment: Dict[str, Any]
    workflow: Dict[str, Any]
    step: Dict[str, Any]
    form_data: Optional[Dict[str, Any]]
    attachments: Optional[Dict[str, Any]]
    history: List[Dict[str, Any]]


class ClaimTaskRequest(BaseModel):
    """Request to claim a task"""
    pass  # No additional data needed


class CompleteTaskRequest(BaseModel):
    """Request to complete a task"""
    result: str = Field(..., min_length=1, max_length=50)
    result_data: Optional[Dict[str, Any]] = None
    comments: Optional[str] = Field(None, max_length=1000)


class ApproveTaskRequest(BaseModel):
    """Request to approve a task"""
    comments: Optional[str] = Field(None, max_length=1000)


class RejectTaskRequest(BaseModel):
    """Request to reject a task"""
    reason: str = Field(..., min_length=1, max_length=500)
    comments: Optional[str] = Field(None, max_length=1000)


class ReturnTaskRequest(BaseModel):
    """Request to return task for rework"""
    reason: str = Field(..., min_length=1, max_length=500)
    return_to_step: Optional[str] = Field(None, max_length=100)
    comments: Optional[str] = Field(None, max_length=1000)


class DelegateTaskRequest(BaseModel):
    """Request to delegate a task"""
    delegate_to: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=500)


class ReassignTaskRequest(BaseModel):
    """Request to reassign a task (admin)"""
    assign_to: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=500)


class TaskStatistics(BaseModel):
    """Task statistics for user"""
    user_id: int
    status_breakdown: Dict[str, int]
    overdue_tasks: int
    completed_last_30_days: int
    average_completion_hours: float


class TeamTaskStatistics(BaseModel):
    """Task statistics for team"""
    roles: List[str]
    status_breakdown: Dict[str, int]
    available_tasks: int


# ==================== SLA TRACKING SCHEMAS ====================

class SLATrackingResponse(BaseModel):
    """Schema for SLA tracking response"""
    id: int
    workflow_instance_id: int
    workflow_step_id: Optional[int]
    sla_type: str
    sla_hours: int
    start_time: datetime
    deadline: datetime
    completion_time: Optional[datetime]
    status: str
    breach_time: Optional[datetime]
    time_taken: Optional[int]
    escalation_level: int
    
    class Config:
        from_attributes = True


class SLAStatusResponse(BaseModel):
    """SLA status for workflow/step"""
    sla_type: str
    deadline: datetime
    status: str
    time_remaining_hours: Optional[float]
    is_breached: bool
    escalation_level: int


# ==================== ANALYTICS SCHEMAS ====================

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_workflows: int
    active_workflows: int
    completed_today: int
    overdue_workflows: int
    pending_tasks: int
    my_pending_tasks: int
    sla_compliance_rate: float
    average_completion_hours: float


class SLAReportItem(BaseModel):
    """SLA report item"""
    template_name: str
    total_instances: int
    met_sla: int
    breached_sla: int
    compliance_rate: float
    average_completion_hours: float


class SLAReport(BaseModel):
    """SLA compliance report"""
    from_date: date
    to_date: date
    overall_compliance_rate: float
    by_template: List[SLAReportItem]


class BottleneckItem(BaseModel):
    """Bottleneck analysis item"""
    step_name: str
    template_name: str
    average_duration_hours: float
    instances_count: int
    overdue_count: int


class BottleneckAnalysis(BaseModel):
    """Bottleneck analysis"""
    bottlenecks: List[BottleneckItem]
    recommendations: List[str]


class UserPerformanceItem(BaseModel):
    """User performance item"""
    user_id: int
    tasks_completed: int
    average_completion_hours: float
    overdue_count: int
    on_time_rate: float


class UserPerformance(BaseModel):
    """User performance report"""
    from_date: date
    to_date: date
    users: List[UserPerformanceItem]


class WorkflowMetrics(BaseModel):
    """Workflow metrics"""
    template_code: str
    template_name: str
    total_instances: int
    completed_instances: int
    failed_instances: int
    average_completion_hours: float
    completion_rate: float
    sla_compliance_rate: float


# ==================== SEARCH & FILTER SCHEMAS ====================

class WorkflowTemplateFilter(BaseModel):
    """Filter for workflow templates"""
    category: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    is_active: Optional[bool] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class WorkflowInstanceFilter(BaseModel):
    """Filter for workflow instances"""
    status: Optional[InstanceStatus] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = Field(None, gt=0)
    priority: Optional[Priority] = None
    initiated_by: Optional[int] = Field(None, gt=0)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class WorkflowTaskFilter(BaseModel):
    """Filter for workflow tasks"""
    assigned_to: Optional[int] = Field(None, gt=0)
    assigned_role: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    task_type: Optional[TaskType] = None
    overdue_only: bool = False
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# ==================== COMMON RESPONSE SCHEMAS ====================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int
    skip: int
    limit: int
    has_more: bool


class TemplateListResponse(BaseModel):
    """List of templates with pagination"""
    templates: List[WorkflowTemplateResponse]
    total: int
    skip: int
    limit: int


class InstanceListResponse(BaseModel):
    """List of instances with pagination"""
    instances: List[WorkflowInstanceResponse]
    total: int
    skip: int
    limit: int


class TaskListResponse(BaseModel):
    """List of tasks with pagination"""
    tasks: List[WorkflowTaskResponse]
    total: int
    skip: int
    limit: int


class StepListResponse(BaseModel):
    """List of steps"""
    steps: List[WorkflowStepResponse]
    total: int


class HistoryListResponse(BaseModel):
    """List of history entries"""
    history: List[WorkflowHistoryResponse]
    total: int


# ==================== CLONE & VERSION SCHEMAS ====================

class CloneTemplateRequest(BaseModel):
    """Request to clone template"""
    new_code: str = Field(..., min_length=2, max_length=50)
    new_name: str = Field(..., min_length=3, max_length=200)


class CreateVersionRequest(BaseModel):
    """Request to create new version"""
    changes_description: str = Field(..., min_length=1, max_length=500)


class TemplateVersionListResponse(BaseModel):
    """List of template versions"""
    template_code: str
    versions: List[WorkflowTemplateResponse]
    total_versions: int


# ==================== ESCALATION SCHEMAS ====================

class EscalateWorkflowRequest(BaseModel):
    """Request to manually escalate workflow"""
    escalate_to: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=500)


# ==================== WORKFLOW DIAGRAM ====================

class WorkflowDiagramNode(BaseModel):
    """Node in workflow diagram"""
    id: str
    label: str
    type: str
    status: Optional[str]
    data: Optional[Dict[str, Any]]


class WorkflowDiagramEdge(BaseModel):
    """Edge in workflow diagram"""
    from_node: str
    to_node: str
    label: Optional[str]
    condition: Optional[str]


class WorkflowDiagram(BaseModel):
    """Workflow diagram (for visualization)"""
    instance_number: str
    template_name: str
    nodes: List[WorkflowDiagramNode]
    edges: List[WorkflowDiagramEdge]
    current_node: Optional[str]


# ==================== VALIDATORS ====================

@validator('to_date')
def validate_date_range(cls, v, values):
    """Validate date range"""
    if 'from_date' in values and values['from_date'] and v:
        if v <= values['from_date']:
            raise ValueError('to_date must be after from_date')
    return v
