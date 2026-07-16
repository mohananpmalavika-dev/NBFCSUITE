"""
Workflow Engine Models
Enterprise-grade BPMN 2.0 compliant workflow engine models
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from backend.core.database import Base


# =====================================================================
# ENUMS
# =====================================================================

class NodeType(str, Enum):
    """BPMN Node Types"""
    START_EVENT = "START_EVENT"
    END_EVENT = "END_EVENT"
    USER_TASK = "USER_TASK"
    SERVICE_TASK = "SERVICE_TASK"
    SCRIPT_TASK = "SCRIPT_TASK"
    MANUAL_TASK = "MANUAL_TASK"
    BUSINESS_RULE_TASK = "BUSINESS_RULE_TASK"
    EXCLUSIVE_GATEWAY = "EXCLUSIVE_GATEWAY"  # if-then-else
    PARALLEL_GATEWAY = "PARALLEL_GATEWAY"    # concurrent paths
    INCLUSIVE_GATEWAY = "INCLUSIVE_GATEWAY"  # multiple conditions
    EVENT_BASED_GATEWAY = "EVENT_BASED_GATEWAY"
    TIMER_EVENT = "TIMER_EVENT"
    SIGNAL_EVENT = "SIGNAL_EVENT"
    MESSAGE_EVENT = "MESSAGE_EVENT"
    SUBPROCESS = "SUBPROCESS"


class GatewayType(str, Enum):
    """Gateway decision types"""
    EXCLUSIVE = "EXCLUSIVE"  # One path only
    PARALLEL = "PARALLEL"    # All paths
    INCLUSIVE = "INCLUSIVE"  # One or more paths


class ApprovalType(str, Enum):
    """Approval execution types"""
    SEQUENTIAL = "SEQUENTIAL"      # One after another
    PARALLEL = "PARALLEL"          # All must approve simultaneously
    ANY_ONE = "ANY_ONE"            # First to approve wins
    MAJORITY = "MAJORITY"          # Threshold-based (e.g., 3 out of 5)
    CONSENSUS = "CONSENSUS"        # All must agree
    CONDITIONAL = "CONDITIONAL"    # Rule-based routing


class SLAUnit(str, Enum):
    """SLA time units"""
    MINUTES = "MINUTES"
    HOURS = "HOURS"
    DAYS = "DAYS"
    BUSINESS_DAYS = "BUSINESS_DAYS"


class EscalationType(str, Enum):
    """Escalation types"""
    SOFT = "SOFT"          # Send reminder + notify supervisor
    HARD = "HARD"          # Auto-transfer to next level
    MULTI_LEVEL = "MULTI_LEVEL"  # Escalate up hierarchy


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ApprovalDecision(str, Enum):
    """Approval decisions"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SENT_BACK = "SENT_BACK"
    ESCALATED = "ESCALATED"
    PENDING = "PENDING"


class WorkflowTrigger(str, Enum):
    """Workflow trigger events"""
    MANUAL = "MANUAL"
    APPLICATION_SUBMIT = "APPLICATION_SUBMIT"
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    SCHEDULE = "SCHEDULE"
    API_CALL = "API_CALL"
    WEBHOOK = "WEBHOOK"


# =====================================================================
# DATABASE MODELS
# =====================================================================

class WorkflowTemplate(Base):
    """Workflow template definition - BPMN 2.0 compliant"""
    __tablename__ = "workflow_templates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(100))  # e.g., "Loan Approval", "Customer Onboarding"
    version = Column(String(20), default="1.0")
    
    # Status
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    is_active = Column(Boolean, default=False)
    
    # Trigger configuration
    trigger_type = Column(SQLEnum(WorkflowTrigger), default=WorkflowTrigger.MANUAL)
    trigger_config = Column(JSON)  # Additional trigger configuration
    
    # BPMN diagram data
    bpmn_xml = Column(Text)  # BPMN 2.0 XML representation
    diagram_json = Column(JSON)  # Visual diagram data for UI
    
    # Metadata
    tags = Column(JSON)  # List of tags
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    
    # Relationships
    nodes = relationship("WorkflowNode", back_populates="template", cascade="all, delete-orphan")
    connections = relationship("WorkflowConnection", back_populates="template", cascade="all, delete-orphan")
    instances = relationship("WorkflowInstance", back_populates="template")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    updated_by = Column(PGUUID(as_uuid=True))


class WorkflowNode(Base):
    """Workflow node (task, gateway, event)"""
    __tablename__ = "workflow_nodes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_templates.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Node identification
    node_id = Column(String(100), nullable=False)  # Unique ID in diagram
    node_type = Column(SQLEnum(NodeType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Position in diagram
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    width = Column(Float, default=100)
    height = Column(Float, default=80)
    
    # Node configuration
    config = Column(JSON)  # Node-specific configuration
    
    # For User Tasks
    assignee_type = Column(String(50))  # "ROLE", "USER", "GROUP", "EXPRESSION"
    assignee_value = Column(String(255))  # Role ID, User ID, or expression
    form_key = Column(String(255))  # Form to display
    
    # For Service Tasks
    service_class = Column(String(255))  # Service class to execute
    service_method = Column(String(100))  # Method name
    service_params = Column(JSON)  # Method parameters
    
    # For Script Tasks
    script_language = Column(String(50))  # "python", "javascript"
    script_content = Column(Text)
    
    # For Gateways
    gateway_type = Column(SQLEnum(GatewayType))
    default_path = Column(String(100))  # Default connection ID
    
    # For Timer Events
    timer_duration = Column(String(50))  # ISO 8601 duration (e.g., "PT2H", "P1D")
    timer_date = Column(DateTime)  # Specific date/time
    timer_cycle = Column(String(100))  # Cron expression for recurring
    
    # SLA Configuration
    sla_duration = Column(Integer)  # Duration value
    sla_unit = Column(SQLEnum(SLAUnit))  # Unit of duration
    sla_business_hours_only = Column(Boolean, default=False)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="nodes")
    approval_config = relationship("ApprovalConfig", back_populates="node", uselist=False, cascade="all, delete-orphan")
    escalation_rules = relationship("EscalationRule", back_populates="node", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowConnection(Base):
    """Connection between workflow nodes"""
    __tablename__ = "workflow_connections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_templates.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Connection identification
    connection_id = Column(String(100), nullable=False)
    name = Column(String(255))
    
    # Source and target
    source_node_id = Column(String(100), nullable=False)
    target_node_id = Column(String(100), nullable=False)
    
    # Condition (for gateways)
    condition_expression = Column(Text)  # Expression to evaluate
    condition_type = Column(String(50))  # "EXPRESSION", "SCRIPT"
    is_default = Column(Boolean, default=False)
    
    # Visual properties
    waypoints = Column(JSON)  # List of {x, y} coordinates for drawing
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="connections")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class ApprovalConfig(Base):
    """Approval configuration for user tasks"""
    __tablename__ = "approval_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    node_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_nodes.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Approval type
    approval_type = Column(SQLEnum(ApprovalType), nullable=False)
    
    # Approvers
    approver_roles = Column(JSON)  # List of role IDs
    approver_users = Column(JSON)  # List of user IDs
    approver_expression = Column(Text)  # Dynamic expression for approvers
    
    # For Sequential approval
    approval_order = Column(JSON)  # Ordered list of approvers
    
    # For Majority approval
    approval_threshold = Column(Integer)  # Number of approvals needed
    approval_percentage = Column(Float)  # Percentage of approvals needed (0-100)
    
    # Maker-Checker
    is_maker_checker = Column(Boolean, default=False)
    maker_roles = Column(JSON)
    checker_roles = Column(JSON)
    min_checkers = Column(Integer, default=1)
    same_branch_required = Column(Boolean, default=False)
    cooling_period_hours = Column(Integer)  # Hours between maker and checker
    
    # Approval rules
    allow_self_approval = Column(Boolean, default=False)
    allow_reassignment = Column(Boolean, default=True)
    allow_delegation = Column(Boolean, default=True)
    require_comments = Column(Boolean, default=False)
    
    # Routing rules (for conditional approval)
    routing_rules = Column(JSON)  # List of {condition, approver} mappings
    
    # Relationships
    node = relationship("WorkflowNode", back_populates="approval_config")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EscalationRule(Base):
    """Escalation rules for tasks"""
    __tablename__ = "escalation_rules"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    node_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_nodes.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Escalation configuration
    escalation_type = Column(SQLEnum(EscalationType), nullable=False)
    escalation_level = Column(Integer, default=1)  # For multi-level escalation
    
    # Timing
    trigger_after_duration = Column(Integer, nullable=False)  # Duration value
    trigger_after_unit = Column(SQLEnum(SLAUnit), nullable=False)
    
    # Reminder configuration
    send_reminder = Column(Boolean, default=True)
    reminder_before_duration = Column(Integer)
    reminder_before_unit = Column(SQLEnum(SLAUnit))
    
    # Escalation targets
    escalate_to_supervisor = Column(Boolean, default=True)
    escalate_to_roles = Column(JSON)  # List of role IDs
    escalate_to_users = Column(JSON)  # List of user IDs
    
    # Actions
    auto_reassign = Column(Boolean, default=False)
    notify_assignee = Column(Boolean, default=True)
    notify_supervisor = Column(Boolean, default=True)
    notify_stakeholders = Column(JSON)  # Additional people to notify
    
    # Escalation message
    escalation_subject = Column(String(500))
    escalation_message = Column(Text)
    
    # Relationships
    node = relationship("WorkflowNode", back_populates="escalation_rules")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowInstance(Base):
    """Runtime instance of a workflow"""
    __tablename__ = "workflow_instances"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_templates.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Instance information
    instance_name = Column(String(255))
    business_key = Column(String(255), index=True)  # External reference (e.g., loan_application_id)
    
    # Status
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.ACTIVE, index=True)
    current_node_id = Column(String(100))  # Current position in workflow
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)
    
    # Process variables (context data)
    variables = Column(JSON)  # Key-value pairs of workflow variables
    
    # Parent/child relationships (for subprocesses)
    parent_instance_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_instances.id"))
    
    # Priority
    priority = Column(Integer, default=5)  # 1-10, higher = more urgent
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="instances")
    executions = relationship("WorkflowExecution", back_populates="instance", cascade="all, delete-orphan")
    approvals = relationship("ApprovalExecution", back_populates="instance", cascade="all, delete-orphan")
    sla_tracking = relationship("SLATracking", back_populates="instance", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    updated_by = Column(PGUUID(as_uuid=True))


class WorkflowExecution(Base):
    """Execution log for workflow nodes"""
    __tablename__ = "workflow_executions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_instances.id"), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Node information
    node_id = Column(String(100), nullable=False)
    node_name = Column(String(255))
    node_type = Column(SQLEnum(NodeType))
    
    # Execution details
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    assigned_to = Column(PGUUID(as_uuid=True))  # User ID
    assigned_role = Column(String(100))
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    due_date = Column(DateTime)  # Based on SLA
    
    # Execution data
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Comments
    comments = Column(Text)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="executions")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApprovalExecution(Base):
    """Approval execution tracking"""
    __tablename__ = "approval_executions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_instances.id"), nullable=False, index=True)
    execution_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_executions.id"))
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Approver information
    approver_id = Column(PGUUID(as_uuid=True), nullable=False)
    approver_name = Column(String(255))
    approver_role = Column(String(100))
    approval_level = Column(Integer)
    
    # Decision
    decision = Column(SQLEnum(ApprovalDecision), default=ApprovalDecision.PENDING, index=True)
    comments = Column(Text)
    reason = Column(String(500))
    
    # Timing
    assigned_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    due_date = Column(DateTime)
    
    # Escalation tracking
    is_escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime)
    escalation_level = Column(Integer, default=0)
    
    # Reminder tracking
    reminder_count = Column(Integer, default=0)
    last_reminder_at = Column(DateTime)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="approvals")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SLATracking(Base):
    """SLA tracking for workflow tasks"""
    __tablename__ = "sla_tracking"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_instances.id"), nullable=False, index=True)
    execution_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_executions.id"))
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Node information
    node_id = Column(String(100), nullable=False)
    node_name = Column(String(255))
    
    # SLA definition
    sla_duration = Column(Integer)
    sla_unit = Column(SQLEnum(SLAUnit))
    business_hours_only = Column(Boolean, default=False)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)
    resumed_at = Column(DateTime)
    paused_duration = Column(Integer, default=0)  # Total paused time in seconds
    
    # Status
    is_breached = Column(Boolean, default=False, index=True)
    breach_duration = Column(Integer)  # Duration of breach in seconds
    is_paused = Column(Boolean, default=False)
    pause_reason = Column(String(500))
    
    # Escalation
    is_escalated = Column(Boolean, default=False)
    escalation_count = Column(Integer, default=0)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="sla_tracking")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HolidayCalendar(Base):
    """Holiday calendar for business day calculation"""
    __tablename__ = "holiday_calendars"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    country = Column(String(50))
    state = Column(String(100))
    city = Column(String(100))
    
    holiday_date = Column(DateTime, nullable=False, index=True)
    holiday_name = Column(String(255))
    is_working_day = Column(Boolean, default=False)  # Some holidays might be working days
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))


# =====================================================================
# PYDANTIC SCHEMAS (for API validation)
# =====================================================================

class WorkflowTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = None
    version: str = "1.0"
    trigger_type: WorkflowTrigger = WorkflowTrigger.MANUAL
    trigger_config: Optional[Dict[str, Any]] = None
    bpmn_xml: Optional[str] = None
    diagram_json: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class WorkflowNodeCreate(BaseModel):
    node_id: str = Field(..., min_length=1)
    node_type: NodeType
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    position_x: float = 0
    position_y: float = 0
    width: float = 100
    height: float = 80
    config: Optional[Dict[str, Any]] = None
    assignee_type: Optional[str] = None
    assignee_value: Optional[str] = None
    form_key: Optional[str] = None
    service_class: Optional[str] = None
    service_method: Optional[str] = None
    service_params: Optional[Dict[str, Any]] = None
    script_language: Optional[str] = None
    script_content: Optional[str] = None
    gateway_type: Optional[GatewayType] = None
    default_path: Optional[str] = None
    timer_duration: Optional[str] = None
    timer_date: Optional[datetime] = None
    timer_cycle: Optional[str] = None
    sla_duration: Optional[int] = None
    sla_unit: Optional[SLAUnit] = None
    sla_business_hours_only: bool = False


class WorkflowConnectionCreate(BaseModel):
    connection_id: str = Field(..., min_length=1)
    name: Optional[str] = None
    source_node_id: str = Field(..., min_length=1)
    target_node_id: str = Field(..., min_length=1)
    condition_expression: Optional[str] = None
    condition_type: Optional[str] = None
    is_default: bool = False
    waypoints: Optional[List[Dict[str, float]]] = None


class ApprovalConfigCreate(BaseModel):
    approval_type: ApprovalType
    approver_roles: Optional[List[str]] = None
    approver_users: Optional[List[str]] = None
    approver_expression: Optional[str] = None
    approval_order: Optional[List[str]] = None
    approval_threshold: Optional[int] = None
    approval_percentage: Optional[float] = None
    is_maker_checker: bool = False
    maker_roles: Optional[List[str]] = None
    checker_roles: Optional[List[str]] = None
    min_checkers: int = 1
    same_branch_required: bool = False
    cooling_period_hours: Optional[int] = None
    allow_self_approval: bool = False
    allow_reassignment: bool = True
    allow_delegation: bool = True
    require_comments: bool = False
    routing_rules: Optional[List[Dict[str, Any]]] = None


class EscalationRuleCreate(BaseModel):
    escalation_type: EscalationType
    escalation_level: int = 1
    trigger_after_duration: int = Field(..., gt=0)
    trigger_after_unit: SLAUnit
    send_reminder: bool = True
    reminder_before_duration: Optional[int] = None
    reminder_before_unit: Optional[SLAUnit] = None
    escalate_to_supervisor: bool = True
    escalate_to_roles: Optional[List[str]] = None
    escalate_to_users: Optional[List[str]] = None
    auto_reassign: bool = False
    notify_assignee: bool = True
    notify_supervisor: bool = True
    notify_stakeholders: Optional[List[str]] = None
    escalation_subject: Optional[str] = None
    escalation_message: Optional[str] = None


class WorkflowInstanceCreate(BaseModel):
    template_id: UUID
    instance_name: Optional[str] = None
    business_key: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    priority: int = Field(default=5, ge=1, le=10)


class ApprovalDecisionRequest(BaseModel):
    decision: ApprovalDecision
    comments: Optional[str] = None
    reason: Optional[str] = None


class WorkflowStats(BaseModel):
    total_instances: int
    active_instances: int
    completed_instances: int
    pending_approvals: int
    sla_breached: int
    avg_cycle_time_hours: float
    completion_rate: float


class NodeStats(BaseModel):
    node_id: str
    node_name: str
    total_executions: int
    avg_duration_minutes: float
    pending_count: int
    sla_breach_count: int
