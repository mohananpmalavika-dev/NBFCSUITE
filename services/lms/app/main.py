from fastapi import FastAPI, Depends, HTTPException, Query, Header
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal
import os
import jwt

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
AUTH_SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
AUTH_ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Models
class LoanAccount(Base):
    __tablename__ = "loan_accounts"
    
    id = Column(String, primary_key=True)
    application_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    branch_id = Column(String, index=True, nullable=True)
    product_id = Column(String)
    account_number = Column("loan_account_number", String, unique=True, index=True)
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
    penalty_paid = Column(Float, default=0)
    reference = Column("transaction_reference", String)
    status = Column("payment_status", String)


# Pydantic Schemas
class EMIScheduleResponse(BaseModel):
    emi_number: int
    due_date: datetime
    emi_amount: float
    principal_amount: float
    interest_amount: float
    penalty_amount: float = 0.0
    status: str
    
    class Config:
        from_attributes = True


class LoanAccountResponse(BaseModel):
    id: str
    account_number: str
    application_id: str
    customer_id: str
    branch_id: Optional[str] = None
    sanction_amount: float
    disbursed_amount: float
    outstanding_principal: float
    outstanding_interest: float
    status: str
    emi_amount: float
    
    class Config:
        from_attributes = True


class LoanAccountCreate(BaseModel):
    application_id: str
    customer_id: str
    branch_id: Optional[str] = None
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


class DisbursementRequest(BaseModel):
    amount: Optional[float] = None
    reference: Optional[str] = None


class DisbursementResponse(BaseModel):
    loan_id: str
    account_number: str
    disbursed_amount: float
    status: str


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    transaction_date: datetime
    
    class Config:
        from_attributes = True


class OverdueComputationResponse(BaseModel):
    loan_id: str
    branch_id: Optional[str] = None
    days_past_due: int
    overdue_emi_count: int
    overdue_amount: float
    penalty_amount: float
    status: str


# FastAPI App
app = FastAPI(title="lms-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PrincipalScope:
    def __init__(self, branch_id: Optional[str] = None):
        self.branch_id = branch_id

    @property
    def is_scoped(self) -> bool:
        return bool(self.branch_id)


def get_principal_scope(
    authorization: Optional[str] = Header(default=None),
    branch_id: Optional[str] = Header(default=None, alias="X-Scope-Branch-Id"),
    legacy_branch_id: Optional[str] = Header(default=None, alias="X-Branch-Id"),
) -> PrincipalScope:
    if authorization:
        if not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        try:
            payload = jwt.decode(authorization.split(" ", 1)[1], AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return PrincipalScope(branch_id=payload.get("branch_id"))
    return PrincipalScope(branch_id=branch_id or legacy_branch_id)


def _assert_loan_in_scope(loan: LoanAccount, scope: PrincipalScope) -> None:
    if not isinstance(scope, PrincipalScope):
        return
    if scope.is_scoped and loan.branch_id != scope.branch_id:
        raise HTTPException(status_code=403, detail="Loan is outside the caller's branch scope")


def _resolve_branch_id(requested_branch_id: Optional[str], scope: PrincipalScope) -> Optional[str]:
    if not isinstance(scope, PrincipalScope):
        return requested_branch_id
    if scope.is_scoped and requested_branch_id and requested_branch_id != scope.branch_id:
        raise HTTPException(status_code=403, detail="Branch is outside the caller's branch scope")
    return requested_branch_id or scope.branch_id


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


def build_amortization_schedule(principal: float, annual_rate: float, tenure_months: int):
    emi_amount = round(calculate_emi(principal, annual_rate, tenure_months), 2)
    monthly_rate = annual_rate / 100 / 12
    outstanding = principal
    rows = []
    for sequence in range(1, tenure_months + 1):
        interest_component = round(outstanding * monthly_rate, 2)
        principal_component = round(emi_amount - interest_component, 2)
        if sequence == tenure_months:
            principal_component = round(outstanding, 2)
            emi_for_row = round(principal_component + interest_component, 2)
        else:
            emi_for_row = emi_amount
        outstanding = round(max(0.0, outstanding - principal_component), 2)
        rows.append(
            {
                "emi_number": sequence,
                "emi_amount": emi_for_row,
                "principal_amount": principal_component,
                "interest_amount": interest_component,
            }
        )
    return emi_amount, rows


def trigger_findna_assistant(customer_id: str, assistant_type: str, source_reference_id: str, context_text: str) -> None:
    """Best-effort FinDNA assistant hook; LMS operations must remain primary."""
    try:
        import httpx

        findna_base = os.getenv("FINDNA_BASE_URL", "http://localhost:8006")
        endpoint = "relationship-manager" if assistant_type == "relationship" else "collections-assistant"
        payload = {
            "customer_id": customer_id,
            "subject_type": "customer",
            "subject_id": customer_id,
            "source_service": "lms",
            "source_reference_id": source_reference_id,
            "context_text": context_text,
        }
        with httpx.Client(timeout=5.0) as client:
            client.post(f"{findna_base}/{endpoint}/{customer_id}", json=payload)
    except Exception:
        pass


def post_accounting_event(
    source_module: str,
    source_event: str,
    amount: float,
    source_reference: str,
    idempotency_key: str,
    tenant_id: str,
    metadata: Optional[dict] = None,
) -> None:
    """Best-effort accounting posting hook; should not block core LMS flows."""
    try:
        import httpx

        accounting_base = os.getenv("ACCOUNTING_BASE_URL", "http://localhost:8008")
        payload = {
            "tenant_id": tenant_id,
            "source_module": source_module,
            "source_event": source_event,
            "source_reference": source_reference,
            "amount": amount,
            "idempotency_key": idempotency_key,
            "metadata": metadata,
        }
        with httpx.Client(timeout=5.0) as client:
            client.post(f"{accounting_base}/gl-postings/auto", json=payload)
    except Exception:
        pass


@app.post("/loans", response_model=LoanAccountResponse)
async def create_loan(
    loan_data: LoanAccountCreate,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    from uuid import uuid4

    existing = db.query(LoanAccount).filter(LoanAccount.application_id == loan_data.application_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Loan already exists for this application")

    branch_id = _resolve_branch_id(loan_data.branch_id, scope)
    account_number = f"LA-{str(uuid4())[:8].upper()}"
    if loan_data.sanction_amount <= 0:
        raise HTTPException(status_code=400, detail="sanction_amount must be positive")
    if loan_data.tenure_months <= 0:
        raise HTTPException(status_code=400, detail="tenure_months must be positive")
    if loan_data.interest_rate < 0:
        raise HTTPException(status_code=400, detail="interest_rate cannot be negative")

    emi_amount, amortization_rows = build_amortization_schedule(
        loan_data.sanction_amount,
        loan_data.interest_rate,
        loan_data.tenure_months,
    )
    start_date = loan_data.start_date or datetime.utcnow()
    end_date = start_date + timedelta(days=30 * loan_data.tenure_months)
    outstanding_interest = round(sum(row["interest_amount"] for row in amortization_rows), 2)

    new_loan = LoanAccount(
        id=str(uuid4()),
        application_id=loan_data.application_id,
        customer_id=loan_data.customer_id,
        branch_id=branch_id,
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
        status="active" if loan_data.disbursed_amount > 0 else "sanctioned",
    )

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)

    for row in amortization_rows:
        schedule_entry = EMISchedule(
            id=str(uuid4()),
            loan_account_id=new_loan.id,
            emi_number=row["emi_number"],
            due_date=start_date + timedelta(days=30 * row["emi_number"]),
            emi_amount=row["emi_amount"],
            principal_amount=row["principal_amount"],
            interest_amount=row["interest_amount"],
        )
        db.add(schedule_entry)

    db.commit()
    trigger_findna_assistant(
        customer_id=new_loan.customer_id,
        assistant_type="relationship",
        source_reference_id=new_loan.id,
        context_text=(
            f"LMS loan booked: account={new_loan.account_number}, "
            f"sanction_amount={new_loan.sanction_amount}, emi={new_loan.emi_amount}"
        ),
    )
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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Get loan account details."""
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)
    
    return loan


@app.get("/loans")
async def list_loans(
    customer_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """List loans with optional filters."""
    query = db.query(LoanAccount)
    
    if customer_id:
        query = query.filter(LoanAccount.customer_id == customer_id)
    selected_branch_id = _resolve_branch_id(branch_id, scope)
    if selected_branch_id:
        query = query.filter(LoanAccount.branch_id == selected_branch_id)
    
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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Get EMI schedule for a loan."""
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)
    
    schedule = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_id
    ).order_by(EMISchedule.emi_number).all()
    
    return {
        "loan_id": loan_id,
        "total_emis": loan.tenure_months,
        "emi_amount": loan.emi_amount,
        "schedule": schedule
    }


@app.post("/loans/{loan_id}/disburse", response_model=DisbursementResponse)
async def disburse_loan(
    loan_id: str,
    disbursement: DisbursementRequest,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)
    if loan.status not in {"active", "sanctioned"}:
        raise HTTPException(status_code=400, detail="Loan is not eligible for disbursement")

    amount = disbursement.amount if disbursement.amount is not None else loan.sanction_amount
    if loan.disbursed_amount >= loan.sanction_amount and amount == loan.sanction_amount:
        return {
            "loan_id": loan.id,
            "account_number": loan.account_number,
            "disbursed_amount": loan.disbursed_amount,
            "status": loan.status,
        }
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Disbursement amount must be positive")
    if loan.disbursed_amount + amount > loan.sanction_amount:
        raise HTTPException(status_code=400, detail="Disbursement exceeds sanctioned amount")

    loan.disbursed_amount = round(loan.disbursed_amount + amount, 2)
    loan.status = "active"
    db.commit()
    db.refresh(loan)

    try:
        import httpx

        los_base = os.getenv("LOS_BASE_URL", "http://localhost:8002")
        with httpx.Client(timeout=5.0) as client:
            client.post(
                f"{los_base}/applications/{loan.application_id}/disburse",
                params={"amount": loan.disbursed_amount},
                headers={"X-Scope-Branch-Id": loan.branch_id} if loan.branch_id else None,
            )
    except Exception:
        pass

    tenant_id = loan.branch_id or loan.customer_id or "default"
    post_accounting_event(
        source_module="loans",
        source_event="disbursement",
        amount=loan.disbursed_amount,
        source_reference=loan.id,
        idempotency_key=f"lms-disbursement-{loan.id}-{loan.disbursed_amount}",
        tenant_id=tenant_id,
        metadata={"application_id": loan.application_id, "branch_id": loan.branch_id},
    )

    return {
        "loan_id": loan.id,
        "account_number": loan.account_number,
        "disbursed_amount": loan.disbursed_amount,
        "status": loan.status,
    }


@app.post("/loans/{loan_id}/payment", response_model=PaymentResponse)
async def record_payment(
    loan_id: str,
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Record payment for a loan."""
    from uuid import uuid4
    
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")
    existing_payment = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.loan_account_id == loan_id, PaymentTransaction.reference == payment.reference)
        .first()
    )
    if existing_payment:
        return {
            "transaction_id": existing_payment.id,
            "status": existing_payment.status,
            "amount": existing_payment.amount,
            "transaction_date": existing_payment.transaction_date,
        }
    
    # Create payment transaction
    transaction_id = str(uuid4())
    
    interest_due = loan.outstanding_interest
    interest_paid = round(min(payment.amount, interest_due), 2)
    principal_paid = round(min(loan.outstanding_principal, max(0, payment.amount - interest_paid)), 2)
    
    # Update loan
    loan.outstanding_interest = round(max(0, loan.outstanding_interest - interest_paid), 2)
    loan.outstanding_principal = round(max(0, loan.outstanding_principal - principal_paid), 2)
    if loan.outstanding_principal == 0 and loan.outstanding_interest == 0:
        loan.status = "closed"

    remaining_payment = payment.amount
    pending_emis = db.query(EMISchedule).filter(
        EMISchedule.loan_account_id == loan_id,
        EMISchedule.status == "pending",
    ).order_by(EMISchedule.emi_number).all()
    for emi in pending_emis:
        due_amount = round((emi.emi_amount or 0) + (emi.penalty_amount or 0), 2)
        if remaining_payment + 0.01 < due_amount:
            break
        emi.status = "paid"
        emi.paid_date = datetime.utcnow()
        remaining_payment = round(remaining_payment - due_amount, 2)
    
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

    tenant_id = loan.branch_id or loan.customer_id or "default"
    post_accounting_event(
        source_module="loans",
        source_event="payment",
        amount=payment.amount,
        source_reference=transaction_id,
        idempotency_key=f"lms-payment-{transaction_id}",
        tenant_id=tenant_id,
        metadata={"loan_id": loan_id, "reference": payment.reference},
    )

    trigger_findna_assistant(
        customer_id=loan.customer_id,
        assistant_type="collections",
        source_reference_id=transaction_id,
        context_text=(
            f"LMS payment recorded: loan_id={loan_id}, amount={payment.amount}, "
            f"principal_paid={principal_paid}, interest_paid={interest_paid}, "
            f"outstanding_principal={loan.outstanding_principal}"
        ),
    )

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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Get payment history for a loan."""
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)
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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Foreclose a loan."""
    loan = db.query(LoanAccount).filter(
        LoanAccount.id == loan_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)
    
    # Calculate foreclosure amount (outstanding principal + interest + charges)
    foreclosure_amount = loan.outstanding_principal + loan.outstanding_interest
    
    return {
        "loan_id": loan_id,
        "foreclosure_amount": foreclosure_amount,
        "message": "Foreclosure quote generated"
    }


@app.post("/loans/{loan_id}/compute-overdue", response_model=OverdueComputationResponse)
async def compute_loan_overdue(
    loan_id: str,
    as_of: Optional[datetime] = Query(None),
    penalty_rate_per_day: float = Query(0.001, ge=0),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    _assert_loan_in_scope(loan, scope)

    effective_date = as_of or datetime.utcnow()
    overdue_emis = (
        db.query(EMISchedule)
        .filter(
            EMISchedule.loan_account_id == loan_id,
            EMISchedule.status.in_(["pending", "overdue"]),
            EMISchedule.due_date < effective_date,
        )
        .order_by(EMISchedule.due_date.asc())
        .all()
    )

    max_dpd = 0
    overdue_amount = 0.0
    penalty_amount = 0.0
    for emi in overdue_emis:
        days_past_due = max(0, (effective_date - emi.due_date).days)
        max_dpd = max(max_dpd, days_past_due)
        emi.status = "overdue"
        emi.penalty_amount = round((emi.emi_amount or 0) * penalty_rate_per_day * days_past_due, 2)
        overdue_amount += emi.emi_amount or 0
        penalty_amount += emi.penalty_amount or 0

    if overdue_emis and loan.status not in {"closed", "written_off"}:
        loan.status = "delinquent"

    db.commit()

    if overdue_emis:
        try:
            import httpx

            collections_base = os.getenv("COLLECTIONS_BASE_URL", "http://localhost:8004")
            payload = {
                "loan_account_id": loan.id,
                "customer_id": loan.customer_id,
                "collector_user_id": "unassigned",
                "branch_id": loan.branch_id,
                "days_past_due": max_dpd,
                "outstanding_amount": round((loan.outstanding_principal or 0) + (loan.outstanding_interest or 0), 2),
                "priority": "high" if max_dpd >= 60 else "medium",
            }
            with httpx.Client(timeout=5.0) as client:
                client.post(f"{collections_base}/assignments", json=payload)
        except Exception:
            pass

    return OverdueComputationResponse(
        loan_id=loan.id,
        branch_id=loan.branch_id,
        days_past_due=max_dpd,
        overdue_emi_count=len(overdue_emis),
        overdue_amount=round(overdue_amount, 2),
        penalty_amount=round(penalty_amount, 2),
        status=loan.status,
    )


@app.get("/")
async def root():
    return {"service": "lms", "version": "0.1.0"}
