"""
Insurance Commission Router

API endpoints for commission tracking including:
- Commission calculation and tracking
- Approval and payment workflow
- Agent commission reports
- Batch commission calculation
- Statistics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.insurance.commission_service import CommissionService
from backend.services.insurance.schemas import (
    InsuranceCommissionCreate,
    InsuranceCommissionResponse,
    InsuranceCommissionApproval,
    InsuranceCommissionPayment,
    CommissionFilter,
    CommissionStatistics,
    CommissionStatus,
    BatchCommissionCalculation
)

router = APIRouter(prefix="/insurance/commissions", tags=["Insurance - Commissions"])


# ==================== CRUD OPERATIONS ====================

@router.post("", response_model=dict, status_code=201)
async def create_commission(
    commission_data: InsuranceCommissionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create new commission entry
    
    - **policy_id**: Policy UUID
    - **agent_id**: Agent UUID
    - **commission_type**: first_year, renewal, performance
    - **base_amount**: Amount on which commission is calculated
    - **commission_rate**: Commission percentage
    
    Automatically calculates TDS and net payable
    Returns created commission with generated commission number
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.create_commission(commission_data.dict())
    
    return success_response(
        message="Commission created successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


@router.get("", response_model=dict)
async def list_commissions(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    agent_id: Optional[uuid.UUID] = Query(None, description="Filter by agent"),
    commission_status: Optional[CommissionStatus] = Query(None, description="Filter by status"),
    commission_type: Optional[str] = Query(None, description="first_year, renewal, performance"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List all commissions with optional filters
    
    - **policy_id**: Filter by specific policy
    - **agent_id**: Filter by specific agent
    - **commission_status**: pending, approved, paid, cancelled
    - **commission_type**: first_year, renewal, performance
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commissions = service.list_commissions(
        policy_id=policy_id,
        agent_id=agent_id,
        commission_status=commission_status,
        commission_type=commission_type,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(commissions)} commissions",
        data={
            "commissions": [InsuranceCommissionResponse.from_orm(c).dict() for c in commissions],
            "total": len(commissions),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{commission_id}", response_model=dict)
async def get_commission(
    commission_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get commission by ID"""
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.get_commission(commission_id)
    
    return success_response(
        message="Commission retrieved successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


@router.get("/number/{commission_number}", response_model=dict)
async def get_commission_by_number(
    commission_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get commission by commission number"""
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.get_commission_by_number(commission_number)
    
    return success_response(
        message="Commission retrieved successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


# ==================== WORKFLOW OPERATIONS ====================

@router.post("/{commission_id}/approve", response_model=dict)
async def approve_commission(
    commission_id: uuid.UUID,
    approval_data: InsuranceCommissionApproval,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Approve commission for payment
    
    - **approved_by**: Approver UUID
    - **approval_remarks**: Approval notes
    
    Only pending or calculated commissions can be approved
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.approve_commission(commission_id, approval_data.dict())
    
    return success_response(
        message="Commission approved successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


@router.post("/{commission_id}/pay", response_model=dict)
async def pay_commission(
    commission_id: uuid.UUID,
    payment_data: InsuranceCommissionPayment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Record commission payment
    
    - **payment_method**: cheque, neft, rtgs, cash
    - **payment_reference**: Payment reference number
    - **paid_amount**: Amount paid
    
    Only approved commissions can be paid
    Updates agent statistics
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.pay_commission(commission_id, payment_data.dict())
    
    return success_response(
        message="Commission paid successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


@router.post("/{commission_id}/cancel", response_model=dict)
async def cancel_commission(
    commission_id: uuid.UUID,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Cancel commission
    
    Cannot cancel paid commissions
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.cancel_commission(commission_id, reason)
    
    return success_response(
        message="Commission cancelled successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


# ==================== CALCULATION OPERATIONS ====================

@router.post("/calculate/first-year", response_model=dict)
async def calculate_first_year_commission(
    policy_id: uuid.UUID = Query(..., description="Policy UUID"),
    agent_id: uuid.UUID = Query(..., description="Agent UUID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Calculate first year commission for new policy
    
    Commission is calculated on annual premium amount
    Uses agent's default commission rate
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.calculate_first_year_commission(policy_id, agent_id)
    
    return success_response(
        message="First year commission calculated successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


@router.post("/calculate/renewal", response_model=dict)
async def calculate_renewal_commission(
    premium_id: uuid.UUID = Query(..., description="Premium UUID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Calculate renewal commission for premium payment
    
    Commission is calculated on premium amount
    Renewal rate is typically lower than first year
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    commission = service.calculate_renewal_commission(premium_id)
    
    return success_response(
        message="Renewal commission calculated successfully",
        data=InsuranceCommissionResponse.from_orm(commission).dict()
    )


# ==================== BATCH OPERATIONS ====================

@router.post("/batch/calculate", response_model=dict)
async def batch_calculate_commissions(
    batch_data: BatchCommissionCalculation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Calculate commissions for all eligible agents in a period
    
    - **calculation_period**: Q1-2024 or Jan-2024
    - **commission_type**: first_year, renewal, performance
    - **agent_ids**: Optional list of agent UUIDs (if None, all agents)
    
    This is typically run as a scheduled job
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    result = service.calculate_commissions_for_period(
        batch_data.calculation_period,
        batch_data.commission_type,
        batch_data.agent_ids
    )
    
    return success_response(
        message=f"Generated {result['generated']} commissions",
        data=result
    )


# ==================== STATISTICS ====================

@router.get("/stats/summary", response_model=dict)
async def get_commission_statistics(
    agent_id: Optional[uuid.UUID] = Query(None, description="Filter by agent"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get comprehensive commission statistics
    
    Returns:
    - Total commissions by status and type
    - Commission amounts (total, paid, outstanding)
    - Top performing agents
    
    Can be filtered by specific agent
    """
    service = CommissionService(db, tenant_id, current_user["id"])
    stats = service.get_commission_statistics(agent_id=agent_id)
    
    return success_response(
        message="Commission statistics retrieved successfully",
        data=stats
    )
