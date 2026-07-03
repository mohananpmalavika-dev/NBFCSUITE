"""
Recurring Deposit Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from ..database import get_db
from ..schemas import RDInstallmentPayment
from ..engines import RDEngine

router = APIRouter(prefix="/rd", tags=["Recurring Deposit"])


@router.post("/calculate-maturity")
def calculate_rd_maturity(
    installment_amount: float,
    num_months: int,
    interest_rate: float,
    db: Session = Depends(get_db)
):
    """Calculate RD maturity amount"""
    rd_engine = RDEngine(db)
    return rd_engine.calculate_rd_maturity(
        Decimal(str(installment_amount)),
        num_months,
        Decimal(str(interest_rate))
    )


@router.get("/{account_id}/schedule")
def get_installment_schedule(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Get RD installment schedule"""
    from ..models import RDSchedule
    
    schedules = db.query(RDSchedule).filter(
        RDSchedule.account_id == account_id
    ).order_by(RDSchedule.installment_number).all()
    
    return [
        {
            "schedule_id": str(s.id),
            "installment_number": s.installment_number,
            "installment_amount": float(s.installment_amount),
            "due_date": s.due_date.isoformat(),
            "status": s.status,
            "paid_amount": float(s.paid_amount) if s.paid_amount else 0,
            "paid_date": s.paid_date.isoformat() if s.paid_date else None,
            "penalty_amount": float(s.penalty_amount) if s.penalty_amount else 0
        }
        for s in schedules
    ]


@router.post("/installments/pay")
def pay_installment(
    payment: RDInstallmentPayment,
    db: Session = Depends(get_db)
):
    """Pay RD installment"""
    try:
        rd_engine = RDEngine(db)
        return rd_engine.process_installment_payment(
            payment.schedule_id,
            payment.amount,
            payment.payment_date,
            payment.payment_mode,
            payment.payment_reference
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/overdue")
def get_overdue_installments(
    account_id: str = None,
    customer_id: str = None,
    db: Session = Depends(get_db)
):
    """Get overdue RD installments"""
    rd_engine = RDEngine(db)
    return rd_engine.get_overdue_installments(account_id, customer_id)


@router.post("/installments/{schedule_id}/waive-penalty")
def waive_penalty(
    schedule_id: str,
    reason: str,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Waive penalty for late payment"""
    try:
        rd_engine = RDEngine(db)
        return rd_engine.waive_penalty(schedule_id, reason, approved_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{account_id}/auto-debit")
def setup_auto_debit(
    account_id: str,
    debit_account: str,
    bank_name: str = None,
    ifsc_code: str = None,
    db: Session = Depends(get_db)
):
    """Setup auto-debit for RD"""
    try:
        rd_engine = RDEngine(db)
        return rd_engine.auto_debit_setup(
            account_id,
            debit_account,
            bank_name,
            ifsc_code
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{account_id}/summary")
def get_rd_summary(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Get complete RD account summary"""
    try:
        rd_engine = RDEngine(db)
        return rd_engine.get_rd_account_summary(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
