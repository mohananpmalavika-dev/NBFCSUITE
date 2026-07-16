"""
Workflow Engine Module
Enterprise-grade BPMN 2.0 compliant workflow engine
"""
from backend.services.workflow.workflow_models import (
    # Enums
    NodeType,
    GatewayType,
    ApprovalType,
    SLAUnit,
    EscalationType,
    WorkflowStatus,
    TaskStatus,
    ApprovalDecision,
    WorkflowTrigger,
    
    # Database Models
    WorkflowTemplate,
    WorkflowNode,
    WorkflowConnection,
    ApprovalConfig,
    EscalationRule,
    WorkflowInstance,
    WorkflowExecution,
    ApprovalExecution,
    SLATracking,
    HolidayCalendar,
    
    # Pydantic Schemas
    WorkflowTemplateCreate,
    WorkflowNodeCreate,
    WorkflowConnectionCreate,
    ApprovalConfigCreate,
    EscalationRuleCreate,
    WorkflowInstanceCreate,
    ApprovalDecisionRequest,
    WorkflowStats,
    NodeStats
)

from backend.services.workflow.workflow_service import WorkflowService
from backend.services.workflow.workflow_router import router as workflow_router

__all__ = [
    # Enums
    "NodeType",
    "GatewayType",
    "ApprovalType",
    "SLAUnit",
    "EscalationType",
    "WorkflowStatus",
    "TaskStatus",
    "ApprovalDecision",
    "WorkflowTrigger",
    
    # Models
    "WorkflowTemplate",
    "WorkflowNode",
    "WorkflowConnection",
    "ApprovalConfig",
    "EscalationRule",
    "WorkflowInstance",
    "WorkflowExecution",
    "ApprovalExecution",
    "SLATracking",
    "HolidayCalendar",
    
    # Schemas
    "WorkflowTemplateCreate",
    "WorkflowNodeCreate",
    "WorkflowConnectionCreate",
    "ApprovalConfigCreate",
    "EscalationRuleCreate",
    "WorkflowInstanceCreate",
    "ApprovalDecisionRequest",
    "WorkflowStats",
    "NodeStats",
    
    # Service & Router
    "WorkflowService",
    "workflow_router"
]
