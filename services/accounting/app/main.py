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
    parent_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=True)
    category = Column(String, nullable=True)
    currency = Column(String, default="INR")
    branch_id = Column(String, nullable=True, index=True)
    branch_specific = Column(String, default="false")
    posting_allowed = Column(String, default="true")
    status = Column(String, default="active")
    opening_balance = Column(Float, default=0.0)
    financial_year = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    parent = relationship("GLAccount", remote_side=[id])



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
    business_date = Column(DateTime, nullable=True)
    financial_year = Column(String, nullable=True)
    branch_id = Column(String, nullable=True, index=True)
    voucher_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("JournalLine", back_populates="journal_entry")


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id = Column(String, primary_key=True)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"))
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"))
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    branch_id = Column(String, nullable=True, index=True)
    cost_center = Column(String, nullable=True)
    profit_center = Column(String, nullable=True)
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
    debit_account_code = Column(String, nullable=True)
    credit_account_code = Column(String, nullable=True)
    posting_lines = Column(JSON, nullable=True)
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


class GLBalance(Base):
    __tablename__ = "gl_balances"
    __table_args__ = (
        UniqueConstraint("tenant_id", "gl_account_id", "branch_id", "currency", "financial_year", name="uq_gl_balances_scope"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=False)
    branch_id = Column(String, nullable=True, index=True)
    currency = Column(String, default="INR")
    financial_year = Column(String, nullable=False)
    opening_balance = Column(Float, default=0.0)
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    closing_balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Voucher(Base):
    __tablename__ = "vouchers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "voucher_number", name="uq_vouchers_tenant_number"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    voucher_number = Column(String, nullable=False, index=True)
    voucher_type = Column(String, nullable=False, index=True)
    voucher_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    reference = Column(String, nullable=True)
    branch_id = Column(String, nullable=True, index=True)
    currency = Column(String, default="INR")
    status = Column(String, default="draft", index=True)
    created_by = Column(String, nullable=True)
    verified_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    posted_journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    payment_mode = Column(String, nullable=True, index=True)
    payment_reference = Column(String, nullable=True)
    payment_details = Column(JSON, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("VoucherLine", back_populates="voucher")


class VoucherLine(Base):
    __tablename__ = "voucher_lines"

    id = Column(String, primary_key=True)
    voucher_id = Column(String, ForeignKey("vouchers.id"), nullable=False)
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    cost_center = Column(String, nullable=True)
    profit_center = Column(String, nullable=True)
    voucher = relationship("Voucher", back_populates="lines")


class DayEndClose(Base):
    __tablename__ = "day_end_closes"
    __table_args__ = (
        UniqueConstraint("tenant_id", "business_date", "branch_id", name="uq_day_end_tenant_date_branch"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    business_date = Column(DateTime, nullable=False)
    branch_id = Column(String, nullable=True, index=True)
    status = Column(String, default="closed")
    trial_balance_debit = Column(Float, default=0.0)
    trial_balance_credit = Column(Float, default=0.0)
    is_balanced = Column(String, default="true")
    checks = Column(JSON, nullable=True)
    closed_by = Column(String, nullable=True)
    closed_at = Column(DateTime, default=datetime.utcnow)


class GLAccountResponse(BaseModel):
    id: str
    tenant_id: str
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    branch_id: Optional[str] = None
    branch_specific: Optional[str] = None
    posting_allowed: Optional[str] = None
    status: Optional[str] = None
    opening_balance: Optional[float] = 0.0
    financial_year: Optional[str] = None
    balance: float

    class Config:
        from_attributes = True


class GLAccountCreate(BaseModel):
    tenant_id: str
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = "INR"
    branch_id: Optional[str] = None
    branch_specific: Optional[str] = "false"
    posting_allowed: Optional[str] = "true"
    status: Optional[str] = "active"
    opening_balance: Optional[float] = 0.0
    financial_year: Optional[str] = None


class GLAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    parent_account_id: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    branch_id: Optional[str] = None
    branch_specific: Optional[str] = None
    posting_allowed: Optional[str] = None
    status: Optional[str] = None
    opening_balance: Optional[float] = None
    financial_year: Optional[str] = None


class COASeedRequest(BaseModel):
    tenant_id: str
    currency: Optional[str] = "INR"
    financial_year: Optional[str] = None


class JournalLineCreate(BaseModel):
    gl_account_id: str
    debit: float = 0.0
    credit: float = 0.0
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    tenant_id: str
    entry_date: Optional[datetime] = None
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
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
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    voucher_id: Optional[str] = None

    class Config:
        from_attributes = True


class PostingRuleLineCreate(BaseModel):
    account_code: str
    direction: str
    description: Optional[str] = None


class PostingRuleLineResponse(BaseModel):
    account_code: str
    direction: str
    description: Optional[str] = None


class PostingRuleCreate(BaseModel):
    tenant_id: str
    source_module: str
    source_event: str
    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    description: Optional[str] = None
    lines: Optional[List[PostingRuleLineCreate]] = None


class PostingRuleResponse(BaseModel):
    id: str
    tenant_id: str
    source_module: str
    source_event: str
    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    description: Optional[str] = None
    is_active: str
    lines: List[PostingRuleLineResponse] = []

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


class SubLedgerSummaryItem(BaseModel):
    source_module: str
    ledger_name: str
    transaction_count: int
    total_amount: float
    last_entry_at: Optional[datetime] = None
    rollup_to: str = "General Ledger"


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
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    currency: Optional[str] = "INR"

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


class PostingEngineLine(BaseModel):
    gl_account_id: Optional[str] = None
    account_code: Optional[str] = None
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None


class PostingValidationRequest(BaseModel):
    tenant_id: str
    source_module: Optional[str] = None
    source_event: Optional[str] = None
    source_reference: Optional[str] = None
    lines: List[PostingEngineLine]


class PostingEngineRequest(BaseModel):
    tenant_id: str
    source_module: str
    source_event: str
    source_reference: str
    description: Optional[str] = None
    idempotency_key: Optional[str] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    currency: Optional[str] = "INR"
    metadata: Optional[dict] = None
    lines: List[PostingEngineLine]


class PostingEnginePostResponse(JournalEntryResponse):
    pipeline: Optional[dict] = None


class VoucherLineCreate(BaseModel):
    gl_account_id: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None


class VoucherLineResponse(BaseModel):
    gl_account_id: str
    debit: float
    credit: float
    description: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None

    class Config:
        from_attributes = True


class VoucherCreate(BaseModel):
    tenant_id: str
    voucher_type: str
    voucher_date: Optional[datetime] = None
    description: str
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    metadata: Optional[dict] = None
    lines: List[VoucherLineCreate]


class PaymentVoucherCreate(BaseModel):
    tenant_id: str
    payment_category: str
    amount: float
    payee_name: str
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    payment_mode: str = "cash"
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class ReceiptVoucherCreate(BaseModel):
    tenant_id: str
    receipt_category: str = "customer_payments"
    amount: float
    payer_name: str
    customer_id: Optional[str] = None
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    payment_mode: str = "cash"
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class ContraVoucherCreate(BaseModel):
    tenant_id: str
    transfer_type: str
    amount: float
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    transfer_reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    transfer_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class VoucherActionRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None


class VoucherResponse(BaseModel):
    id: str
    tenant_id: str
    voucher_number: str
    voucher_type: str
    voucher_date: datetime
    description: str
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: str
    status: str
    posted_journal_entry_id: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    verified_by: Optional[str] = None
    approved_by: Optional[str] = None
    lines: List[VoucherLineResponse] = []
    payment_category: Optional[str] = None
    receipt_category: Optional[str] = None
    contra_transfer_type: Optional[str] = None
    payee_name: Optional[str] = None
    payer_name: Optional[str] = None
    customer_id: Optional[str] = None
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    transfer_reference: Optional[str] = None
    amount: Optional[float] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class DayEndCloseRequest(BaseModel):
    tenant_id: str
    business_date: datetime
    branch_id: Optional[str] = None
    closed_by: Optional[str] = None


class DayEndCloseResponse(BaseModel):
    id: str
    tenant_id: str
    business_date: datetime
    branch_id: Optional[str] = None
    status: str
    trial_balance_debit: float
    trial_balance_credit: float
    is_balanced: str
    checks: Optional[dict] = None
    closed_by: Optional[str] = None
    closed_at: datetime

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

SUB_LEDGER_LEDGER_MAP = {
    "loans": "Customer Loan Ledger",
    "deposit": "Deposit Ledger",
    "deposits": "Deposit Ledger",
    "gold": "Gold Loan Ledger",
    "forex": "Forex Ledger",
    "vendor": "Vendor Ledger",
    "employee": "Employee Ledger",
}

DEFAULT_ACCOUNT_NAMES = {
    "1000_CASH": ("Cash", "asset"),
    "1110_BRANCH_CASH": ("Branch Cash", "asset"),
    "1120_BANK": ("Bank Account", "asset"),
    "1130_VAULT_CASH": ("Vault Cash", "asset"),
    "1200_LOAN_RECEIVABLE": ("Loan Receivable", "asset"),
    "1210_GOLD_LOAN_RECEIVABLE": ("Gold Loan Receivable", "asset"),
    "1500_TREASURY": ("Treasury Account", "asset"),
    "2200_CUSTOMER_DEPOSITS": ("Customer Deposit Liability", "liability"),
    "2300_GST_PAYABLE": ("GST Payable", "liability"),
    "2310_TDS_PAYABLE": ("TDS Payable", "liability"),
    "2400_VENDOR_PAYABLE": ("Vendor Payable", "liability"),
    "4100_FOREX_INCOME": ("Forex Income", "revenue"),
    "5100_OPERATING_EXPENSE": ("Operating Expense", "expense"),
    "5110_RENT_EXPENSE": ("Rent Expense", "expense"),
    "5120_ELECTRICITY_EXPENSE": ("Electricity Expense", "expense"),
    "5130_INSURANCE_EXPENSE": ("Insurance Expense", "expense"),
    "5200_TAX_EXPENSE": ("Tax Expense", "expense"),
    "5210_SALARY_EXPENSE": ("Salary Expense", "expense"),
}

PAYMENT_VOUCHER_CATEGORIES = {
    "vendor_payments": {
        "label": "Vendor payments",
        "debit_account_code": "2400_VENDOR_PAYABLE",
        "description": "Vendor payment",
    },
    "salary": {
        "label": "Salary",
        "debit_account_code": "5210_SALARY_EXPENSE",
        "description": "Salary payment",
    },
    "rent": {
        "label": "Rent",
        "debit_account_code": "5110_RENT_EXPENSE",
        "description": "Rent payment",
    },
    "electricity": {
        "label": "Electricity",
        "debit_account_code": "5120_ELECTRICITY_EXPENSE",
        "description": "Electricity payment",
    },
    "tax": {
        "label": "Tax",
        "debit_account_code": "2300_GST_PAYABLE",
        "description": "Tax payment",
    },
    "insurance": {
        "label": "Insurance",
        "debit_account_code": "5130_INSURANCE_EXPENSE",
        "description": "Insurance payment",
    },
}

RECEIPT_PAYMENT_MODES = ["cash", "cheque", "upi", "rtgs", "neft", "imps"]

RECEIPT_VOUCHER_CATEGORIES = {
    "customer_payments": {
        "label": "Customer payments",
        "credit_account_code": "1200_LOAN_RECEIVABLE",
        "description": "Customer payment receipt",
    },
}

CONTRA_TRANSFER_TYPES = {
    "cash_to_bank": {
        "label": "Cash to Bank",
        "debit_account_code": "1120_BANK",
        "credit_account_code": "1000_CASH",
        "source_label": "Cash",
        "destination_label": "Bank",
        "description": "Cash deposited to bank",
    },
    "bank_to_cash": {
        "label": "Bank to Cash",
        "debit_account_code": "1000_CASH",
        "credit_account_code": "1120_BANK",
        "source_label": "Bank",
        "destination_label": "Cash",
        "description": "Cash withdrawn from bank",
    },
    "vault_to_branch": {
        "label": "Vault to Branch",
        "debit_account_code": "1110_BRANCH_CASH",
        "credit_account_code": "1130_VAULT_CASH",
        "source_label": "Vault",
        "destination_label": "Branch",
        "description": "Cash moved from vault to branch",
    },
    "branch_to_treasury": {
        "label": "Branch to Treasury",
        "debit_account_code": "1500_TREASURY",
        "credit_account_code": "1110_BRANCH_CASH",
        "source_label": "Branch",
        "destination_label": "Treasury",
        "description": "Cash moved from branch to treasury",
    },
}

DEFAULT_NBFC_COA = [
    {"account_code": "100000", "account_name": "Assets", "account_type": "asset", "category": "Assets", "posting_allowed": "false"},
    {"account_code": "110000", "account_name": "Cash", "account_type": "asset", "category": "Assets", "parent_code": "100000", "posting_allowed": "false"},
    {"account_code": "111000", "account_name": "Branch Cash", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "1110_BRANCH_CASH", "account_name": "Branch Cash Transfer", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "112000", "account_name": "Vault Cash", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "1130_VAULT_CASH", "account_name": "Vault Cash Transfer", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "120000", "account_name": "Loans", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "130000", "account_name": "Gold Loan", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "140000", "account_name": "Deposits", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "150000", "account_name": "Treasury", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "1500_TREASURY", "account_name": "Treasury Transfer", "account_type": "asset", "category": "Assets", "parent_code": "150000"},
    {"account_code": "200000", "account_name": "Liabilities", "account_type": "liability", "category": "Liabilities", "posting_allowed": "false"},
    {"account_code": "210000", "account_name": "Customer Deposits", "account_type": "liability", "category": "Liabilities", "parent_code": "200000"},
    {"account_code": "220000", "account_name": "Borrowings", "account_type": "liability", "category": "Liabilities", "parent_code": "200000"},
    {"account_code": "300000", "account_name": "Capital", "account_type": "equity", "category": "Capital", "posting_allowed": "false"},
    {"account_code": "310000", "account_name": "Share Capital", "account_type": "equity", "category": "Capital", "parent_code": "300000"},
    {"account_code": "400000", "account_name": "Income", "account_type": "revenue", "category": "Income", "posting_allowed": "false"},
    {"account_code": "410000", "account_name": "Interest Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "420000", "account_name": "Processing Fee Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "500000", "account_name": "Expenses", "account_type": "expense", "category": "Expenses", "posting_allowed": "false"},
    {"account_code": "510000", "account_name": "Operating Expenses", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "5110_RENT_EXPENSE", "account_name": "Rent Expense", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "5120_ELECTRICITY_EXPENSE", "account_name": "Electricity Expense", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "5130_INSURANCE_EXPENSE", "account_name": "Insurance Expense", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "520000", "account_name": "Employee Expenses", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "5210_SALARY_EXPENSE", "account_name": "Salary Expense", "account_type": "expense", "category": "Expenses", "parent_code": "520000"},
    {"account_code": "900000", "account_name": "Off Balance Sheet", "account_type": "off_balance", "category": "Off Balance Sheet", "posting_allowed": "false"},
    {"account_code": "910000", "account_name": "Guarantees", "account_type": "off_balance", "category": "Off Balance Sheet", "parent_code": "900000"},
    {"account_code": "990000", "account_name": "Memo Accounts", "account_type": "memo", "category": "Memo Accounts", "posting_allowed": "false"},
]


def _current_financial_year(moment: Optional[datetime] = None) -> str:
    value = moment or datetime.utcnow()
    start_year = value.year if value.month >= 4 else value.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _is_truthy(value: Optional[str]) -> bool:
    return str(value or "").lower() in {"true", "1", "yes", "active", "allowed"}


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
        category=account_type,
        currency="INR",
        posting_allowed="true",
        status="active",
        balance=0.0,
    )
    db.add(account)
    db.flush()
    return account


def _get_postable_account_by_id(account_id: str, tenant_id: str, db: Session) -> GLAccount:
    account = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"GL account not found for tenant: {account_id}")
    if not _is_truthy(account.posting_allowed):
        raise HTTPException(status_code=400, detail=f"Posting is not allowed for GL account {account.account_code}")
    if str(account.status or "").lower() not in {"active", ""}:
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is not active")
    return account


def _get_postable_account_by_code(account_code: str, tenant_id: str, db: Session) -> GLAccount:
    account = _get_or_create_account(account_code, tenant_id, db)
    if not _is_truthy(account.posting_allowed):
        raise HTTPException(status_code=400, detail=f"Posting is not allowed for GL account {account.account_code}")
    if str(account.status or "").lower() not in {"active", ""}:
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is not active")
    return account


def _validate_parent_account(
    db: Session,
    tenant_id: str,
    parent_account_id: Optional[str],
    account_id: Optional[str] = None,
) -> Optional[GLAccount]:
    if not parent_account_id:
        return None
    if account_id and parent_account_id == account_id:
        raise HTTPException(status_code=400, detail="GL account cannot be its own parent")
    parent = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.id == parent_account_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent GL account not found for tenant")
    seen = {account_id} if account_id else set()
    cursor = parent
    while cursor:
        if cursor.id in seen:
            raise HTTPException(status_code=400, detail="Parent GL account would create a cycle")
        seen.add(cursor.id)
        if not cursor.parent_account_id:
            break
        cursor = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.id == cursor.parent_account_id).first()
    return parent


def _account_tree_node(account: GLAccount) -> dict:
    return {
        "id": account.id,
        "account_code": account.account_code,
        "account_name": account.account_name,
        "account_type": account.account_type,
        "category": account.category,
        "currency": account.currency,
        "branch_specific": account.branch_specific,
        "posting_allowed": account.posting_allowed,
        "status": account.status,
        "balance": account.balance,
        "children": [],
    }


def _build_coa_tree(accounts: list[GLAccount]) -> list[dict]:
    nodes = {account.id: _account_tree_node(account) for account in accounts}
    roots = []
    for account in accounts:
        node = nodes[account.id]
        if account.parent_account_id and account.parent_account_id in nodes:
            nodes[account.parent_account_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def _validate_double_entry(lines: List[PostingEngineLine]) -> dict:
    if not lines or len(lines) < 2:
        raise HTTPException(status_code=400, detail="Posting must contain at least two lines")
    total_debit = round(sum(line.debit or 0.0 for line in lines), 2)
    total_credit = round(sum(line.credit or 0.0 for line in lines), 2)
    if total_debit <= 0 or total_credit <= 0:
        raise HTTPException(status_code=400, detail="Posting must include debit and credit values")
    if total_debit != total_credit:
        raise HTTPException(status_code=400, detail="Posting must be balanced")
    for line in lines:
        if (line.debit or 0.0) < 0 or (line.credit or 0.0) < 0:
            raise HTTPException(status_code=400, detail="Debit and credit cannot be negative")
        if (line.debit or 0.0) > 0 and (line.credit or 0.0) > 0:
            raise HTTPException(status_code=400, detail="A posting line cannot contain both debit and credit")
        if not line.gl_account_id and not line.account_code:
            raise HTTPException(status_code=400, detail="Each posting line needs gl_account_id or account_code")
    return {"total_debit": total_debit, "total_credit": total_credit, "is_balanced": True}


def _update_gl_balance(
    db: Session,
    tenant_id: str,
    account: GLAccount,
    debit: float,
    credit: float,
    branch_id: Optional[str],
    currency: Optional[str],
    financial_year: Optional[str],
) -> None:
    fy = financial_year or _current_financial_year()
    balance = (
        db.query(GLBalance)
        .filter(
            GLBalance.tenant_id == tenant_id,
            GLBalance.gl_account_id == account.id,
            GLBalance.branch_id == branch_id,
            GLBalance.currency == (currency or account.currency or "INR"),
            GLBalance.financial_year == fy,
        )
        .first()
    )
    if not balance:
        balance = GLBalance(
            id=str(uuid4()),
            tenant_id=tenant_id,
            gl_account_id=account.id,
            branch_id=branch_id,
            currency=currency or account.currency or "INR",
            financial_year=fy,
            opening_balance=account.opening_balance or 0.0,
            total_debit=0.0,
            total_credit=0.0,
            closing_balance=account.opening_balance or 0.0,
        )
        db.add(balance)
    balance.total_debit = round((balance.total_debit or 0.0) + (debit or 0.0), 2)
    balance.total_credit = round((balance.total_credit or 0.0) + (credit or 0.0), 2)
    balance.closing_balance = round((balance.opening_balance or 0.0) + balance.total_debit - balance.total_credit, 2)
    balance.updated_at = datetime.utcnow()


def _post_journal(
    db: Session,
    tenant_id: str,
    description: str,
    lines: List[PostingEngineLine],
    reference: Optional[str] = None,
    metadata: Optional[dict] = None,
    entry_date: Optional[datetime] = None,
    posting_status: str = "posted",
    idempotency_key: Optional[str] = None,
    source_module: Optional[str] = None,
    source_event: Optional[str] = None,
    source_reference: Optional[str] = None,
    branch_id: Optional[str] = None,
    business_date: Optional[datetime] = None,
    financial_year: Optional[str] = None,
    voucher_id: Optional[str] = None,
) -> JournalEntry:
    _validate_double_entry(lines)
    journal_entry = JournalEntry(
        id=str(uuid4()),
        tenant_id=tenant_id,
        entry_date=entry_date or datetime.utcnow(),
        description=description,
        reference=reference,
        metadata_json=metadata,
        posting_status=posting_status,
        idempotency_key=idempotency_key,
        source_module=source_module,
        source_event=source_event,
        source_reference=source_reference,
        business_date=business_date,
        financial_year=financial_year or _current_financial_year(business_date or entry_date),
        branch_id=branch_id,
        voucher_id=voucher_id,
    )
    db.add(journal_entry)
    db.flush()

    for line in lines:
        account = (
            _get_postable_account_by_id(line.gl_account_id, tenant_id, db)
            if line.gl_account_id
            else _get_postable_account_by_code(line.account_code or "", tenant_id, db)
        )
        debit = line.debit or 0.0
        credit = line.credit or 0.0
        db.add(
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=journal_entry.id,
                gl_account_id=account.id,
                debit=debit,
                credit=credit,
                currency=line.currency or account.currency or "INR",
                branch_id=line.branch_id or branch_id,
                cost_center=line.cost_center,
                profit_center=line.profit_center,
                description=line.description,
            )
        )
        account.balance += debit
        account.balance -= credit
        _update_gl_balance(
            db=db,
            tenant_id=tenant_id,
            account=account,
            debit=debit,
            credit=credit,
            branch_id=line.branch_id or branch_id,
            currency=line.currency or account.currency or "INR",
            financial_year=journal_entry.financial_year,
        )
    return journal_entry


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


def _normalize_posting_rule_lines(rule: Optional[PostingRule]) -> List[dict]:
    if not rule:
        return []
    if isinstance(rule.posting_lines, list):
        return [
            {
                "account_code": str(line.get("account_code", "")).strip(),
                "direction": str(line.get("direction", "debit")).strip().lower(),
                "description": line.get("description"),
            }
            for line in rule.posting_lines
            if line
        ]
    if rule.debit_account_code or rule.credit_account_code:
        return [
            {"account_code": rule.debit_account_code, "direction": "debit"},
            {"account_code": rule.credit_account_code, "direction": "credit"},
        ]
    return []


def _build_posting_lines_from_rule(
    rule: Optional[PostingRule],
    amount: float,
    branch_id: Optional[str] = None,
    currency: Optional[str] = None,
    description_prefix: Optional[str] = None,
) -> List[PostingEngineLine]:
    normalized_lines = _normalize_posting_rule_lines(rule)
    if not normalized_lines:
        raise HTTPException(status_code=400, detail="Posting rule has no configured lines")

    posting_lines = []
    for line in normalized_lines:
        account_code = line.get("account_code")
        direction = str(line.get("direction", "debit")).lower()
        if not account_code:
            raise HTTPException(status_code=400, detail="Posting rule line is missing account_code")
        if direction not in {"debit", "credit"}:
            raise HTTPException(status_code=400, detail="Posting rule line direction must be debit or credit")
        posting_lines.append(
            PostingEngineLine(
                account_code=account_code,
                debit=amount if direction == "debit" else 0.0,
                credit=amount if direction == "credit" else 0.0,
                currency=currency or "INR",
                branch_id=branch_id,
                description=line.get("description") or f"{description_prefix or 'Posting'} {direction}",
            )
        )
    return posting_lines


def _resolve_posting_map(
    posting: AutomatedGLPostingRequest,
    db: Session,
    amount: float,
    branch_id: Optional[str] = None,
    currency: Optional[str] = None,
    description_prefix: Optional[str] = None,
) -> tuple[List[PostingEngineLine], Optional[PostingRule]]:
    if posting.debit_account_code and posting.credit_account_code:
        return [
            PostingEngineLine(
                account_code=posting.debit_account_code,
                debit=amount,
                credit=0.0,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} debit",
            ),
            PostingEngineLine(
                account_code=posting.credit_account_code,
                debit=0.0,
                credit=amount,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} credit",
            ),
        ], None

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
        return _build_posting_lines_from_rule(rule, amount, branch_id, currency, description_prefix), rule

    mapped = DEFAULT_POSTING_MAP.get((posting.source_module, posting.source_event))
    if mapped:
        return [
            PostingEngineLine(
                account_code=mapped[0],
                debit=amount,
                credit=0.0,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} debit",
            ),
            PostingEngineLine(
                account_code=mapped[1],
                debit=0.0,
                credit=amount,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} credit",
            ),
        ], None

    raise HTTPException(status_code=400, detail="No GL posting map found for source module/event")


def _posting_rule_line_response(line: dict) -> dict:
    return {
        "account_code": line.get("account_code"),
        "direction": line.get("direction", "debit"),
        "description": line.get("description"),
    }


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
        "lines": [
            _posting_rule_line_response(line)
            for line in _normalize_posting_rule_lines(rule)
        ],
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


def _subledger_ledger_name(source_module: str) -> str:
    return SUB_LEDGER_LEDGER_MAP.get(source_module.lower(), f"{source_module.replace('_', ' ').title()} Ledger")


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
        "branch_id": entry.branch_id,
        "business_date": entry.business_date,
        "financial_year": entry.financial_year,
        "voucher_id": entry.voucher_id,
    }


def _posting_pipeline(
    *,
    validation_status: str = "passed",
    validation_balanced: bool = True,
    posting_rule_status: str = "manual",
    posting_rule: Optional[dict] = None,
    subledger_entry_id: Optional[str] = None,
) -> dict:
    return {
        "validation": {"status": validation_status, "is_balanced": validation_balanced},
        "posting_rule": {"status": posting_rule_status, "rule": posting_rule},
        "debit_entry": {"status": "recorded"},
        "credit_entry": {"status": "recorded"},
        "gl_update": {"status": "applied"},
        "audit_log": {"status": "recorded"},
        "subledger": {"status": "recorded", "entry_id": subledger_entry_id},
    }


def _voucher_response(voucher: Voucher) -> dict:
    metadata = voucher.metadata_json or {}
    payment_voucher = metadata.get("payment_voucher") if isinstance(metadata, dict) else None
    payment_voucher = payment_voucher if isinstance(payment_voucher, dict) else {}
    receipt_voucher = metadata.get("receipt_voucher") if isinstance(metadata, dict) else None
    receipt_voucher = receipt_voucher if isinstance(receipt_voucher, dict) else {}
    contra_voucher = metadata.get("contra_voucher") if isinstance(metadata, dict) else None
    contra_voucher = contra_voucher if isinstance(contra_voucher, dict) else {}
    return {
        "id": voucher.id,
        "tenant_id": voucher.tenant_id,
        "voucher_number": voucher.voucher_number,
        "voucher_type": voucher.voucher_type,
        "voucher_date": voucher.voucher_date,
        "description": voucher.description,
        "reference": voucher.reference,
        "branch_id": voucher.branch_id,
        "currency": voucher.currency,
        "status": voucher.status,
        "posted_journal_entry_id": voucher.posted_journal_entry_id,
        "created_by": voucher.created_by,
        "verified_by": voucher.verified_by,
        "approved_by": voucher.approved_by,
        "lines": [
            {
                "gl_account_id": line.gl_account_id,
                "debit": line.debit,
                "credit": line.credit,
                "description": line.description,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
            }
            for line in voucher.lines
        ],
        "payment_mode": voucher.payment_mode,
        "payment_reference": voucher.payment_reference,
        "payment_details": voucher.payment_details,
        "payment_category": payment_voucher.get("category"),
        "receipt_category": receipt_voucher.get("category"),
        "contra_transfer_type": contra_voucher.get("transfer_type"),
        "payee_name": payment_voucher.get("payee_name"),
        "payer_name": receipt_voucher.get("payer_name"),
        "customer_id": receipt_voucher.get("customer_id"),
        "source_location": contra_voucher.get("source_location"),
        "destination_location": contra_voucher.get("destination_location"),
        "transfer_reference": contra_voucher.get("transfer_reference"),
        "amount": payment_voucher.get("amount") or receipt_voucher.get("amount") or contra_voucher.get("amount"),
        "metadata": metadata,
    }


def _next_voucher_number(tenant_id: str, voucher_type: str, db: Session) -> str:
    prefix = voucher_type.upper().replace("-", "_")[:8]
    count = db.query(Voucher).filter(Voucher.tenant_id == tenant_id, Voucher.voucher_type == voucher_type).count() + 1
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d')}-{count:05d}"


def _normalize_payment_category(category: str) -> str:
    return category.strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_receipt_category(category: str) -> str:
    return category.strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_contra_transfer_type(transfer_type: str) -> str:
    return transfer_type.strip().lower().replace(" ", "_").replace("-", "_")


def _payment_category_options() -> list[dict]:
    return [
        {"key": key, **value}
        for key, value in PAYMENT_VOUCHER_CATEGORIES.items()
    ]


def _receipt_voucher_options() -> dict:
    return {
        "categories": [
            {"key": key, **value}
            for key, value in RECEIPT_VOUCHER_CATEGORIES.items()
        ],
        "payment_modes": RECEIPT_PAYMENT_MODES,
    }


def _contra_voucher_options() -> dict:
    return {
        "transfer_types": [
            {"key": key, **value}
            for key, value in CONTRA_TRANSFER_TYPES.items()
        ]
    }


def _payment_credit_account_code(payment_mode: Optional[str]) -> str:
    return "1000_CASH" if str(payment_mode or "").lower() == "cash" else "1120_BANK"


def _receipt_debit_account_code(payment_mode: Optional[str]) -> str:
    return "1000_CASH" if str(payment_mode or "").lower() == "cash" else "1120_BANK"


def _build_payment_voucher_payload(payment: PaymentVoucherCreate, db: Session) -> VoucherCreate:
    category_key = _normalize_payment_category(payment.payment_category)
    category = PAYMENT_VOUCHER_CATEGORIES.get(category_key)
    if not category:
        raise HTTPException(status_code=400, detail="Unsupported payment voucher category")
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if not payment.payee_name.strip():
        raise HTTPException(status_code=400, detail="payee_name is required")
    if not payment.payment_mode:
        raise HTTPException(status_code=400, detail="payment_mode is required")
    if payment.payment_mode != "cash" and not payment.payment_reference:
        raise HTTPException(status_code=400, detail="payment_reference is required for non-cash payment vouchers")

    if payment.debit_account_id:
        debit_account = _get_postable_account_by_id(payment.debit_account_id, payment.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            payment.debit_account_code or category["debit_account_code"],
            payment.tenant_id,
            db,
        )

    if payment.credit_account_id:
        credit_account = _get_postable_account_by_id(payment.credit_account_id, payment.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            payment.credit_account_code or _payment_credit_account_code(payment.payment_mode),
            payment.tenant_id,
            db,
        )

    amount = round(payment.amount, 2)
    description = payment.description or f"{category['description']} to {payment.payee_name}"
    metadata = {
        **(payment.metadata or {}),
        "payment_voucher": {
            "module": "module_8",
            "category": category_key,
            "category_label": category["label"],
            "payee_name": payment.payee_name,
            "amount": amount,
        },
    }
    return VoucherCreate(
        tenant_id=payment.tenant_id,
        voucher_type="payment",
        voucher_date=payment.voucher_date,
        description=description,
        reference=payment.reference,
        branch_id=payment.branch_id,
        currency=payment.currency or "INR",
        payment_mode=payment.payment_mode,
        payment_reference=payment.payment_reference,
        payment_details=payment.payment_details,
        created_by=payment.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"{category['label']} debit",
                cost_center=payment.cost_center,
                profit_center=payment.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"Payment via {payment.payment_mode.upper()}",
                cost_center=payment.cost_center,
                profit_center=payment.profit_center,
            ),
        ],
    )


def _build_contra_voucher_payload(contra: ContraVoucherCreate, db: Session) -> VoucherCreate:
    transfer_key = _normalize_contra_transfer_type(contra.transfer_type)
    transfer = CONTRA_TRANSFER_TYPES.get(transfer_key)
    if not transfer:
        raise HTTPException(status_code=400, detail="Unsupported contra transfer type")
    if contra.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    if contra.debit_account_id:
        debit_account = _get_postable_account_by_id(contra.debit_account_id, contra.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            contra.debit_account_code or transfer["debit_account_code"],
            contra.tenant_id,
            db,
        )

    if contra.credit_account_id:
        credit_account = _get_postable_account_by_id(contra.credit_account_id, contra.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            contra.credit_account_code or transfer["credit_account_code"],
            contra.tenant_id,
            db,
        )

    amount = round(contra.amount, 2)
    description = contra.description or transfer["description"]
    source_location = contra.source_location or transfer["source_label"]
    destination_location = contra.destination_location or transfer["destination_label"]
    metadata = {
        **(contra.metadata or {}),
        "contra_voucher": {
            "module": "module_9",
            "transfer_type": transfer_key,
            "transfer_label": transfer["label"],
            "source_location": source_location,
            "destination_location": destination_location,
            "transfer_reference": contra.transfer_reference,
            "amount": amount,
        },
    }
    return VoucherCreate(
        tenant_id=contra.tenant_id,
        voucher_type="contra",
        voucher_date=contra.voucher_date,
        description=description,
        reference=contra.reference or contra.transfer_reference,
        branch_id=contra.branch_id,
        currency=contra.currency or "INR",
        payment_reference=contra.transfer_reference,
        payment_details=contra.transfer_details,
        created_by=contra.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"{transfer['label']} debit to {destination_location}",
                cost_center=contra.cost_center,
                profit_center=contra.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"{transfer['label']} credit from {source_location}",
                cost_center=contra.cost_center,
                profit_center=contra.profit_center,
            ),
        ],
    )


def _build_receipt_voucher_payload(receipt: ReceiptVoucherCreate, db: Session) -> VoucherCreate:
    category_key = _normalize_receipt_category(receipt.receipt_category)
    category = RECEIPT_VOUCHER_CATEGORIES.get(category_key)
    if not category:
        raise HTTPException(status_code=400, detail="Unsupported receipt voucher category")
    if receipt.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if not receipt.payer_name.strip():
        raise HTTPException(status_code=400, detail="payer_name is required")

    payment_mode = str(receipt.payment_mode or "").lower()
    if payment_mode not in RECEIPT_PAYMENT_MODES:
        raise HTTPException(status_code=400, detail="Unsupported receipt payment mode")
    if payment_mode != "cash" and not receipt.payment_reference:
        raise HTTPException(status_code=400, detail="payment_reference is required for non-cash receipt vouchers")

    if receipt.debit_account_id:
        debit_account = _get_postable_account_by_id(receipt.debit_account_id, receipt.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            receipt.debit_account_code or _receipt_debit_account_code(payment_mode),
            receipt.tenant_id,
            db,
        )

    if receipt.credit_account_id:
        credit_account = _get_postable_account_by_id(receipt.credit_account_id, receipt.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            receipt.credit_account_code or category["credit_account_code"],
            receipt.tenant_id,
            db,
        )

    amount = round(receipt.amount, 2)
    description = receipt.description or f"{category['description']} from {receipt.payer_name}"
    metadata = {
        **(receipt.metadata or {}),
        "receipt_voucher": {
            "module": "module_7",
            "category": category_key,
            "category_label": category["label"],
            "payer_name": receipt.payer_name,
            "customer_id": receipt.customer_id,
            "amount": amount,
            "payment_mode": payment_mode,
        },
    }
    return VoucherCreate(
        tenant_id=receipt.tenant_id,
        voucher_type="receipt",
        voucher_date=receipt.voucher_date,
        description=description,
        reference=receipt.reference,
        branch_id=receipt.branch_id,
        currency=receipt.currency or "INR",
        payment_mode=payment_mode,
        payment_reference=receipt.payment_reference,
        payment_details=receipt.payment_details,
        created_by=receipt.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"Receipt via {payment_mode.upper()}",
                cost_center=receipt.cost_center,
                profit_center=receipt.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"{category['label']} credit",
                cost_center=receipt.cost_center,
                profit_center=receipt.profit_center,
            ),
        ],
    )


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

    _validate_parent_account(db, account.tenant_id, account.parent_account_id)

    new_account = GLAccount(
        id=str(uuid4()),
        tenant_id=account.tenant_id,
        account_code=account.account_code,
        account_name=account.account_name,
        account_type=account.account_type,
        parent_account_id=account.parent_account_id,
        category=account.category or account.account_type,
        currency=account.currency or "INR",
        branch_id=account.branch_id,
        branch_specific=account.branch_specific or "false",
        posting_allowed=account.posting_allowed or "true",
        status=account.status or "active",
        opening_balance=account.opening_balance or 0.0,
        financial_year=account.financial_year,
        balance=0.0
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@app.get("/gl-accounts", response_model=List[GLAccountResponse])
async def list_gl_accounts(
    tenant_id: str = Query(...),
    category: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
    posting_allowed: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id)
    if category:
        query = query.filter(GLAccount.category == category)
    if account_type:
        query = query.filter(GLAccount.account_type == account_type)
    if posting_allowed:
        query = query.filter(GLAccount.posting_allowed == posting_allowed)
    if status:
        query = query.filter(GLAccount.status == status)
    return query.order_by(GLAccount.account_code).all()


@app.get("/gl-accounts/summary")
async def gl_account_summary(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    categories: dict[str, dict] = {}
    for account in accounts:
        key = account.category or account.account_type or "Uncategorized"
        if key not in categories:
            categories[key] = {"category": key, "count": 0, "posting_allowed": 0, "control_accounts": 0, "balance": 0.0}
        categories[key]["count"] += 1
        if _is_truthy(account.posting_allowed):
            categories[key]["posting_allowed"] += 1
        else:
            categories[key]["control_accounts"] += 1
        categories[key]["balance"] = round(categories[key]["balance"] + (account.balance or 0.0), 2)
    return {
        "tenant_id": tenant_id,
        "total_accounts": len(accounts),
        "posting_accounts": sum(1 for account in accounts if _is_truthy(account.posting_allowed)),
        "control_accounts": sum(1 for account in accounts if not _is_truthy(account.posting_allowed)),
        "categories": sorted(categories.values(), key=lambda row: row["category"]),
    }


@app.get("/gl-accounts/hierarchy")
async def gl_account_hierarchy(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).order_by(GLAccount.account_code).all()
    return {"tenant_id": tenant_id, "items": _build_coa_tree(accounts)}


@app.post("/gl-accounts/seed-defaults")
async def seed_default_gl_accounts(request: COASeedRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    existing_by_code = {
        account.account_code: account
        for account in db.query(GLAccount).filter(GLAccount.tenant_id == request.tenant_id).all()
    }
    created = []
    for item in DEFAULT_NBFC_COA:
        if item["account_code"] in existing_by_code:
            continue
        parent = existing_by_code.get(item.get("parent_code"))
        account = GLAccount(
            id=str(uuid4()),
            tenant_id=request.tenant_id,
            account_code=item["account_code"],
            account_name=item["account_name"],
            account_type=item["account_type"],
            parent_account_id=parent.id if parent else None,
            category=item["category"],
            currency=request.currency or "INR",
            branch_specific=item.get("branch_specific", "false"),
            posting_allowed=item.get("posting_allowed", "true"),
            status="active",
            opening_balance=0.0,
            financial_year=request.financial_year,
            balance=0.0,
        )
        db.add(account)
        db.flush()
        existing_by_code[account.account_code] = account
        created.append(account.account_code)
    _log_audit(
        db,
        request.tenant_id,
        "gl_account",
        None,
        "seed_defaults",
        {"created": created, "count": len(created)},
    )
    db.commit()
    return {"tenant_id": request.tenant_id, "created": created, "created_count": len(created)}


@app.put("/gl-accounts/{account_id}", response_model=GLAccountResponse)
async def update_gl_account(account_id: str, payload: GLAccountUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    account = db.query(GLAccount).filter(GLAccount.id == account_id, GLAccount.tenant_id == tenant_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL account not found for tenant")
    if payload.parent_account_id is not None:
        _validate_parent_account(db, tenant_id, payload.parent_account_id, account_id=account.id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account



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

    posting_lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            branch_id=line.branch_id,
            currency=line.currency,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            description=line.description,
        )
        for line in entry.lines
    ]

    journal_entry = _post_journal(
        db=db,
        tenant_id=entry.tenant_id,
        description=entry.description,
        lines=posting_lines,
        entry_date=entry.entry_date or datetime.utcnow(),
        reference=entry.reference,
        metadata=entry.metadata,
        branch_id=entry.branch_id,
        business_date=entry.business_date,
        financial_year=entry.financial_year,
    )

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
    if not rule.lines and not (rule.debit_account_code and rule.credit_account_code):
        raise HTTPException(status_code=400, detail="Provide either lines or debit/credit account codes")

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

    normalized_lines = []
    if rule.lines:
        for line in rule.lines:
            normalized_lines.append(
                {
                    "account_code": line.account_code,
                    "direction": str(line.direction or "debit").lower(),
                    "description": line.description,
                }
            )

    debit_account_code = rule.debit_account_code
    credit_account_code = rule.credit_account_code
    if normalized_lines:
        debit_account_code = next((line["account_code"] for line in normalized_lines if line["direction"] == "debit"), None)
        credit_account_code = next((line["account_code"] for line in normalized_lines if line["direction"] == "credit"), None)

    posting_rule = PostingRule(
        id=str(uuid4()),
        tenant_id=rule.tenant_id,
        source_module=rule.source_module,
        source_event=rule.source_event,
        debit_account_code=debit_account_code,
        credit_account_code=credit_account_code,
        posting_lines=normalized_lines or None,
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
            "debit_account_code": debit_account_code,
            "credit_account_code": credit_account_code,
            "lines": normalized_lines,
        },
    )
    db.commit()
    db.refresh(posting_rule)
    return _posting_rule_response(posting_rule)


@app.get("/posting-rules", response_model=List[PostingRuleResponse])
async def list_posting_rules(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    rules = (
        db.query(PostingRule)
        .filter(PostingRule.tenant_id == tenant_id)
        .order_by(PostingRule.source_module, PostingRule.source_event)
        .all()
    )
    return [_posting_rule_response(rule) for rule in rules]


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
    entries = query.order_by(SubLedgerEntry.created_at.desc()).all()
    return [_subledger_response(entry) for entry in entries]


@app.get("/sub-ledger-summary")
async def subledger_summary(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    entries = db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id).all()
    grouped: dict[str, dict] = {}
    for entry in entries:
        key = entry.source_module.lower()
        summary = grouped.setdefault(
            key,
            {
                "source_module": entry.source_module,
                "ledger_name": _subledger_ledger_name(entry.source_module),
                "transaction_count": 0,
                "total_amount": 0.0,
                "last_entry_at": None,
                "rollup_to": "General Ledger",
            },
        )
        summary["transaction_count"] += 1
        summary["total_amount"] += entry.amount or 0.0
        if summary["last_entry_at"] is None or (entry.created_at and entry.created_at > summary["last_entry_at"]):
            summary["last_entry_at"] = entry.created_at

    items = [
        {
            "source_module": item["source_module"],
            "ledger_name": item["ledger_name"],
            "transaction_count": item["transaction_count"],
            "total_amount": round(item["total_amount"], 2),
            "last_entry_at": item["last_entry_at"],
            "rollup_to": item["rollup_to"],
        }
        for item in grouped.values()
    ]
    items.sort(key=lambda row: (row["ledger_name"].lower(), row["source_module"].lower()))
    return {"items": items, "total": len(items)}


@app.post("/posting-engine/validate")
async def validate_posting(request: PostingValidationRequest, db: Session = Depends(get_db)):
    result = _validate_double_entry(request.lines)
    resolved_accounts = []
    for line in request.lines:
        account = (
            _get_postable_account_by_id(line.gl_account_id, request.tenant_id, db)
            if line.gl_account_id
            else _get_postable_account_by_code(line.account_code or "", request.tenant_id, db)
        )
        resolved_accounts.append(
            {
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "debit": line.debit,
                "credit": line.credit,
            }
        )

    posting_rule = None
    posting_rule_status = "manual"
    if request.source_module and request.source_event:
        rule = (
            db.query(PostingRule)
            .filter(
                PostingRule.tenant_id == request.tenant_id,
                PostingRule.source_module == request.source_module,
                PostingRule.source_event == request.source_event,
                PostingRule.is_active.in_(["true", "1", "yes", "active"]),
            )
            .first()
        )
        if rule:
            posting_rule = _posting_rule_response(rule)
            posting_rule_status = "matched"
        else:
            mapped = DEFAULT_POSTING_MAP.get((request.source_module, request.source_event))
            if mapped:
                posting_rule = {
                    "source_module": request.source_module,
                    "source_event": request.source_event,
                    "debit_account_code": mapped[0],
                    "credit_account_code": mapped[1],
                }
                posting_rule_status = "default_map"

    return {
        **result,
        "lines": resolved_accounts,
        "pipeline": {
            **_posting_pipeline(
                validation_status="passed",
                validation_balanced=result["is_balanced"],
                posting_rule_status=posting_rule_status,
                posting_rule=posting_rule,
            ),
            "debit_entry": {"status": "pending"},
            "credit_entry": {"status": "pending"},
            "gl_update": {"status": "pending"},
            "audit_log": {"status": "pending"},
            "subledger": {"status": "pending"},
        },
    }


@app.post("/posting-engine/post", response_model=PostingEnginePostResponse)
async def post_engine_transaction(request: PostingEngineRequest, db: Session = Depends(get_db)):
    if request.idempotency_key:
        existing = (
            db.query(JournalEntry)
            .filter(JournalEntry.tenant_id == request.tenant_id, JournalEntry.idempotency_key == request.idempotency_key)
            .first()
        )
        if existing:
            return {
                **_journal_entry_response(existing),
                "pipeline": _posting_pipeline(subledger_entry_id=None),
            }

    journal_entry = _post_journal(
        db=db,
        tenant_id=request.tenant_id,
        description=request.description or f"{request.source_module}.{request.source_event}",
        lines=request.lines,
        reference=request.source_reference,
        metadata=request.metadata,
        idempotency_key=request.idempotency_key,
        source_module=request.source_module,
        source_event=request.source_event,
        source_reference=request.source_reference,
        branch_id=request.branch_id,
        business_date=request.business_date,
        financial_year=request.financial_year,
    )
    subledger_entry = _create_subledger_entry(
        db=db,
        tenant_id=request.tenant_id,
        source_module=request.source_module,
        source_event=request.source_event,
        source_reference=request.source_reference,
        amount=sum(line.debit for line in request.lines),
        journal_entry_id=journal_entry.id,
        metadata=request.metadata,
    )
    _log_audit(
        db,
        tenant_id=request.tenant_id,
        entity="posting_engine",
        entity_id=journal_entry.id,
        action="post",
        payload={
            "source_module": request.source_module,
            "source_event": request.source_event,
            "source_reference": request.source_reference,
            "subledger_entry_id": subledger_entry.id,
        },
    )
    db.commit()
    db.refresh(journal_entry)
    return {
        **_journal_entry_response(journal_entry),
        "pipeline": _posting_pipeline(
            posting_rule_status="applied",
            posting_rule={
                "source_module": request.source_module,
                "source_event": request.source_event,
                "source_reference": request.source_reference,
            },
            subledger_entry_id=subledger_entry.id,
        ),
    }


@app.post("/vouchers", response_model=VoucherResponse)
async def create_voucher(voucher: VoucherCreate, db: Session = Depends(get_db)):
    if not voucher.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if voucher.voucher_type == "receipt" and not voucher.payment_mode:
        raise HTTPException(status_code=400, detail="payment_mode is required for receipt vouchers")
    if voucher.voucher_type == "receipt" and voucher.payment_mode != "cash" and not voucher.payment_reference:
        raise HTTPException(status_code=400, detail="payment_reference is required for non-cash receipt vouchers")
    engine_lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            description=line.description,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            branch_id=voucher.branch_id,
            currency=voucher.currency,
        )
        for line in voucher.lines
    ]
    _validate_double_entry(engine_lines)
    for line in voucher.lines:
        _get_postable_account_by_id(line.gl_account_id, voucher.tenant_id, db)

    new_voucher = Voucher(
        id=str(uuid4()),
        tenant_id=voucher.tenant_id,
        voucher_number=_next_voucher_number(voucher.tenant_id, voucher.voucher_type, db),
        voucher_type=voucher.voucher_type,
        voucher_date=voucher.voucher_date or datetime.utcnow(),
        description=voucher.description,
        reference=voucher.reference,
        branch_id=voucher.branch_id,
        currency=voucher.currency or "INR",
        status="draft",
        created_by=voucher.created_by,
        payment_mode=voucher.payment_mode,
        payment_reference=voucher.payment_reference,
        payment_details=voucher.payment_details,
        metadata_json=voucher.metadata,
    )
    db.add(new_voucher)
    db.flush()
    for line in voucher.lines:
        db.add(
            VoucherLine(
                id=str(uuid4()),
                voucher_id=new_voucher.id,
                gl_account_id=line.gl_account_id,
                debit=line.debit,
                credit=line.credit,
                description=line.description,
                cost_center=line.cost_center,
                profit_center=line.profit_center,
            )
        )
    _log_audit(db, voucher.tenant_id, "voucher", new_voucher.id, "create", {"voucher_type": voucher.voucher_type, "payment_mode": voucher.payment_mode}, voucher.created_by)
    db.commit()
    db.refresh(new_voucher)
    return _voucher_response(new_voucher)


@app.get("/payment-vouchers/categories")
async def payment_voucher_categories():
    return {"items": _payment_category_options()}


@app.get("/receipt-vouchers/options")
async def receipt_voucher_options():
    return _receipt_voucher_options()


@app.get("/contra-vouchers/options")
async def contra_voucher_options():
    return _contra_voucher_options()


@app.post("/payment-vouchers", response_model=VoucherResponse)
async def create_payment_voucher(payment: PaymentVoucherCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_payment_voucher_payload(payment, db)
    return await create_voucher(voucher_payload, db)


@app.post("/contra-vouchers", response_model=VoucherResponse)
async def create_contra_voucher(contra: ContraVoucherCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_contra_voucher_payload(contra, db)
    return await create_voucher(voucher_payload, db)


@app.post("/receipt-vouchers", response_model=VoucherResponse)
async def create_receipt_voucher(receipt: ReceiptVoucherCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_receipt_voucher_payload(receipt, db)
    return await create_voucher(voucher_payload, db)


@app.get("/vouchers")
async def list_vouchers(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    voucher_type: Optional[str] = Query(None),
    payment_category: Optional[str] = Query(None),
    receipt_category: Optional[str] = Query(None),
    contra_transfer_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Voucher).filter(Voucher.tenant_id == tenant_id)
    if status:
        query = query.filter(Voucher.status == status)
    if voucher_type:
        query = query.filter(Voucher.voucher_type == voucher_type)
    items = query.order_by(Voucher.voucher_date.desc()).all()
    if payment_category:
        category_key = _normalize_payment_category(payment_category)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("payment_voucher") or {}).get("category") == category_key
        ]
    if receipt_category:
        category_key = _normalize_receipt_category(receipt_category)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("receipt_voucher") or {}).get("category") == category_key
        ]
    if contra_transfer_type:
        transfer_key = _normalize_contra_transfer_type(contra_transfer_type)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("contra_voucher") or {}).get("transfer_type") == transfer_key
        ]
    return {"items": [_voucher_response(item) for item in items], "total": len(items)}


@app.post("/vouchers/{voucher_id}/verify", response_model=VoucherResponse)
async def verify_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft vouchers can be verified")
    voucher.status = "verified"
    voucher.verified_by = request.performed_by
    voucher.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "voucher", voucher.id, "verify", None, request.performed_by)
    db.commit()
    db.refresh(voucher)
    return _voucher_response(voucher)


@app.post("/vouchers/{voucher_id}/approve", response_model=VoucherResponse)
async def approve_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "verified":
        raise HTTPException(status_code=400, detail="Only verified vouchers can be approved")
    voucher.status = "approved"
    voucher.approved_by = request.performed_by
    voucher.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "voucher", voucher.id, "approve", None, request.performed_by)
    db.commit()
    db.refresh(voucher)
    return _voucher_response(voucher)


@app.post("/vouchers/{voucher_id}/post", response_model=JournalEntryResponse)
async def post_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved vouchers can be posted")

    lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            description=line.description,
            branch_id=voucher.branch_id,
            currency=voucher.currency,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
        )
        for line in voucher.lines
    ]
    journal_entry = _post_journal(
        db=db,
        tenant_id=request.tenant_id,
        description=voucher.description,
        lines=lines,
        reference=voucher.reference or voucher.voucher_number,
        metadata=voucher.metadata_json,
        source_module="accounting",
        source_event=f"{voucher.voucher_type}.voucher",
        source_reference=voucher.voucher_number,
        branch_id=voucher.branch_id,
        business_date=voucher.voucher_date,
        voucher_id=voucher.id,
    )
    voucher.status = "posted"
    voucher.posted_journal_entry_id = journal_entry.id
    voucher.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "voucher", voucher.id, "post", {"journal_entry_id": journal_entry.id}, request.performed_by)
    db.commit()
    db.refresh(journal_entry)
    return _journal_entry_response(journal_entry)


@app.post("/vouchers/{voucher_id}/reverse", response_model=VoucherResponse)
async def reverse_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "posted":
        raise HTTPException(status_code=400, detail="Only posted vouchers can be reversed")
    if not voucher.posted_journal_entry_id:
        raise HTTPException(status_code=400, detail="Voucher has no posted journal entry to reverse")

    reversal_entry = await reverse_gl_posting(voucher.posted_journal_entry_id, request.tenant_id, db)
    voucher.status = "reversed"
    voucher.updated_at = datetime.utcnow()
    _log_audit(
        db,
        request.tenant_id,
        "voucher",
        voucher.id,
        "reverse",
        {"reversal_journal_entry_id": reversal_entry["id"]},
        request.performed_by,
    )
    db.commit()
    db.refresh(voucher)
    return _voucher_response(voucher)


@app.get("/gl-balances")
async def gl_balances(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    return {"accounts": accounts}


@app.get("/gl-ledger")
async def gl_ledger(
    tenant_id: str = Query(...),
    financial_year: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GLBalance).filter(GLBalance.tenant_id == tenant_id)
    if financial_year:
        query = query.filter(GLBalance.financial_year == financial_year)
    if branch_id:
        query = query.filter(GLBalance.branch_id == branch_id)
    balances = query.all()
    accounts = {account.id: account for account in db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()}
    rows = []
    for balance in balances:
        account = accounts.get(balance.gl_account_id)
        rows.append(
            {
                "gl_account_id": balance.gl_account_id,
                "gl_number": account.account_code if account else None,
                "account_code": account.account_code if account else None,
                "account_name": account.account_name if account else None,
                "branch": balance.branch_id or "all",
                "branch_id": balance.branch_id,
                "currency": balance.currency,
                "financial_year": balance.financial_year,
                "opening_balance": balance.opening_balance,
                "debit": balance.total_debit,
                "credit": balance.total_credit,
                "balance": balance.closing_balance,
                "closing_balance": balance.closing_balance,
            }
        )
    return {"items": rows, "total": len(rows)}


@app.get("/dashboard")
async def accounting_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    trial = await trial_balance(tenant_id=tenant_id, start_date=None, end_date=None, db=db)
    vouchers_pending = (
        db.query(Voucher)
        .filter(Voucher.tenant_id == tenant_id, Voucher.status.in_(["draft", "verified", "approved"]))
        .count()
    )
    return {
        "tenant_id": tenant_id,
        "chart_of_accounts": db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).count(),
        "posting_rules": db.query(PostingRule).filter(PostingRule.tenant_id == tenant_id).count(),
        "journal_entries": db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id).count(),
        "subledger_entries": db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id).count(),
        "pending_vouchers": vouchers_pending,
        "trial_balance": {
            "total_debit": trial["total_debit"],
            "total_credit": trial["total_credit"],
            "is_balanced": trial["is_balanced"],
        },
    }


@app.post("/day-end/close", response_model=DayEndCloseResponse)
async def close_day(request: DayEndCloseRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(DayEndClose)
        .filter(
            DayEndClose.tenant_id == request.tenant_id,
            DayEndClose.business_date == request.business_date,
            DayEndClose.branch_id == request.branch_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Day end is already closed for this scope")
    trial = await trial_balance(tenant_id=request.tenant_id, start_date=None, end_date=request.business_date, db=db)
    close = DayEndClose(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        business_date=request.business_date,
        branch_id=request.branch_id,
        status="closed" if trial["is_balanced"] else "exception",
        trial_balance_debit=trial["total_debit"],
        trial_balance_credit=trial["total_credit"],
        is_balanced="true" if trial["is_balanced"] else "false",
        checks={"trial_balance_rows": len(trial["rows"])},
        closed_by=request.closed_by,
    )
    db.add(close)
    _log_audit(db, request.tenant_id, "day_end", close.id, "close", close.checks, request.closed_by)
    db.commit()
    db.refresh(close)
    return close


@app.get("/day-end/closes", response_model=List[DayEndCloseResponse])
async def list_day_end_closes(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(DayEndClose).filter(DayEndClose.tenant_id == tenant_id).order_by(DayEndClose.business_date.desc()).all()



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

    posting_lines, posting_rule = _resolve_posting_map(
        posting,
        db,
        posting.amount,
        branch_id=posting.branch_id,
        currency=posting.currency,
        description_prefix=f"{posting.source_module}.{posting.source_event}",
    )
    journal_entry = _post_journal(
        db=db,
        tenant_id=posting.tenant_id,
        description=posting.description or f"{posting.source_module}.{posting.source_event}",
        reference=posting.source_reference,
        metadata=posting.metadata,
        idempotency_key=posting.idempotency_key,
        source_module=posting.source_module,
        source_event=posting.source_event,
        source_reference=posting.source_reference,
        branch_id=posting.branch_id,
        business_date=posting.business_date,
        financial_year=posting.financial_year,
        lines=posting_lines,
    )

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

    _log_audit(
        db,
        tenant_id=posting.tenant_id,
        entity="gl_posting",
        entity_id=journal_entry.id,
        action="create",
        payload={
            "source_module": posting.source_module,
            "source_event": posting.source_event,
            "amount": posting.amount,
            "posting_rule_id": posting_rule.id if posting_rule else None,
            "lines": [line.dict() for line in posting_lines],
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
        branch_id=original.branch_id,
        financial_year=original.financial_year or _current_financial_year(original.entry_date),
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
        journal_line = JournalLine(
            id=str(uuid4()),
            journal_entry_id=reversal.id,
            gl_account_id=line.gl_account_id,
            debit=line.credit,
            credit=line.debit,
            currency=line.currency or account.currency or "INR",
            branch_id=line.branch_id or original.branch_id,
            description=f"Reversal of {line.id}",
        )
        db.add(journal_line)
        account.balance += (line.credit or 0.0) - (line.debit or 0.0)
        _update_gl_balance(
            db=db,
            tenant_id=tenant_id,
            account=account,
            debit=journal_line.debit or 0.0,
            credit=journal_line.credit or 0.0,
            branch_id=journal_line.branch_id,
            currency=journal_line.currency,
            financial_year=reversal.financial_year,
        )

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
