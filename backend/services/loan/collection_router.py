"""
Loan Collection Router
API endpoints for collection management and overdue tracking
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.loan.collection_service import LoanCollectionService


router = APIRouter(prefix="/collection", tags=["Loan Collection"])


def get_collection_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> LoanCollectionService:
    """Dependency to get collection service"""
    return LoanCollectionService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"]
    )


@router.post("/update-overdue-status", response_model=dict)
async def update_overdue_status(
    account_id: Optional[int] = None,
    service: LoanCollectionService = Depends(get_collection_service)
):
    """
    Update overdue status for all or specific loan accounts
    Calculates overdue days, penal interest, and DPD
    """
    try:
        result = await service.update_overdue_status(account_id=account_id)
        
        return success_response(
            data=result,
            message="Overdue status updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overdue-accounts", response_model=dict)
async def get_overdue_accounts(
    dpd_bucket: Optional[str] = Query(
        None,
        regex="^(current|bucket_1_30|bucket_31_60|bucket_61_90|bucket_91_180|bucket_180_plus)$"
    ),
    min_overdue_amount: Optional[Decimal] = None,
    customer_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: LoanCollectionService = Depends(get_collection_service)
):
    """Get list of overdue loan accounts with filters"""
    try:
        skip = (page - 1) * page_size
        result = await service.get_overdue_accounts(
            dpd_bucket=dpd_bucket,
            min_overdue_amount=min_overdue_amount,
            customer_id=customer_id,
            skip=skip,
            limit=page_size
        )
        
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection-queue", response_model=dict)
async def get_collection_queue(
    priority: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    service: LoanCollectionService = Depends(get_collection_service)
):
    """
    Get collection queue with prioritization
    Priority: High (DPD > 60), Medium (DPD 30-60), Low (DPD < 30)
    """
    try:
        queue = await service.get_collection_queue(priority=priority)
        
        return success_response(data=queue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=dict)
async def get_collection_statistics(
    service: LoanCollectionService = Depends(get_collection_service)
):
    """Get collection statistics and metrics"""
    try:
        stats = await service.get_collection_statistics()
        
        return success_response(data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
