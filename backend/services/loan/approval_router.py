"""
Loan Approval Router
API endpoints for approval workflow management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from backend.shared.database.connection import get_db
from .approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["Loan Approvals"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ApproveRequest(BaseModel):
    comments: Optional[str] = Field(None, max_length=1000)
    conditions: Optional[List[str]] = None
    approved_amount: Optional[Decimal] = Field(None, gt=0)


class RejectRequest(BaseModel):
    rejection_reason: str = Field(..., min_length=10, max_length=500)
    comments: Optional[str] = Field(None, max_length=1000)


class ReturnRequest(BaseModel):
    return_reason: str = Field(..., min_length=10, max_length=500)
    comments: Optional[str] = Field(None, max_length=1000)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_approval_service(db: Session = Depends(get_db)) -> ApprovalService:
    """Dependency to get approval service"""
    # TODO: Get tenant_id from authenticated user context
    tenant_id = 1  # Hardcoded for now
    return ApprovalService(db, tenant_id)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/pending", summary="Get pending approvals")
async def get_pending_approvals(
    approver_role: Optional[str] = Query(
        None,
        description="Filter by role: credit_officer, manager, senior_manager"
    ),
    approver_id: Optional[int] = Query(None, description="Filter by specific approver"),
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Get all pending applications requiring approval
    
    - Filter by approver role (credit_officer, manager, senior_manager)
    - Filter by specific approver ID
    - Returns applications where previous levels are approved
    - Includes application details, credit score, risk rating
    """
    try:
        pending = service.get_pending_approvals(
            approver_role=approver_role,
            approver_id=approver_id
        )
        
        return {
            "success": True,
            "data": {
                "pending_approvals": pending,
                "total": len(pending)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pending approvals: {str(e)}"
        )


@router.get("/stats", summary="Get approval statistics")
async def get_approval_stats(
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Get approval workflow statistics
    
    Returns:
    - Pending approvals by level
    - Total approved/rejected/returned
    - Approval rate
    """
    try:
        stats = service.get_approval_statistics()
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch approval stats: {str(e)}"
        )


@router.post("/applications/{application_id}/create-workflow", summary="Create approval workflow")
async def create_approval_workflow(
    application_id: int,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Create approval workflow for application
    
    - Determines required approval levels based on loan amount
    - Creates workflow records for each level
    - Updates application status to pending_approval
    
    Approval levels:
    - Level 1 (Credit Officer): Up to ₹5 lakhs
    - Level 2 (Manager): ₹5 lakhs to ₹25 lakhs  
    - Level 3 (Senior Manager): Above ₹25 lakhs
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        
        workflows = service.create_approval_workflow(application_id, user_id)
        
        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "workflows_created": len(workflows),
                "levels": [
                    {
                        "level": w.approval_level,
                        "role": w.approver_role,
                        "status": w.status,
                        "max_amount": float(w.max_approval_amount) if w.max_approval_amount else None
                    }
                    for w in workflows
                ],
                "message": f"Approval workflow created with {len(workflows)} level(s)"
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.post("/applications/{application_id}/auto-move-to-approval", summary="Auto assess and move to approval")
async def auto_move_to_approval(
    application_id: int,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Automatically assess application and create approval workflow
    
    This endpoint combines:
    1. Credit scoring assessment
    2. Risk rating determination
    3. Approval workflow creation
    
    Use this after application submission for automatic processing
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        
        result = service.auto_move_to_approval(application_id, user_id)
        
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process application: {str(e)}"
        )


@router.post("/{workflow_id}/approve", summary="Approve application")
async def approve_application(
    workflow_id: int,
    request: ApproveRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Approve application at current workflow level
    
    - Requires previous levels to be approved (if any)
    - Can specify conditions for approval
    - Can approve different amount than requested
    - If all levels approved, moves application to approved status
    
    Request body:
    - comments: Optional approval comments
    - conditions: Optional list of approval conditions
    - approved_amount: Optional different amount (if not provided, uses requested amount)
    """
    try:
        # TODO: Get approver_id from authenticated user
        approver_id = 1
        
        workflow = service.approve_application(
            workflow_id=workflow_id,
            approver_id=approver_id,
            comments=request.comments,
            conditions=request.conditions,
            approved_amount=request.approved_amount
        )
        
        application = workflow.application
        
        return {
            "success": True,
            "data": {
                "workflow_id": workflow.id,
                "application_id": application.id,
                "application_number": application.application_number,
                "status": workflow.status,
                "decision": workflow.decision,
                "approval_level": workflow.approval_level,
                "application_status": application.status,
                "approved_amount": float(application.approved_amount) if application.approved_amount else None,
                "message": (
                    "Application fully approved and ready for disbursement"
                    if application.status == "approved"
                    else f"Level {workflow.approval_level} approved, awaiting next level"
                )
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve application: {str(e)}"
        )


@router.post("/{workflow_id}/reject", summary="Reject application")
async def reject_application(
    workflow_id: int,
    request: RejectRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Reject application
    
    - Rejection at any level stops the entire workflow
    - All pending workflow levels are cancelled
    - Application status changed to rejected
    - Rejection reason is mandatory
    
    Request body:
    - rejection_reason: Reason for rejection (required, 10-500 chars)
    - comments: Additional comments (optional)
    """
    try:
        # TODO: Get approver_id from authenticated user
        approver_id = 1
        
        workflow = service.reject_application(
            workflow_id=workflow_id,
            approver_id=approver_id,
            rejection_reason=request.rejection_reason,
            comments=request.comments
        )
        
        application = workflow.application
        
        return {
            "success": True,
            "data": {
                "workflow_id": workflow.id,
                "application_id": application.id,
                "application_number": application.application_number,
                "status": workflow.status,
                "decision": workflow.decision,
                "rejection_level": workflow.approval_level,
                "rejection_reason": application.rejection_reason,
                "rejection_date": application.rejection_date.isoformat() if application.rejection_date else None,
                "message": f"Application rejected at level {workflow.approval_level}"
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject application: {str(e)}"
        )


@router.post("/{workflow_id}/return", summary="Return application for clarification")
async def return_application(
    workflow_id: int,
    request: ReturnRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Return application to applicant for more information
    
    - Application status changed to under_review
    - Workflow remains in returned state
    - Applicant can resubmit with additional information
    
    Request body:
    - return_reason: Reason for returning (required, 10-500 chars)
    - comments: Additional comments (optional)
    """
    try:
        # TODO: Get approver_id from authenticated user
        approver_id = 1
        
        workflow = service.return_application(
            workflow_id=workflow_id,
            approver_id=approver_id,
            return_reason=request.return_reason,
            comments=request.comments
        )
        
        application = workflow.application
        
        return {
            "success": True,
            "data": {
                "workflow_id": workflow.id,
                "application_id": application.id,
                "application_number": application.application_number,
                "status": workflow.status,
                "decision": workflow.decision,
                "return_reason": application.status_reason,
                "message": "Application returned for clarification"
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to return application: {str(e)}"
        )


@router.get("/applications/{application_id}/history", summary="Get approval history")
async def get_approval_history(
    application_id: int,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Get complete approval history for application
    
    Returns all workflow records with:
    - Approval level
    - Approver role and ID
    - Status and decision
    - Action date
    - Comments and conditions
    """
    try:
        history = service.get_approval_history(application_id)
        
        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "approval_history": history,
                "total_levels": len(history)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch approval history: {str(e)}"
        )


@router.get("/my-queue", summary="Get my approval queue")
async def get_my_approval_queue(
    approver_id: int = Query(..., description="Your user ID"),
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Get approval queue for specific approver
    
    Returns all pending applications assigned to you
    """
    try:
        pending = service.get_pending_approvals(approver_id=approver_id)
        
        return {
            "success": True,
            "data": {
                "approver_id": approver_id,
                "pending_approvals": pending,
                "total": len(pending)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch your queue: {str(e)}"
        )
