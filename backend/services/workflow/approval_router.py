"""
Approval Workflow API Router

Endpoints for advanced approval workflows:
- Sequential, Parallel, Any One, Majority, Conditional
- Maker-Checker pattern
- Approval chain configuration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.shared.database.connection import get_db
from backend.shared.common.dependencies import get_current_user
from backend.shared.database.models import User
from backend.services.workflow.approval_models import (
    ApprovalChainConfig, ApprovalAction, ApprovalChainTemplates
)
from backend.services.workflow.approval_engine import ApprovalEngine

router = APIRouter(prefix="/api/v1/approvals", tags=["Advanced Approvals"])


# ==================== REQUEST SCHEMAS ====================

class StartApprovalRequest(BaseModel):
    """Request to start approval"""
    chain_id: str
    entity_type: str
    entity_id: int
    variables: Optional[dict] = None


class ProcessApprovalRequest(BaseModel):
    """Request to process approval"""
    action: str  # approve, reject, delegate, return
    comments: Optional[str] = None
    delegate_to: Optional[int] = None
    return_to_level: Optional[int] = None


# ==================== APPROVAL CHAIN MANAGEMENT ====================

@router.post("/chains")
def create_approval_chain(
    chain_config: ApprovalChainConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new approval chain configuration"""
    # Store in database (implementation needed)
    return {
        "success": True,
        "message": "Approval chain created",
        "chain_id": chain_config.chain_id
    }


@router.get("/chains")
def list_approval_chains(
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all approval chains"""
    # Get from database
    chains = []
    
    # Include templates
    templates = [
        ApprovalChainTemplates.loan_approval_chain(),
        ApprovalChainTemplates.parallel_approval_chain(),
        ApprovalChainTemplates.any_one_approval_chain(),
        ApprovalChainTemplates.maker_checker_chain()
    ]
    
    if entity_type:
        templates = [t for t in templates if t.entity_type == entity_type]
    
    return {
        "success": True,
        "chains": [t.dict() for t in templates],
        "total": len(templates)
    }


@router.get("/chains/{chain_id}")
def get_approval_chain(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval chain configuration"""
    # Try templates first
    templates = {
        "loan_approval_standard": ApprovalChainTemplates.loan_approval_chain(),
        "parallel_approval_all_teams": ApprovalChainTemplates.parallel_approval_chain(),
        "any_one_regional_manager": ApprovalChainTemplates.any_one_approval_chain(),
        "maker_checker_simple": ApprovalChainTemplates.maker_checker_chain()
    }
    
    if chain_id in templates:
        return {
            "success": True,
            "chain": templates[chain_id].dict()
        }
    
    raise HTTPException(status_code=404, detail="Approval chain not found")


@router.put("/chains/{chain_id}")
def update_approval_chain(
    chain_id: str,
    chain_config: ApprovalChainConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update approval chain configuration"""
    return {
        "success": True,
        "message": "Approval chain updated"
    }


# ==================== APPROVAL EXECUTION ====================

@router.post("/start")
def start_approval(
    request: StartApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start approval process"""
    engine = ApprovalEngine(db, current_user.tenant_id, current_user.id)
    
    # Get chain config
    templates = {
        "loan_approval_standard": ApprovalChainTemplates.loan_approval_chain(),
        "parallel_approval_all_teams": ApprovalChainTemplates.parallel_approval_chain(),
        "any_one_regional_manager": ApprovalChainTemplates.any_one_approval_chain(),
        "maker_checker_simple": ApprovalChainTemplates.maker_checker_chain()
    }
    
    chain_config = templates.get(request.chain_id)
    if not chain_config:
        raise HTTPException(status_code=404, detail="Approval chain not found")
    
    result = engine.start_approval(
        chain_config=chain_config,
        entity_id=request.entity_id,
        maker_id=current_user.id,
        variables=request.variables
    )
    
    return result


@router.post("/instances/{instance_id}/tasks/{task_id}/process")
def process_approval(
    instance_id: int,
    task_id: int,
    request: ProcessApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process approval action (approve/reject/delegate/return)"""
    engine = ApprovalEngine(db, current_user.tenant_id, current_user.id)
    
    action = ApprovalAction(
        action=request.action,
        comments=request.comments,
        delegate_to=request.delegate_to,
        return_to_level=request.return_to_level
    )
    
    result = engine.process_approval(
        instance_id=instance_id,
        task_id=task_id,
        action=action
    )
    
    return result


# ==================== APPROVAL STATUS ====================

@router.get("/instances/{instance_id}")
def get_approval_status(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval instance status"""
    from backend.shared.database.workflow_models import WorkflowInstance
    
    instance = db.query(WorkflowInstance).filter(
        WorkflowInstance.id == instance_id,
        WorkflowInstance.tenant_id == current_user.tenant_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Approval instance not found")
    
    return {
        "success": True,
        "instance": {
            "id": instance.id,
            "instance_number": instance.instance_number,
            "entity_type": instance.entity_type,
            "entity_id": instance.entity_id,
            "status": instance.status,
            "result": instance.result,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "approval_levels": instance.workflow_variables.get('approval_levels', [])
        }
    }


@router.get("/entity/{entity_type}/{entity_id}")
def get_entity_approvals(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all approvals for an entity"""
    from backend.shared.database.workflow_models import WorkflowInstance
    
    instances = db.query(WorkflowInstance).filter(
        WorkflowInstance.tenant_id == current_user.tenant_id,
        WorkflowInstance.entity_type == entity_type,
        WorkflowInstance.entity_id == entity_id
    ).order_by(WorkflowInstance.created_at.desc()).all()
    
    return {
        "success": True,
        "approvals": [
            {
                "id": inst.id,
                "instance_number": inst.instance_number,
                "status": inst.status,
                "result": inst.result,
                "started_at": inst.started_at.isoformat() if inst.started_at else None,
                "completed_at": inst.completed_at.isoformat() if inst.completed_at else None
            }
            for inst in instances
        ],
        "total": len(instances)
    }


# ==================== MY APPROVALS ====================

@router.get("/my-pending")
def get_my_pending_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get my pending approval tasks"""
    from backend.shared.database.workflow_models import WorkflowTask
    
    tasks = db.query(WorkflowTask).filter(
        WorkflowTask.tenant_id == current_user.tenant_id,
        WorkflowTask.assigned_to == current_user.id,
        WorkflowTask.status == 'pending',
        WorkflowTask.task_type == 'approval'
    ).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "tasks": [
            {
                "id": task.id,
                "instance_id": task.workflow_instance_id,
                "title": task.task_title,
                "description": task.task_description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ],
        "total": len(tasks)
    }


# ==================== TEMPLATES ====================

@router.get("/templates")
def get_approval_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pre-built approval chain templates"""
    templates = [
        {
            "id": "loan_approval_standard",
            "name": "Standard Loan Approval",
            "description": "Multi-level loan approval with conditional routing",
            "type": "sequential",
            "levels": 3
        },
        {
            "id": "parallel_approval_all_teams",
            "name": "Parallel Approval - All Teams",
            "description": "Risk, Legal, Finance must all approve",
            "type": "parallel",
            "levels": 3
        },
        {
            "id": "any_one_regional_manager",
            "name": "Any Regional Manager",
            "description": "Any one regional manager can approve",
            "type": "any_one",
            "levels": 1
        },
        {
            "id": "maker_checker_simple",
            "name": "Maker-Checker",
            "description": "Simple maker-checker with no self-approval",
            "type": "maker_checker",
            "levels": 1
        }
    ]
    
    return {
        "success": True,
        "templates": templates
    }
