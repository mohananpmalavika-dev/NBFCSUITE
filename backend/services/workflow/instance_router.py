"""
Workflow Instance Router

API endpoints for workflow instance management including:
- Starting workflows
- Instance monitoring
- Instance control (cancel, retry, escalate)
- Instance history and SLA status
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .execution_service import WorkflowExecutionService
from .schemas import (
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
    WorkflowInstanceDetails,
    CancelWorkflowRequest,
    EscalateWorkflowRequest,
    ReassignTaskRequest,
    WorkflowStepResponse,
    WorkflowHistoryResponse,
    SLAStatusResponse,
    WorkflowDiagram,
    InstanceStatus,
    Priority
)

router = APIRouter(prefix="/workflows/instances", tags=["Workflow Instances"])


# ==================== WORKFLOW LIFECYCLE ====================

@router.post("", response_model=dict, status_code=201)
def start_workflow(
    workflow_data: WorkflowInstanceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Start new workflow instance
    
    Creates and starts a workflow from a template.
    
    **Required**:
    - template_code: Code of template to instantiate
    
    **Optional**:
    - entity_type: Type of business entity (loan_application, customer, etc.)
    - entity_id: ID of the entity this workflow is for
    - variables: Initial workflow variables
    - priority: Workflow priority (low, normal, high, urgent)
    - instance_name: Custom name for this instance
    
    **Returns**: Created instance with unique instance_number (WF-YYYYMM-XXXX)
    """
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.start_workflow(
        template_code=workflow_data.template_code,
        entity_type=workflow_data.entity_type,
        entity_id=workflow_data.entity_id,
        variables=workflow_data.variables,
        priority=workflow_data.priority,
        instance_name=workflow_data.instance_name
    )
    
    return success_response(
        message="Workflow started successfully",
        data=WorkflowInstanceResponse.from_orm(instance).dict()
    )


@router.get("", response_model=dict)
def list_instances(
    status: Optional[InstanceStatus] = Query(None, description="Filter by status"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    initiated_by: Optional[int] = Query(None, description="Filter by initiator"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List workflow instances
    
    Returns workflow instances with optional filters.
    Ordered by creation date (newest first).
    
    **Filters**:
    - status: pending, in_progress, completed, failed, cancelled
    - entity_type: Business entity type
    - entity_id: Specific entity ID
    - priority: low, normal, high, urgent
    - initiated_by: User ID who started the workflow
    """
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instances = service.list_instances(
        status=status,
        entity_type=entity_type,
        entity_id=entity_id,
        priority=priority,
        initiated_by=initiated_by,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(instances)} workflow instances",
        data={
            "instances": [WorkflowInstanceResponse.from_orm(i).dict() for i in instances],
            "total": len(instances),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{instance_id}", response_model=dict)
def get_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get workflow instance details
    
    Returns complete instance information including:
    - Instance details
    - Template information
    - Current step
    - All steps with status
    - Pending tasks
    """
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowStep, WorkflowTask
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    # Get all steps
    steps = db.query(WorkflowStep).filter(
        and_(
            WorkflowStep.workflow_instance_id == instance_id,
            WorkflowStep.tenant_id == tenant_id
        )
    ).order_by(WorkflowStep.created_at).all()
    
    # Get pending tasks
    pending_tasks = db.query(WorkflowTask).filter(
        and_(
            WorkflowTask.workflow_instance_id == instance_id,
            WorkflowTask.tenant_id == tenant_id,
            WorkflowTask.status.in_(['pending', 'claimed', 'in_progress']),
            WorkflowTask.is_deleted == False
        )
    ).all()
    
    # Get current step details
    current_step = None
    if instance.current_step_id:
        current_step = db.query(WorkflowStep).filter(
            WorkflowStep.id == instance.current_step_id
        ).first()
    
    return success_response(
        message="Instance retrieved successfully",
        data={
            "instance": WorkflowInstanceResponse.from_orm(instance).dict(),
            "template": {
                "id": instance.template.id,
                "code": instance.template.template_code,
                "name": instance.template.template_name,
                "type": instance.template.workflow_type
            },
            "current_step": WorkflowStepResponse.from_orm(current_step).dict() if current_step else None,
            "steps": [WorkflowStepResponse.from_orm(s).dict() for s in steps],
            "pending_tasks": [
                {
                    "id": t.id,
                    "title": t.task_title,
                    "type": t.task_type,
                    "status": t.status,
                    "assigned_to": t.assigned_to,
                    "assigned_role": t.assigned_role,
                    "due_date": t.due_date.isoformat() if t.due_date else None
                }
                for t in pending_tasks
            ]
        }
    )


@router.post("/{instance_id}/cancel", response_model=dict)
def cancel_workflow(
    instance_id: int,
    cancel_request: CancelWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Cancel workflow instance
    
    Cancels a running workflow instance.
    Cannot cancel completed, failed, or already cancelled workflows.
    All pending steps and tasks will be cancelled.
    
    **Note**: This action cannot be undone
    """
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.cancel_workflow(
        instance_id=instance_id,
        reason=cancel_request.reason
    )
    
    return success_response(
        message="Workflow cancelled successfully",
        data=WorkflowInstanceResponse.from_orm(instance).dict()
    )


# ==================== WORKFLOW HISTORY ====================

@router.get("/{instance_id}/history", response_model=dict)
def get_instance_history(
    instance_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get workflow instance history
    
    Returns complete audit trail of workflow execution including:
    - Workflow started/completed/cancelled
    - Step transitions
    - Task actions
    - User actions
    
    History ordered by timestamp (newest first).
    """
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowHistory
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    # Get history
    history = db.query(WorkflowHistory).filter(
        and_(
            WorkflowHistory.workflow_instance_id == instance_id,
            WorkflowHistory.tenant_id == tenant_id
        )
    ).order_by(
        WorkflowHistory.event_timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    # Count total
    from sqlalchemy import func
    total = db.query(func.count(WorkflowHistory.id)).filter(
        and_(
            WorkflowHistory.workflow_instance_id == instance_id,
            WorkflowHistory.tenant_id == tenant_id
        )
    ).scalar()
    
    return success_response(
        message=f"Retrieved {len(history)} history entries",
        data={
            "history": [WorkflowHistoryResponse.from_orm(h).dict() for h in history],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{instance_id}/steps", response_model=dict)
def get_instance_steps(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all steps for workflow instance
    
    Returns all steps executed or pending for this workflow.
    Steps ordered by creation date.
    """
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowStep
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    steps = db.query(WorkflowStep).filter(
        and_(
            WorkflowStep.workflow_instance_id == instance_id,
            WorkflowStep.tenant_id == tenant_id
        )
    ).order_by(WorkflowStep.created_at).all()
    
    return success_response(
        message=f"Retrieved {len(steps)} steps",
        data={
            "steps": [WorkflowStepResponse.from_orm(s).dict() for s in steps],
            "total": len(steps)
        }
    )


# ==================== USER'S WORKFLOWS ====================

@router.get("/my-workflows/list", response_model=dict)
def get_my_workflows(
    status: Optional[InstanceStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get workflows initiated by current user
    
    Returns workflows started by the logged-in user.
    """
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instances = service.list_instances(
        initiated_by=current_user["id"],
        status=status,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(instances)} workflows",
        data={
            "instances": [WorkflowInstanceResponse.from_orm(i).dict() for i in instances],
            "total": len(instances),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/pending/list", response_model=dict)
def get_pending_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get pending workflows
    
    Returns workflows that are pending or in progress.
    Useful for monitoring active workflows.
    """
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    
    # Get pending and in_progress workflows
    from sqlalchemy import and_, or_
    from backend.shared.database.workflow_models import WorkflowInstance
    
    instances = db.query(WorkflowInstance).filter(
        and_(
            WorkflowInstance.tenant_id == tenant_id,
            WorkflowInstance.status.in_(['pending', 'in_progress']),
            WorkflowInstance.is_deleted == False
        )
    ).order_by(
        WorkflowInstance.priority.desc(),
        WorkflowInstance.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return success_response(
        message=f"Retrieved {len(instances)} pending workflows",
        data={
            "instances": [WorkflowInstanceResponse.from_orm(i).dict() for i in instances],
            "total": len(instances),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/overdue/list", response_model=dict)
def get_overdue_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get overdue workflows
    
    Returns workflows that have passed their SLA deadline.
    Excludes completed, failed, and cancelled workflows.
    """
    from datetime import datetime
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowInstance
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    
    instances = db.query(WorkflowInstance).filter(
        and_(
            WorkflowInstance.tenant_id == tenant_id,
            WorkflowInstance.deadline < datetime.utcnow(),
            WorkflowInstance.status.in_(['pending', 'in_progress']),
            WorkflowInstance.is_deleted == False
        )
    ).order_by(
        WorkflowInstance.deadline.asc()
    ).offset(skip).limit(limit).all()
    
    return success_response(
        message=f"Retrieved {len(instances)} overdue workflows",
        data={
            "instances": [WorkflowInstanceResponse.from_orm(i).dict() for i in instances],
            "total": len(instances),
            "skip": skip,
            "limit": limit
        }
    )


# ==================== SLA STATUS ====================

@router.get("/{instance_id}/sla-status", response_model=dict)
def get_sla_status(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get SLA status for workflow instance
    
    Returns SLA tracking information including:
    - Workflow-level SLA
    - Step-level SLAs
    - Time remaining/breached
    - Escalation status
    """
    from datetime import datetime
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowSLATracking
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    # Get all SLA tracking records
    slas = db.query(WorkflowSLATracking).filter(
        and_(
            WorkflowSLATracking.workflow_instance_id == instance_id,
            WorkflowSLATracking.tenant_id == tenant_id
        )
    ).all()
    
    # Format SLA status
    sla_status = []
    for sla in slas:
        time_remaining = None
        is_breached = False
        
        if sla.status == 'active':
            now = datetime.utcnow()
            if now > sla.deadline:
                is_breached = True
                time_remaining = 0
            else:
                time_remaining = (sla.deadline - now).total_seconds() / 3600  # hours
        
        sla_status.append({
            "id": sla.id,
            "sla_type": sla.sla_type,
            "sla_hours": sla.sla_hours,
            "start_time": sla.start_time.isoformat(),
            "deadline": sla.deadline.isoformat(),
            "completion_time": sla.completion_time.isoformat() if sla.completion_time else None,
            "status": sla.status,
            "time_remaining_hours": round(time_remaining, 2) if time_remaining is not None else None,
            "is_breached": is_breached,
            "escalation_level": sla.escalation_level,
            "breach_time": sla.breach_time.isoformat() if sla.breach_time else None
        })
    
    return success_response(
        message="SLA status retrieved successfully",
        data={
            "instance_id": instance_id,
            "instance_status": instance.status,
            "sla_tracking": sla_status,
            "overall_breached": any(s["is_breached"] for s in sla_status)
        }
    )


# ==================== ADMIN OPERATIONS ====================

@router.post("/{instance_id}/escalate", response_model=dict)
def escalate_workflow(
    instance_id: int,
    escalate_request: EscalateWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Manually escalate workflow (admin operation)
    
    Escalates workflow to a specific user or role.
    Used for handling stuck or critical workflows.
    
    **Required**:
    - escalate_to: User ID to escalate to
    - reason: Escalation reason
    """
    from datetime import datetime
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowHistory
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    # Mark as escalated
    instance.is_escalated = True
    instance.escalated_at = datetime.utcnow()
    instance.escalated_to = escalate_request.escalate_to
    
    # Create history entry
    history = WorkflowHistory(
        tenant_id=tenant_id,
        workflow_instance_id=instance_id,
        event_type='escalated',
        actor_id=current_user["id"],
        actor_type='user',
        event_data={
            'escalated_to': escalate_request.escalate_to,
            'reason': escalate_request.reason
        },
        comments=escalate_request.reason
    )
    db.add(history)
    
    db.commit()
    db.refresh(instance)
    
    return success_response(
        message="Workflow escalated successfully",
        data=WorkflowInstanceResponse.from_orm(instance).dict()
    )


@router.post("/{instance_id}/skip-step", response_model=dict)
def skip_step(
    instance_id: int,
    step_key: str = Query(..., description="Step key to skip"),
    reason: str = Query(..., description="Reason for skipping"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Skip current step (admin operation)
    
    Marks current step as skipped and moves to next step.
    Use with caution - can break workflow logic.
    
    **Required admin permission**
    """
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowStep
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    # TODO: Check admin permission
    
    # Find step
    step = db.query(WorkflowStep).filter(
        and_(
            WorkflowStep.workflow_instance_id == instance_id,
            WorkflowStep.step_key == step_key,
            WorkflowStep.tenant_id == tenant_id
        )
    ).first()
    
    if not step:
        from backend.shared.common.response import CustomException
        raise CustomException(status_code=404, message="Step not found")
    
    # Skip the step
    step.status = 'skipped'
    step.comments = f"Skipped by admin: {reason}"
    
    # Create history entry
    from backend.shared.database.workflow_models import WorkflowHistory
    history = WorkflowHistory(
        tenant_id=tenant_id,
        workflow_instance_id=instance_id,
        workflow_step_id=step.id,
        event_type='step_skipped',
        actor_id=current_user["id"],
        actor_type='user',
        from_step=step_key,
        comments=reason
    )
    db.add(history)
    
    db.commit()
    
    return success_response(
        message="Step skipped successfully",
        data={
            "instance_id": instance_id,
            "step_key": step_key,
            "skipped": True
        }
    )


@router.post("/{instance_id}/retry", response_model=dict)
def retry_failed_workflow(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Retry failed workflow
    
    Retries execution of a failed workflow from the failed step.
    Only works for workflows in 'failed' status.
    """
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    from backend.shared.common.response import CustomException
    if instance.status != 'failed':
        raise CustomException(
            status_code=400,
            message="Only failed workflows can be retried"
        )
    
    # Reset status
    instance.status = 'in_progress'
    instance.result = None
    instance.result_message = None
    
    # Create history entry
    from backend.shared.database.workflow_models import WorkflowHistory
    history = WorkflowHistory(
        tenant_id=tenant_id,
        workflow_instance_id=instance_id,
        event_type='retried',
        actor_id=current_user["id"],
        actor_type='user',
        comments="Workflow retried after failure"
    )
    db.add(history)
    
    # TODO: Implement retry logic - re-execute from failed step
    
    db.commit()
    db.refresh(instance)
    
    return success_response(
        message="Workflow retry initiated",
        data=WorkflowInstanceResponse.from_orm(instance).dict()
    )


# ==================== WORKFLOW DIAGRAM ====================

@router.get("/{instance_id}/diagram", response_model=dict)
def get_workflow_diagram(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get workflow diagram data (for visualization)
    
    Returns workflow structure as nodes and edges for visual rendering.
    Includes current step highlighting and step status.
    
    **Use this for frontend diagram/flowchart visualization**
    """
    from sqlalchemy import and_
    from backend.shared.database.workflow_models import WorkflowStep
    
    service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = service.get_instance(instance_id)
    
    # Get workflow definition
    workflow_def = instance.template.workflow_definition
    steps_def = workflow_def.get('steps', [])
    
    # Get executed steps for status
    executed_steps = db.query(WorkflowStep).filter(
        and_(
            WorkflowStep.workflow_instance_id == instance_id,
            WorkflowStep.tenant_id == tenant_id
        )
    ).all()
    
    step_status_map = {s.step_key: s.status for s in executed_steps}
    
    # Build nodes
    nodes = []
    for step_def in steps_def:
        nodes.append({
            "id": step_def['key'],
            "label": step_def['name'],
            "type": step_def['type'],
            "status": step_status_map.get(step_def['key']),
            "data": {
                "description": step_def.get('description'),
                "sla_hours": step_def.get('sla_hours')
            }
        })
    
    # Build edges
    edges = []
    for step_def in steps_def:
        # Default next edge
        if step_def.get('next'):
            edges.append({
                "from_node": step_def['key'],
                "to_node": step_def['next'],
                "label": None,
                "condition": None
            })
        
        # Transition edges
        if step_def.get('transitions'):
            for trans in step_def['transitions']:
                edges.append({
                    "from_node": step_def['key'],
                    "to_node": trans['next'],
                    "label": trans.get('action'),
                    "condition": None
                })
        
        # Condition edges
        if step_def.get('conditions'):
            for cond in step_def['conditions']:
                edges.append({
                    "from_node": step_def['key'],
                    "to_node": cond['next'],
                    "label": None,
                    "condition": cond.get('condition')
                })
    
    # Get current node
    current_node = None
    if instance.current_step_id:
        current_step = db.query(WorkflowStep).filter(
            WorkflowStep.id == instance.current_step_id
        ).first()
        if current_step:
            current_node = current_step.step_key
    
    return success_response(
        message="Workflow diagram retrieved successfully",
        data={
            "instance_number": instance.instance_number,
            "template_name": instance.template.template_name,
            "nodes": nodes,
            "edges": edges,
            "current_node": current_node
        }
    )
