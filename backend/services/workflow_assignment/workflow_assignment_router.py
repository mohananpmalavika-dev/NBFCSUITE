"""
Workflow Assignment API Router
RESTful API endpoints for workflow assignment management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from .workflow_assignment_models import (
    WorkflowAssignment, WorkflowAssignmentFilter, WorkflowAssignmentStats,
    WorkflowAssignmentClone, AssignmentStatus, ApprovalRouting, StageAssignment
)
from .workflow_assignment_service import workflow_assignment_service

# Create router
router = APIRouter(prefix="/workflow-assignments", tags=["Workflow Assignments"])


# ============================================================================
# AUTHENTICATION & TENANT HELPERS
# ============================================================================

async def get_current_user():
    """Get current authenticated user"""
    return {"user_id": "USER001", "tenant_id": "TENANT001"}


async def get_tenant_id(user: dict = Depends(get_current_user)) -> str:
    """Extract tenant ID"""
    return user["tenant_id"]


async def get_user_id(user: dict = Depends(get_current_user)) -> str:
    """Extract user ID"""
    return user["user_id"]


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=WorkflowAssignment, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Create new workflow assignment
    
    **Parameters:**
    - assignment_data: Workflow assignment configuration
    
    **Returns:**
    - Created workflow assignment
    """
    try:
        assignment = workflow_assignment_service.create_assignment(assignment_data, tenant_id, user_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create assignment: {str(e)}")


@router.get("/", response_model=List[WorkflowAssignment])
async def list_assignments(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[AssignmentStatus] = None,
    product_id: Optional[str] = None,
    product_code: Optional[str] = None,
    workflow_template_id: Optional[str] = None,
    search_term: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List workflow assignments with filters
    
    **Query Parameters:**
    - status: Filter by assignment status
    - product_id: Filter by product ID
    - product_code: Filter by product code
    - workflow_template_id: Filter by workflow template
    - search_term: Search in code, name, description
    - skip: Number of records to skip
    - limit: Maximum records to return
    
    **Returns:**
    - List of workflow assignments
    """
    try:
        filters = WorkflowAssignmentFilter(
            status=status,
            product_id=product_id,
            product_code=product_code,
            workflow_template_id=workflow_template_id,
            search_term=search_term
        )
        assignments = workflow_assignment_service.list_assignments(tenant_id, filters, skip, limit)
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list assignments: {str(e)}")


@router.get("/{assignment_id}", response_model=WorkflowAssignment)
async def get_assignment(
    assignment_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get assignment by ID
    
    **Parameters:**
    - assignment_id: Assignment ID
    
    **Returns:**
    - Workflow assignment details
    """
    try:
        assignment = workflow_assignment_service.get_assignment(assignment_id, tenant_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assignment: {str(e)}")


@router.put("/{assignment_id}", response_model=WorkflowAssignment)
async def update_assignment(
    assignment_id: str,
    assignment_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Update workflow assignment
    
    **Parameters:**
    - assignment_id: Assignment ID
    - assignment_data: Updated assignment data
    
    **Returns:**
    - Updated assignment
    """
    try:
        assignment = workflow_assignment_service.update_assignment(assignment_id, assignment_data, tenant_id, user_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update assignment: {str(e)}")


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete workflow assignment
    
    **Parameters:**
    - assignment_id: Assignment ID
    
    **Returns:**
    - 204 No Content
    """
    try:
        workflow_assignment_service.delete_assignment(assignment_id, tenant_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete assignment: {str(e)}")


# ============================================================================
# ASSIGNMENT OPERATIONS
# ============================================================================

@router.post("/{assignment_id}/clone", response_model=WorkflowAssignment, status_code=status.HTTP_201_CREATED)
async def clone_assignment(
    assignment_id: str,
    clone_data: WorkflowAssignmentClone,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Clone workflow assignment
    
    **Parameters:**
    - assignment_id: Assignment ID to clone
    - clone_data: Clone configuration
    
    **Returns:**
    - Cloned assignment
    """
    try:
        assignment = workflow_assignment_service.clone_assignment(assignment_id, clone_data, tenant_id, user_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone assignment: {str(e)}")


@router.post("/{assignment_id}/activate", response_model=WorkflowAssignment)
async def activate_assignment(
    assignment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Activate assignment
    
    **Parameters:**
    - assignment_id: Assignment ID
    
    **Returns:**
    - Activated assignment
    """
    try:
        assignment = workflow_assignment_service.activate_assignment(assignment_id, tenant_id, user_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate assignment: {str(e)}")


@router.post("/{assignment_id}/deactivate", response_model=WorkflowAssignment)
async def deactivate_assignment(
    assignment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Deactivate assignment
    
    **Parameters:**
    - assignment_id: Assignment ID
    
    **Returns:**
    - Deactivated assignment
    """
    try:
        assignment = workflow_assignment_service.deactivate_assignment(assignment_id, tenant_id, user_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate assignment: {str(e)}")


# ============================================================================
# APPROVAL ROUTING
# ============================================================================

@router.get("/{assignment_id}/routing", response_model=ApprovalRouting)
async def get_approval_routing(
    assignment_id: str,
    loan_amount: float = Query(..., ge=0),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get approval routing for loan amount
    
    **Parameters:**
    - assignment_id: Assignment ID
    - loan_amount: Loan amount to route
    
    **Returns:**
    - Approval routing with required approvers and committees
    """
    try:
        routing = workflow_assignment_service.get_approval_routing(assignment_id, loan_amount, tenant_id)
        return routing
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get routing: {str(e)}")


@router.get("/{assignment_id}/stage-assignments", response_model=List[StageAssignment])
async def get_stage_assignments(
    assignment_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get stage assignments
    
    **Parameters:**
    - assignment_id: Assignment ID
    
    **Returns:**
    - List of stage assignments with roles and SLA
    """
    try:
        assignments = workflow_assignment_service.get_stage_assignments(assignment_id, tenant_id)
        return assignments
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stage assignments: {str(e)}")


# ============================================================================
# STATISTICS & UTILITIES
# ============================================================================

@router.get("/stats/summary", response_model=WorkflowAssignmentStats)
async def get_stats(
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get workflow assignment statistics
    
    **Returns:**
    - Statistics including total assignments, avg stages, etc.
    """
    try:
        stats = workflow_assignment_service.get_stats(tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/validation/validate", response_model=dict)
async def validate_assignment_data(assignment_data: dict):
    """
    Validate assignment data
    
    **Parameters:**
    - assignment_data: Assignment data to validate
    
    **Returns:**
    - Validation result with errors and warnings
    """
    try:
        validation = workflow_assignment_service.validate_assignment_data(assignment_data)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate: {str(e)}")


@router.get("/validation/check-code/{assignment_code}", response_model=dict)
async def check_assignment_code(
    assignment_code: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Check if assignment code is available
    
    **Parameters:**
    - assignment_code: Assignment code to check
    
    **Returns:**
    - Availability status
    """
    try:
        exists = any(
            a.assignment_code == assignment_code 
            for a in workflow_assignment_service.assignments_storage.values() 
            if a.tenant_id == tenant_id
        )
        
        return {
            "available": not exists,
            "message": f"Assignment code '{assignment_code}' is {'already in use' if exists else 'available'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check code: {str(e)}")
