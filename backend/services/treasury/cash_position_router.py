"""
Treasury Cash Position - API Router
REST API endpoints for cash position management
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .cash_position_service import CashPositionService
from .cash_position_schemas import (
    CashPositionCreate,
    CashPositionUpdate,
    CashPositionResponse,
    CashPositionListResponse,
    CashPositionStatistics,
    BranchCashSummary,
    CashMovementSummary,
    CashAlertResponse,
    BulkCashPositionCreate,
    BulkCashPositionResponse,
    DenominationBreakup
)


router = APIRouter(prefix="/cash-position", tags=["Treasury - Cash Position"])


# ============================================
# CRUD Endpoints
# ============================================

@router.post("/", response_model=CashPositionResponse, status_code=status.HTTP_201_CREATED)
async def create_cash_position(
    data: CashPositionCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new cash position record
    
    Records daily cash position including:
    - Opening and closing balances
    - Cash received and paid
    - Bank deposits and withdrawals
    - Denomination breakup
    """
    service = CashPositionService(db, tenant_id)
    position = await service.create_cash_position(data, current_user["id"])
    return position


@router.get("/{position_id}", response_model=CashPositionResponse)
async def get_cash_position(
    position_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cash position by ID
    
    Returns complete cash position details including:
    - All transactions
    - Denomination details
    - Verification status
    """
    service = CashPositionService(db, tenant_id)
    position = await service.get_cash_position(position_id)
    return position


@router.get("/", response_model=CashPositionListResponse)
async def list_cash_positions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    status: Optional[str] = Query(None, description="Filter by status (draft, verified, finalized)"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    List cash positions with filters and pagination
    
    Supports filtering by:
    - Branch
    - Status
    - Date range
    """
    service = CashPositionService(db, tenant_id)
    positions, total = await service.list_cash_positions(
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        status_filter=status,
        start_date=start_date,
        end_date=end_date
    )
    
    pages = (total + page_size - 1) // page_size
    
    return CashPositionListResponse(
        items=positions,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.patch("/{position_id}", response_model=CashPositionResponse)
async def update_cash_position(
    position_id: int,
    data: CashPositionUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Update cash position
    
    Cannot update finalized positions
    Automatically recalculates closing balance
    """
    service = CashPositionService(db, tenant_id)
    position = await service.update_cash_position(position_id, data, current_user["id"])
    return position


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cash_position(
    position_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete cash position (soft delete)
    
    Cannot delete finalized positions
    """
    service = CashPositionService(db, tenant_id)
    await service.delete_cash_position(position_id, current_user["id"])
    return None


# ============================================
# Business Operations
# ============================================

@router.post("/{position_id}/verify", response_model=CashPositionResponse)
async def verify_cash_position(
    position_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Verify cash position
    
    Marks position as verified by current user
    Required before finalization
    """
    service = CashPositionService(db, tenant_id)
    position = await service.verify_cash_position(position_id, current_user["id"])
    return position


@router.post("/{position_id}/finalize", response_model=CashPositionResponse)
async def finalize_cash_position(
    position_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Finalize cash position
    
    Makes position immutable
    Requires prior verification
    """
    service = CashPositionService(db, tenant_id)
    position = await service.finalize_cash_position(position_id, current_user["id"])
    return position


@router.get("/current/today", response_model=CashPositionResponse)
async def get_current_position(
    branch_id: Optional[int] = Query(None, description="Branch ID"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current cash position for today
    
    Returns today's position for specified branch
    If no branch specified, returns consolidated position
    """
    service = CashPositionService(db, tenant_id)
    position = await service.get_current_position(branch_id)
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cash position found for today"
        )
    
    return position


@router.get("/date/{position_date}", response_model=CashPositionResponse)
async def get_position_by_date(
    position_date: date,
    branch_id: Optional[int] = Query(None, description="Branch ID"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cash position for specific date
    
    Returns position for the specified date and branch
    """
    service = CashPositionService(db, tenant_id)
    position = await service.get_position_by_date(position_date, branch_id)
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cash position found for {position_date}"
        )
    
    return position


# ============================================
# Statistics & Reports
# ============================================

@router.get("/statistics/summary", response_model=CashPositionStatistics)
async def get_cash_statistics(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cash position statistics
    
    Returns:
    - Total cash on hand
    - Branch statistics
    - Daily movements
    - Alerts and warnings
    """
    service = CashPositionService(db, tenant_id)
    stats = await service.get_statistics()
    return stats


@router.get("/branch/{branch_id}/summary", response_model=BranchCashSummary)
async def get_branch_summary(
    branch_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cash summary for specific branch
    
    Returns current cash position and alerts for branch
    """
    service = CashPositionService(db, tenant_id)
    summary = await service.get_branch_summary(branch_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cash position found for this branch"
        )
    
    return summary


@router.get("/movement/summary", response_model=List[CashMovementSummary])
async def get_cash_movement(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    branch_id: Optional[int] = Query(None, description="Branch ID"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cash movement summary for date range
    
    Shows daily cash movements including:
    - Opening/closing balances
    - Receipts and payments
    - Bank transactions
    """
    service = CashPositionService(db, tenant_id)
    movements = await service.get_cash_movement(start_date, end_date, branch_id)
    return movements


@router.get("/alerts/active", response_model=List[CashAlertResponse])
async def get_cash_alerts(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get active cash alerts
    
    Returns alerts for:
    - Low cash (< ₹50,000)
    - High cash (> ₹5,00,000)
    - Cash discrepancies
    - Pending verifications
    """
    service = CashPositionService(db, tenant_id)
    alerts = await service.get_alerts()
    return alerts


# ============================================
# Denomination Management
# ============================================

@router.post("/denomination/calculate", response_model=dict)
async def calculate_denomination_total(
    denomination: DenominationBreakup,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate total amount from denomination breakup
    
    Validates denomination counts and returns total
    """
    total = denomination.calculate_total()
    
    return {
        "denomination": denomination.dict(),
        "total_amount": float(total),
        "currency": "INR"
    }


# ============================================
# Bulk Operations
# ============================================

@router.post("/bulk/create", response_model=BulkCashPositionResponse)
async def bulk_create_cash_positions(
    data: BulkCashPositionCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Bulk create cash positions
    
    Creates multiple cash position records at once
    Useful for end-of-day batch processing
    """
    service = CashPositionService(db, tenant_id)
    created_ids, errors = await service.bulk_create_positions(
        data.positions,
        current_user["id"]
    )
    
    return BulkCashPositionResponse(
        success_count=len(created_ids),
        failure_count=len(errors),
        created_ids=created_ids,
        errors=errors
    )


# ============================================
# History & Audit
# ============================================

@router.get("/history/{branch_id}", response_model=List[CashPositionResponse])
async def get_position_history(
    branch_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cash position history for branch
    
    Returns historical cash positions for specified number of days
    """
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    service = CashPositionService(db, tenant_id)
    movements = await service.get_cash_movement(start_date, end_date, branch_id)
    
    # Convert to response format
    # This is a simplified version - you may want to enhance this
    return []
