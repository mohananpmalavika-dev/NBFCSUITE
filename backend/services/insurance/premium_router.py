"""
Insurance Premium Router

API endpoints for premium collection including:
- Premium listing and tracking
- Payment recording
- Due and overdue premium management
- Waiver and discount operations
- Batch operations
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
from backend.services.insurance.premium_service import PremiumService
from backend.services.insurance.schemas import (
    InsurancePremiumResponse,
    InsurancePremiumPayment,
    PremiumFilter,
    PremiumStatistics,
    PremiumStatus,
    PremiumFrequency,
    BatchPremiumGeneration
)

router = APIRouter(prefix="/insurance/premiums", tags=["Insurance - Premiums"])


# ==================== LISTING & TRACKING ====================

@router.get("", response_model=dict)
async def list_premiums(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    premium_status: Optional[PremiumStatus] = Query(None, description="Filter by status"),
    from_due_date: Optional[datetime] = Query(None, description="From due date"),
    to_due_date: Optional[datetime] = Query(None, description="To due date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List all premiums with optional filters
    
    - **policy_id**: Filter by specific policy
    - **premium_status**: due, paid, overdue, waived
    - **from_due_date**: Start date filter
    - **to_due_date**: End date filter
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    premiums = service.list_premiums(
        policy_id=policy_id,
        premium_status=premium_status,
        from_due_date=from_due_date,
        to_due_date=to_due_date,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(premiums)} premiums",
        data={
            "premiums": [InsurancePremiumResponse.from_orm(p).dict() for p in premiums],
            "total": len(premiums),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{premium_id}", response_model=dict)
async def get_premium(
    premium_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get premium by ID"""
    service = PremiumService(db, tenant_id, current_user["id"])
    premium = service.get_premium(premium_id)
    
    return success_response(
        message="Premium retrieved successfully",
        data=InsurancePremiumResponse.from_orm(premium).dict()
    )


@router.get("/number/{premium_number}", response_model=dict)
async def get_premium_by_number(
    premium_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get premium by premium number"""
    service = PremiumService(db, tenant_id, current_user["id"])
    premium = service.get_premium_by_number(premium_number)
    
    return success_response(
        message="Premium retrieved successfully",
        data=InsurancePremiumResponse.from_orm(premium).dict()
    )


# ==================== PAYMENT OPERATIONS ====================

@router.post("/{premium_id}/pay", response_model=dict)
async def record_payment(
    premium_id: uuid.UUID,
    payment_data: InsurancePremiumPayment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Record premium payment
    
    - **payment_date**: Date of payment
    - **payment_amount**: Amount paid
    - **payment_method**: cash, cheque, online, etc.
    - **payment_reference**: Transaction reference
    
    Automatically calculates late fee if payment is after grace period
    Updates policy financial tracking
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    premium = service.record_payment(premium_id, payment_data.dict())
    
    return success_response(
        message="Premium payment recorded successfully",
        data=InsurancePremiumResponse.from_orm(premium).dict()
    )


@router.post("/{premium_id}/waive", response_model=dict)
async def waive_premium(
    premium_id: uuid.UUID,
    waived_amount: float = Query(..., description="Amount to waive"),
    waived_reason: str = Query(..., description="Reason for waiver"),
    remarks: Optional[str] = Query(None, description="Additional remarks"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Waive premium payment
    
    Requires proper authorization
    Updates policy outstanding amount
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    premium = service.waive_premium(premium_id, {
        "waived_amount": waived_amount,
        "waived_reason": waived_reason,
        "remarks": remarks
    })
    
    return success_response(
        message="Premium waived successfully",
        data=InsurancePremiumResponse.from_orm(premium).dict()
    )


@router.post("/{premium_id}/discount", response_model=dict)
async def apply_discount(
    premium_id: uuid.UUID,
    discount_amount: float = Query(..., description="Discount amount"),
    discount_reason: str = Query(..., description="Reason for discount"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Apply discount to premium
    
    Customer will pay (premium_amount - discount_amount)
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    premium = service.apply_discount(premium_id, {
        "discount_amount": discount_amount,
        "discount_reason": discount_reason
    })
    
    return success_response(
        message="Discount applied successfully",
        data=InsurancePremiumResponse.from_orm(premium).dict()
    )


# ==================== DUE PREMIUM TRACKING ====================

@router.get("/status/due", response_model=dict)
async def get_due_premiums(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    include_overdue: bool = Query(True, description="Include overdue premiums"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all due premiums
    
    - **include_overdue**: Include overdue premiums in results
    - **policy_id**: Filter by specific policy
    
    Returns premiums that need to be collected
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    premiums = service.get_due_premiums(
        policy_id=policy_id,
        include_overdue=include_overdue,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(premiums)} due premiums",
        data={
            "premiums": [InsurancePremiumResponse.from_orm(p).dict() for p in premiums],
            "total": len(premiums),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/status/overdue", response_model=dict)
async def get_overdue_premiums(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all overdue premiums (past grace period)
    
    These premiums require immediate attention
    Policy may be at risk of lapse
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    premiums = service.get_overdue_premiums(
        policy_id=policy_id,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(premiums)} overdue premiums",
        data={
            "premiums": [InsurancePremiumResponse.from_orm(p).dict() for p in premiums],
            "total": len(premiums),
            "skip": skip,
            "limit": limit
        }
    )


@router.post("/batch/mark-overdue", response_model=dict)
async def mark_overdue_premiums(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Mark all eligible premiums as overdue (batch operation)
    
    This is typically run as a scheduled job
    Updates status from DUE to OVERDUE for premiums past grace period
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    count = service.mark_overdue_premiums()
    
    return success_response(
        message=f"Marked {count} premiums as overdue",
        data={"count": count}
    )


# ==================== BATCH OPERATIONS ====================

@router.post("/batch/generate", response_model=dict)
async def generate_premiums(
    batch_data: BatchPremiumGeneration,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Generate premium entries for all eligible policies
    
    - **generation_date**: Date for which to generate premiums
    - **frequency**: monthly, quarterly, annually, etc.
    
    This is typically run as a scheduled job to create premium entries
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    result = service.generate_premiums_for_period(
        batch_data.generation_date,
        batch_data.frequency
    )
    
    return success_response(
        message=f"Generated {result['generated']} premiums out of {result['total_policies']} policies",
        data=result
    )


# ==================== STATISTICS ====================

@router.get("/stats/summary", response_model=dict)
async def get_premium_statistics(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get comprehensive premium statistics
    
    Returns:
    - Total premiums (paid, due, overdue)
    - Collection amounts and rates
    - Outstanding amounts
    
    Can be filtered by specific policy
    """
    service = PremiumService(db, tenant_id, current_user["id"])
    stats = service.get_premium_statistics(policy_id=policy_id)
    
    return success_response(
        message="Premium statistics retrieved successfully",
        data=stats
    )
