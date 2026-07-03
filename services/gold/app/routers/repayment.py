"""
Phase 7: Loan Servicing & Repayment - API Router
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from app.database import get_db
from app.models.repayment import (
    EMISchedule, RepaymentTransaction, InterestAccrual, LoanAdjustment,
    LoanPrepayment, LoanStatement, AutoDebitMandate, LoanPenalty,
    LoanRenewal, RepaymentAllocationRule
)
from app.models.loan import LoanAccount
from app.schemas.repayment import (
    # EMI schemas
    EMIScheduleCreate, EMIScheduleUpdate, EMIScheduleResponse, EMISummary,
    # Repayment schemas
    RepaymentTransactionCreate, RepaymentTransactionUpdate, RepaymentTransactionResponse,
    PaymentAllocation, RepaymentSummary,
    # Interest schemas
    InterestAccrualCreate, InterestAccrualResponse,
    # Adjustment schemas
    LoanAdjustmentCreate, LoanAdjustmentApproval, LoanAdjustmentResponse,
    # Prepayment schemas
    LoanPrepaymentCreate, LoanPrepaymentResponse,
    # Statement schemas
    LoanStatementCreate, LoanStatementResponse,
    # Mandate schemas
    AutoDebitMandateCreate, AutoDebitMandateUpdate, AutoDebitMandateResponse,
    # Penalty schemas
    LoanPenaltyCreate, LoanPenaltyWaiver, LoanPenaltyResponse,
    # Renewal schemas
    LoanRenewalCreate, LoanRenewalResponse,
    # Allocation schemas
    RepaymentAllocationRuleCreate, RepaymentAllocationRuleResponse,
    # Summary schemas
    LoanAccountSummary, OverdueEMISummary, PortfolioHealthMetrics,
    # Bulk operations
    BulkEMIGeneration, BulkInterestAccrual, BulkStatementGeneration,
    # Enums
    PaymentStatus, TransactionStatus, PaymentMode
)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

def generate_receipt_number() -> str:
    """Generate unique receipt number"""
    today = datetime.now()
    prefix = f"RCP{today.strftime('%Y%m%d')}"
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"{prefix}{random_suffix}"


def generate_mandate_reference() -> str:
    """Generate unique mandate reference"""
    today = datetime.now()
    prefix = f"MND{today.strftime('%Y%m%d')}"
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"{prefix}{random_suffix}"


def calculate_emi(principal: Decimal, rate_annual: Decimal, tenure_months: int) -> Decimal:
    """Calculate EMI using reducing balance method"""
    if tenure_months == 0:
        return principal
    
    rate_monthly = rate_annual / Decimal(12) / Decimal(100)
    if rate_monthly == 0:
        return principal / Decimal(tenure_months)
    
    numerator = principal * rate_monthly * ((1 + rate_monthly) ** tenure_months)
    denominator = ((1 + rate_monthly) ** tenure_months) - 1
    return numerator / denominator


def allocate_payment(
    payment_amount: Decimal,
    outstanding_principal: Decimal,
    outstanding_interest: Decimal,
    overdue_interest: Decimal,
    penalty_amount: Decimal,
    other_charges: Decimal,
    allocation_rule: Optional[RepaymentAllocationRule] = None
) -> PaymentAllocation:
    """Allocate payment according to priority rules"""
    
    # Default allocation order: penalty > overdue_interest > current_interest > principal > charges
    remaining = payment_amount
    allocation = PaymentAllocation()
    
    # Penalty first
    if remaining > 0 and penalty_amount > 0:
        paid = min(remaining, penalty_amount)
        allocation.penalty_paid = paid
        remaining -= paid
    
    # Overdue interest
    if remaining > 0 and overdue_interest > 0:
        paid = min(remaining, overdue_interest)
        allocation.overdue_interest_paid = paid
        remaining -= paid
    
    # Current interest
    if remaining > 0 and outstanding_interest > 0:
        paid = min(remaining, outstanding_interest)
        allocation.interest_paid = paid
        remaining -= paid
    
    # Principal
    if remaining > 0 and outstanding_principal > 0:
        paid = min(remaining, outstanding_principal)
        allocation.principal_paid = paid
        remaining -= paid
    
    # Other charges
    if remaining > 0 and other_charges > 0:
        paid = min(remaining, other_charges)
        allocation.other_charges_paid = paid
        remaining -= paid
    
    return allocation


# ============================================================================
# EMI Schedule Endpoints
# ============================================================================

@router.post("/emi-schedule", response_model=List[EMIScheduleResponse], status_code=status.HTTP_201_CREATED)
def generate_emi_schedule(
    loan_account_id: str,
    db: Session = Depends(get_db)
):
    """Generate EMI schedule for a loan account"""
    
    # Get loan account
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_account_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    # Check if schedule already exists
    existing = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_account_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="EMI schedule already exists")
    
    # Calculate EMI
    emi_amount = calculate_emi(
        loan.principal_amount,
        loan.interest_rate,
        loan.tenure_months
    )
    
    # Generate schedule
    schedules = []
    remaining_principal = loan.principal_amount
    rate_monthly = loan.interest_rate / Decimal(12) / Decimal(100)
    
    disbursement_date = loan.disbursement_date or date.today()
    
    for i in range(1, loan.tenure_months + 1):
        # Calculate due date (monthly)
        due_date = disbursement_date + timedelta(days=30 * i)
        
        # Interest component
        interest_component = remaining_principal * rate_monthly
        
        # Principal component
        principal_component = emi_amount - interest_component
        
        # Ensure last EMI clears remaining principal
        if i == loan.tenure_months:
            principal_component = remaining_principal
            emi_amount = principal_component + interest_component
        
        schedule = EMISchedule(
            loan_account_id=loan_account_id,
            installment_number=i,
            due_date=due_date,
            principal_component=principal_component,
            interest_component=interest_component,
            total_emi_amount=emi_amount,
            outstanding_principal=principal_component,
            outstanding_interest=interest_component,
            payment_status="pending"
        )
        
        db.add(schedule)
        schedules.append(schedule)
        
        remaining_principal -= principal_component
    
    db.commit()
    
    # Refresh all schedules
    for schedule in schedules:
        db.refresh(schedule)
    
    return schedules


@router.get("/emi-schedule/{loan_account_id}", response_model=List[EMIScheduleResponse])
def get_emi_schedule(
    loan_account_id: str,
    payment_status: Optional[PaymentStatus] = None,
    db: Session = Depends(get_db)
):
    """Get EMI schedule for a loan account"""
    
    query = db.query(EMISchedule).filter(EMISchedule.loan_account_id == loan_account_id)
    
    if payment_status:
        query = query.filter(EMISchedule.payment_status == payment_status.value)
    
    schedules = query.order_by(EMISchedule.installment_number).all()
    return schedules


@router.get("/emi-schedule/{loan_account_id}/overdue", response_model=List[EMIScheduleResponse])
def get_overdue_emis(
    loan_account_id: str,
    db: Session = Depends(get_db)
):
    """Get overdue EMIs for a loan account"""
    
    schedules = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_account_id,
        EMISchedule.payment_status.in_(["overdue", "partially_paid"]),
        EMISchedule.due_date < date.today()
    ).order_by(EMISchedule.due_date).all()
    
    return schedules


@router.put("/emi-schedule/{schedule_id}", response_model=EMIScheduleResponse)
def update_emi_schedule(
    schedule_id: str,
    update_data: EMIScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update EMI schedule payment status"""
    
    schedule = db.query(EMISchedule).filter(EMISchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="EMI schedule not found")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.get("/emi-schedule/{loan_account_id}/summary", response_model=EMISummary)
def get_emi_summary(
    loan_account_id: str,
    db: Session = Depends(get_db)
):
    """Get EMI summary statistics"""
    
    schedules = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_account_id
    ).all()
    
    if not schedules:
        raise HTTPException(status_code=404, detail="No EMI schedule found")
    
    total_emis = len(schedules)
    paid_emis = sum(1 for s in schedules if s.payment_status == "paid")
    pending_emis = sum(1 for s in schedules if s.payment_status == "pending")
    overdue_emis = sum(1 for s in schedules if s.payment_status == "overdue")
    
    total_emi_amount = sum(s.total_emi_amount for s in schedules)
    total_paid = sum(s.paid_amount for s in schedules)
    total_pending = sum(s.total_emi_amount - s.paid_amount for s in schedules if s.payment_status != "paid")
    total_overdue = sum(s.total_emi_amount - s.paid_amount for s in schedules if s.payment_status == "overdue")
    
    return EMISummary(
        total_emis=total_emis,
        paid_emis=paid_emis,
        pending_emis=pending_emis,
        overdue_emis=overdue_emis,
        total_emi_amount=total_emi_amount,
        total_paid=total_paid,
        total_pending=total_pending,
        total_overdue=total_overdue
    )


# ============================================================================
# Repayment Transaction Endpoints
# ============================================================================

@router.post("/repayments", response_model=RepaymentTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_repayment(
    repayment_data: RepaymentTransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new repayment transaction"""
    
    # Get loan account
    loan = db.query(LoanAccount).filter(LoanAccount.id == repayment_data.loan_account_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    # Calculate allocation
    allocation = allocate_payment(
        repayment_data.payment_amount,
        loan.outstanding_principal,
        loan.outstanding_interest,
        Decimal(0),  # TODO: Get overdue interest from EMI schedule
        Decimal(0),  # TODO: Get pending penalties
        Decimal(0)   # TODO: Get other charges
    )
    
    # Create transaction
    transaction = RepaymentTransaction(
        **repayment_data.dict(),
        receipt_number=generate_receipt_number(),
        principal_paid=allocation.principal_paid,
        interest_paid=allocation.interest_paid,
        overdue_interest_paid=allocation.overdue_interest_paid,
        penalty_paid=allocation.penalty_paid,
        other_charges_paid=allocation.other_charges_paid,
        transaction_status="completed"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.get("/repayments", response_model=List[RepaymentTransactionResponse])
def list_repayments(
    loan_account_id: Optional[str] = None,
    payment_mode: Optional[PaymentMode] = None,
    transaction_status: Optional[TransactionStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List repayment transactions with filters"""
    
    query = db.query(RepaymentTransaction)
    
    if loan_account_id:
        query = query.filter(RepaymentTransaction.loan_account_id == loan_account_id)
    
    if payment_mode:
        query = query.filter(RepaymentTransaction.payment_mode == payment_mode.value)
    
    if transaction_status:
        query = query.filter(RepaymentTransaction.transaction_status == transaction_status.value)
    
    if from_date:
        query = query.filter(RepaymentTransaction.transaction_date >= from_date)
    
    if to_date:
        query = query.filter(RepaymentTransaction.transaction_date <= to_date)
    
    transactions = query.order_by(RepaymentTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/repayments/{transaction_id}", response_model=RepaymentTransactionResponse)
def get_repayment(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get repayment transaction details"""
    
    transaction = db.query(RepaymentTransaction).filter(
        RepaymentTransaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.post("/repayments/{transaction_id}/verify", response_model=RepaymentTransactionResponse)
def verify_repayment(
    transaction_id: str,
    verified_by_user_id: str,
    db: Session = Depends(get_db)
):
    """Verify a repayment transaction"""
    
    transaction = db.query(RepaymentTransaction).filter(
        RepaymentTransaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.transaction_status != "pending":
        raise HTTPException(status_code=400, detail="Transaction is not pending verification")
    
    transaction.verified_by_user_id = verified_by_user_id
    transaction.verification_date = datetime.utcnow()
    transaction.transaction_status = "completed"
    transaction.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.post("/repayments/{transaction_id}/reverse", response_model=RepaymentTransactionResponse)
def reverse_repayment(
    transaction_id: str,
    reversed_by_user_id: str,
    reversal_reason: str,
    db: Session = Depends(get_db)
):
    """Reverse a repayment transaction"""
    
    transaction = db.query(RepaymentTransaction).filter(
        RepaymentTransaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.transaction_status == "reversed":
        raise HTTPException(status_code=400, detail="Transaction already reversed")
    
    transaction.transaction_status = "reversed"
    transaction.reversed_by_user_id = reversed_by_user_id
    transaction.reversed_at = datetime.utcnow()
    transaction.reversal_reason = reversal_reason
    transaction.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.get("/repayments/{loan_account_id}/summary", response_model=RepaymentSummary)
def get_repayment_summary(
    loan_account_id: str,
    db: Session = Depends(get_db)
):
    """Get repayment summary for a loan account"""
    
    transactions = db.query(RepaymentTransaction).filter(
        RepaymentTransaction.loan_account_id == loan_account_id,
        RepaymentTransaction.transaction_status == "completed"
    ).all()
    
    if not transactions:
        return RepaymentSummary(
            total_transactions=0,
            total_amount_collected=Decimal(0),
            total_principal_collected=Decimal(0),
            total_interest_collected=Decimal(0),
            total_penalty_collected=Decimal(0),
            average_transaction_amount=Decimal(0)
        )
    
    total_transactions = len(transactions)
    total_amount = sum(t.payment_amount for t in transactions)
    total_principal = sum(t.principal_paid for t in transactions)
    total_interest = sum(t.interest_paid + t.overdue_interest_paid for t in transactions)
    total_penalty = sum(t.penalty_paid for t in transactions)
    average_amount = total_amount / Decimal(total_transactions) if total_transactions > 0 else Decimal(0)
    
    return RepaymentSummary(
        total_transactions=total_transactions,
        total_amount_collected=total_amount,
        total_principal_collected=total_principal,
        total_interest_collected=total_interest,
        total_penalty_collected=total_penalty,
        average_transaction_amount=average_amount
    )


# ============================================================================
# Interest Accrual Endpoints
# ============================================================================

@router.post("/interest-accrual", response_model=InterestAccrualResponse, status_code=status.HTTP_201_CREATED)
def create_interest_accrual(
    accrual_data: InterestAccrualCreate,
    db: Session = Depends(get_db)
):
    """Create interest accrual entry"""
    
    # Check if already exists
    existing = db.query(InterestAccrual).filter(
        InterestAccrual.loan_account_id == accrual_data.loan_account_id,
        InterestAccrual.accrual_date == accrual_data.accrual_date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Interest accrual already exists for this date")
    
    accrual = InterestAccrual(**accrual_data.dict())
    db.add(accrual)
    db.commit()
    db.refresh(accrual)
    
    return accrual


@router.get("/interest-accrual/{loan_account_id}", response_model=List[InterestAccrualResponse])
def get_interest_accruals(
    loan_account_id: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get interest accrual history"""
    
    query = db.query(InterestAccrual).filter(
        InterestAccrual.loan_account_id == loan_account_id
    )
    
    if from_date:
        query = query.filter(InterestAccrual.accrual_date >= from_date)
    
    if to_date:
        query = query.filter(InterestAccrual.accrual_date <= to_date)
    
    accruals = query.order_by(InterestAccrual.accrual_date.desc()).all()
    return accruals


@router.post("/interest-accrual/bulk", status_code=status.HTTP_201_CREATED)
def bulk_interest_accrual(
    bulk_data: BulkInterestAccrual,
    db: Session = Depends(get_db)
):
    """Process bulk interest accrual for multiple loans"""
    
    results = []
    for loan_id in bulk_data.loan_account_ids:
        loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
        if not loan:
            continue
        
        # Calculate daily interest
        daily_rate = loan.interest_rate / Decimal(365) / Decimal(100)
        interest_accrued = loan.outstanding_principal * daily_rate
        
        accrual = InterestAccrual(
            loan_account_id=loan_id,
            accrual_date=bulk_data.accrual_date,
            accrual_period_start=bulk_data.accrual_date,
            accrual_period_end=bulk_data.accrual_date,
            opening_principal=loan.outstanding_principal,
            closing_principal=loan.outstanding_principal,
            applicable_rate=loan.interest_rate,
            days_in_period=1,
            interest_accrued=interest_accrued,
            cumulative_interest=loan.outstanding_interest + interest_accrued,
            calculation_method="simple"
        )
        
        db.add(accrual)
        results.append({"loan_account_id": loan_id, "interest_accrued": float(interest_accrued)})
    
    db.commit()
    
    return {"accruals_created": len(results), "details": results}


# Continued in next part...


# ============================================================================
# Loan Adjustment Endpoints
# ============================================================================

@router.post("/adjustments", response_model=LoanAdjustmentResponse, status_code=status.HTTP_201_CREATED)
def create_adjustment(
    adjustment_data: LoanAdjustmentCreate,
    db: Session = Depends(get_db)
):
    """Create loan adjustment request"""
    
    adjustment = LoanAdjustment(**adjustment_data.dict())
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    
    return adjustment


@router.get("/adjustments", response_model=List[LoanAdjustmentResponse])
def list_adjustments(
    loan_account_id: Optional[str] = None,
    adjustment_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List loan adjustments"""
    
    query = db.query(LoanAdjustment)
    
    if loan_account_id:
        query = query.filter(LoanAdjustment.loan_account_id == loan_account_id)
    
    if adjustment_type:
        query = query.filter(LoanAdjustment.adjustment_type == adjustment_type)
    
    if approval_status:
        query = query.filter(LoanAdjustment.approval_status == approval_status)
    
    adjustments = query.order_by(LoanAdjustment.adjustment_date.desc()).offset(skip).limit(limit).all()
    return adjustments


@router.post("/adjustments/{adjustment_id}/approve", response_model=LoanAdjustmentResponse)
def approve_adjustment(
    adjustment_id: str,
    approval_data: LoanAdjustmentApproval,
    db: Session = Depends(get_db)
):
    """Approve or reject adjustment"""
    
    adjustment = db.query(LoanAdjustment).filter(LoanAdjustment.id == adjustment_id).first()
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    
    if adjustment.approval_status != "pending":
        raise HTTPException(status_code=400, detail="Adjustment already processed")
    
    adjustment.approved_by_user_id = approval_data.approved_by_user_id
    adjustment.approval_status = approval_data.approval_status
    adjustment.approval_date = datetime.utcnow()
    adjustment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(adjustment)
    
    return adjustment


# ============================================================================
# Prepayment Endpoints
# ============================================================================

@router.post("/prepayments", response_model=LoanPrepaymentResponse, status_code=status.HTTP_201_CREATED)
def create_prepayment(
    prepayment_data: LoanPrepaymentCreate,
    db: Session = Depends(get_db)
):
    """Create prepayment request"""
    
    loan = db.query(LoanAccount).filter(LoanAccount.id == prepayment_data.loan_account_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    # Calculate prepayment charges
    prepayment_charges = Decimal(0)
    if prepayment_data.prepayment_charge_percentage:
        prepayment_charges = (prepayment_data.prepayment_amount * 
                            prepayment_data.prepayment_charge_percentage / Decimal(100))
    
    # Calculate principal reduced
    principal_reduced = min(prepayment_data.prepayment_amount, 
                          prepayment_data.outstanding_principal_before)
    
    prepayment = LoanPrepayment(
        **prepayment_data.dict(),
        prepayment_charges=prepayment_charges,
        principal_reduced=principal_reduced,
        prepayment_status="pending"
    )
    
    db.add(prepayment)
    db.commit()
    db.refresh(prepayment)
    
    return prepayment


@router.get("/prepayments", response_model=List[LoanPrepaymentResponse])
def list_prepayments(
    loan_account_id: Optional[str] = None,
    prepayment_type: Optional[str] = None,
    prepayment_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List prepayments"""
    
    query = db.query(LoanPrepayment)
    
    if loan_account_id:
        query = query.filter(LoanPrepayment.loan_account_id == loan_account_id)
    
    if prepayment_type:
        query = query.filter(LoanPrepayment.prepayment_type == prepayment_type)
    
    if prepayment_status:
        query = query.filter(LoanPrepayment.prepayment_status == prepayment_status)
    
    prepayments = query.order_by(LoanPrepayment.prepayment_date.desc()).offset(skip).limit(limit).all()
    return prepayments


@router.post("/prepayments/{prepayment_id}/approve", response_model=LoanPrepaymentResponse)
def approve_prepayment(
    prepayment_id: str,
    approved_by_user_id: str,
    db: Session = Depends(get_db)
):
    """Approve prepayment request"""
    
    prepayment = db.query(LoanPrepayment).filter(LoanPrepayment.id == prepayment_id).first()
    if not prepayment:
        raise HTTPException(status_code=404, detail="Prepayment not found")
    
    if prepayment.prepayment_status != "pending":
        raise HTTPException(status_code=400, detail="Prepayment already processed")
    
    prepayment.approved_by_user_id = approved_by_user_id
    prepayment.approval_date = datetime.utcnow()
    prepayment.prepayment_status = "approved"
    prepayment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(prepayment)
    
    return prepayment


# ============================================================================
# Statement Endpoints
# ============================================================================

@router.post("/statements", response_model=LoanStatementResponse, status_code=status.HTTP_201_CREATED)
def create_statement(
    statement_data: LoanStatementCreate,
    db: Session = Depends(get_db)
):
    """Create loan statement"""
    
    statement = LoanStatement(**statement_data.dict())
    db.add(statement)
    db.commit()
    db.refresh(statement)
    
    return statement


@router.get("/statements/{loan_account_id}", response_model=List[LoanStatementResponse])
def get_statements(
    loan_account_id: str,
    statement_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get loan statements"""
    
    query = db.query(LoanStatement).filter(LoanStatement.loan_account_id == loan_account_id)
    
    if statement_type:
        query = query.filter(LoanStatement.statement_type == statement_type)
    
    statements = query.order_by(LoanStatement.statement_date.desc()).all()
    return statements


@router.post("/statements/bulk", status_code=status.HTTP_201_CREATED)
def bulk_generate_statements(
    bulk_data: BulkStatementGeneration,
    db: Session = Depends(get_db)
):
    """Generate statements for multiple loans"""
    
    results = []
    for loan_id in bulk_data.loan_account_ids:
        loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
        if not loan:
            continue
        
        statement = LoanStatement(
            loan_account_id=loan_id,
            statement_date=date.today(),
            statement_period_start=bulk_data.period_start,
            statement_period_end=bulk_data.period_end,
            statement_type=bulk_data.statement_type.value,
            opening_principal=loan.principal_amount,
            opening_interest=Decimal(0),
            closing_principal=loan.outstanding_principal,
            closing_interest=loan.outstanding_interest,
            total_outstanding=loan.outstanding_principal + loan.outstanding_interest
        )
        
        db.add(statement)
        results.append({"loan_account_id": loan_id})
    
    db.commit()
    
    return {"statements_created": len(results), "details": results}


# ============================================================================
# Auto Debit Mandate Endpoints
# ============================================================================

@router.post("/mandates", response_model=AutoDebitMandateResponse, status_code=status.HTTP_201_CREATED)
def create_mandate(
    mandate_data: AutoDebitMandateCreate,
    db: Session = Depends(get_db)
):
    """Create auto-debit mandate"""
    
    mandate = AutoDebitMandate(
        **mandate_data.dict(),
        mandate_reference=generate_mandate_reference(),
        mandate_status="pending"
    )
    
    db.add(mandate)
    db.commit()
    db.refresh(mandate)
    
    return mandate


@router.get("/mandates", response_model=List[AutoDebitMandateResponse])
def list_mandates(
    loan_account_id: Optional[str] = None,
    mandate_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List auto-debit mandates"""
    
    query = db.query(AutoDebitMandate)
    
    if loan_account_id:
        query = query.filter(AutoDebitMandate.loan_account_id == loan_account_id)
    
    if mandate_status:
        query = query.filter(AutoDebitMandate.mandate_status == mandate_status)
    
    mandates = query.order_by(AutoDebitMandate.created_at.desc()).offset(skip).limit(limit).all()
    return mandates


@router.put("/mandates/{mandate_id}", response_model=AutoDebitMandateResponse)
def update_mandate(
    mandate_id: str,
    update_data: AutoDebitMandateUpdate,
    db: Session = Depends(get_db)
):
    """Update mandate status"""
    
    mandate = db.query(AutoDebitMandate).filter(AutoDebitMandate.id == mandate_id).first()
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(mandate, field, value)
    
    if update_data.mandate_status == "cancelled":
        mandate.cancellation_date = date.today()
    elif update_data.mandate_status == "active":
        mandate.activation_date = date.today()
    
    mandate.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mandate)
    
    return mandate


# ============================================================================
# Penalty Endpoints
# ============================================================================

@router.post("/penalties", response_model=LoanPenaltyResponse, status_code=status.HTTP_201_CREATED)
def create_penalty(
    penalty_data: LoanPenaltyCreate,
    db: Session = Depends(get_db)
):
    """Create penalty charge"""
    
    penalty = LoanPenalty(**penalty_data.dict(), penalty_status="pending")
    db.add(penalty)
    db.commit()
    db.refresh(penalty)
    
    return penalty


@router.get("/penalties", response_model=List[LoanPenaltyResponse])
def list_penalties(
    loan_account_id: Optional[str] = None,
    penalty_type: Optional[str] = None,
    penalty_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List penalties"""
    
    query = db.query(LoanPenalty)
    
    if loan_account_id:
        query = query.filter(LoanPenalty.loan_account_id == loan_account_id)
    
    if penalty_type:
        query = query.filter(LoanPenalty.penalty_type == penalty_type)
    
    if penalty_status:
        query = query.filter(LoanPenalty.penalty_status == penalty_status)
    
    penalties = query.order_by(LoanPenalty.penalty_date.desc()).offset(skip).limit(limit).all()
    return penalties


@router.post("/penalties/{penalty_id}/waive", response_model=LoanPenaltyResponse)
def waive_penalty(
    penalty_id: str,
    waiver_data: LoanPenaltyWaiver,
    db: Session = Depends(get_db)
):
    """Waive penalty charges"""
    
    penalty = db.query(LoanPenalty).filter(LoanPenalty.id == penalty_id).first()
    if not penalty:
        raise HTTPException(status_code=404, detail="Penalty not found")
    
    penalty.waived_amount = waiver_data.waived_amount
    penalty.waived_by_user_id = waiver_data.waived_by_user_id
    penalty.waiver_reason = waiver_data.waiver_reason
    penalty.waiver_date = date.today()
    penalty.approved_by_user_id = waiver_data.approved_by_user_id
    penalty.penalty_status = "waived"
    penalty.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(penalty)
    
    return penalty


# ============================================================================
# Renewal Endpoints
# ============================================================================

@router.post("/renewals", response_model=LoanRenewalResponse, status_code=status.HTTP_201_CREATED)
def create_renewal(
    renewal_data: LoanRenewalCreate,
    db: Session = Depends(get_db)
):
    """Create loan renewal request"""
    
    renewal = LoanRenewal(**renewal_data.dict(), renewal_status="pending")
    db.add(renewal)
    db.commit()
    db.refresh(renewal)
    
    return renewal


@router.get("/renewals", response_model=List[LoanRenewalResponse])
def list_renewals(
    original_loan_account_id: Optional[str] = None,
    renewal_type: Optional[str] = None,
    renewal_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List loan renewals"""
    
    query = db.query(LoanRenewal)
    
    if original_loan_account_id:
        query = query.filter(LoanRenewal.original_loan_account_id == original_loan_account_id)
    
    if renewal_type:
        query = query.filter(LoanRenewal.renewal_type == renewal_type)
    
    if renewal_status:
        query = query.filter(LoanRenewal.renewal_status == renewal_status)
    
    renewals = query.order_by(LoanRenewal.renewal_date.desc()).offset(skip).limit(limit).all()
    return renewals


@router.post("/renewals/{renewal_id}/approve", response_model=LoanRenewalResponse)
def approve_renewal(
    renewal_id: str,
    approved_by_user_id: str,
    db: Session = Depends(get_db)
):
    """Approve loan renewal"""
    
    renewal = db.query(LoanRenewal).filter(LoanRenewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status_code=404, detail="Renewal not found")
    
    if renewal.renewal_status != "pending":
        raise HTTPException(status_code=400, detail="Renewal already processed")
    
    renewal.approved_by_user_id = approved_by_user_id
    renewal.approval_date = date.today()
    renewal.renewal_status = "approved"
    renewal.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(renewal)
    
    return renewal


# ============================================================================
# Allocation Rule Endpoints
# ============================================================================

@router.post("/allocation-rules", response_model=RepaymentAllocationRuleResponse, status_code=status.HTTP_201_CREATED)
def create_allocation_rule(
    rule_data: RepaymentAllocationRuleCreate,
    db: Session = Depends(get_db)
):
    """Create payment allocation rule"""
    
    rule = RepaymentAllocationRule(**rule_data.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("/allocation-rules", response_model=List[RepaymentAllocationRuleResponse])
def list_allocation_rules(
    is_active: Optional[bool] = None,
    is_default: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List allocation rules"""
    
    query = db.query(RepaymentAllocationRule)
    
    if is_active is not None:
        query = query.filter(RepaymentAllocationRule.is_active == is_active)
    
    if is_default is not None:
        query = query.filter(RepaymentAllocationRule.is_default == is_default)
    
    rules = query.all()
    return rules


# ============================================================================
# Summary and Analytics Endpoints
# ============================================================================

@router.get("/loan-accounts/{loan_account_id}/summary", response_model=LoanAccountSummary)
def get_loan_account_summary(
    loan_account_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive loan account summary"""
    
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_account_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    # Get next EMI
    next_emi = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_account_id,
        EMISchedule.payment_status == "pending",
        EMISchedule.due_date >= date.today()
    ).order_by(EMISchedule.due_date).first()
    
    # Get payment statistics
    payments = db.query(RepaymentTransaction).filter(
        RepaymentTransaction.loan_account_id == loan_account_id,
        RepaymentTransaction.transaction_status == "completed"
    ).all()
    
    # Calculate days past due
    overdue_emi = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_account_id,
        EMISchedule.payment_status.in_(["overdue", "partially_paid"])
    ).order_by(EMISchedule.due_date).first()
    
    days_past_due = 0
    if overdue_emi:
        days_past_due = (date.today() - overdue_emi.due_date).days
    
    return LoanAccountSummary(
        loan_account_number=loan.loan_account_number,
        outstanding_principal=loan.outstanding_principal,
        outstanding_interest=loan.outstanding_interest,
        total_outstanding=loan.outstanding_principal + loan.outstanding_interest,
        days_past_due=days_past_due,
        next_emi_due_date=next_emi.due_date if next_emi else None,
        next_emi_amount=next_emi.total_emi_amount if next_emi else None,
        total_payments_made=len(payments),
        last_payment_date=loan.last_payment_date,
        last_payment_amount=loan.last_payment_amount
    )


@router.get("/overdue-summary", response_model=List[OverdueEMISummary])
def get_overdue_summary(
    branch_id: Optional[str] = None,
    min_days_overdue: int = 0,
    db: Session = Depends(get_db)
):
    """Get overdue EMIs summary across all loans"""
    
    # This would use the view gold_overdue_emis_summary
    # For now, implementing direct query
    query = db.query(
        EMISchedule.loan_account_id,
        LoanAccount.loan_account_number,
        LoanAccount.customer_id,
        func.count(EMISchedule.id).label("overdue_count"),
        func.sum(EMISchedule.total_emi_amount - EMISchedule.paid_amount).label("total_overdue_amount"),
        func.max(EMISchedule.days_overdue).label("max_days_overdue"),
        func.sum(EMISchedule.overdue_charges).label("total_overdue_charges"),
        func.min(EMISchedule.due_date).label("earliest_overdue_date")
    ).join(
        LoanAccount, EMISchedule.loan_account_id == LoanAccount.id
    ).filter(
        EMISchedule.payment_status.in_(["overdue", "partially_paid"]),
        EMISchedule.days_overdue >= min_days_overdue
    )
    
    if branch_id:
        query = query.filter(LoanAccount.branch_id == branch_id)
    
    results = query.group_by(
        EMISchedule.loan_account_id,
        LoanAccount.loan_account_number,
        LoanAccount.customer_id
    ).all()
    
    return [
        OverdueEMISummary(
            loan_account_id=str(r.loan_account_id),
            loan_account_number=r.loan_account_number,
            customer_id=r.customer_id,
            overdue_count=r.overdue_count,
            total_overdue_amount=r.total_overdue_amount or Decimal(0),
            max_days_overdue=r.max_days_overdue or 0,
            total_overdue_charges=r.total_overdue_charges or Decimal(0),
            earliest_overdue_date=r.earliest_overdue_date
        )
        for r in results
    ]


@router.get("/portfolio-health", response_model=List[PortfolioHealthMetrics])
def get_portfolio_health(
    branch_id: Optional[str] = None,
    product_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get portfolio health metrics"""
    
    query = db.query(
        LoanAccount.branch_id,
        LoanAccount.product_id,
        func.count(LoanAccount.id).label("total_loans"),
        func.sum(LoanAccount.principal_amount).label("total_principal_disbursed"),
        func.sum(LoanAccount.outstanding_principal).label("total_principal_outstanding"),
        func.sum(LoanAccount.outstanding_interest).label("total_interest_outstanding"),
        func.sum(func.cast(LoanAccount.is_npa, Integer)).label("npa_count"),
        func.sum(
            func.case((LoanAccount.is_npa == True, LoanAccount.outstanding_principal), else_=0)
        ).label("npa_amount"),
        func.sum(
            func.case((LoanAccount.account_status == "active", 1), else_=0)
        ).label("active_count"),
        func.sum(
            func.case((LoanAccount.account_status == "closed", 1), else_=0)
        ).label("closed_count"),
        func.avg(LoanAccount.outstanding_principal).label("avg_outstanding_principal")
    )
    
    if branch_id:
        query = query.filter(LoanAccount.branch_id == branch_id)
    
    if product_id:
        query = query.filter(LoanAccount.product_id == product_id)
    
    results = query.group_by(LoanAccount.branch_id, LoanAccount.product_id).all()
    
    return [
        PortfolioHealthMetrics(
            branch_id=r.branch_id,
            product_id=r.product_id,
            total_loans=r.total_loans,
            total_principal_disbursed=r.total_principal_disbursed or Decimal(0),
            total_principal_outstanding=r.total_principal_outstanding or Decimal(0),
            total_interest_outstanding=r.total_interest_outstanding or Decimal(0),
            npa_count=r.npa_count or 0,
            npa_amount=r.npa_amount or Decimal(0),
            active_count=r.active_count or 0,
            closed_count=r.closed_count or 0,
            avg_outstanding_principal=r.avg_outstanding_principal or Decimal(0)
        )
        for r in results
    ]
