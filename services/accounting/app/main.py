from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, JSON, UniqueConstraint
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
    __table_args__ = (
        UniqueConstraint("tenant_id", "account_code", name="uq_gl_accounts_tenant_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    account_code = Column(String, index=True, nullable=False)
    account_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)



class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_journal_entries_tenant_idempotency"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    entry_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    reference = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    posting_status = Column(String, default="posted", index=True)
    idempotency_key = Column(String, nullable=True, index=True)
    source_module = Column(String, nullable=True, index=True)
    source_event = Column(String, nullable=True, index=True)
    source_reference = Column(String, nullable=True, index=True)
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
    __table_args__ = (
        UniqueConstraint("tenant_id", "reference", name="uq_bank_statement_transactions_tenant_reference"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    reference = Column(String, index=True)
    transaction_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    status = Column(String, default="unmatched")
    matched_journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)


class TaxRule(Base):
    __tablename__ = "tax_rules"
    __table_args__ = (
        UniqueConstraint("tenant_id", "tax_code", name="uq_tax_rules_tenant_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    tax_code = Column(String, index=True)
    tax_type = Column(String)
    rate_percent = Column(Float)
    payable_gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=True)
    payable_gl_account_code = Column(String, nullable=True)
    expense_gl_account_code = Column(String, nullable=True)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxComputation(Base):
    __tablename__ = "tax_computations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    tax_rule_id = Column(String, ForeignKey("tax_rules.id"))
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    source_module = Column(String)
    source_reference = Column(String)
    taxable_amount = Column(Float)
    tax_amount = Column(Float)
    breakdown = Column(JSON, nullable=True)
    status = Column(String, default="computed")
    created_at = Column(DateTime, default=datetime.utcnow)


class PostingRule(Base):
    __tablename__ = "posting_rules"
    __table_args__ = (
        UniqueConstraint("tenant_id", "source_module", "source_event", name="uq_posting_rules_tenant_source"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    source_module = Column(String, index=True, nullable=False)
    source_event = Column(String, index=True, nullable=False)
    debit_account_code = Column(String, nullable=False)
    credit_account_code = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    performed_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubLedgerEntry(Base):
    __tablename__ = "sub_ledger_entries"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    source_module = Column(String, nullable=False)
    source_event = Column(String, nullable=False)
    source_reference = Column(String, nullable=False)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    amount = Column(Float, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GLAccountResponse(BaseModel):
    id: str
    tenant_id: str
    account_code: str
    account_name: str
    account_type: str
    balance: float

    class Config:
        from_attributes = True


class GLAccountCreate(BaseModel):
    tenant_id: str
    account_code: str
    account_name: str
    account_type: str



class JournalLineCreate(BaseModel):
    gl_account_id: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    tenant_id: str
    entry_date: Optional[datetime] = None
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None
    lines: List[JournalLineCreate]


class JournalEntryResponse(BaseModel):
    id: str
    tenant_id: str
    entry_date: datetime
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None
    posting_status: str
    idempotency_key: Optional[str] = None
    source_module: Optional[str] = None
    source_event: Optional[str] = None
    source_reference: Optional[str] = None

    class Config:
        from_attributes = True


class PostingRuleCreate(BaseModel):
    tenant_id: str
    source_module: str
    source_event: str
    debit_account_code: str
    credit_account_code: str
    description: Optional[str] = None


class PostingRuleResponse(BaseModel):
    id: str
    tenant_id: str
    source_module: str
    source_event: str
    debit_account_code: str
    credit_account_code: str
    description: Optional[str] = None
    is_active: str

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str
    entity: str
    entity_id: Optional[str] = None
    action: str
    payload: Optional[dict] = None
    performed_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubLedgerEntryResponse(BaseModel):
    id: str
    tenant_id: str
    source_module: str
    source_event: str
    source_reference: str
    journal_entry_id: Optional[str] = None
    amount: float
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BankTransactionCreate(BaseModel):
    tenant_id: str
    reference: str
    transaction_date: datetime
    amount: float
    description: str



class AutomatedGLPostingRequest(BaseModel):
    tenant_id: str
    idempotency_key: Optional[str] = None
    source_module: str
    source_event: str
    source_reference: str
    amount: float
    description: Optional[str] = None

    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    metadata: Optional[dict] = None


class TaxRuleCreate(BaseModel):
    tenant_id: str
    tax_code: str
    tax_type: str
    rate_percent: float
    payable_gl_account_id: Optional[str] = None
    payable_gl_account_code: Optional[str] = None
    expense_gl_account_code: Optional[str] = None


class TaxRuleResponse(BaseModel):
    id: str
    tenant_id: str
    tax_code: str
    tax_type: str
    rate_percent: float
    payable_gl_account_id: Optional[str]
    payable_gl_account_code: Optional[str]
    expense_gl_account_code: Optional[str]
    is_active: str

    class Config:
        from_attributes = True


class TaxComputationRequest(BaseModel):
    tenant_id: str
    tax_code: str
    source_module: str
    source_reference: str
    taxable_amount: float


class TaxComputationResponse(BaseModel):
    id: str
    tenant_id: str
    journal_entry_id: Optional[str]
    source_module: str
    source_reference: str
    taxable_amount: float
    tax_amount: float
    breakdown: Optional[dict]
    status: str

    class Config:
        from_attributes = True


class ReconciliationRequest(BaseModel):
    tenant_id: str
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


DEFAULT_POSTING_MAP = {
    ("loans", "disbursement"): ("1200_LOAN_RECEIVABLE", "1000_CASH"),
    ("loans", "payment"): ("1000_CASH", "1200_LOAN_RECEIVABLE"),
    ("deposits", "deposit"): ("1000_CASH", "2200_CUSTOMER_DEPOSITS"),
    ("deposits", "withdrawal"): ("2200_CUSTOMER_DEPOSITS", "1000_CASH"),
    ("forex", "transaction"): ("1000_CASH", "4100_FOREX_INCOME"),
    ("gold", "disbursement"): ("1210_GOLD_LOAN_RECEIVABLE", "1000_CASH"),
}

DEFAULT_ACCOUNT_NAMES = {
    "1000_CASH": ("Cash", "asset"),
    "1200_LOAN_RECEIVABLE": ("Loan Receivable", "asset"),
    "1210_GOLD_LOAN_RECEIVABLE": ("Gold Loan Receivable", "asset"),
    "2200_CUSTOMER_DEPOSITS": ("Customer Deposit Liability", "liability"),
    "2300_GST_PAYABLE": ("GST Payable", "liability"),
    "2310_TDS_PAYABLE": ("TDS Payable", "liability"),
    "4100_FOREX_INCOME": ("Forex Income", "revenue"),
    "5100_OPERATING_EXPENSE": ("Operating Expense", "expense"),
    "5200_TAX_EXPENSE": ("Tax Expense", "expense"),
}


def _get_or_create_account(code: str, tenant_id: str, db: Session) -> GLAccount:
    account = (
        db.query(GLAccount)
        .filter(GLAccount.tenant_id == tenant_id, GLAccount.account_code == code)
        .first()
    )
    if account:
        return account

    name, account_type = DEFAULT_ACCOUNT_NAMES.get(code, (code.replace("_", " ").title(), "asset"))
    account = GLAccount(
        id=str(uuid4()),
        tenant_id=tenant_id,
        account_code=code,
        account_name=name,
        account_type=account_type,
        balance=0.0,
    )
    db.add(account)
    db.flush()
    return account


def _log_audit(
    db: Session,
    tenant_id: str,
    entity: str,
    entity_id: Optional[str],
    action: str,
    payload: Optional[dict] = None,
    performed_by: Optional[str] = None,
) -> None:
    db.add(
        AuditLog(
            id=str(uuid4()),
            tenant_id=tenant_id,
            entity=entity,
            entity_id=entity_id,
            action=action,
            payload=payload,
            performed_by=performed_by,
        )
    )


def _create_subledger_entry(
    db: Session,
    tenant_id: str,
    source_module: str,
    source_event: str,
    source_reference: str,
    amount: float,
    journal_entry_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> SubLedgerEntry:
    entry = SubLedgerEntry(
        id=str(uuid4()),
        tenant_id=tenant_id,
        source_module=source_module,
        source_event=source_event,
        source_reference=source_reference,
        journal_entry_id=journal_entry_id,
        amount=amount,
        metadata_json=metadata,
    )
    db.add(entry)
    return entry


def _resolve_posting_map(posting: AutomatedGLPostingRequest, db: Session) -> tuple[str, str, Optional[PostingRule]]:
    if posting.debit_account_code and posting.credit_account_code:
        return posting.debit_account_code, posting.credit_account_code, None

    rule = (
        db.query(PostingRule)
        .filter(
            PostingRule.tenant_id == posting.tenant_id,
            PostingRule.source_module == posting.source_module,
            PostingRule.source_event == posting.source_event,
            PostingRule.is_active.in_(["true", "1", "yes", "active"]),
        )
        .first()
    )
    if rule:
        return rule.debit_account_code, rule.credit_account_code, rule

    mapped = DEFAULT_POSTING_MAP.get((posting.source_module, posting.source_event))
    if mapped:
        return mapped[0], mapped[1], None

    raise HTTPException(status_code=400, detail="No GL posting map found for source module/event")


def _posting_rule_response(rule: PostingRule) -> dict:
    return {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "source_module": rule.source_module,
        "source_event": rule.source_event,
        "debit_account_code": rule.debit_account_code,
        "credit_account_code": rule.credit_account_code,
        "description": rule.description,
        "is_active": rule.is_active,
    }


def _audit_log_response(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "tenant_id": log.tenant_id,
        "entity": log.entity,
        "entity_id": log.entity_id,
        "action": log.action,
        "payload": log.payload,
        "performed_by": log.performed_by,
        "created_at": log.created_at,
    }


def _subledger_response(entry: SubLedgerEntry) -> dict:
    return {
        "id": entry.id,
        "tenant_id": entry.tenant_id,
        "source_module": entry.source_module,
        "source_event": entry.source_event,
        "source_reference": entry.source_reference,
        "journal_entry_id": entry.journal_entry_id,
        "amount": entry.amount,
        "metadata": entry.metadata_json,
        "created_at": entry.created_at,
    }


def _financial_rows(accounts: list[GLAccount], account_types: set[str]):
    rows = []
    total = 0.0
    for account in accounts:
        if account.account_type not in account_types:
            continue
        normal_balance = account.balance or 0.0
        if account.account_type in {"liability", "equity", "revenue"}:
            normal_balance = -normal_balance
        total += normal_balance
        rows.append(
            {
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "amount": round(normal_balance, 2),
            }
        )
    return rows, round(total, 2)


def _journal_entry_response(entry: JournalEntry) -> dict:
    return {
        "id": entry.id,
        "tenant_id": entry.tenant_id,
        "entry_date": entry.entry_date,
        "description": entry.description,
        "reference": entry.reference,
        "metadata": entry.metadata_json,
        "posting_status": entry.posting_status,
        "idempotency_key": entry.idempotency_key,
        "source_module": entry.source_module,
        "source_event": entry.source_event,
        "source_reference": entry.source_reference,
    }


def _period_filter(query, start_date: Optional[datetime], end_date: Optional[datetime]):
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
    return query


def _account_balances(
    tenant_id: str,
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[dict]:
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    rows = []
    for account in accounts:
        query = (
            db.query(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .filter(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.posting_status != "failed",
                JournalLine.gl_account_id == account.id,
            )
        )
        query = _period_filter(query, start_date, end_date)
        debit = 0.0
        credit = 0.0
        for line in query.all():
            debit += line.debit or 0.0
            credit += line.credit or 0.0
        rows.append(
            {
                "account": account,
                "debit": round(debit, 2),
                "credit": round(credit, 2),
                "balance": round(debit - credit, 2),
            }
        )
    return rows


def _financial_rows_from_balances(account_balances: list[dict], account_types: set[str]):
    rows = []
    total = 0.0
    for item in account_balances:
        account = item["account"]
        if account.account_type not in account_types:
            continue
        normal_balance = item["balance"]
        if account.account_type in {"liability", "equity", "revenue"}:
            normal_balance = -normal_balance
        total += normal_balance
        rows.append(
            {
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "amount": round(normal_balance, 2),
            }
        )
    return rows, round(total, 2)


def _tax_breakdown(tax_type: str, taxable_amount: float, rate_percent: float) -> dict:
    tax_type_normalized = tax_type.lower()
    tax_amount = round(taxable_amount * rate_percent / 100, 2)
    if tax_type_normalized == "gst":
        component_rate = round(rate_percent / 2, 4)
        component_amount = round(tax_amount / 2, 2)
        return {
            "taxable_amount": taxable_amount,
            "total_rate_percent": rate_percent,
            "total_tax_amount": tax_amount,
            "components": [
                {"name": "CGST", "rate_percent": component_rate, "amount": component_amount},
                {"name": "SGST", "rate_percent": component_rate, "amount": round(tax_amount - component_amount, 2)},
            ],
        }
    return {
        "taxable_amount": taxable_amount,
        "total_rate_percent": rate_percent,
        "total_tax_amount": tax_amount,
        "components": [
            {"name": tax_type.upper(), "rate_percent": rate_percent, "amount": tax_amount},
        ],
    }


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

    if not account.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = (
        db.query(GLAccount)
        .filter(
            GLAccount.tenant_id == account.tenant_id,
            GLAccount.account_code == account.account_code,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="GL account code already exists for tenant")

    new_account = GLAccount(
        id=str(uuid4()),
        tenant_id=account.tenant_id,
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
async def list_gl_accounts(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()



@app.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(entry: JournalEntryCreate, db: Session = Depends(get_db)):
    if not entry.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    if not entry.lines or len(entry.lines) < 2:
        raise HTTPException(status_code=400, detail="Journal entry must contain at least two lines")

    total_debit = sum(line.debit for line in entry.lines)
    total_credit = sum(line.credit for line in entry.lines)
    if round(total_debit, 2) != round(total_credit, 2):
        raise HTTPException(status_code=400, detail="Journal entry must be balanced")

    account_ids = {line.gl_account_id for line in entry.lines}
    accounts = (
        db.query(GLAccount)
        .filter(GLAccount.tenant_id == entry.tenant_id, GLAccount.id.in_(account_ids))
        .all()
    )
    account_by_id = {account.id: account for account in accounts}
    missing_account_ids = account_ids - set(account_by_id)
    if missing_account_ids:
        missing = ", ".join(sorted(missing_account_ids))
        raise HTTPException(status_code=404, detail=f"GL account(s) not found for tenant: {missing}")

    journal_entry = JournalEntry(
        id=str(uuid4()),
        tenant_id=entry.tenant_id,
        entry_date=entry.entry_date or datetime.utcnow(),
        description=entry.description,
        reference=entry.reference,
        metadata_json=entry.metadata,
        posting_status="posted",
    )
    db.add(journal_entry)

    for line in entry.lines:
        gl_account = account_by_id[line.gl_account_id]

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
    return _journal_entry_response(journal_entry)


@app.get("/journal-entries")
async def list_journal_entries(
    tenant_id: str = Query(...),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = (
        db.query(JournalEntry)
        .filter(JournalEntry.tenant_id == tenant_id)
        .order_by(JournalEntry.entry_date.desc())
    )
    items = query.offset(skip).limit(limit).all()
    return {
        "items": [_journal_entry_response(item) for item in items],
        "skip": skip,
        "limit": limit,
        "total": query.count(),
    }


@app.post("/posting-rules", response_model=PostingRuleResponse)
async def create_posting_rule(rule: PostingRuleCreate, db: Session = Depends(get_db)):
    if not rule.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = (
        db.query(PostingRule)
        .filter(
            PostingRule.tenant_id == rule.tenant_id,
            PostingRule.source_module == rule.source_module,
            PostingRule.source_event == rule.source_event,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Posting rule already exists for source module/event")

    posting_rule = PostingRule(
        id=str(uuid4()),
        tenant_id=rule.tenant_id,
        source_module=rule.source_module,
        source_event=rule.source_event,
        debit_account_code=rule.debit_account_code,
        credit_account_code=rule.credit_account_code,
        description=rule.description,
        is_active="true",
    )
    db.add(posting_rule)
    _log_audit(
        db,
        tenant_id=rule.tenant_id,
        entity="posting_rule",
        entity_id=posting_rule.id,
        action="create",
        payload={
            "source_module": rule.source_module,
            "source_event": rule.source_event,
            "debit_account_code": rule.debit_account_code,
            "credit_account_code": rule.credit_account_code,
        },
    )
    db.commit()
    db.refresh(posting_rule)
    return posting_rule


@app.get("/posting-rules", response_model=List[PostingRuleResponse])
async def list_posting_rules(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(PostingRule)
        .filter(PostingRule.tenant_id == tenant_id)
        .order_by(PostingRule.source_module, PostingRule.source_event)
        .all()
    )


@app.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    tenant_id: str = Query(...),
    entity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
    if entity:
        query = query.filter(AuditLog.entity == entity)
    return query.order_by(AuditLog.created_at.desc()).all()


@app.get("/sub-ledger-entries", response_model=List[SubLedgerEntryResponse])
async def list_subledger_entries(
    tenant_id: str = Query(...),
    source_module: Optional[str] = Query(None),
    source_event: Optional[str] = Query(None),
    source_reference: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id)
    if source_module:
        query = query.filter(SubLedgerEntry.source_module == source_module)
    if source_event:
        query = query.filter(SubLedgerEntry.source_event == source_event)
    if source_reference:
        query = query.filter(SubLedgerEntry.source_reference == source_reference)
    return query.order_by(SubLedgerEntry.created_at.desc()).all()


@app.get("/gl-balances")
async def gl_balances(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    return {"accounts": accounts}



@app.get("/reports/trial-balance")
async def trial_balance(
    tenant_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    account_balances = _account_balances(tenant_id, db, start_date, end_date)
    rows = []
    total_debit = 0.0
    total_credit = 0.0
    for item in account_balances:
        account = item["account"]
        balance = item["balance"]
        debit = round(balance, 2) if balance >= 0 else 0.0
        credit = round(abs(balance), 2) if balance < 0 else 0.0
        total_debit += debit
        total_credit += credit
        rows.append(
            {
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "debit": debit,
                "credit": credit,
            }
        )

    return {
        "tenant_id": tenant_id,
        "start_date": start_date,
        "end_date": end_date,
        "as_of": end_date or datetime.utcnow(),
        "rows": rows,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "is_balanced": round(total_debit, 2) == round(total_credit, 2),
    }


@app.post("/gl-postings/auto", response_model=JournalEntryResponse)
async def create_automated_gl_posting(posting: AutomatedGLPostingRequest, db: Session = Depends(get_db)):
    if not posting.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    if posting.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    if posting.idempotency_key:
        existing = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.tenant_id == posting.tenant_id,
                JournalEntry.idempotency_key == posting.idempotency_key,
            )
            .first()
        )
        if existing:
            return _journal_entry_response(existing)

    debit_code, credit_code, posting_rule = _resolve_posting_map(posting, db)
    debit_account = _get_or_create_account(debit_code, posting.tenant_id, db)
    credit_account = _get_or_create_account(credit_code, posting.tenant_id, db)

    journal_entry = JournalEntry(
        id=str(uuid4()),
        tenant_id=posting.tenant_id,
        entry_date=datetime.utcnow(),
        description=posting.description or f"{posting.source_module}.{posting.source_event}",
        reference=posting.source_reference,
        metadata_json=posting.metadata,
        posting_status="posted",
        idempotency_key=posting.idempotency_key,
        source_module=posting.source_module,
        source_event=posting.source_event,
        source_reference=posting.source_reference,
    )
    db.add(journal_entry)

    lines = [
        JournalLine(
            id=str(uuid4()),
            journal_entry_id=journal_entry.id,
            gl_account_id=debit_account.id,
            debit=posting.amount,
            credit=0.0,
            description=f"Debit for {posting.source_module}.{posting.source_event}",
        ),
        JournalLine(
            id=str(uuid4()),
            journal_entry_id=journal_entry.id,
            gl_account_id=credit_account.id,
            debit=0.0,
            credit=posting.amount,
            description=f"Credit for {posting.source_module}.{posting.source_event}",
        ),
    ]
    db.add_all(lines)

    _create_subledger_entry(
        db=db,
        tenant_id=posting.tenant_id,
        source_module=posting.source_module,
        source_event=posting.source_event,
        source_reference=posting.source_reference,
        amount=posting.amount,
        journal_entry_id=journal_entry.id,
        metadata=posting.metadata,
    )

    debit_account.balance += posting.amount
    credit_account.balance -= posting.amount

    _log_audit(
        db,
        tenant_id=posting.tenant_id,
        entity="gl_posting",
        entity_id=journal_entry.id,
        action="create",
        payload={
            "source_module": posting.source_module,
            "source_event": posting.source_event,
            "debit_account_code": debit_code,
            "credit_account_code": credit_code,
            "amount": posting.amount,
            "posting_rule_id": posting_rule.id if posting_rule else None,
        },
    )

    db.commit()
    db.refresh(journal_entry)
    return _journal_entry_response(journal_entry)


@app.post("/gl-postings/{journal_entry_id}/reverse", response_model=JournalEntryResponse)
async def reverse_gl_posting(
    journal_entry_id: str,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    original = (
        db.query(JournalEntry)
        .filter(JournalEntry.id == journal_entry_id, JournalEntry.tenant_id == tenant_id)
        .first()
    )
    if not original:
        raise HTTPException(status_code=404, detail="Journal entry not found for tenant")
    if original.posting_status == "reversed":
        raise HTTPException(status_code=400, detail="Journal entry is already reversed")

    reversal = JournalEntry(
        id=str(uuid4()),
        tenant_id=tenant_id,
        entry_date=datetime.utcnow(),
        description=f"Reversal: {original.description}",
        reference=f"REV-{original.reference or original.id}",
        metadata_json={"reverses_journal_entry_id": original.id},
        posting_status="posted",
        source_module=original.source_module,
        source_event=f"{original.source_event or 'journal'}.reversal",
        source_reference=original.source_reference,
    )
    db.add(reversal)

    for line in original.lines:
        account = (
            db.query(GLAccount)
            .filter(GLAccount.id == line.gl_account_id, GLAccount.tenant_id == tenant_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="GL account not found for tenant")
        db.add(
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=reversal.id,
                gl_account_id=line.gl_account_id,
                debit=line.credit,
                credit=line.debit,
                description=f"Reversal of {line.id}",
            )
        )
        account.balance += (line.credit or 0.0) - (line.debit or 0.0)

    original.posting_status = "reversed"
    db.commit()
    db.refresh(reversal)
    return _journal_entry_response(reversal)


@app.get("/reports/profit-loss")
async def profit_loss(
    tenant_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    account_balances = _account_balances(tenant_id, db, start_date, end_date)
    revenue_rows, total_revenue = _financial_rows_from_balances(account_balances, {"revenue"})
    expense_rows, total_expenses = _financial_rows_from_balances(account_balances, {"expense"})
    return {
        "tenant_id": tenant_id,
        "start_date": start_date,
        "end_date": end_date,
        "as_of": end_date or datetime.utcnow(),
        "revenue": revenue_rows,
        "expenses": expense_rows,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": round(total_revenue - total_expenses, 2),
    }


@app.get("/reports/balance-sheet")
async def balance_sheet(
    tenant_id: str = Query(...),
    as_of: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    statement_date = as_of or datetime.utcnow()
    account_balances = _account_balances(tenant_id, db, None, statement_date)
    asset_rows, total_assets = _financial_rows_from_balances(account_balances, {"asset"})
    liability_rows, total_liabilities = _financial_rows_from_balances(account_balances, {"liability"})
    equity_rows, total_equity = _financial_rows_from_balances(account_balances, {"equity"})
    return {
        "tenant_id": tenant_id,
        "as_of": statement_date,
        "assets": asset_rows,
        "liabilities": liability_rows,
        "equity": equity_rows,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "is_balanced": round(total_assets, 2) == round(total_liabilities + total_equity, 2),
    }


@app.post("/tax-rules", response_model=TaxRuleResponse)
async def create_tax_rule(rule: TaxRuleCreate, db: Session = Depends(get_db)):
    if not rule.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = db.query(TaxRule).filter(TaxRule.tenant_id == rule.tenant_id, TaxRule.tax_code == rule.tax_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tax code already exists")
    if rule.payable_gl_account_id:
        payable_account = (
            db.query(GLAccount)
            .filter(
                GLAccount.id == rule.payable_gl_account_id,
                GLAccount.tenant_id == rule.tenant_id,
            )
            .first()
        )
        if not payable_account:
            raise HTTPException(status_code=404, detail="Payable GL account not found for tenant")

    tax_rule = TaxRule(
        id=str(uuid4()),
        tenant_id=rule.tenant_id,
        tax_code=rule.tax_code,
        tax_type=rule.tax_type,
        rate_percent=rule.rate_percent,
        payable_gl_account_id=rule.payable_gl_account_id,
        payable_gl_account_code=rule.payable_gl_account_code,
        expense_gl_account_code=rule.expense_gl_account_code,
    )
    db.add(tax_rule)
    db.commit()
    db.refresh(tax_rule)
    return tax_rule


@app.get("/tax-rules", response_model=List[TaxRuleResponse])
async def list_tax_rules(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(TaxRule).filter(TaxRule.tenant_id == tenant_id).all()


@app.post("/tax/compute", response_model=TaxComputationResponse)
async def compute_tax(request: TaxComputationRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    rule = db.query(TaxRule).filter(TaxRule.tenant_id == request.tenant_id, TaxRule.tax_code == request.tax_code).first()

    if not rule or str(rule.is_active).lower() not in {"true", "1", "yes", "active"}:
        raise HTTPException(status_code=404, detail="Active tax rule not found")
    if request.taxable_amount <= 0:
        raise HTTPException(status_code=400, detail="taxable_amount must be positive")

    breakdown = _tax_breakdown(rule.tax_type, request.taxable_amount, rule.rate_percent)
    tax_amount = breakdown["total_tax_amount"]
    expense_code = rule.expense_gl_account_code or "5200_TAX_EXPENSE"
    if rule.payable_gl_account_id:
        payable_account = (
            db.query(GLAccount)
            .filter(
                GLAccount.id == rule.payable_gl_account_id,
                GLAccount.tenant_id == request.tenant_id,
            )
            .first()
        )
        if not payable_account:
            raise HTTPException(status_code=404, detail="Payable GL account not found for tenant")
    else:
        default_payable_code = "2310_TDS_PAYABLE" if rule.tax_type.lower() == "tds" else "2300_GST_PAYABLE"
        payable_account = _get_or_create_account(
            rule.payable_gl_account_code or default_payable_code,
            request.tenant_id,
            db,
        )
    expense_account = _get_or_create_account(expense_code, request.tenant_id, db)

    journal_entry = JournalEntry(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        entry_date=datetime.utcnow(),
        description=f"Tax computation {request.tax_code} for {request.source_module}",
        reference=request.source_reference,
        metadata_json={"tax_code": request.tax_code, "tax_breakdown": breakdown},
        posting_status="posted",
        source_module=request.source_module,
        source_event="tax_computed",
        source_reference=request.source_reference,
    )
    db.add(journal_entry)
    db.add_all(
        [
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=journal_entry.id,
                gl_account_id=expense_account.id,
                debit=tax_amount,
                credit=0.0,
                description=f"{rule.tax_type.upper()} expense",
            ),
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=journal_entry.id,
                gl_account_id=payable_account.id,
                debit=0.0,
                credit=tax_amount,
                description=f"{rule.tax_type.upper()} payable",
            ),
        ]
    )
    expense_account.balance += tax_amount
    payable_account.balance -= tax_amount

    tax = TaxComputation(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        tax_rule_id=rule.id,
        journal_entry_id=journal_entry.id,
        source_module=request.source_module,
        source_reference=request.source_reference,
        taxable_amount=request.taxable_amount,
        tax_amount=tax_amount,
        breakdown=breakdown,
        status="posted",
    )
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax


@app.post("/bank-transactions", response_model=BankStatementResponse)
async def add_bank_transaction(transaction: BankTransactionCreate, db: Session = Depends(get_db)):
    if not transaction.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = (
        db.query(BankStatementTransaction)
        .filter(
            BankStatementTransaction.tenant_id == transaction.tenant_id,
            BankStatementTransaction.reference == transaction.reference,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Bank transaction reference already exists")

    bank_tx = BankStatementTransaction(
        id=str(uuid4()),
        tenant_id=transaction.tenant_id,
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
    transaction = (
        db.query(BankStatementTransaction)
        .filter(
            BankStatementTransaction.id == request.transaction_id,
            BankStatementTransaction.tenant_id == request.tenant_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Bank transaction not found for tenant")

    journal_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.id == request.journal_entry_id,
            JournalEntry.tenant_id == request.tenant_id,
        )
        .first()
    )

    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found for tenant")

    transaction.matched_journal_id = journal_entry.id
    transaction.status = "matched"
    db.commit()
    return {"transaction_id": transaction.id, "status": transaction.status, "matched_journal_id": transaction.matched_journal_id}



@app.get("/bank-transactions")
async def list_bank_transactions(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    transactions = db.query(BankStatementTransaction).filter(BankStatementTransaction.tenant_id == tenant_id).all()
    return {"transactions": transactions}


@app.get("/")
async def root():
    return {"service": "accounting", "version": "0.1.0"}
