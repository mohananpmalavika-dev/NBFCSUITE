"""
Interest Calculation Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from ..database import get_db
from ..schemas import InterestCalculationRequest, InterestCalculationResponse
from ..engines import InterestEngine

router = APIRouter(prefix="/interest", tags=["Interest"])


@router.post("/calculate", response_model=InterestCalculationResponse)
def calculate_interest(
    request: InterestCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate interest for given parameters"""
    result = InterestEngine.calculate_interest(
        request.principal,
        request.rate,
        request.days,
        request.method
    )
    
    return InterestCalculationResponse(
        principal=request.principal,
        rate=request.rate,
        days=request.days,
        years=Decimal(str(result["years"])),
        method=request.method,
        interest=Decimal(str(result["interest"])),
        maturity_amount=Decimal(str(result["maturity_amount"])),
        calculation_details=result
    )


@router.post("/calculate-simple")
def calculate_simple_interest(
    principal: float,
    rate: float,
    days: int
):
    """Calculate simple interest"""
    return InterestEngine.calculate_simple_interest(
        Decimal(str(principal)),
        Decimal(str(rate)),
        days
    )


@router.post("/calculate-compound")
def calculate_compound_interest(
    principal: float,
    rate: float,
    days: int,
    frequency: int = 4
):
    """Calculate compound interest"""
    return InterestEngine.calculate_compound_interest(
        Decimal(str(principal)),
        Decimal(str(rate)),
        days,
        frequency
    )


@router.post("/generate-schedule")
def generate_interest_schedule(
    principal: float,
    rate: float,
    open_date: str,
    maturity_date: str,
    payout_frequency: str,
    method: str = "SIMPLE"
):
    """Generate interest payment schedule"""
    from ..engines.interest_engine import PayoutFrequency, InterestMethod
    
    schedule = InterestEngine.generate_interest_schedule(
        Decimal(str(principal)),
        Decimal(str(rate)),
        date.fromisoformat(open_date),
        date.fromisoformat(maturity_date),
        PayoutFrequency(payout_frequency),
        InterestMethod(method)
    )
    
    return {
        "total_periods": len(schedule),
        "schedule": schedule
    }


@router.post("/calculate-tds")
def calculate_tds(
    interest_amount: float,
    tds_rate: float = 10.0,
    pan_available: bool = True
):
    """Calculate TDS on interest"""
    return InterestEngine.calculate_tds(
        Decimal(str(interest_amount)),
        Decimal(str(tds_rate)),
        pan_available
    )


@router.get("/{account_id}/postings")
def get_interest_postings(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Get all interest postings for account"""
    from ..models import InterestPosting
    
    postings = db.query(InterestPosting).filter(
        InterestPosting.account_id == account_id
    ).order_by(InterestPosting.from_date).all()
    
    return [
        {
            "id": str(p.id),
            "from_date": p.from_date.isoformat(),
            "to_date": p.to_date.isoformat(),
            "days": p.days,
            "interest_amount": float(p.interest_amount),
            "tds_amount": float(p.tds_amount),
            "net_interest": float(p.net_interest),
            "is_paid": p.is_paid,
            "posting_date": p.posting_date.isoformat() if p.posting_date else None
        }
        for p in postings
    ]
