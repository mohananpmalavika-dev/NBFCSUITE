"""
Workflow Integration Router

API endpoints for workflow integration with NBFC modules
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.shared.database.connection import get_db
from backend.shared.common.dependencies import get_current_user
from backend.shared.database.models import User
from backend.services.workflow.integrations import WorkflowIntegration

router = APIRouter(prefix="/api/v1/workflow/integrations", tags=["Workflow Integrations"])


# ==================== REQUEST SCHEMAS ====================

class StartLoanWorkflowRequest(BaseModel):
    """Request to start loan approval workflow"""
    loan_application_id: int
    loan_amount: float
    customer_id: int
    priority: str = "normal"


class StartDepositWorkflowRequest(BaseModel):
    """Request to start deposit approval workflow"""
    account_id: int
    customer_id: int
    customer_email: str
    priority: str = "normal"


class StartKYCWorkflowRequest(BaseModel):
    """Request to start KYC verification workflow"""
    customer_id: int
    priority: str = "high"


class StartCustomWorkflowRequest(BaseModel):
    """Request to start custom workflow"""
    workflow_code: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    variables: Optional[dict] = None
    priority: str = "normal"


class CancelEntityWorkflowsRequest(BaseModel):
    """Request to cancel entity workflows"""
    entity_type: str
    entity_id: int
    reason: str


# ==================== LOAN MODULE ENDPOINTS ====================

@router.post("/loan/start-approval")
def start_loan_approval(
    request: StartLoanWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start loan approval workflow"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    result = integration.start_loan_approval_workflow(
        loan_application_id=request.loan_application_id,
        loan_amount=request.loan_amount,
        customer_id=request.customer_id,
        priority=request.priority
    )
    
    return result


@router.get("/loan/{loan_application_id}/status")
def get_loan_workflow_status(
    loan_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow status for loan application"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    status = integration.get_loan_workflow_status(loan_application_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="No workflow found for this loan")
    
    return {
        "success": True,
        "workflow": status
    }


# ==================== DEPOSIT MODULE ENDPOINTS ====================

@router.post("/deposit/start-approval")
def start_deposit_approval(
    request: StartDepositWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start deposit account approval workflow"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    result = integration.start_deposit_approval_workflow(
        account_id=request.account_id,
        customer_id=request.customer_id,
        customer_email=request.customer_email,
        priority=request.priority
    )
    
    return result


# ==================== CUSTOMER MODULE ENDPOINTS ====================

@router.post("/customer/start-kyc")
def start_kyc_verification(
    request: StartKYCWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start KYC verification workflow"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    result = integration.start_kyc_verification_workflow(
        customer_id=request.customer_id,
        priority=request.priority
    )
    
    return result


# ==================== GENERIC ENDPOINTS ====================

@router.post("/custom/start")
def start_custom_workflow(
    request: StartCustomWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start any custom workflow"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    result = integration.start_custom_workflow(
        workflow_code=request.workflow_code,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        variables=request.variables,
        priority=request.priority
    )
    
    return result


@router.get("/entity/{entity_type}/{entity_id}")
def get_entity_workflows(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all workflows for a specific entity"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    workflows = integration.get_entity_workflows(entity_type, entity_id)
    
    return {
        "success": True,
        "workflows": workflows,
        "total": len(workflows)
    }


@router.post("/entity/cancel")
def cancel_entity_workflows(
    request: CancelEntityWorkflowsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel all active workflows for an entity"""
    integration = WorkflowIntegration(db, current_user.tenant_id, current_user.id)
    
    result = integration.cancel_entity_workflows(
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        reason=request.reason
    )
    
    return result
