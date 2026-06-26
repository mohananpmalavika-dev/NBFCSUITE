from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, String, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(String, primary_key=True)
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    buy_rate = Column(Float)
    sell_rate = Column(Float)
    provider = Column(String, default="manual")
    effective_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class CashInventory(Base):
    __tablename__ = "cash_inventory"
    __table_args__ = (UniqueConstraint("branch_id", "currency", name="uq_cash_inventory_branch_currency"),)

    id = Column(String, primary_key=True)
    branch_id = Column(String, index=True)
    currency = Column(String, index=True)
    cash_on_hand = Column(Float, default=0.0)
    reserved_amount = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ForexTransaction(Base):
    __tablename__ = "forex_transactions"

    id = Column(String, primary_key=True)
    branch_id = Column(String, index=True)
    customer_id = Column(String, index=True, nullable=True)
    transaction_type = Column(String)
    base_currency = Column(String)
    quote_currency = Column(String)
    base_amount = Column(Float)
    quote_amount = Column(Float)
    rate_applied = Column(Float)
    status = Column(String, default="completed")
    reference = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExchangeRateCreate(BaseModel):
    base_currency: str
    quote_currency: str = "INR"
    buy_rate: float = Field(gt=0)
    sell_rate: float = Field(gt=0)
    provider: str = "manual"


class ExchangeRateResponse(BaseModel):
    id: str
    base_currency: str
    quote_currency: str
    buy_rate: float
    sell_rate: float
    provider: str
    effective_at: datetime

    class Config:
        from_attributes = True


class CashInventoryAdjust(BaseModel):
    branch_id: str
    currency: str
    amount: float
    movement_type: str = Field(pattern="^(inflow|outflow|reserve|release)$")


class CashInventoryResponse(BaseModel):
    id: str
    branch_id: str
    currency: str
    cash_on_hand: float
    reserved_amount: float
    updated_at: datetime

    class Config:
        from_attributes = True


class ForexTransactionCreate(BaseModel):
    branch_id: str
    customer_id: Optional[str] = None
    transaction_type: str = Field(pattern="^(buy|sell)$")
    base_currency: str
    quote_currency: str = "INR"
    base_amount: float = Field(gt=0)
    reference: Optional[str] = None


class ForexTransactionResponse(BaseModel):
    id: str
    branch_id: str
    customer_id: Optional[str]
    transaction_type: str
    base_currency: str
    quote_currency: str
    base_amount: float
    quote_amount: float
    rate_applied: float
    status: str
    reference: str
    created_at: datetime

    class Config:
        from_attributes = True


app = FastAPI(title="treasury-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "treasury"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def _latest_rate(base_currency: str, quote_currency: str, db: Session) -> ExchangeRate:
    rate = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency == base_currency.upper(),
            ExchangeRate.quote_currency == quote_currency.upper(),
        )
        .order_by(ExchangeRate.effective_at.desc())
        .first()
    )
    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    return rate


def _inventory(branch_id: str, currency: str, db: Session) -> CashInventory:
    currency = currency.upper()
    record = (
        db.query(CashInventory)
        .filter(CashInventory.branch_id == branch_id, CashInventory.currency == currency)
        .first()
    )
    if record:
        return record
    record = CashInventory(id=str(uuid4()), branch_id=branch_id, currency=currency)
    db.add(record)
    db.flush()
    return record


@app.post("/exchange-rates", response_model=ExchangeRateResponse)
async def upsert_exchange_rate(rate: ExchangeRateCreate, db: Session = Depends(get_db)):
    if rate.sell_rate < rate.buy_rate:
        raise HTTPException(status_code=400, detail="sell_rate must be greater than or equal to buy_rate")
    record = ExchangeRate(
        id=str(uuid4()),
        base_currency=rate.base_currency.upper(),
        quote_currency=rate.quote_currency.upper(),
        buy_rate=rate.buy_rate,
        sell_rate=rate.sell_rate,
        provider=rate.provider,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/exchange-rates/{base_currency}/{quote_currency}", response_model=ExchangeRateResponse)
async def get_exchange_rate(base_currency: str, quote_currency: str = "INR", db: Session = Depends(get_db)):
    return _latest_rate(base_currency, quote_currency, db)


@app.post("/cash-inventory/adjust", response_model=CashInventoryResponse)
async def adjust_cash_inventory(adjustment: CashInventoryAdjust, db: Session = Depends(get_db)):
    record = _inventory(adjustment.branch_id, adjustment.currency, db)
    if adjustment.movement_type == "inflow":
        record.cash_on_hand = round(record.cash_on_hand + adjustment.amount, 2)
    elif adjustment.movement_type == "outflow":
        if record.cash_on_hand - record.reserved_amount < adjustment.amount:
            raise HTTPException(status_code=400, detail="Insufficient available cash")
        record.cash_on_hand = round(record.cash_on_hand - adjustment.amount, 2)
    elif adjustment.movement_type == "reserve":
        if record.cash_on_hand - record.reserved_amount < adjustment.amount:
            raise HTTPException(status_code=400, detail="Insufficient available cash to reserve")
        record.reserved_amount = round(record.reserved_amount + adjustment.amount, 2)
    elif adjustment.movement_type == "release":
        record.reserved_amount = round(max(0.0, record.reserved_amount - adjustment.amount), 2)
    db.commit()
    db.refresh(record)
    return record


@app.get("/cash-inventory", response_model=List[CashInventoryResponse])
async def list_cash_inventory(
    branch_id: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(CashInventory)
    if branch_id:
        query = query.filter(CashInventory.branch_id == branch_id)
    if currency:
        query = query.filter(CashInventory.currency == currency.upper())
    return query.order_by(CashInventory.branch_id.asc(), CashInventory.currency.asc()).all()


@app.post("/forex-transactions", response_model=ForexTransactionResponse)
async def create_forex_transaction(transaction: ForexTransactionCreate, db: Session = Depends(get_db)):
    rate = _latest_rate(transaction.base_currency, transaction.quote_currency, db)
    rate_applied = rate.buy_rate if transaction.transaction_type == "buy" else rate.sell_rate
    quote_amount = round(transaction.base_amount * rate_applied, 2)
    base_inventory = _inventory(transaction.branch_id, transaction.base_currency, db)
    quote_inventory = _inventory(transaction.branch_id, transaction.quote_currency, db)

    if transaction.transaction_type == "buy":
        if quote_inventory.cash_on_hand - quote_inventory.reserved_amount < quote_amount:
            raise HTTPException(status_code=400, detail="Insufficient quote currency cash")
        base_inventory.cash_on_hand = round(base_inventory.cash_on_hand + transaction.base_amount, 2)
        quote_inventory.cash_on_hand = round(quote_inventory.cash_on_hand - quote_amount, 2)
    else:
        if base_inventory.cash_on_hand - base_inventory.reserved_amount < transaction.base_amount:
            raise HTTPException(status_code=400, detail="Insufficient base currency cash")
        base_inventory.cash_on_hand = round(base_inventory.cash_on_hand - transaction.base_amount, 2)
        quote_inventory.cash_on_hand = round(quote_inventory.cash_on_hand + quote_amount, 2)

    record = ForexTransaction(
        id=str(uuid4()),
        branch_id=transaction.branch_id,
        customer_id=transaction.customer_id,
        transaction_type=transaction.transaction_type,
        base_currency=transaction.base_currency.upper(),
        quote_currency=transaction.quote_currency.upper(),
        base_amount=transaction.base_amount,
        quote_amount=quote_amount,
        rate_applied=rate_applied,
        reference=transaction.reference or f"FX-{str(uuid4())[:10].upper()}",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/forex-transactions", response_model=List[ForexTransactionResponse])
async def list_forex_transactions(
    branch_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(ForexTransaction)
    if branch_id:
        query = query.filter(ForexTransaction.branch_id == branch_id)
    if customer_id:
        query = query.filter(ForexTransaction.customer_id == customer_id)
    return query.order_by(ForexTransaction.created_at.desc()).all()


@app.get("/treasury/branch-summary/{branch_id}")
async def branch_treasury_summary(branch_id: str, db: Session = Depends(get_db)):
    inventory = db.query(CashInventory).filter(CashInventory.branch_id == branch_id).all()
    transactions = db.query(ForexTransaction).filter(ForexTransaction.branch_id == branch_id).all()
    return {
        "branch_id": branch_id,
        "inventory": inventory,
        "forex_transaction_count": len(transactions),
        "total_quote_turnover": round(sum(transaction.quote_amount for transaction in transactions), 2),
        "generated_at": datetime.utcnow(),
    }


@app.get("/")
async def root():
    return {"service": "treasury", "version": "0.1.0"}
