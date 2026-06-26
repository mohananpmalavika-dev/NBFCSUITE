from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GLAccount(Base):
    __tablename__ = "gl_accounts"

    id = Column(String, primary_key=True)
    account_code = Column(String, unique=True, index=True)
    account_name = Column(String)
    account_type = Column(String)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(String, primary_key=True)
    entry_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    reference = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("JournalLine", back_populates="journal_entry")


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id = Column(String, primary_key=True)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"))
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"))
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    journal_entry = relationship("JournalEntry", back_populates="lines")


class BankStatementTransaction(Base):
    __tablename__ = "bank_statement_transactions"

    id = Column(String, primary_key=True)
    reference = Column(String, index=True)
    transaction_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    status = Column(String, default="unmatched")
    matched_journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)


class GLAccountResponse(BaseModel):
    id: str
    account_code: str
    account_name: str
    account_type: str
    balance: float

    class Config:
        from_attributes = True


class GLAccountCreate(BaseModel):
    account_code: str
    account_name: str
    account_type: str


class JournalLineCreate(BaseModel):
    gl_account_id: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None
    lines: List[JournalLineCreate]


class JournalEntryResponse(BaseModel):
    id: str
    entry_date: datetime
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class BankTransactionCreate(BaseModel):
    reference: str
    transaction_date: datetime
    amount: float
    description: str


class ReconciliationRequest(BaseModel):
    transaction_id: str
    journal_entry_id: str


class BankStatementResponse(BaseModel):
    id: str
    reference: str
    transaction_date: datetime
    amount: float
    description: str
    status: str

    class Config:
        from_attributes = True


app = FastAPI(title="accounting-service", version="0.1.0")


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
    return {"status": "ok", "service": "accounting"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/gl-accounts", response_model=GLAccountResponse)
async def create_gl_account(account: GLAccountCreate, db: Session = Depends(get_db)):
    existing = db.query(GLAccount).filter(GLAccount.account_code == account.account_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="GL account code already exists")

    new_account = GLAccount(
        id=str(uuid4()),
        account_code=account.account_code,
        account_name=account.account_name,
        account_type=account.account_type,
        balance=0.0
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@app.get("/gl-accounts", response_model=List[GLAccountResponse])
async def list_gl_accounts(db: Session = Depends(get_db)):
    return db.query(GLAccount).all()


@app.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(entry: JournalEntryCreate, db: Session = Depends(get_db)):
    if not entry.lines or len(entry.lines) < 2:
        raise HTTPException(status_code=400, detail="Journal entry must contain at least two lines")

    total_debit = sum(line.debit for line in entry.lines)
    total_credit = sum(line.credit for line in entry.lines)
    if round(total_debit, 2) != round(total_credit, 2):
        raise HTTPException(status_code=400, detail="Journal entry must be balanced")

    journal_entry = JournalEntry(
        id=str(uuid4()),
        entry_date=datetime.utcnow(),
        description=entry.description,
        reference=entry.reference,
        metadata=entry.metadata
    )
    db.add(journal_entry)
    db.commit()

    for line in entry.lines:
        gl_account = db.query(GLAccount).filter(GLAccount.id == line.gl_account_id).first()
        if not gl_account:
            raise HTTPException(status_code=404, detail=f"GL account {line.gl_account_id} not found")

        journal_line = JournalLine(
            id=str(uuid4()),
            journal_entry_id=journal_entry.id,
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            description=line.description
        )
        db.add(journal_line)
        if line.debit:
            gl_account.balance += line.debit
        if line.credit:
            gl_account.balance -= line.credit

    db.commit()
    db.refresh(journal_entry)
    return journal_entry


@app.get("/journal-entries")
async def list_journal_entries(
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(JournalEntry).offset(skip).limit(limit).all()
    return {"items": query, "skip": skip, "limit": limit, "total": len(query)}


@app.get("/gl-balances")
async def gl_balances(db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).all()
    return {"accounts": accounts}


@app.post("/bank-transactions", response_model=BankStatementResponse)
async def add_bank_transaction(transaction: BankTransactionCreate, db: Session = Depends(get_db)):
    existing = db.query(BankStatementTransaction).filter(BankStatementTransaction.reference == transaction.reference).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bank transaction reference already exists")

    bank_tx = BankStatementTransaction(
        id=str(uuid4()),
        reference=transaction.reference,
        transaction_date=transaction.transaction_date,
        amount=transaction.amount,
        description=transaction.description,
        status="unmatched"
    )
    db.add(bank_tx)
    db.commit()
    db.refresh(bank_tx)
    return bank_tx


@app.post("/bank-reconciliation")
async def reconcile_bank_transaction(request: ReconciliationRequest, db: Session = Depends(get_db)):
    transaction = db.query(BankStatementTransaction).filter(BankStatementTransaction.id == request.transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Bank transaction not found")

    journal_entry = db.query(JournalEntry).filter(JournalEntry.id == request.journal_entry_id).first()
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    transaction.matched_journal_id = journal_entry.id
    transaction.status = "matched"
    db.commit()
    return {"transaction_id": transaction.id, "status": transaction.status, "matched_journal_id": transaction.matched_journal_id}


@app.get("/bank-transactions")
async def list_bank_transactions(db: Session = Depends(get_db)):
    transactions = db.query(BankStatementTransaction).all()
    return {"transactions": transactions}
