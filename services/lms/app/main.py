from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Models
class LoanAccount(Base):
    __tablename__ = "loan_accounts"
    
    id = Column(String, primary_key=True)
    application_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    product_id = Column(String)
    account_number = Column(String, unique=True, index=True)
    sanction_amount = Column(Float)
    disbursed_amount = Column(Float, default=0)
    tenure_months = Column(Integer)
    interest_rate = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    emi_amount = Column(Float)
    outstanding_principal = Column(Float)
    outstanding_interest = Column(Float)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class EMISchedule(Base):
    __tablename__ = "emi_schedule"
    
    id = Column(String, primary_key=True)
    loan_account_id = Column(String, ForeignKey("loan_accounts.id"))
    emi_number = Column(Integer)
    due_date = Column(DateTime)
    emi_amount = Column(Float)
    principal_amount = Column(Float)
    interest_amount = Column(Float)
    penalty_amount = Column(Float, default=0)
    paid_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(String, primary_key=True)
    loan_account_id = Column(String, ForeignKey("loan_accounts.id"))
    transaction_date = Column(DateTime, default=datetime.utcnow)
    payment_mode = Column(String)
    amount = Column(Float)
    principal_paid = Column(Float)
    interest_paid = Column(Float)
    reference = Column(String)
    status = Column(String)


# Pydantic Schemas
class EMIScheduleResponse(BaseModel):
    emi_number: int
    due_date: datetime
    emi_amount: float
    principal_amount: float
    interest_amount: float
    status: str
    
    class Config:
        from_attributes = True


class LoanAccountResponse(BaseModel):
    id: str
    account_number: str
    sanction_amount: float
    disbursed_amount: float
    outstanding_principal: float
    status: str
    emi_amount: float
    
    class Config:
        from_attributes = True


class LoanAccountCreate(BaseModel):
    application_id: str
    customer_id: str
    product_id: str
    sanction_amount: float
    tenure_months: int
    interest_rate: float
    disbursed_amount: float = 0.0
    start_date: Optional[datetime] = None


class LoanAccountSummaryResponse(BaseModel):
    loan_id: str
    account_number: str
    outstanding_principal: float
    outstanding_interest: float
    status: str

    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    amount: float
    payment_mode: str
    reference: str


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    transaction_date: datetime
    
    class Config:
        from_attributes = True


# FastAPI App
app = FastAPI(title="lms-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    if tenure_months <= 0:
        return 0.0
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        return principal / tenure_months
    numerator = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
    denominator = (1 + monthly_rate) ** tenure_months - 1
    return float(numerator / denominator)


@app.post("/loans", response_model=LoanAccountResponse)
async def create_loan(
    loan_data: LoanAccountCreate,
    db: Session = Depends(get_db)
):
    from uuid import uuid4

    existing = db.query(LoanAccount).filter(LoanAccount.application_id == loan_data.application_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Loan already exists for this application")

    account_number = f"LA-{str(uuid4())[:8].upper()}"
    emi_amount = calculate_emi(loan_data.sanction_amount, loan_data.interest_rate, loan_data.tenure_months)
    start_date = loan_data.start_date or datetime.utcnow()
    end_date = start_date + timedelta(days=30 * loan_data.tenure_months)
    outstanding_interest = round(emi_amount * loan_data.tenure_months - loan_data.sanction_amount, 2)

    new_loan = LoanAccount(
        id=str(uuid4()),
        application_id=loan_data.application_id,
        customer_id=loan_data.customer_id,
        product_id=loan_data.product_id,
        account_number=account_number,
        sanction_amount=loan_data.sanction_amount,
        disbursed_amount=loan_data.disbursed_amount,
        tenure_months=loan_data.tenure_months,
        interest_rate=loan_data.interest_rate,
        start_date=start_date,
        end_date=end_date,
        emi_amount=emi_amount,
        outstanding_principal=loan_data.sanction_amount,
        outstanding_interest=outstanding_interest,
        status="active",
    )

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)

    # Build EMI schedule
    for sequence in range(1, loan_data.tenure_months + 1):
        principal_component = round(loan_data.sanction_amount / loan_data.tenure_months, 2)
        interest_component = round(max(0.0, emi_amount - principal_component), 2)
        schedule_entry = EMISchedule(
            id=str(uuid4()),
            loan_account_id=new_loan.id,
            emi_number=sequence,
            due_date=start_date + timedelta(days=30 * sequence),
            emi_amount=emi_amount,
            principal_amount=principal_component,
            interest_amount=interest_component,
        )
        db.add(schedule_entry)

    db.commit()
    return new_loan


@app.get("/health")
async def health():
    return {"status": "ok", "service": "lms"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.get("/loans/{loan_id}", response_model=LoanAccountResponse)
async def get_loan(
    loan_id: str,
    db: Session = Depends(get_db)
):
    """Get loan account details."""
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    return loan


@app.get("/loans")
async def list_loans(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """List loans with optional filters."""
    query = db.query(LoanAccount)
    
    if customer_id:
        query = query.filter(LoanAccount.customer_id == customer_id)
    
    if status:
        query = query.filter(LoanAccount.status == status)
    
    total = query.count()
    loans = query.offset(skip).limit(limit).all()
    
    return {
        "items": loans,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.get("/loans/{loan_id}/emi-schedule")
async def get_emi_schedule(
    loan_id: str,
    db: Session = Depends(get_db)
):
    """Get EMI schedule for a loan."""
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    schedule = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_id
    ).order_by(EMISchedule.emi_number).all()
    
    return {
        "loan_id": loan_id,
        "total_emis": loan.tenure_months,
        "emi_amount": loan.emi_amount,
        "schedule": schedule
    }


@app.post("/loans/{loan_id}/payment", response_model=PaymentResponse)
async def record_payment(
    loan_id: str,
    payment: PaymentRequest,
    db: Session = Depends(get_db)
):
    """Record payment for a loan."""
    from uuid import uuid4
    
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Create payment transaction
    transaction_id = str(uuid4())
    
    # Calculate allocation (simplified)
    interest_due = loan.outstanding_interest
    principal_paid = max(0, payment.amount - interest_due)
    interest_paid = min(payment.amount, interest_due)
    
    # Update loan
    loan.outstanding_interest = max(0, loan.outstanding_interest - interest_paid)
    loan.outstanding_principal = max(0, loan.outstanding_principal - principal_paid)
    
    # Create transaction
    transaction = PaymentTransaction(
        id=transaction_id,
        loan_account_id=loan_id,
        payment_mode=payment.payment_mode,
        amount=payment.amount,
        principal_paid=principal_paid,
        interest_paid=interest_paid,
        reference=payment.reference,
        status="success"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Phase 1 wiring: on successful payment, log repayment activity in Collections (best-effort)
    try:
        import httpx

        collections_base = os.getenv("COLLECTIONS_BASE_URL", "http://localhost:8004")

        # Collections expects: POST /loan/{loan_id}/activity with activity_type, notes, promised_amount?, promised_date?, customer_response
        httpx_payload = {
            "activity_type": "repayment",
            "notes": f"Payment received: ref={payment.reference}",
            "promised_amount": None,
            "promised_date": None,
            "customer_response": "paid"
        }

        with httpx.Client(timeout=5.0) as client:
            client.post(f"{collections_base}/loan/{loan_id}/activity", json=httpx_payload)
    except Exception:
        # Do not fail LMS payment on downstream collections logging
        pass

    return {
        "transaction_id": transaction_id,
        "status": "success",
        "amount": payment.amount,
        "transaction_date": transaction.transaction_date
    }



@app.get("/loans/{loan_id}/payments")
async def get_payment_history(
    loan_id: str,
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get payment history for a loan."""
    payments = db.query(PaymentTransaction).filter(
        PaymentTransaction.loan_account_id == loan_id
    ).order_by(PaymentTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "loan_id": loan_id,
        "payments": payments,
        "count": len(payments)
    }


@app.post("/loans/{loan_id}/foreclose")
async def foreclose_loan(
    loan_id: str,
    db: Session = Depends(get_db)
):
    """Foreclose a loan."""
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Calculate foreclosure amount (outstanding principal + interest + charges)
    foreclosure_amount = loan.outstanding_principal + loan.outstanding_interest
    
    return {
        "loan_id": loan_id,
        "foreclosure_amount": foreclosure_amount,
        "message": "Foreclosure quote generated"
    }


@app.get("/")
async def root():
    return {"service": "lms", "version": "0.1.0"}
