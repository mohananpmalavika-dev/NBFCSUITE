"""
Workflow Engine API Router
FastAPI routes for workflow management and execution
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id as get_current_tenant
from backend.services.workflow.workflow_service import WorkflowService
from backend.services.workflow.workflow_models import (
    WorkflowTemplate, WorkflowNode, WorkflowConnection,
    ApprovalConfig, EscalationRule, WorkflowInstance,
    ApprovalExecution, SLATracking, HolidayCalendar,
    WorkflowTemplateCreate, WorkflowNodeCreate, WorkflowConnectionCreate,
    ApprovalConfigCreate, EscalationRuleCreate, WorkflowInstanceCreate,
    ApprovalDecisionRequest, WorkflowStats, NodeStats,
    WorkflowStatus, ApprovalDecision
)

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflow Engine"])


def get_workflow_service(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    user_id: UUID = Depends(get_current_user)
) -> WorkflowService:
    """Dependency to get workflow service"""
    return WorkflowService(db, tenant_id, user_id)


# =====================================================================
# WORKFLOW TEMPLATE ENDPOINTS
# =====================================================================

@router.post("/templates/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_workflow_template(
    data: WorkflowTemplateCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create a new workflow template"""
    try:
        template = service.create_template(data)
        return {
            "id": str(template.id),
            "name": template.name,
            "code": template.code,
            "status": template.status,
            "message": "Workflow template created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates/", response_model=List[dict])
def list_workflow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[WorkflowStatus] = None,
    search: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """List workflow templates with filters"""
    templates = service.list_templates(skip, limit, category, status, search)
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "code": t.code,
            "description": t.description,
            "category": t.category,
            "version": t.version,
            "status": t.status,
            "is_active": t.is_active,
            "trigger_type": t.trigger_type,
            "node_count": len(t.nodes),
            "connection_count": len(t.connections),
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat()
        }
        for t in templates
    ]


@router.get("/templates/{template_id}", response_model=dict)
def get_workflow_template(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow template by ID"""
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": str(template.id),
        "name": template.name,
        "code": template.code,
        "description": template.description,
        "category": template.category,
        "version": template.version,
        "status": template.status,
        "is_active": template.is_active,
        "trigger_type": template.trigger_type,
        "trigger_config": template.trigger_config,
        "bpmn_xml": template.bpmn_xml,
        "diagram_json": template.diagram_json,
        "tags": template.tags,
        "effective_from": template.effective_from.isoformat() if template.effective_from else None,
        "effective_to": template.effective_to.isoformat() if template.effective_to else None,
        "nodes": [
            {
                "id": str(n.id),
                "node_id": n.node_id,
                "node_type": n.node_type,
                "name": n.name,
                "position_x": n.position_x,
                "position_y": n.position_y,
                "config": n.config
            }
            for n in template.nodes
        ],
        "connections": [
            {
                "id": str(c.id),
                "connection_id": c.connection_id,
                "source_node_id": c.source_node_id,
                "target_node_id": c.target_node_id,
                "condition_expression": c.condition_expression
            }
            for c in template.connections
        ],
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat()
    }



@router.put("/templates/{template_id}", response_model=dict)
def update_workflow_template(
    template_id: UUID,
    data: dict,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Update workflow template"""
    template = service.update_template(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": str(template.id),
        "name": template.name,
        "message": "Template updated successfully"
    }


@router.delete("/templates/{template_id}", response_model=dict)
def delete_workflow_template(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Delete workflow template"""
    try:
        success = service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/templates/{template_id}/activate", response_model=dict)
def activate_workflow_template(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Activate workflow template"""
    try:
        template = service.activate_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return {
            "id": str(template.id),
            "is_active": template.is_active,
            "message": "Template activated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/templates/{template_id}/deactivate", response_model=dict)
def deactivate_workflow_template(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Deactivate workflow template"""
    template = service.deactivate_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": str(template.id),
        "is_active": template.is_active,
        "message": "Template deactivated successfully"
    }


@router.post("/templates/{template_id}/clone", response_model=dict)
def clone_workflow_template(
    template_id: UUID,
    new_name: str,
    new_code: str,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Clone workflow template"""
    cloned = service.clone_template(template_id, new_name, new_code)
    if not cloned:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": str(cloned.id),
        "name": cloned.name,
        "code": cloned.code,
        "message": "Template cloned successfully"
    }



# =====================================================================
# WORKFLOW NODE ENDPOINTS
# =====================================================================

@router.post("/templates/{template_id}/nodes/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_workflow_node(
    template_id: UUID,
    data: WorkflowNodeCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create workflow node"""
    try:
        node = service.create_node(template_id, data)
        return {
            "id": str(node.id),
            "node_id": node.node_id,
            "name": node.name,
            "message": "Node created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nodes/{node_id}", response_model=dict)
def get_workflow_node(
    node_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow node by ID"""
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {
        "id": str(node.id),
        "node_id": node.node_id,
        "node_type": node.node_type,
        "name": node.name,
        "description": node.description,
        "position_x": node.position_x,
        "position_y": node.position_y,
        "width": node.width,
        "height": node.height,
        "config": node.config,
        "assignee_type": node.assignee_type,
        "assignee_value": node.assignee_value,
        "sla_duration": node.sla_duration,
        "sla_unit": node.sla_unit,
        "approval_config": {
            "approval_type": node.approval_config.approval_type,
            "approver_roles": node.approval_config.approver_roles,
            "approver_users": node.approval_config.approver_users
        } if node.approval_config else None,
        "escalation_rules": [
            {
                "escalation_type": rule.escalation_type,
                "trigger_after_duration": rule.trigger_after_duration,
                "trigger_after_unit": rule.trigger_after_unit
            }
            for rule in node.escalation_rules
        ]
    }


@router.put("/nodes/{node_id}", response_model=dict)
def update_workflow_node(
    node_id: UUID,
    data: dict,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Update workflow node"""
    node = service.update_node(node_id, data)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"id": str(node.id), "message": "Node updated successfully"}


@router.delete("/nodes/{node_id}", response_model=dict)
def delete_workflow_node(
    node_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Delete workflow node"""
    success = service.delete_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted successfully"}



# =====================================================================
# WORKFLOW CONNECTION ENDPOINTS
# =====================================================================

@router.post("/templates/{template_id}/connections/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_workflow_connection(
    template_id: UUID,
    data: WorkflowConnectionCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create workflow connection"""
    try:
        connection = service.create_connection(template_id, data)
        return {
            "id": str(connection.id),
            "connection_id": connection.connection_id,
            "message": "Connection created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/connections/{connection_id}", response_model=dict)
def delete_workflow_connection(
    connection_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Delete workflow connection"""
    success = service.delete_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Connection deleted successfully"}


# =====================================================================
# APPROVAL CONFIGURATION ENDPOINTS
# =====================================================================

@router.post("/nodes/{node_id}/approval-config/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_approval_config(
    node_id: UUID,
    data: ApprovalConfigCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create approval configuration for a node"""
    try:
        config = service.create_approval_config(node_id, data)
        return {
            "id": str(config.id),
            "approval_type": config.approval_type,
            "message": "Approval configuration created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/approval-configs/{config_id}", response_model=dict)
def update_approval_config(
    config_id: UUID,
    data: dict,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Update approval configuration"""
    config = service.update_approval_config(config_id, data)
    if not config:
        raise HTTPException(status_code=404, detail="Approval config not found")
    return {"id": str(config.id), "message": "Approval config updated successfully"}



# =====================================================================
# ESCALATION RULE ENDPOINTS
# =====================================================================

@router.post("/nodes/{node_id}/escalation-rules/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_escalation_rule(
    node_id: UUID,
    data: EscalationRuleCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create escalation rule for a node"""
    try:
        rule = service.create_escalation_rule(node_id, data)
        return {
            "id": str(rule.id),
            "escalation_type": rule.escalation_type,
            "message": "Escalation rule created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nodes/{node_id}/escalation-rules/", response_model=List[dict])
def get_escalation_rules(
    node_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get all escalation rules for a node"""
    rules = service.get_escalation_rules(node_id)
    return [
        {
            "id": str(rule.id),
            "escalation_type": rule.escalation_type,
            "escalation_level": rule.escalation_level,
            "trigger_after_duration": rule.trigger_after_duration,
            "trigger_after_unit": rule.trigger_after_unit,
            "escalate_to_supervisor": rule.escalate_to_supervisor,
            "auto_reassign": rule.auto_reassign
        }
        for rule in rules
    ]


# =====================================================================
# WORKFLOW INSTANCE ENDPOINTS
# =====================================================================

@router.post("/instances/", response_model=dict, status_code=status.HTTP_201_CREATED)
def start_workflow_instance(
    data: WorkflowInstanceCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Start a new workflow instance"""
    try:
        instance = service.start_workflow(data)
        return {
            "id": str(instance.id),
            "instance_name": instance.instance_name,
            "status": instance.status,
            "current_node_id": instance.current_node_id,
            "message": "Workflow started successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/instances/", response_model=List[dict])
def list_workflow_instances(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[WorkflowStatus] = None,
    template_id: Optional[UUID] = None,
    business_key: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """List workflow instances with filters"""
    instances = service.list_instances(skip, limit, status, template_id, business_key)
    return [
        {
            "id": str(inst.id),
            "template_id": str(inst.template_id),
            "instance_name": inst.instance_name,
            "business_key": inst.business_key,
            "status": inst.status,
            "current_node_id": inst.current_node_id,
            "priority": inst.priority,
            "started_at": inst.started_at.isoformat(),
            "completed_at": inst.completed_at.isoformat() if inst.completed_at else None
        }
        for inst in instances
    ]



@router.get("/instances/{instance_id}", response_model=dict)
def get_workflow_instance(
    instance_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow instance by ID"""
    instance = service.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return {
        "id": str(instance.id),
        "template_id": str(instance.template_id),
        "template_name": instance.template.name,
        "instance_name": instance.instance_name,
        "business_key": instance.business_key,
        "status": instance.status,
        "current_node_id": instance.current_node_id,
        "priority": instance.priority,
        "variables": instance.variables,
        "started_at": instance.started_at.isoformat(),
        "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
        "error_message": instance.error_message,
        "executions": [
            {
                "id": str(ex.id),
                "node_id": ex.node_id,
                "node_name": ex.node_name,
                "status": ex.status,
                "started_at": ex.started_at.isoformat(),
                "completed_at": ex.completed_at.isoformat() if ex.completed_at else None,
                "due_date": ex.due_date.isoformat() if ex.due_date else None
            }
            for ex in instance.executions
        ],
        "approvals": [
            {
                "id": str(ap.id),
                "approver_id": str(ap.approver_id),
                "approver_name": ap.approver_name,
                "decision": ap.decision,
                "assigned_at": ap.assigned_at.isoformat(),
                "responded_at": ap.responded_at.isoformat() if ap.responded_at else None
            }
            for ap in instance.approvals
        ]
    }


@router.post("/instances/{instance_id}/cancel", response_model=dict)
def cancel_workflow_instance(
    instance_id: UUID,
    reason: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Cancel workflow instance"""
    instance = service.cancel_instance(instance_id, reason)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {
        "id": str(instance.id),
        "status": instance.status,
        "message": "Workflow instance cancelled successfully"
    }


# =====================================================================
# APPROVAL PROCESSING ENDPOINTS
# =====================================================================

@router.post("/approvals/{approval_id}/process", response_model=dict)
def process_approval(
    approval_id: UUID,
    decision_data: ApprovalDecisionRequest,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Process an approval decision"""
    try:
        approval = service.process_approval(approval_id, decision_data)
        return {
            "id": str(approval.id),
            "decision": approval.decision,
            "responded_at": approval.responded_at.isoformat(),
            "message": "Approval processed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/approvals/pending", response_model=List[dict])
def get_pending_approvals(
    user_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get pending approvals for a user"""
    approvals = service.get_pending_approvals(user_id, skip, limit)
    return [
        {
            "id": str(ap.id),
            "instance_id": str(ap.instance_id),
            "workflow_name": ap.instance.template.name if ap.instance else None,
            "business_key": ap.instance.business_key if ap.instance else None,
            "approver_id": str(ap.approver_id),
            "approval_level": ap.approval_level,
            "decision": ap.decision,
            "assigned_at": ap.assigned_at.isoformat(),
            "due_date": ap.due_date.isoformat() if ap.due_date else None,
            "is_escalated": ap.is_escalated,
            "reminder_count": ap.reminder_count
        }
        for ap in approvals
    ]



# =====================================================================
# SLA TRACKING ENDPOINTS
# =====================================================================

@router.get("/sla/breaches", response_model=List[dict])
def get_sla_breaches(
    service: WorkflowService = Depends(get_workflow_service)
):
    """Check and get SLA breaches"""
    breached = service.check_sla_breaches()
    return [
        {
            "id": str(sla.id),
            "instance_id": str(sla.instance_id),
            "node_id": sla.node_id,
            "node_name": sla.node_name,
            "due_date": sla.due_date.isoformat(),
            "breach_duration": sla.breach_duration,
            "started_at": sla.started_at.isoformat()
        }
        for sla in breached
    ]


@router.post("/sla/{sla_id}/pause", response_model=dict)
def pause_sla_tracking(
    sla_id: UUID,
    reason: str,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Pause SLA tracking"""
    sla = service.pause_sla(sla_id, reason)
    if not sla:
        raise HTTPException(status_code=404, detail="SLA tracking not found")
    return {
        "id": str(sla.id),
        "is_paused": sla.is_paused,
        "message": "SLA tracking paused"
    }


@router.post("/sla/{sla_id}/resume", response_model=dict)
def resume_sla_tracking(
    sla_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Resume SLA tracking"""
    sla = service.resume_sla(sla_id)
    if not sla:
        raise HTTPException(status_code=404, detail="SLA tracking not found or not paused")
    return {
        "id": str(sla.id),
        "is_paused": sla.is_paused,
        "new_due_date": sla.due_date.isoformat(),
        "message": "SLA tracking resumed"
    }


# =====================================================================
# ESCALATION ENDPOINTS
# =====================================================================

@router.get("/escalations/check", response_model=List[dict])
def check_escalations(
    service: WorkflowService = Depends(get_workflow_service)
):
    """Check and trigger escalations"""
    escalated = service.check_escalations()
    return [
        {
            "id": str(ap.id),
            "instance_id": str(ap.instance_id),
            "approver_id": str(ap.approver_id),
            "escalation_level": ap.escalation_level,
            "escalated_at": ap.escalated_at.isoformat()
        }
        for ap in escalated
    ]



# =====================================================================
# ANALYTICS & MONITORING ENDPOINTS
# =====================================================================

@router.get("/stats", response_model=WorkflowStats)
def get_workflow_statistics(
    template_id: Optional[UUID] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow statistics"""
    return service.get_workflow_stats(template_id)


@router.get("/templates/{template_id}/node-stats", response_model=List[NodeStats])
def get_node_statistics(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get statistics per node for a template"""
    return service.get_node_stats(template_id)


@router.get("/templates/{template_id}/bottlenecks", response_model=List[dict])
def get_bottleneck_nodes(
    template_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Identify bottleneck nodes"""
    return service.get_bottleneck_nodes(template_id, limit)


@router.get("/users/{user_id}/productivity", response_model=dict)
def get_user_productivity(
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get user productivity metrics"""
    return service.get_user_productivity(user_id, start_date, end_date)


@router.get("/users/my-productivity", response_model=dict)
def get_my_productivity(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get current user's productivity metrics"""
    return service.get_user_productivity(None, start_date, end_date)


# =====================================================================
# PROCESS MINING ENDPOINTS
# =====================================================================

@router.get("/templates/{template_id}/process-mining/paths", response_model=dict)
def get_actual_workflow_paths(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Analyze actual workflow execution paths"""
    return service.get_actual_workflow_paths(template_id)


@router.get("/templates/{template_id}/process-mining/deviations", response_model=dict)
def get_deviation_analysis(
    template_id: UUID,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Analyze deviations from designed workflow"""
    return service.get_deviation_analysis(template_id)



# =====================================================================
# HOLIDAY CALENDAR ENDPOINTS
# =====================================================================

@router.post("/holidays/", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_holiday(
    holiday_date: datetime,
    holiday_name: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Add holiday to calendar"""
    holiday = service.add_holiday(holiday_date, holiday_name, country, state, city)
    return {
        "id": str(holiday.id),
        "holiday_date": holiday.holiday_date.isoformat(),
        "holiday_name": holiday.holiday_name,
        "message": "Holiday added successfully"
    }


@router.get("/holidays/", response_model=List[dict])
def get_holidays(
    start_date: datetime,
    end_date: datetime,
    country: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get holidays in date range"""
    holidays = service.get_holidays(start_date, end_date, country)
    return [
        {
            "id": str(h.id),
            "holiday_date": h.holiday_date.isoformat(),
            "holiday_name": h.holiday_name,
            "country": h.country,
            "state": h.state,
            "city": h.city,
            "is_working_day": h.is_working_day
        }
        for h in holidays
    ]


# =====================================================================
# DASHBOARD ENDPOINTS
# =====================================================================

@router.get("/dashboard/summary", response_model=dict)
def get_dashboard_summary(
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get dashboard summary data"""
    stats = service.get_workflow_stats()
    pending_approvals = service.get_pending_approvals(limit=10)
    sla_breaches = service.check_sla_breaches()
    
    return {
        "stats": {
            "total_instances": stats.total_instances,
            "active_instances": stats.active_instances,
            "completed_instances": stats.completed_instances,
            "pending_approvals": stats.pending_approvals,
            "sla_breached": stats.sla_breached,
            "avg_cycle_time_hours": stats.avg_cycle_time_hours,
            "completion_rate": stats.completion_rate
        },
        "my_pending_approvals": [
            {
                "id": str(ap.id),
                "workflow_name": ap.instance.template.name if ap.instance else None,
                "due_date": ap.due_date.isoformat() if ap.due_date else None,
                "is_escalated": ap.is_escalated
            }
            for ap in pending_approvals[:5]
        ],
        "recent_sla_breaches": [
            {
                "id": str(sla.id),
                "node_name": sla.node_name,
                "breach_duration": sla.breach_duration
            }
            for sla in sla_breaches[:5]
        ]
    }


@router.get("/dashboard/trends", response_model=dict)
def get_dashboard_trends(
    days: int = Query(30, ge=1, le=365),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow trends data"""
    # Simplified trends - in production, implement proper time-series analysis
    stats = service.get_workflow_stats()
    
    return {
        "period_days": days,
        "stats": {
            "total_instances": stats.total_instances,
            "completion_rate": stats.completion_rate,
            "avg_cycle_time_hours": stats.avg_cycle_time_hours
        },
        "message": "Trends data - implement time-series analysis for detailed trends"
    }
