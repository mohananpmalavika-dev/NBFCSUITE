"""
Insurance Policy Router

API endpoints for policy management including:
- CRUD operations
- Policy lifecycle management
- Premium schedule generation
- Statistics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.insurance.policy_service import PolicyService
from backend.services.insurance.schemas import (
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsurancePolicyResponse,
    PolicyFilter,
    PolicyStatistics,
    PolicyStatus,
    PolicyType
)

router = APIRouter(prefix="/insurance/policies", tags=["Insurance - Policies"])


# ==================== CRUD OPERATIONS ====================

@router.post("", response_model=dict, status_code=201)
async def create_policy(
    policy_data: InsurancePolicyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create new insurance policy
    
    - **customer_id**: Customer UUID
    - **policy_type**: life, health, general, motor, etc.
    - **sum_assured**: Total insured amount
    - **premium_amount**: Premium amount per frequency
    - **premium_frequency**: monthly, quarterly, annually, etc.
    
    Returns created policy with generated policy number
    """
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.create_policy(policy_data.dict())
    
    return success_response(
        message="Insurance policy created successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.get("", response_model=dict)
async def list_policies(
    policy_type: Optional[PolicyType] = Query(None, description="Filter by policy type"),
    policy_status: Optional[PolicyStatus] = Query(None, description="Filter by status"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer"),
    agent_id: Optional[uuid.UUID] = Query(None, description="Filter by agent"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List all insurance policies with optional filters
    
    - **policy_type**: Filter by type
    - **policy_status**: Filter by status
    - **customer_id**: Get policies for specific customer
    - **agent_id**: Get policies for specific agent
    """
    service = PolicyService(db, tenant_id, current_user["id"])
    policies = service.list_policies(
        policy_type=policy_type,
        policy_status=policy_status,
        customer_id=customer_id,
        agent_id=agent_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(policies)} policies",
        data={
            "policies": [InsurancePolicyResponse.from_orm(p).dict() for p in policies],
            "total": len(policies),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{policy_id}", response_model=dict)
async def get_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get policy by ID"""
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.get_policy(policy_id)
    
    return success_response(
        message="Policy retrieved successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.get("/number/{policy_number}", response_model=dict)
async def get_policy_by_number(
    policy_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get policy by policy number"""
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.get_policy_by_number(policy_number)
    
    return success_response(
        message="Policy retrieved successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.patch("/{policy_id}", response_model=dict)
async def update_policy(
    policy_id: uuid.UUID,
    policy_data: InsurancePolicyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update policy information"""
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.update_policy(policy_id, policy_data.dict(exclude_unset=True))
    
    return success_response(
        message="Policy updated successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.delete("/{policy_id}", response_model=dict)
async def delete_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete policy (soft delete)"""
    service = PolicyService(db, tenant_id, current_user["id"])
    service.delete_policy(policy_id)
    
    return success_response(message="Policy deleted successfully")


# ==================== LIFECYCLE OPERATIONS ====================

@router.post("/{policy_id}/activate", response_model=dict)
async def activate_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Activate a draft policy
    
    This will:
    - Change status from DRAFT to ACTIVE
    - Generate premium payment schedule
    - Make policy effective
    """
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.activate_policy(policy_id)
    
    return success_response(
        message="Policy activated successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.post("/{policy_id}/lapse", response_model=dict)
async def lapse_policy(
    policy_id: uuid.UUID,
    reason: Optional[str] = Query(None, description="Reason for lapse"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Mark policy as lapsed due to non-payment"""
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.lapse_policy(policy_id, reason)
    
    return success_response(
        message="Policy marked as lapsed",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.post("/{policy_id}/revive", response_model=dict)
async def revive_policy(
    policy_id: uuid.UUID,
    arrear_amount: float = Query(..., description="Arrear premium amount to be paid"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Revive a lapsed policy by paying arrear premiums"""
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.revive_policy(policy_id, {"arrear_amount": arrear_amount})
    
    return success_response(
        message="Policy revived successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.post("/{policy_id}/surrender", response_model=dict)
async def surrender_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Surrender policy before maturity
    
    Returns surrender value based on policy terms
    """
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.surrender_policy(policy_id, {})
    
    return success_response(
        message="Policy surrendered successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


@router.post("/{policy_id}/mature", response_model=dict)
async def mature_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Mark policy as matured and calculate maturity value"""
    service = PolicyService(db, tenant_id, current_user["id"])
    policy = service.mature_policy(policy_id)
    
    return success_response(
        message="Policy matured successfully",
        data=InsurancePolicyResponse.from_orm(policy).dict()
    )


# ==================== STATISTICS ====================

@router.get("/stats/summary", response_model=dict)
async def get_policy_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get comprehensive policy statistics
    
    Returns:
    - Total policies, active, lapsed, matured
    - Sum assured totals
    - Premium collection status
    - Policies by type and status
    """
    service = PolicyService(db, tenant_id, current_user["id"])
    stats = service.get_policy_statistics()
    
    return success_response(
        message="Policy statistics retrieved successfully",
        data=stats
    )
