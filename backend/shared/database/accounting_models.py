"""
Accounting Database Models
Chart of Accounts, Journal Entries, General Ledger, Trial Balance
Event-driven accounting for NBFC operations
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text,
    ForeignKey, Enum, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.connection import Base


# Enums
class AccountType(str, enum.Enum):
    """Account types following accounting standards"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class AccountSubType(str, enum.Enum):
    """Account sub-types for detailed classification"""
    # Assets
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    LOAN_ASSET = "loan_asset"
    INVESTMENT = "investment"
    CASH_BANK = "cash_bank"
    
    # Liabilities
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    DEPOSIT = "deposit"
    BORROWING = "borrowing"
    
    # Equity
    CAPITAL = "capital"
    RESERVES = "reserves"
    RETAINED_EARNINGS = "retained_earnings"
    
    # Income
    INTEREST_INCOME = "interest_income"
    FEE_INCOME = "fee_income"
    OTHER_INCOME = "other_income"
    
    # Expense
    INTEREST_EXPENSE = "interest_expense"
    OPERATING_EXPENSE = "operating_expense"
    ADMINISTRATIVE_EXPENSE = "administrative_expense"
    FINANCIAL_EXPENSE = "financial_expense"


class JournalEntryType(str, enum.Enum):
    """Types of journal entries"""
    MANUAL = "manual"
    SYSTEM = "system"
    LOAN_DISBURSEMENT = "loan_disbursement"
    LOAN_REPAYMENT = "loan_repayment"
    INTEREST_ACCRUAL = "interest_accrual"
    DEPOSIT_RECEIPT = "deposit_receipt"
    DEPOSIT_MATURITY = "deposit_maturity"
    FEE_COLLECTION = "fee_collection"
    EXPENSE_BOOKING = "expense_booking"
    ADJUSTMENT = "adjustment"
    REVERSAL = "reversal"


class JournalEntryStatus(str, enum.Enum):
    """Journal entry status"""
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"
    VOID = "void"


class FinancialPeriod(str, enum.Enum):
    """Financial period types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


# Models
class ChartOfAccounts(Base):
    """
    Chart of Accounts (CoA)
    Master list of all GL accounts
    """
    __tablename__ = "chart_of_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Account identification
    account_code = Column(String(20), nullable=False, index=True)  # e.g., 1001, 2001
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    account_sub_type = Column(Enum(AccountSubType), nullable=False)
    
    # Hierarchy
    parent_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    level = Column(Integer, default=1)  # Account hierarchy level
    is_group = Column(Boolean, default=False)  # Group account or leaf account
    
    # Properties
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System-managed accounts
    allow_manual_entry = Column(Boolean, default=True)
    
    # Balance tracking
    opening_balance = Column(Numeric(15, 2), default=0.00)
    current_balance = Column(Numeric(15, 2), default=0.00)
    debit_balance = Column(Numeric(15, 2), default=0.00)  # Total debits
    credit_balance = Column(Numeric(15, 2), default=0.00)  # Total credits
    
    # Description and notes
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    parent_account = relationship("ChartOfAccounts", remote_side=[id], backref="child_accounts")
    general_ledger_entries = relationship("GeneralLedger", back_populates="account")
    
    # Indexes
    __table_args__ = (
        Index("ix_coa_tenant_code", "tenant_id", "account_code", unique=True),
        Index("ix_coa_tenant_type", "tenant_id", "account_type"),
        Index("ix_coa_parent", "parent_account_id"),
    )


class JournalEntry(Base):
    """
    Journal Entry Header
    Groups related debit and credit entries
    """
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Entry identification
    entry_number = Column(String(50), nullable=False, unique=True, index=True)  # JE-YYYYMM-XXXX
    entry_date = Column(Date, nullable=False, index=True)
    posting_date = Column(Date, nullable=True)  # Date when posted to GL
    
    # Entry classification
    entry_type = Column(Enum(JournalEntryType), nullable=False, default=JournalEntryType.MANUAL)
    status = Column(Enum(JournalEntryStatus), nullable=False, default=JournalEntryStatus.DRAFT)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # loan_account, customer, deposit, etc.
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Description
    narration = Column(Text, nullable=False)
    internal_notes = Column(Text, nullable=True)
    
    # Totals (for validation - debits must equal credits)
    total_debit = Column(Numeric(15, 2), nullable=False, default=0.00)
    total_credit = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Reversal support
    is_reversal = Column(Boolean, default=False)
    reversed_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    reversal_date = Column(Date, nullable=True)
    
    # Approval workflow
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    line_items = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    reversed_entry = relationship("JournalEntry", remote_side=[id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint("total_debit >= 0", name="check_total_debit_positive"),
        CheckConstraint("total_credit >= 0", name="check_total_credit_positive"),
        Index("ix_je_tenant_date", "tenant_id", "entry_date"),
        Index("ix_je_status", "status"),
        Index("ix_je_reference", "reference_type", "reference_id"),
    )


class JournalEntryLine(Base):
    """
    Journal Entry Line Items
    Individual debit/credit lines within a journal entry
    """
    __tablename__ = "journal_entry_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Link to header
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    line_number = Column(Integer, nullable=False)  # Sequence within entry
    
    # Account link
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    account_code = Column(String(20), nullable=False)  # Denormalized for query performance
    
    # Debit or Credit
    debit_amount = Column(Numeric(15, 2), default=0.00)
    credit_amount = Column(Numeric(15, 2), default=0.00)
    
    # Description
    description = Column(String(500), nullable=True)
    
    # Cost center / department (optional for analysis)
    cost_center = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    
    # Reference to original transaction
    transaction_type = Column(String(50), nullable=True)  # repayment, disbursement, etc.
    transaction_id = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="line_items")
    account = relationship("ChartOfAccounts")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)",
            name="check_debit_or_credit"
        ),
        Index("ix_jel_journal", "journal_entry_id", "line_number"),
        Index("ix_jel_account", "account_id"),
    )


class GeneralLedger(Base):
    """
    General Ledger (GL)
    Posted journal entry lines for each account
    This is the master record of all accounting transactions
    """
    __tablename__ = "general_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Account reference
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    account_code = Column(String(20), nullable=False, index=True)
    
    # Transaction details
    transaction_date = Column(Date, nullable=False, index=True)
    posting_date = Column(Date, nullable=False, index=True)
    
    # Journal entry reference
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    journal_entry_number = Column(String(50), nullable=False)
    line_item_id = Column(Integer, ForeignKey("journal_entry_lines.id"), nullable=False)
    
    # Amounts
    debit_amount = Column(Numeric(15, 2), default=0.00)
    credit_amount = Column(Numeric(15, 2), default=0.00)
    balance = Column(Numeric(15, 2), nullable=False)  # Running balance
    
    # Description
    description = Column(Text, nullable=True)
    narration = Column(Text, nullable=True)
    
    # Reference to source document
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Financial period
    financial_year = Column(Integer, nullable=False, index=True)
    financial_period = Column(String(20), nullable=False)  # 202601, 2026Q1, etc.
    
    # Cost center (optional)
    cost_center = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_date = Column(Date, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    account = relationship("ChartOfAccounts", back_populates="general_ledger_entries")
    journal_entry = relationship("JournalEntry")
    line_item = relationship("JournalEntryLine")
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_gl_account_date", "account_id", "transaction_date"),
        Index("ix_gl_tenant_account", "tenant_id", "account_id"),
        Index("ix_gl_period", "financial_year", "financial_period"),
        Index("ix_gl_reference", "reference_type", "reference_id"),
    )


class TrialBalance(Base):
    """
    Trial Balance Snapshots
    Periodic snapshots of account balances
    """
    __tablename__ = "trial_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Period identification
    balance_date = Column(Date, nullable=False, index=True)
    financial_year = Column(Integer, nullable=False)
    financial_period = Column(String(20), nullable=False)
    period_type = Column(Enum(FinancialPeriod), nullable=False)
    
    # Account reference
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    
    # Balances
    opening_balance = Column(Numeric(15, 2), default=0.00)
    total_debit = Column(Numeric(15, 2), default=0.00)
    total_credit = Column(Numeric(15, 2), default=0.00)
    closing_balance = Column(Numeric(15, 2), default=0.00)
    
    # Debit or Credit nature
    debit_balance = Column(Numeric(15, 2), default=0.00)
    credit_balance = Column(Numeric(15, 2), default=0.00)
    
    # Status
    is_finalized = Column(Boolean, default=False)
    finalized_at = Column(DateTime, nullable=True)
    finalized_by = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    account = relationship("ChartOfAccounts")
    
    # Indexes
    __table_args__ = (
        Index("ix_tb_tenant_date", "tenant_id", "balance_date", "account_id", unique=True),
        Index("ix_tb_period", "financial_year", "financial_period"),
    )


class AccountingPeriod(Base):
    """
    Accounting Periods
    Manages financial period opening, closing, and locking
    """
    __tablename__ = "accounting_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Period identification
    period_name = Column(String(100), nullable=False)  # "January 2026", "Q1 2026", etc.
    period_code = Column(String(20), nullable=False)  # "202601", "2026Q1", etc.
    financial_year = Column(Integer, nullable=False)
    period_type = Column(Enum(FinancialPeriod), nullable=False)
    
    # Date range
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    # Closing process
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(Integer, nullable=True)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_ap_tenant_code", "tenant_id", "period_code", unique=True),
        Index("ix_ap_dates", "start_date", "end_date"),
    )
