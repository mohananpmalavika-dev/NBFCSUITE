"""
BPMN 2.0 Workflow Engine Models

Complete BPMN 2.0 compliant workflow models including:
- Start Events (None, Timer, Message, Signal)
- End Events (None, Terminate, Error)
- Tasks (User, Service, Script, Send, Receive)
- Gateways (Exclusive, Parallel, Inclusive, Event-Based)
- Intermediate Events (Timer, Message, Signal, Error)
- Sequence Flows with Conditions
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ==================== BPMN NODE TYPES ====================

class BPMNNodeType(str, Enum):
    """BPMN 2.0 Node Types"""
    # Start Events
    START_NONE = "start_none"
    START_TIMER = "start_timer"
    START_MESSAGE = "start_message"
    START_SIGNAL = "start_signal"
    
    # End Events
    END_NONE = "end_none"
    END_TERMINATE = "end_terminate"
    END_ERROR = "end_error"
    END_MESSAGE = "end_message"
    
    # Tasks
    USER_TASK = "user_task"
    SERVICE_TASK = "service_task"
    SCRIPT_TASK = "script_task"
    SEND_TASK = "send_task"
    RECEIVE_TASK = "receive_task"
    MANUAL_TASK = "manual_task"
    BUSINESS_RULE_TASK = "business_rule_task"
    
    # Gateways
    EXCLUSIVE_GATEWAY = "exclusive_gateway"  # XOR - one path
    PARALLEL_GATEWAY = "parallel_gateway"  # AND - all paths
    INCLUSIVE_GATEWAY = "inclusive_gateway"  # OR - multiple paths
    EVENT_BASED_GATEWAY = "event_based_gateway"  # Wait for event
    
    # Intermediate Events
    INTERMEDIATE_TIMER = "intermediate_timer"
    INTERMEDIATE_MESSAGE = "intermediate_message"
    INTERMEDIATE_SIGNAL = "intermediate_signal"
    INTERMEDIATE_ERROR = "intermediate_error"
    
    # Subprocesses
    SUBPROCESS = "subprocess"
    CALL_ACTIVITY = "call_activity"


class GatewayType(str, Enum):
    """Gateway Types"""
    EXCLUSIVE = "exclusive"  # XOR
    PARALLEL = "parallel"  # AND
    INCLUSIVE = "inclusive"  # OR
    EVENT_BASED = "event_based"


class EventType(str, Enum):
    """Event Types"""
    NONE = "none"
    TIMER = "timer"
    MESSAGE = "message"
    SIGNAL = "signal"
    ERROR = "error"
    CONDITIONAL = "conditional"


# ==================== BPMN NODE SCHEMAS ====================

class BPMNPosition(BaseModel):
    """Visual position on canvas"""
    x: float
    y: float


class BPMNSize(BaseModel):
    """Visual size on canvas"""
    width: float
    height: float


class BPMNNodeBase(BaseModel):
    """Base BPMN Node"""
    id: str = Field(..., description="Unique node ID")
    name: str = Field(..., description="Node display name")
    type: BPMNNodeType
    
    # Visual properties
    position: Optional[BPMNPosition] = None
    size: Optional[BPMNSize] = None
    
    # Documentation
    description: Optional[str] = None
    documentation: Optional[str] = None


# ==================== START EVENTS ====================

class TimerDefinition(BaseModel):
    """Timer definition"""
    type: str = Field(..., description="duration, date, cycle")
    value: str = Field(..., description="ISO8601 duration or date")


class MessageDefinition(BaseModel):
    """Message definition"""
    message_name: str
    correlation_key: Optional[str] = None


class SignalDefinition(BaseModel):
    """Signal definition"""
    signal_name: str
    scope: str = "global"  # global, process


class BPMNStartEvent(BPMNNodeBase):
    """BPMN Start Event"""
    event_type: EventType = EventType.NONE
    
    # Event-specific configuration
    timer: Optional[TimerDefinition] = None
    message: Optional[MessageDefinition] = None
    signal: Optional[SignalDefinition] = None


# ==================== END EVENTS ====================

class ErrorDefinition(BaseModel):
    """Error definition"""
    error_code: str
    error_message: Optional[str] = None


class BPMNEndEvent(BPMNNodeBase):
    """BPMN End Event"""
    event_type: EventType = EventType.NONE
    
    # Event-specific configuration
    error: Optional[ErrorDefinition] = None
    message: Optional[MessageDefinition] = None
    terminate_all: bool = False  # For terminate events


# ==================== TASKS ====================

class UserTaskConfig(BaseModel):
    """User Task Configuration"""
    assignment_type: str = Field(..., description="direct, role, expression")
    
    # Assignment
    assigned_user_id: Optional[int] = None
    assigned_role: Optional[str] = None
    assignment_expression: Optional[str] = None
    candidate_users: Optional[List[int]] = None
    candidate_groups: Optional[List[str]] = None
    
    # Form
    form_key: Optional[str] = None
    form_fields: Optional[List[Dict[str, Any]]] = None
    
    # Timing
    due_date: Optional[str] = None  # Expression
    priority: str = "normal"


class ServiceTaskConfig(BaseModel):
    """Service Task Configuration"""
    implementation: str = Field(..., description="api, class, expression")
    
    # API Configuration
    api_endpoint: Optional[str] = None
    api_method: Optional[str] = "POST"
    api_headers: Optional[Dict[str, str]] = None
    api_body: Optional[Dict[str, Any]] = None
    
    # Class Configuration
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    
    # Expression Configuration
    expression: Optional[str] = None
    
    # Result
    result_variable: Optional[str] = None
    
    # Error Handling
    retry_enabled: bool = False
    max_retries: int = 3
    retry_delay: int = 60  # seconds


class ScriptTaskConfig(BaseModel):
    """Script Task Configuration"""
    script_format: str = "python"
    script: str
    result_variable: Optional[str] = None
    timeout: int = 300  # seconds


class SendTaskConfig(BaseModel):
    """Send Task Configuration"""
    send_type: str = Field(..., description="email, sms, notification, webhook")
    
    # Email Configuration
    to: Optional[str] = None  # Expression
    subject: Optional[str] = None
    template: Optional[str] = None
    
    # SMS Configuration
    phone: Optional[str] = None
    message: Optional[str] = None
    
    # Webhook Configuration
    webhook_url: Optional[str] = None
    webhook_method: str = "POST"
    webhook_body: Optional[Dict[str, Any]] = None


class BPMNUserTask(BPMNNodeBase):
    """BPMN User Task"""
    config: UserTaskConfig


class BPMNServiceTask(BPMNNodeBase):
    """BPMN Service Task"""
    config: ServiceTaskConfig


class BPMNScriptTask(BPMNNodeBase):
    """BPMN Script Task"""
    config: ScriptTaskConfig


class BPMNSendTask(BPMNNodeBase):
    """BPMN Send Task"""
    config: SendTaskConfig


# ==================== GATEWAYS ====================

class BPMNGateway(BPMNNodeBase):
    """BPMN Gateway"""
    gateway_type: GatewayType
    default_flow: Optional[str] = None  # Default outgoing flow ID


# ==================== INTERMEDIATE EVENTS ====================

class BPMNIntermediateEvent(BPMNNodeBase):
    """BPMN Intermediate Event"""
    event_type: EventType
    
    # Event-specific configuration
    timer: Optional[TimerDefinition] = None
    message: Optional[MessageDefinition] = None
    signal: Optional[SignalDefinition] = None
    error: Optional[ErrorDefinition] = None
    
    # Catching vs Throwing
    catching: bool = True


# ==================== SEQUENCE FLOWS ====================

class ConditionExpression(BaseModel):
    """Condition expression for sequence flow"""
    type: str = Field(..., description="simple, script")
    
    # Simple condition
    variable: Optional[str] = None
    operator: Optional[str] = None  # ==, !=, >, <, >=, <=, in, not_in
    value: Optional[Any] = None
    
    # Script condition
    script: Optional[str] = None
    language: str = "python"


class BPMNSequenceFlow(BaseModel):
    """BPMN Sequence Flow (Connection)"""
    id: str = Field(..., description="Unique flow ID")
    name: Optional[str] = None
    
    # Connection
    source_ref: str = Field(..., description="Source node ID")
    target_ref: str = Field(..., description="Target node ID")
    
    # Condition
    condition: Optional[ConditionExpression] = None
    
    # Visual
    waypoints: Optional[List[BPMNPosition]] = None
    
    # Documentation
    description: Optional[str] = None


# ==================== BPMN PROCESS ====================

class BPMNProcess(BaseModel):
    """BPMN 2.0 Process Definition"""
    id: str = Field(..., description="Process ID")
    name: str = Field(..., description="Process name")
    version: str = "1.0"
    
    # Process attributes
    is_executable: bool = True
    process_type: str = "None"  # None, Public, Private
    
    # Documentation
    description: Optional[str] = None
    documentation: Optional[str] = None
    
    # Elements
    start_events: List[BPMNStartEvent] = []
    end_events: List[BPMNEndEvent] = []
    user_tasks: List[BPMNUserTask] = []
    service_tasks: List[BPMNServiceTask] = []
    script_tasks: List[BPMNScriptTask] = []
    send_tasks: List[BPMNSendTask] = []
    gateways: List[BPMNGateway] = []
    intermediate_events: List[BPMNIntermediateEvent] = []
    
    # Connections
    sequence_flows: List[BPMNSequenceFlow] = []
    
    # Process variables
    variables: Optional[Dict[str, Any]] = None
    
    # Canvas settings
    canvas_settings: Optional[Dict[str, Any]] = None


# ==================== WORKFLOW DEFINITION ====================

class BPMNWorkflowDefinition(BaseModel):
    """Complete BPMN Workflow Definition for storage"""
    workflow_id: str
    workflow_name: str
    workflow_description: Optional[str] = None
    version: str = "1.0"
    
    # BPMN Process
    process: BPMNProcess
    
    # Metadata
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Tags and categories
    tags: Optional[List[str]] = None
    category: Optional[str] = None


# ==================== VISUAL DESIGNER DATA ====================

class CanvasNode(BaseModel):
    """Visual canvas node representation"""
    id: str
    type: str
    data: Dict[str, Any]
    position: BPMNPosition
    
    # React Flow properties
    draggable: bool = True
    selectable: bool = True
    connectable: bool = True


class CanvasEdge(BaseModel):
    """Visual canvas edge representation"""
    id: str
    source: str
    target: str
    type: str = "smoothstep"
    label: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    animated: bool = False
    style: Optional[Dict[str, Any]] = None


class WorkflowCanvas(BaseModel):
    """Complete workflow canvas data"""
    nodes: List[CanvasNode]
    edges: List[CanvasEdge]
    viewport: Optional[Dict[str, float]] = None


# ==================== TEMPLATE LIBRARY ====================

class WorkflowTemplateDefinition(BaseModel):
    """Pre-built workflow template"""
    template_id: str
    template_name: str
    description: str
    category: str
    icon: Optional[str] = None
    
    # Template content
    bpmn_definition: BPMNWorkflowDefinition
    
    # Preview
    thumbnail: Optional[str] = None
    tags: List[str] = []
    
    # Configuration
    configurable_fields: Optional[List[Dict[str, Any]]] = None


# ==================== VALIDATION ====================

class ValidationIssue(BaseModel):
    """Validation issue"""
    severity: str = Field(..., description="error, warning, info")
    code: str
    message: str
    node_id: Optional[str] = None
    flow_id: Optional[str] = None


class ValidationResult(BaseModel):
    """Workflow validation result"""
    valid: bool
    issues: List[ValidationIssue]
    
    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]
    
    @property
    def infos(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "info"]
