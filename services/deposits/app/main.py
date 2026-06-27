from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DepositType(Base):
    __tablename__ = "deposit_types"

    id = Column(String, primary_key=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    interest_rate = Column(Float)
    min_balance = Column(Float)
    tenor_months = Column(Integer, nullable=True)
    payout_frequency = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class DepositAccount(Base):
    __tablename__ = "deposit_accounts"

    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    deposit_type_id = Column(String, ForeignKey("deposit_types.id"))
    account_number = Column(String, unique=True, index=True)
    principal_amount = Column(Float)
    current_balance = Column(Float)
    interest_rate = Column(Float)
    start_date = Column(DateTime)
    maturity_date = Column(DateTime)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class DepositTransaction(Base):
    __tablename__ = "deposit_transactions"

    id = Column(String, primary_key=True)
    deposit_account_id = Column(String, ForeignKey("deposit_accounts.id"), index=True)
    transaction_type = Column(String)
    amount = Column(Float)
    running_balance = Column(Float)
    description = Column(String)
    reference = Column(String, nullable=True, index=True)
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StandingInstruction(Base):
    __tablename__ = "standing_instructions"

    id = Column(String, primary_key=True)
    deposit_account_id = Column(String, ForeignKey("deposit_accounts.id"))
    instruction_type = Column(String)
    amount = Column(Float)
    frequency = Column(String)
    next_run_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class DepositTypeResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    interest_rate: float
    min_balance: float
    tenor_months: Optional[int]
    payout_frequency: str

    class Config:
        from_attributes = True


class DepositAccountCreate(BaseModel):
    customer_id: str
    deposit_type_code: str
    principal_amount: float
    start_date: Optional[datetime] = None


class DepositAccountResponse(BaseModel):
    id: str
    customer_id: str
    deposit_type_id: str
    account_number: str
    principal_amount: float
    current_balance: float
    interest_rate: float
    start_date: datetime
    maturity_date: datetime
    status: str

    class Config:
        from_attributes = True


class InterestScheduleResponse(BaseModel):
    deposit_account_id: str
    maturity_amount: float
    total_interest: float
    schedule: List[dict]


class DepositTransactionCreate(BaseModel):
    transaction_type: str = Field(pattern="^(credit|debit|interest|fee)$")
    amount: float = Field(gt=0)
    description: str
    reference: Optional[str] = None
    transaction_date: Optional[datetime] = None
    metadata: Optional[dict] = None


class DepositTransactionResponse(BaseModel):
    id: str
    deposit_account_id: str
    transaction_type: str
    amount: float
    running_balance: float
    description: str
    reference: Optional[str]
    transaction_date: datetime

    class Config:
        from_attributes = True


class StandingInstructionCreate(BaseModel):
    instruction_type: str
    amount: float
    frequency: str
    next_run_date: datetime


class StandingInstructionResponse(BaseModel):
    id: str
    deposit_account_id: str
    instruction_type: str
    amount: float
    frequency: str
    next_run_date: datetime

    class Config:
        from_attributes = True


app = FastAPI(title="deposits-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_interest(principal: float, annual_rate: float, days: int) -> float:
    return round(principal * annual_rate / 100 * max(days, 1) / 365, 2)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    if db.query(DepositType).count() == 0:
        types = [
            DepositType(
                id=str(uuid4()),
                code="CASA",
                name="Savings/Current Account",
                description="Demand deposit account for daily banking",
                interest_rate=3.5,
                min_balance=1000.0,
                tenor_months=None,
                payout_frequency="monthly"
            ),
            DepositType(
                id=str(uuid4()),
                code="FD",
                name="Fixed Deposit",
                description="Fixed deposit with a defined maturity",
                interest_rate=6.8,
                min_balance=5000.0,
                tenor_months=12,
                payout_frequency="maturity"
            ),
            DepositType(
                id=str(uuid4()),
                code="RD",
                name="Recurring Deposit",
                description="Recurring deposit with periodic contributions",
                interest_rate=5.5,
                min_balance=1000.0,
                tenor_months=12,
                payout_frequency="monthly"
            )
        ]
        db.add_all(types)
        db.commit()
    db.close()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "deposits"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.get("/deposit-types", response_model=List[DepositTypeResponse])
async def list_deposit_types(db: Session = Depends(get_db)):
    return db.query(DepositType).all()


@app.post("/deposit-accounts", response_model=DepositAccountResponse)
async def create_deposit_account(account_data: DepositAccountCreate, db: Session = Depends(get_db)):
    deposit_type = db.query(DepositType).filter(DepositType.code == account_data.deposit_type_code).first()
    if not deposit_type:
        raise HTTPException(status_code=404, detail="Deposit type not found")
    if account_data.principal_amount < deposit_type.min_balance:
        raise HTTPException(status_code=400, detail="Principal amount below minimum balance")

    start_date = account_data.start_date or datetime.utcnow()
    maturity_date = start_date + timedelta(days=30 * (deposit_type.tenor_months or 0)) if deposit_type.tenor_months else start_date
    account = DepositAccount(
        id=str(uuid4()),
        customer_id=account_data.customer_id,
        deposit_type_id=deposit_type.id,
        account_number=f"DA-{str(uuid4())[:10].upper()}",
        principal_amount=account_data.principal_amount,
        current_balance=account_data.principal_amount,
        interest_rate=deposit_type.interest_rate,
        start_date=start_date,
        maturity_date=maturity_date,
        status="active"
    )
    db.add(account)
    opening_transaction = DepositTransaction(
        id=str(uuid4()),
        deposit_account_id=account.id,
        transaction_type="credit",
        amount=account_data.principal_amount,
        running_balance=account_data.principal_amount,
        description="Opening deposit",
        reference=f"OPEN-{account.account_number}",
        transaction_date=start_date,
    )
    db.add(opening_transaction)
    db.commit()
    db.refresh(account)

    tenant_id = account.customer_id or "default"
    post_accounting_event(
        source_module="deposits",
        source_event="deposit",
        amount=account_data.principal_amount,
        source_reference=opening_transaction.id,
        idempotency_key=f"deposits-opening-{opening_transaction.id}",
        tenant_id=tenant_id,
        metadata={
            "deposit_account_id": account.id,
            "account_number": account.account_number,
            "reference": opening_transaction.reference,
        },
    )

    return account


@app.get("/deposit-accounts/{account_id}", response_model=DepositAccountResponse)
async def get_deposit_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(DepositAccount).filter(DepositAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Deposit account not found")
    return account


@app.get("/deposit-accounts")
async def list_deposit_accounts(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    query = db.query(DepositAccount)
    if customer_id:
        query = query.filter(DepositAccount.customer_id == customer_id)
    if status:
        query = query.filter(DepositAccount.status == status)
    total = query.count()
    accounts = query.order_by(DepositAccount.created_at.desc()).offset(skip).limit(limit).all()
    return {"items": accounts, "skip": skip, "limit": limit, "total": total}


@app.get("/reports/customer-summary/{customer_id}")
async def customer_deposit_summary(customer_id: str, db: Session = Depends(get_db)):
    accounts = db.query(DepositAccount).filter(DepositAccount.customer_id == customer_id).all()
    by_status: dict[str, int] = {}
    total_principal = 0.0
    weighted_rate_amount = 0.0
    for account in accounts:
        by_status[account.status] = by_status.get(account.status, 0) + 1
        balance = account.current_balance if account.current_balance is not None else account.principal_amount or 0.0
        total_principal += balance
        weighted_rate_amount += balance * (account.interest_rate or 0.0)

    average_interest_rate = round(weighted_rate_amount / total_principal, 2) if total_principal else 0.0
    return {
        "customer_id": customer_id,
        "account_count": len(accounts),
        "total_principal": round(total_principal, 2),
        "average_interest_rate": average_interest_rate,
        "by_status": by_status,
    }


@app.get("/deposit-accounts/{account_id}/interest-schedule", response_model=InterestScheduleResponse)
async def get_interest_schedule(account_id: str, db: Session = Depends(get_db)):
    account = db.query(DepositAccount).filter(DepositAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Deposit account not found")

    days = max(1, (account.maturity_date - account.start_date).days)
    total_interest = calculate_interest(account.principal_amount, account.interest_rate, days)
    schedule = [{
        "date": account.maturity_date,
        "amount": round(account.principal_amount + total_interest, 2)
    }]
    return InterestScheduleResponse(
        deposit_account_id=account.id,
        maturity_amount=round(account.principal_amount + total_interest, 2),
        total_interest=total_interest,
        schedule=schedule,
    )


def _deposit_source_event(transaction_type: str) -> str:
    if transaction_type in {"credit", "interest"}:
        return "deposit"
    return "withdrawal"


def post_accounting_event(
    source_module: str,
    source_event: str,
    amount: float,
    source_reference: str,
    idempotency_key: str,
    tenant_id: str,
    metadata: Optional[dict] = None,
) -> None:
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


@app.post("/deposit-accounts/{account_id}/transactions", response_model=DepositTransactionResponse)
async def create_deposit_transaction(
    account_id: str,
    transaction: DepositTransactionCreate,
    db: Session = Depends(get_db),
):
    account = db.query(DepositAccount).filter(DepositAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Deposit account not found")
    if account.status != "active":
        raise HTTPException(status_code=400, detail="Deposit account is not active")

    current_balance = account.current_balance if account.current_balance is not None else account.principal_amount or 0.0
    signed_amount = transaction.amount if transaction.transaction_type in {"credit", "interest"} else -transaction.amount
    new_balance = round(current_balance + signed_amount, 2)
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient deposit balance")

    account.current_balance = new_balance
    db_transaction = DepositTransaction(
        id=str(uuid4()),
        deposit_account_id=account.id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        running_balance=new_balance,
        description=transaction.description,
        reference=transaction.reference,
        transaction_date=transaction.transaction_date or datetime.utcnow(),
        metadata_=transaction.metadata,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    tenant_id = account.customer_id or "default"
    source_event = _deposit_source_event(transaction.transaction_type)
    post_accounting_event(
        source_module="deposits",
        source_event=source_event,
        amount=transaction.amount,
        source_reference=db_transaction.id,
        idempotency_key=f"deposits-transaction-{db_transaction.id}",
        tenant_id=tenant_id,
        metadata={
            "deposit_account_id": account.id,
            "transaction_type": transaction.transaction_type,
            "reference": transaction.reference,
        },
    )

    return db_transaction


@app.get("/deposit-accounts/{account_id}/transactions", response_model=List[DepositTransactionResponse])
async def list_deposit_transactions(
    account_id: str,
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
):
    account = db.query(DepositAccount).filter(DepositAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Deposit account not found")
    return (
        db.query(DepositTransaction)
        .filter(DepositTransaction.deposit_account_id == account_id)
        .order_by(DepositTransaction.transaction_date.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.get("/deposit-accounts/{account_id}/statement")
async def get_account_statement(
    account_id: str,
    from_date: datetime = Query(...),
    to_date: datetime = Query(...),
    db: Session = Depends(get_db),
):
    account = db.query(DepositAccount).filter(DepositAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Deposit account not found")
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before to_date")

    opening_transaction = (
        db.query(DepositTransaction)
        .filter(
            DepositTransaction.deposit_account_id == account_id,
            DepositTransaction.transaction_date < from_date,
        )
        .order_by(DepositTransaction.transaction_date.desc(), DepositTransaction.created_at.desc())
        .first()
    )
    transactions = (
        db.query(DepositTransaction)
        .filter(
            DepositTransaction.deposit_account_id == account_id,
            DepositTransaction.transaction_date > from_date,
            DepositTransaction.transaction_date <= to_date,
        )
        .order_by(DepositTransaction.transaction_date.asc(), DepositTransaction.created_at.asc())
        .all()
    )

    opening_balance = opening_transaction.running_balance if opening_transaction else account.principal_amount
    closing_balance = transactions[-1].running_balance if transactions else opening_balance
    return {
        "account_id": account.id,
        "account_number": account.account_number,
        "customer_id": account.customer_id,
        "from_date": from_date,
        "to_date": to_date,
        "opening_balance": round(opening_balance, 2),
        "closing_balance": round(closing_balance, 2),
        "transactions": transactions,
    }


@app.post("/deposit-accounts/{account_id}/standing-instructions", response_model=StandingInstructionResponse)
async def add_standing_instruction(account_id: str, instruction: StandingInstructionCreate, db: Session = Depends(get_db)):
    account = db.query(DepositAccount).filter(DepositAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Deposit account not found")

    si = StandingInstruction(
        id=str(uuid4()),
        deposit_account_id=account.id,
        instruction_type=instruction.instruction_type,
        amount=instruction.amount,
        frequency=instruction.frequency,
        next_run_date=instruction.next_run_date
    )
    db.add(si)
    db.commit()
    db.refresh(si)
    return si


@app.get("/deposit-accounts/{account_id}/standing-instructions", response_model=List[StandingInstructionResponse])
async def list_standing_instructions(account_id: str, db: Session = Depends(get_db)):
    return db.query(StandingInstruction).filter(StandingInstruction.deposit_account_id == account_id).all()
