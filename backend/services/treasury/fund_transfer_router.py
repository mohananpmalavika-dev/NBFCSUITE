"""
Treasury - Fund Transfer Router
API endpoints for internal and external fund transfers
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.services.treasury.fund_transfer_service import FundTransferService
from backend.services.treasury.fund_transfer_schemas import (
    FundTransferCreate, FundTransferUpdate, FundTransferResponse,
    FundTransferApprove, FundTransferReject, FundTransferExecute,
    FundTransferCancel, FundTransferStatistics, FundTransferSummary,
    FundTransferSchedule, FundTransferType, FundTransferStatus
)

router = APIRouter(prefix="/fund-transfers", tags=["Treasury - Fund Transfers"])


def get_service(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Dependency to get fund transfer service"""
    return FundTransferService(db, current_user["tenant_id"], current_user["id"])


# ============================================================================
# FUND TRANSFER MANAGEMENT
# ============================================================================

@router.post("", response_model=FundTransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    data: FundTransferCreate,
    service: FundTransferService = Depends(get_service)
):
    """Create a new fund transfer"""
    return service.create_transfer(data)


@router.get("/{transfer_id}", response_model=FundTransferResponse)
def get_transfer(
    transfer_id: int,
    service: FundTransferService = Depends(get_service)
):
    """Get transfer by ID"""
    return service.get_transfer(transfer_id)


@router.get("", response_model=dict)
def list_transfers(
    source_account_id: Optional[int] = Query(None),
    destination_account_id: Optional[int] = Query(None),
    transfer_type: Optional[FundTransferType] = Query(None),
    status: Optional[FundTransferStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_scheduled: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: FundTransferService = Depends(get_service)
):
    """List fund transfers with filters"""
    transfers, total = service.list_transfers(
        source_account_id=source_account_id,
        destination_account_id=destination_account_id,
        transfer_type=transfer_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        is_scheduled=is_scheduled,
        skip=skip,
        limit=limit
    )
    return {"total": total, "items": transfers, "skip": skip, "limit": limit}


@router.patch("/{transfer_id}", response_model=FundTransferResponse)
def update_transfer(
    transfer_id: int,
    data: FundTransferUpdate,
    service: FundTransferService = Depends(get_service)
):
    """Update fund transfer (draft only)"""
    return service.update_transfer(transfer_id, data)


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer(
    transfer_id: int,
    service: FundTransferService = Depends(get_service)
):
    """Delete fund transfer (draft or rejected only)"""
    service.delete_transfer(transfer_id)


# ============================================================================
# APPROVAL WORKFLOW
# ============================================================================

@router.post("/{transfer_id}/submit", response_model=FundTransferResponse)
def submit_for_approval(
    transfer_id: int,
    service: FundTransferService = Depends(get_service)
):
    """Submit transfer for approval"""
    return service.submit_for_approval(transfer_id)


@router.post("/{transfer_id}/approve", response_model=FundTransferResponse)
def approve_transfer(
    transfer_id: int,
    data: FundTransferApprove,
    service: FundTransferService = Depends(get_service)
):
    """Approve fund transfer"""
    return service.approve_transfer(transfer_id, data.approval_notes)


@router.post("/{transfer_id}/reject", response_model=FundTransferResponse)
def reject_transfer(
    transfer_id: int,
    data: FundTransferReject,
    service: FundTransferService = Depends(get_service)
):
    """Reject fund transfer"""
    return service.reject_transfer(transfer_id, data.rejection_reason)


# ============================================================================
# EXECUTION
# ============================================================================

@router.post("/{transfer_id}/execute", response_model=FundTransferResponse)
def execute_transfer(
    transfer_id: int,
    data: FundTransferExecute,
    service: FundTransferService = Depends(get_service)
):
    """Execute approved fund transfer"""
    return service.execute_transfer(transfer_id, data.transaction_reference)


@router.post("/{transfer_id}/cancel", response_model=FundTransferResponse)
def cancel_transfer(
    transfer_id: int,
    data: FundTransferCancel,
    service: FundTransferService = Depends(get_service)
):
    """Cancel fund transfer"""
    return service.cancel_transfer(transfer_id, data.cancellation_reason)


# ============================================================================
# SCHEDULED TRANSFERS
# ============================================================================

@router.get("/scheduled/list", response_model=List[FundTransferResponse])
def get_scheduled_transfers(
    service: FundTransferService = Depends(get_service)
):
    """Get all scheduled transfers"""
    return service.get_scheduled_transfers()


@router.get("/scheduled/due", response_model=List[FundTransferResponse])
def get_due_scheduled_transfers(
    service: FundTransferService = Depends(get_service)
):
    """Get scheduled transfers due for execution"""
    return service.get_due_scheduled_transfers()


@router.get("/scheduled/summary", response_model=FundTransferSchedule)
def get_schedule_summary(
    service: FundTransferService = Depends(get_service)
):
    """Get scheduled transfers summary"""
    return service.get_schedule_summary()


# ============================================================================
# STATISTICS & REPORTS
# ============================================================================

@router.get("/statistics/summary", response_model=FundTransferStatistics)
def get_statistics(
    service: FundTransferService = Depends(get_service)
):
    """Get fund transfer statistics"""
    return service.get_statistics()


@router.get("/account/{account_id}/summary", response_model=FundTransferSummary)
def get_account_summary(
    account_id: int,
    service: FundTransferService = Depends(get_service)
):
    """Get transfer summary for an account"""
    return service.get_account_summary(account_id)
