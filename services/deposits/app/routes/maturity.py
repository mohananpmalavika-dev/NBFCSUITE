"""
Maturity Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..engines import MaturityEngine
from ..schemas import MaturityAction

router = APIRouter(prefix="/maturity", tags=["Maturity"])


@router.get("/{account_id}/calculate")
def calculate_maturity(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Calculate maturity amount for account"""
    try:
        maturity_engine = MaturityEngine(db)
        return maturity_engine.calculate_maturity(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{account_id}/process")
def process_maturity(
    account_id: str,
    action: MaturityAction,
    db: Session = Depends(get_db)
):
    """Process maturity (payout/renewal)"""
    try:
        maturity_engine = MaturityEngine(db)
        return maturity_engine.process_maturity(
            account_id,
            action.action,
            action.renewal_tenure_days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pipeline")
def get_maturity_pipeline(
    days_ahead: int = 30,
    branch_code: str = None,
    db: Session = Depends(get_db)
):
    """Get upcoming maturities"""
    maturity_engine = MaturityEngine(db)
    return maturity_engine.get_maturity_pipeline(days_ahead, branch_code)


@router.get("/{account_id}/recommend-renewal")
def recommend_renewal(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Get renewal recommendation"""
    try:
        maturity_engine = MaturityEngine(db)
        return maturity_engine.recommend_renewal(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{account_id}/auto-renew")
def enable_auto_renewal(
    account_id: str,
    enabled: bool = True,
    db: Session = Depends(get_db)
):
    """Enable/disable auto-renewal"""
    from ..models import DepositAccount
    
    account = db.query(DepositAccount).filter(
        DepositAccount.id == account_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.auto_renewal = enabled
    db.commit()
    
    return {
        "account_id": account_id,
        "auto_renewal": enabled,
        "status": "updated"
    }
