"""
Batch Processing Router

API endpoints for batch operations including:
- Batch maturity processing
- Batch TDS calculation
- Bulk account operations
- Automated jobs
"""

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .batch_service import BatchProcessingService
from .schemas import (
    BatchInterestRequest,
    BatchInterestResponse,
    SuccessResponse
)

router = APIRouter(prefix="/batch", tags=["Deposit Batch Operations"])


@router.post("/maturity/process", response_model=SuccessResponse)
def process_maturity_batch(
    maturity_date: Optional[date] = Query(None, description="Process maturities for specific date"),
    days_ahead: int = Query(0, ge=0, le=30, description="Process maturities due in next N days"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Process maturity batch
    
    Processes accounts that have matured or are maturing soon.
    Handles auto-renewal and notifications.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    # Run in background for large batches
    background_tasks.add_task(
        service.process_maturity_batch,
        maturity_date=maturity_date,
        days_ahead=days_ahead
    )
    
    return SuccessResponse(
        success=True,
        message="Maturity processing started in background",
        data={"status": "processing"}
    )


@router.post("/tds/calculate", response_model=SuccessResponse)
def calculate_tds_batch(
    financial_year: str = Query(..., description="FY in format YYYY-YYYY"),
    quarter: int = Query(..., ge=1, le=4, description="Quarter (1-4)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate TDS for quarter
    
    Calculates TDS for all applicable accounts for the quarter.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    background_tasks.add_task(
        service.calculate_tds_batch,
        financial_year=financial_year,
        quarter=quarter
    )
    
    return SuccessResponse(
        success=True,
        message="TDS calculation started in background",
        data={"financial_year": financial_year, "quarter": quarter}
    )


@router.post("/dormancy/check", response_model=SuccessResponse)
def check_dormant_accounts(
    inactive_months: int = Query(24, ge=12, le=60, description="Mark dormant after N months of inactivity"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check and mark dormant accounts
    
    Identifies accounts with no transactions for specified period.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.check_dormant_accounts(inactive_months=inactive_months)
    
    return SuccessResponse(
        success=True,
        message=f"Marked {result['marked_count']} accounts as dormant",
        data=result
    )


@router.post("/penalties/apply", response_model=SuccessResponse)
def apply_penalties_batch(
    penalty_type: str = Query(..., description="Type: rd_missed, min_balance, late_payment"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Apply penalties in batch
    
    Applies penalties for missed RD installments, minimum balance violations, etc.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    background_tasks.add_task(
        service.apply_penalties_batch,
        penalty_type=penalty_type
    )
    
    return SuccessResponse(
        success=True,
        message=f"Penalty application started for {penalty_type}",
        data={"penalty_type": penalty_type}
    )


@router.post("/mis-payout/process", response_model=SuccessResponse)
def process_mis_payout(
    payout_month: Optional[date] = Query(None, description="Month for payout"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Process MIS monthly payouts
    
    Credits monthly interest to MIS accounts.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    background_tasks.add_task(
        service.process_mis_payout_batch,
        payout_month=payout_month
    )
    
    return SuccessResponse(
        success=True,
        message="MIS payout processing started",
        data={"status": "processing"}
    )


@router.get("/status/{job_id}")
def get_batch_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get batch job status
    
    Returns status of a background batch job.
    """
    # TODO: Implement job tracking
    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "status": "completed",
            "message": "Job tracking not yet implemented"
        }
    }


@router.post("/bulk/close-accounts", response_model=SuccessResponse)
def bulk_close_accounts(
    account_ids: List[int],
    closure_reason: str = Query(..., description="Reason for closure"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Bulk close accounts
    
    Closes multiple accounts at once.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.bulk_close_accounts(
        account_ids=account_ids,
        closure_reason=closure_reason
    )
    
    return SuccessResponse(
        success=True,
        message=f"Processed {result['success_count']} out of {result['total_count']} accounts",
        data=result
    )


@router.post("/interest/schedule-posting", response_model=SuccessResponse)
def schedule_interest_posting(
    posting_date: date = Query(..., description="Date to post interest"),
    account_type: Optional[str] = Query(None, description="Account type filter"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule interest posting
    
    Schedules interest posting for accounts.
    """
    service = BatchProcessingService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    background_tasks.add_task(
        service.schedule_interest_posting,
        posting_date=posting_date,
        account_type=account_type
    )
    
    return SuccessResponse(
        success=True,
        message="Interest posting scheduled",
        data={"posting_date": posting_date.isoformat()}
    )
