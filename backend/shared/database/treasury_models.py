"""
Treasury & Cash Management Database Models
Bank accounts, cash positions, reconciliations, transfers, liquidity, investments, forecasting
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text,
    ForeignKey, Enum, Index, CheckConstraint, JSON
)
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.connection import Base


# Enums
class BankAccountType(str, enum.Enum):
    """Bank account types"""
    SAVINGS = "savings"
    CURRENT = "current"
    CASH_CREDIT = "cash_credit"
    OVERDRAFT = "overdraft"
    FIXED_DEPOSIT = "fixed_deposit"


class BankAccountPurpose(str, enum.Enum):
    """Purpose of bank account"""
    OPERATIONAL = "operational"
    DISBURSEMENT = "disbursement"
    COLLECTION = "collection"
    PAYROLL = "payroll"
    TAX = "tax"
    RESERVE = "reserve"
    INVESTMENT = "investment"


class BankAccountStatus(str, enum.Enum):
    """Bank account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DORMANT = "dormant"
    CLOSED = "closed"
    FROZEN = "frozen"


class ReconciliationStatus(str, enum.Enum):
    """Reconciliation status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    MATCHED = "matched"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReconciliationItemType(str, enum.Enum):
    """Types of reconciliation items"""
    OUTSTANDING_CHEQUE = "outstanding_cheque"
    DEPOSIT_IN_TRANSIT = "deposit_in_transit"
    BANK_CHARGES = "bank_charges"
    INTEREST_EARNED = "interest_earned"
    DIRECT_DEBIT = "direct_debit"
    DIRECT_CREDIT = "direct_credit"
    ERROR_CORRECTION = "error_correction"
    OTHER = "other"


class FundTransferType(str, enum.Enum):
    """Fund transfer types"""
    INTERNAL = "internal"  # Branch to branch
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CHEQUE = "cheque"
    DEMAND_DRAFT = "demand_draft"


class FundTransferStatus(str, enum.Enum):
    """Fund transfer status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvestmentType(str, enum.Enum):
    """Investment types"""
    FIXED_DEPOSIT = "fixed_deposit"
    GOVERNMENT_SECURITIES = "government_securities"
    CORPORATE_BONDS = "corporate_bonds"
    MUTUAL_FUNDS = "mutual_funds"
    COMMERCIAL_PAPER = "commercial_paper"
    CERTIFICATE_OF_DEPOSIT = "certificate_of_deposit"
    TREASURY_BILLS = "treasury_bills"
    EQUITY = "equity"
    OTHER = "other"


class InvestmentStatus(str, enum.Enum):
    """Investment status"""
    ACTIVE = "active"
    MATURED = "matured"
    SOLD = "sold"
    CANCELLED = "cancelled"


class InvestmentTransactionType(str, enum.Enum):
    """Investment transaction types"""
    PURCHASE = "purchase"
    SALE = "sale"
    INTEREST_INCOME = "interest_income"
    DIVIDEND_INCOME = "dividend_income"
    MTM_ADJUSTMENT = "mtm_adjustment"
    MATURITY = "maturity"


# Models
class TreasuryBankAccount(Base):
    """
    Treasury Bank Accounts Master
    All bank accounts managed by treasury
    """
    __tablename__ = "treasury_bank_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Bank details
    bank_name = Column(String(200), nullable=False)
    branch_name = Column(String(200), nullable=True)
    ifsc_code = Column(String(20), nullable=True)
    swift_code = Column(String(20), nullable=True)
    
    # Account details
    account_number = Column(String(50), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(BankAccountType), nullable=False)
    account_purpose = Column(Enum(BankAccountPurpose), nullable=False)
    currency = Column(String(3), default="INR")
    
    # Branch/location
    branch_id = Column(Integer, nullable=True)  # Link to branch master
    location = Column(String(200), nullable=True)
    
    # Balance tracking
    opening_balance = Column(Numeric(15, 2), default=0.00)
    current_balance = Column(Numeric(15, 2), default=0.00)
    available_balance = Column(Numeric(15, 2), default=0.00)
    last_updated_at = Column(DateTime, nullable=True)
    
    # Limits and controls
    minimum_balance = Column(Numeric(15, 2), default=0.00)
    maximum_balance = Column(Numeric(15, 2), nullable=True)
    daily_withdrawal_limit = Column(Numeric(15, 2), nullable=True)
    monthly_withdrawal_limit = Column(Numeric(15, 2), nullable=True)
    
    # GL integration
    gl_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    gl_account_code = Column(String(20), nullable=True)
    
    # Contact and documentation
    contact_person = Column(String(200), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(200), nullable=True)
    documentation = Column(JSON, nullable=True)  # Document URLs, notes
    
    # Status
    status = Column(Enum(BankAccountStatus), default=BankAccountStatus.ACTIVE)
    opening_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    gl_account = relationship("ChartOfAccounts")
    cash_positions = relationship("CashPosition", back_populates="bank_account")
    bank_statements = relationship("BankStatement", back_populates="bank_account")
    reconciliations = relationship("BankReconciliation", back_populates="bank_account")
    
    # Indexes
    __table_args__ = (
        Index("ix_tba_tenant_account", "tenant_id", "account_number", unique=True),
        Index("ix_tba_status", "status"),
        Index("ix_tba_branch", "branch_id"),
    )


class CashPosition(Base):
    """
    Daily Cash Position Tracking
    Records cash holdings across branches and bank accounts
    """
    __tablename__ = "cash_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Position date and location
    position_date = Column(Date, nullable=False, index=True)
    branch_id = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    
    # Bank account (if applicable)
    bank_account_id = Column(Integer, ForeignKey("treasury_bank_accounts.id"), nullable=True)
    
    # Cash type (physical cash vs bank balance)
    is_physical_cash = Column(Boolean, default=False)
    
    # Balances
    opening_balance = Column(Numeric(15, 2), default=0.00)
    receipts = Column(Numeric(15, 2), default=0.00)
    payments = Column(Numeric(15, 2), default=0.00)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    
    # Denomination details (for physical cash)
    denomination_details = Column(JSON, nullable=True)  # {2000: 10, 500: 20, etc.}
    
    # Cash movements
    cash_in_transit = Column(Numeric(15, 2), default=0.00)
    cash_transfers_out = Column(Numeric(15, 2), default=0.00)
    cash_transfers_in = Column(Numeric(15, 2), default=0.00)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_by = Column(Integer, nullable=True)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="draft")  # draft, verified, finalized
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    bank_account = relationship("TreasuryBankAccount", back_populates="cash_positions")
    
    # Indexes
    __table_args__ = (
        Index("ix_cp_tenant_date", "tenant_id", "position_date"),
        Index("ix_cp_branch", "branch_id"),
        Index("ix_cp_bank_account", "bank_account_id"),
    )


class BankStatement(Base):
    """
    Bank Statements
    Imported bank statements for reconciliation
    """
    __tablename__ = "bank_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Bank account
    bank_account_id = Column(Integer, ForeignKey("treasury_bank_accounts.id"), nullable=False)
    
    # Transaction details
    transaction_date = Column(Date, nullable=False, index=True)
    value_date = Column(Date, nullable=True)
    transaction_reference = Column(String(100), nullable=True, index=True)
    
    # Transaction description
    description = Column(Text, nullable=False)
    cheque_number = Column(String(50), nullable=True)
    
    # Amounts
    debit_amount = Column(Numeric(15, 2), default=0.00)
    credit_amount = Column(Numeric(15, 2), default=0.00)
    balance = Column(Numeric(15, 2), nullable=True)
    
    # Import details
    import_batch_id = Column(String(50), nullable=True)
    import_date = Column(DateTime, default=datetime.utcnow)
    imported_by = Column(Integer, nullable=False)
    
    # Matching status
    is_matched = Column(Boolean, default=False)
    matched_gl_entry_id = Column(Integer, nullable=True)
    matched_at = Column(DateTime, nullable=True)
    matched_by = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bank_account = relationship("TreasuryBankAccount", back_populates="bank_statements")
    
    # Indexes
    __table_args__ = (
        Index("ix_bs_account_date", "bank_account_id", "transaction_date"),
        Index("ix_bs_reference", "transaction_reference"),
        Index("ix_bs_matched", "is_matched"),
    )


class BankReconciliation(Base):
    """
    Bank Reconciliation
    Header for bank reconciliation process
    """
    __tablename__ = "bank_reconciliations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Reconciliation identification
    reconciliation_number = Column(String(50), nullable=False, unique=True, index=True)
    reconciliation_date = Column(Date, nullable=False, index=True)
    
    # Bank account
    bank_account_id = Column(Integer, ForeignKey("treasury_bank_accounts.id"), nullable=False)
    
    # Period
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # Balances
    book_balance = Column(Numeric(15, 2), nullable=False)  # GL balance
    bank_balance = Column(Numeric(15, 2), nullable=False)  # Bank statement balance
    difference = Column(Numeric(15, 2), nullable=False)
    
    # Matching summary
    total_matched = Column(Integer, default=0)
    total_unmatched = Column(Integer, default=0)
    matched_amount = Column(Numeric(15, 2), default=0.00)
    unmatched_amount = Column(Numeric(15, 2), default=0.00)
    
    # Status
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.DRAFT)
    
    # Approval
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    bank_account = relationship("TreasuryBankAccount", back_populates="reconciliations")
    items = relationship("ReconciliationItem", back_populates="reconciliation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_br_tenant_date", "tenant_id", "reconciliation_date"),
        Index("ix_br_account", "bank_account_id"),
        Index("ix_br_status", "status"),
    )


class ReconciliationItem(Base):
    """
    Reconciliation Items
    Outstanding items, differences, and matched transactions
    """
    __tablename__ = "reconciliation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Reconciliation link
    reconciliation_id = Column(Integer, ForeignKey("bank_reconciliations.id"), nullable=False)
    
    # Item details
    item_type = Column(Enum(ReconciliationItemType), nullable=False)
    item_date = Column(Date, nullable=False)
    
    # Description
    description = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    is_debit = Column(Boolean, default=True)
    
    # Matching
    bank_statement_id = Column(Integer, ForeignKey("bank_statements.id"), nullable=True)
    gl_entry_id = Column(Integer, nullable=True)
    is_matched = Column(Boolean, default=False)
    
    # Clearance
    is_cleared = Column(Boolean, default=False)
    cleared_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    reconciliation = relationship("BankReconciliation", back_populates="items")
    bank_statement = relationship("BankStatement")
    
    # Indexes
    __table_args__ = (
        Index("ix_ri_reconciliation", "reconciliation_id"),
        Index("ix_ri_type", "item_type"),
        Index("ix_ri_cleared", "is_cleared"),
    )


class FundTransfer(Base):
    """
    Fund Transfers
    Internal and external fund transfer management
    """
    __tablename__ = "fund_transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Transfer identification
    transfer_number = Column(String(50), nullable=False, unique=True, index=True)
    transfer_date = Column(Date, nullable=False, index=True)
    
    # Transfer type
    transfer_type = Column(Enum(FundTransferType), nullable=False)
    
    # Source account
    source_account_id = Column(Integer, ForeignKey("treasury_bank_accounts.id"), nullable=False)
    source_account_number = Column(String(50), nullable=True)
    
    # Destination account
    destination_account_id = Column(Integer, ForeignKey("treasury_bank_accounts.id"), nullable=True)  # For internal
    destination_account_number = Column(String(50), nullable=True)  # For external
    destination_bank_name = Column(String(200), nullable=True)
    destination_ifsc = Column(String(20), nullable=True)
    destination_account_holder = Column(String(200), nullable=True)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="INR")
    
    # Purpose and reference
    purpose = Column(String(500), nullable=False)
    reference_number = Column(String(100), nullable=True, index=True)
    
    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    scheduled_date = Column(Date, nullable=True)
    
    # Status tracking
    status = Column(Enum(FundTransferStatus), default=FundTransferStatus.DRAFT)
    
    # Approval workflow
    requested_by = Column(Integer, nullable=False)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Rejection
    rejected_by = Column(Integer, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Execution
    executed_by = Column(Integer, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    transaction_reference = Column(String(100), nullable=True)
    
    # Failure handling
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # GL integration
    journal_entry_id = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    source_account = relationship("TreasuryBankAccount", foreign_keys=[source_account_id])
    destination_account = relationship("TreasuryBankAccount", foreign_keys=[destination_account_id])
    
    # Indexes
    __table_args__ = (
        Index("ix_ft_tenant_date", "tenant_id", "transfer_date"),
        Index("ix_ft_status", "status"),
        Index("ix_ft_source", "source_account_id"),
        Index("ix_ft_scheduled", "is_scheduled", "scheduled_date"),
    )


class LiquidityPosition(Base):
    """
    Liquidity Position Tracking
    Daily liquidity metrics and ratios
    """
    __tablename__ = "liquidity_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Position date
    position_date = Column(Date, nullable=False, index=True)
    
    # Total positions
    total_cash = Column(Numeric(15, 2), default=0.00)
    total_bank_balance = Column(Numeric(15, 2), default=0.00)
    total_liquid_assets = Column(Numeric(15, 2), default=0.00)
    
    # Maturity bucket analysis
    maturity_0_7_days = Column(Numeric(15, 2), default=0.00)
    maturity_8_14_days = Column(Numeric(15, 2), default=0.00)
    maturity_15_30_days = Column(Numeric(15, 2), default=0.00)
    maturity_1_3_months = Column(Numeric(15, 2), default=0.00)
    maturity_3_6_months = Column(Numeric(15, 2), default=0.00)
    maturity_6_12_months = Column(Numeric(15, 2), default=0.00)
    maturity_above_12_months = Column(Numeric(15, 2), default=0.00)
    
    # Liquidity ratios
    current_ratio = Column(Numeric(10, 4), nullable=True)
    quick_ratio = Column(Numeric(10, 4), nullable=True)
    cash_ratio = Column(Numeric(10, 4), nullable=True)
    liquidity_coverage_ratio = Column(Numeric(10, 4), nullable=True)  # LCR
    net_stable_funding_ratio = Column(Numeric(10, 4), nullable=True)  # NSFR
    
    # Funding gap
    funding_gap = Column(Numeric(15, 2), nullable=True)
    cumulative_gap = Column(Numeric(15, 2), nullable=True)
    
    # Limits and alerts
    minimum_liquidity_required = Column(Numeric(15, 2), nullable=True)
    liquidity_buffer = Column(Numeric(15, 2), nullable=True)
    is_below_threshold = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("ix_lp_tenant_date", "tenant_id", "position_date", unique=True),
    )


class Investment(Base):
    """
    Investment Portfolio
    Tracks all investments made by the organization
    """
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Investment identification
    investment_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Investment details
    investment_type = Column(Enum(InvestmentType), nullable=False)
    investment_name = Column(String(200), nullable=False)
    issuer_name = Column(String(200), nullable=True)
    
    # Dates
    purchase_date = Column(Date, nullable=False, index=True)
    maturity_date = Column(Date, nullable=True, index=True)
    
    # Amounts
    face_value = Column(Numeric(15, 2), nullable=False)
    purchase_price = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2), nullable=False)
    maturity_value = Column(Numeric(15, 2), nullable=True)
    
    # Returns
    interest_rate = Column(Numeric(10, 4), nullable=True)
    interest_frequency = Column(String(20), nullable=True)  # monthly, quarterly, annually
    total_interest_earned = Column(Numeric(15, 2), default=0.00)
    total_dividends_earned = Column(Numeric(15, 2), default=0.00)
    
    # Performance
    book_value = Column(Numeric(15, 2), nullable=False)
    market_value = Column(Numeric(15, 2), nullable=True)
    unrealized_gain_loss = Column(Numeric(15, 2), default=0.00)
    realized_gain_loss = Column(Numeric(15, 2), default=0.00)
    
    # Bank account
    bank_account_id = Column(Integer, ForeignKey("treasury_bank_accounts.id"), nullable=True)
    
    # Status
    status = Column(Enum(InvestmentStatus), default=InvestmentStatus.ACTIVE)
    
    # Documentation
    certificate_number = Column(String(100), nullable=True)
    documentation = Column(JSON, nullable=True)
    
    # Approval
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    bank_account = relationship("TreasuryBankAccount")
    transactions = relationship("InvestmentTransaction", back_populates="investment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_inv_tenant_type", "tenant_id", "investment_type"),
        Index("ix_inv_status", "status"),
        Index("ix_inv_maturity", "maturity_date"),
    )


class InvestmentTransaction(Base):
    """
    Investment Transactions
    All transactions related to investments
    """
    __tablename__ = "investment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Investment link
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False)
    
    # Transaction details
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(Enum(InvestmentTransactionType), nullable=False)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    units = Column(Numeric(15, 4), nullable=True)  # For mutual funds, equity
    price_per_unit = Column(Numeric(15, 4), nullable=True)
    
    # Description
    description = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True)
    
    # GL integration
    journal_entry_id = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    investment = relationship("Investment", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index("ix_it_investment", "investment_id"),
        Index("ix_it_type", "transaction_type"),
        Index("ix_it_date", "transaction_date"),
    )


class CashFlowForecast(Base):
    """
    Cash Flow Forecasting
    Projected cash inflows and outflows
    """
    __tablename__ = "cash_flow_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Forecast identification
    forecast_date = Column(Date, nullable=False, index=True)
    forecast_period = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # Opening and closing
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    
    # Inflows
    expected_loan_repayments = Column(Numeric(15, 2), default=0.00)
    expected_deposit_collections = Column(Numeric(15, 2), default=0.00)
    expected_fee_income = Column(Numeric(15, 2), default=0.00)
    expected_investment_income = Column(Numeric(15, 2), default=0.00)
    expected_other_income = Column(Numeric(15, 2), default=0.00)
    total_expected_inflows = Column(Numeric(15, 2), nullable=False)
    
    # Outflows
    expected_loan_disbursements = Column(Numeric(15, 2), default=0.00)
    expected_deposit_withdrawals = Column(Numeric(15, 2), default=0.00)
    expected_operating_expenses = Column(Numeric(15, 2), default=0.00)
    expected_interest_payments = Column(Numeric(15, 2), default=0.00)
    expected_tax_payments = Column(Numeric(15, 2), default=0.00)
    expected_other_expenses = Column(Numeric(15, 2), default=0.00)
    total_expected_outflows = Column(Numeric(15, 2), nullable=False)
    
    # Net cash flow
    net_cash_flow = Column(Numeric(15, 2), nullable=False)
    
    # Variance (actual vs forecast)
    actual_inflows = Column(Numeric(15, 2), nullable=True)
    actual_outflows = Column(Numeric(15, 2), nullable=True)
    actual_net_cash_flow = Column(Numeric(15, 2), nullable=True)
    variance_amount = Column(Numeric(15, 2), nullable=True)
    variance_percentage = Column(Numeric(10, 2), nullable=True)
    
    # Scenario
    scenario = Column(String(50), default="expected")  # best_case, worst_case, expected
    confidence_level = Column(Numeric(5, 2), nullable=True)  # 0-100%
    
    # Notes
    assumptions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_cff_tenant_date", "tenant_id", "forecast_date"),
        Index("ix_cff_period", "period_start_date", "period_end_date"),
        Index("ix_cff_scenario", "scenario"),
    )
