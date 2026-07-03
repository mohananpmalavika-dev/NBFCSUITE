"""
Premature Closure Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PrematureClosureRequest, PrematureClosureApproval
from ..services import PrematureClosureService

router = APIRouter(prefix="/premature-closure", tags=["Premature Closure"])


@router.post("/calculate")
def calculate_premature_closure(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Calculate premature closure payout"""
    try:
        service = PrematureClosureService(db)
        return service.calculate_premature_closure(account_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/request")
def request_closure(
    request: PrematureClosureRequest,
    requested_by: str,
    db: Session = Depends(get_db)
):
    """Request premature closure"""
    try:
        service = PrematureClosureService(db)
        return service.request_premature_closure(
            request.account_id,
            request.closure_reason,
            requested_by
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approve")
def approve_closure(
    approval: PrematureClosureApproval,
    db: Session = Depends(get_db)
):
    """Approve premature closure"""
    try:
        service = PrematureClosureService(db)
        
        if approval.approved:
            return service.approve_premature_closure(
                approval.closure_id,
                "system",  # Should come from auth
                approval.payment_mode
            )
        else:
            return service.reject_premature_closure(
                approval.closure_id,
                "system",
                approval.rejection_reason
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pending")
def get_pending_closures(
    branch_code: str = None,
    db: Session = Depends(get_db)
):
    """Get pending closure requests"""
    service = PrematureClosureService(db)
    return service.get_pending_closures(branch_code)
