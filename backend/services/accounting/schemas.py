"""
Accounting Schemas
Pydantic models for API request/response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator, field_validator

from backend.shared.database.accounting_models import (
    AccountType,
    AccountSubType,
    JournalEntryType,
    JournalEntryStatus,
    FinancialPeriod
)


# ============================================================================
# Chart of Accounts Schemas
# ============================================================================

class ChartOfAccountsBase(BaseModel):
    """Base schema for Chart of Accounts"""
    account_code: str = Field(..., max_length=20, description="Unique account code")
    account_name: str = Field(..., max_length=200, description="Account name")
    account_type: AccountType = Field(..., description="Asset, Liability, Equity, Income, Expense")
    account_sub_type: AccountSubType = Field(..., description="Detailed account classification")
    parent_account_id: Optional[int] = Field(None, description="Parent account ID for hierarchy")
    level: int = Field(1, ge=1, le=5, description="Account hierarchy level")
    is_group: bool = Field(False, description="Is this a group account")
    allow_manual_entry: bool = Field(True, description="Allow manual journal entries")
    opening_balance: Decimal = Field(Decimal("0.00"), ge=0, description="Opening balance")
    description: Optional[str] = Field(None, description="Account description")
    notes: Optional[str] = Field(None, description="Additional notes")


class ChartOfAccountsCreate(ChartOfAccountsBase):
    """Schema for creating new account"""
    pass


class ChartOfAccountsUpdate(BaseModel):
    """Schema for updating account"""
    account_name: Optional[str] = Field(None, max_length=200)
    account_sub_type: Optional[AccountSubType] = None
    allow_manual_entry: Optional[bool] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class ChartOfAccountsResponse(ChartOfAccountsBase):
    """Schema for account response"""
    id: int
    tenant_id: int
    is_active: bool
    is_system: bool
    current_balance: Decimal
    debit_balance: Decimal
    credit_balance: Decimal
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChartOfAccountsListResponse(BaseModel):
    """Schema for listing accounts"""
    accounts: List[ChartOfAccountsResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AccountHierarchyResponse(BaseModel):
    """Schema for account hierarchy tree"""
    id: int
    account_code: str
    account_name: str
    account_type: AccountType
    is_group: bool
    level: int
    current_balance: Decimal
    children: List['AccountHierarchyResponse'] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# Journal Entry Schemas
# ============================================================================

class JournalEntryLineCreate(BaseModel):
    """Schema for journal entry line creation"""
    account_id: int = Field(..., description="Chart of Accounts ID")
    debit_amount: Decimal = Field(Decimal("0.00"), ge=0, description="Debit amount")
    credit_amount: Decimal = Field(Decimal("0.00"), ge=0, description="Credit amount")
    description: Optional[str] = Field(None, max_length=500)
    cost_center: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=50)
    
    @field_validator("debit_amount", "credit_amount", mode="before")
    @classmethod
    def validate_amounts(cls, v):
        """Validate decimal places"""
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return round(v, 2)
    
    @model_validator(mode='after')
    def validate_debit_or_credit(self):
        """Ensure either debit or credit is provided, not both"""
        debit = self.debit_amount or Decimal("0.00")
        credit = self.credit_amount or Decimal("0.00")
        
        if debit > 0 and credit > 0:
            raise ValueError("Cannot have both debit and credit in same line")
        if debit == 0 and credit == 0:
            raise ValueError("Either debit or credit must be greater than zero")
        
        return self


class JournalEntryLineResponse(BaseModel):
    """Schema for journal entry line response"""
    id: int
    line_number: int
    account_id: int
    account_code: str
    account_name: Optional[str] = None
    debit_amount: Decimal
    credit_amount: Decimal
    description: Optional[str]
    cost_center: Optional[str]
    department: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class JournalEntryBase(BaseModel):
    """Base schema for journal entry"""
    entry_date: date = Field(..., description="Transaction date")
    entry_type: JournalEntryType = Field(JournalEntryType.MANUAL, description="Entry type")
    narration: str = Field(..., max_length=1000, description="Entry narration/description")
    internal_notes: Optional[str] = Field(None, description="Internal notes")
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    reference_number: Optional[str] = Field(None, max_length=100)


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating journal entry"""
    line_items: List[JournalEntryLineCreate] = Field(..., min_items=2, description="At least 2 line items required")
    
    @model_validator(mode='after')
    def validate_balanced_entry(self):
        """Ensure total debits equal total credits"""
        line_items = self.line_items or []
        
        total_debit = sum(item.debit_amount for item in line_items)
        total_credit = sum(item.credit_amount for item in line_items)
        
        if abs(total_debit - total_credit) > Decimal("0.01"):  # Allow small rounding difference
            raise ValueError(f"Total debits ({total_debit}) must equal total credits ({total_credit})")
        
        return self


class JournalEntryUpdate(BaseModel):
    """Schema for updating journal entry (only draft entries)"""
    entry_date: Optional[date] = None
    narration: Optional[str] = Field(None, max_length=1000)
    internal_notes: Optional[str] = None


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response"""
    id: int
    tenant_id: int
    entry_number: str
    posting_date: Optional[date]
    status: JournalEntryStatus
    total_debit: Decimal
    total_credit: Decimal
    is_reversal: bool
    reversed_entry_id: Optional[int]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    line_items: List[JournalEntryLineResponse] = []
    
    class Config:
        from_attributes = True


class JournalEntryListResponse(BaseModel):
    """Schema for listing journal entries"""
    entries: List[JournalEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JournalEntryPostRequest(BaseModel):
    """Schema for posting journal entry"""
    posting_date: Optional[date] = Field(None, description="Posting date (defaults to entry date)")


class JournalEntryReversalRequest(BaseModel):
    """Schema for reversing journal entry"""
    reversal_date: date = Field(..., description="Date of reversal")
    narration: str = Field(..., max_length=1000, description="Reason for reversal")


# ============================================================================
# General Ledger Schemas
# ============================================================================

class GeneralLedgerEntryResponse(BaseModel):
    """Schema for GL entry response"""
    id: int
    account_id: int
    account_code: str
    account_name: Optional[str] = None
    transaction_date: date
    posting_date: date
    journal_entry_id: int
    journal_entry_number: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance: Decimal
    description: Optional[str]
    narration: Optional[str]
    reference_type: Optional[str]
    reference_id: Optional[int]
    reference_number: Optional[str]
    financial_year: int
    financial_period: str
    cost_center: Optional[str]
    department: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class GeneralLedgerQueryRequest(BaseModel):
    """Schema for querying general ledger"""
    account_id: Optional[int] = Field(None, description="Filter by account")
    account_code: Optional[str] = Field(None, description="Filter by account code")
    from_date: Optional[date] = Field(None, description="Start date")
    to_date: Optional[date] = Field(None, description="End date")
    financial_year: Optional[int] = Field(None, description="Filter by financial year")
    reference_type: Optional[str] = Field(None, description="Filter by reference type")
    reference_id: Optional[int] = Field(None, description="Filter by reference ID")
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=500)


class GeneralLedgerListResponse(BaseModel):
    """Schema for GL listing response"""
    entries: List[GeneralLedgerEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    summary: Optional[Dict[str, Any]] = None


class AccountStatementRequest(BaseModel):
    """Schema for account statement request"""
    account_id: int = Field(..., description="Account ID")
    from_date: date = Field(..., description="Start date")
    to_date: date = Field(..., description="End date")


class AccountStatementResponse(BaseModel):
    """Schema for account statement response"""
    account_id: int
    account_code: str
    account_name: str
    account_type: AccountType
    from_date: date
    to_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    entries: List[GeneralLedgerEntryResponse]


# ============================================================================
# Trial Balance Schemas
# ============================================================================

class TrialBalanceEntryResponse(BaseModel):
    """Schema for trial balance entry"""
    account_id: int
    account_code: str
    account_name: str
    account_type: AccountType
    opening_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    closing_balance: Decimal
    debit_balance: Decimal
    credit_balance: Decimal
    
    class Config:
        from_attributes = True


class TrialBalanceRequest(BaseModel):
    """Schema for trial balance request"""
    balance_date: date = Field(..., description="As of date")
    account_type: Optional[AccountType] = Field(None, description="Filter by account type")


class TrialBalanceResponse(BaseModel):
    """Schema for trial balance response"""
    balance_date: date
    financial_year: int
    financial_period: str
    entries: List[TrialBalanceEntryResponse]
    summary: Dict[str, Any]
    is_balanced: bool


class TrialBalanceSummary(BaseModel):
    """Trial balance summary"""
    total_debit: Decimal
    total_credit: Decimal
    total_asset: Decimal
    total_liability: Decimal
    total_equity: Decimal
    total_income: Decimal
    total_expense: Decimal
    net_profit_loss: Decimal
    is_balanced: bool


# ============================================================================
# Financial Statements Schemas
# ============================================================================

class ProfitLossLineItem(BaseModel):
    """P&L line item"""
    account_code: str
    account_name: str
    amount: Decimal
    percentage: Optional[Decimal] = None


class ProfitLossRequest(BaseModel):
    """Request for Profit & Loss statement"""
    from_date: date = Field(..., description="Start date")
    to_date: date = Field(..., description="End date")
    comparative: bool = Field(False, description="Include comparative period")


class ProfitLossResponse(BaseModel):
    """Profit & Loss statement response"""
    from_date: date
    to_date: date
    income: List[ProfitLossLineItem]
    expenses: List[ProfitLossLineItem]
    total_income: Decimal
    total_expenses: Decimal
    gross_profit: Decimal
    operating_profit: Decimal
    net_profit: Decimal
    profit_margin: Decimal


class BalanceSheetLineItem(BaseModel):
    """Balance sheet line item"""
    account_code: str
    account_name: str
    amount: Decimal
    percentage: Optional[Decimal] = None


class BalanceSheetRequest(BaseModel):
    """Request for Balance Sheet"""
    as_of_date: date = Field(..., description="As of date")
    comparative: bool = Field(False, description="Include comparative date")


class BalanceSheetResponse(BaseModel):
    """Balance Sheet response"""
    as_of_date: date
    assets: List[BalanceSheetLineItem]
    liabilities: List[BalanceSheetLineItem]
    equity: List[BalanceSheetLineItem]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    is_balanced: bool


# ============================================================================
# Accounting Period Schemas
# ============================================================================

class AccountingPeriodBase(BaseModel):
    """Base schema for accounting period"""
    period_name: str = Field(..., max_length=100)
    period_code: str = Field(..., max_length=20)
    financial_year: int
    period_type: FinancialPeriod
    start_date: date
    end_date: date


class AccountingPeriodCreate(AccountingPeriodBase):
    """Schema for creating accounting period"""
    pass


class AccountingPeriodResponse(AccountingPeriodBase):
    """Schema for accounting period response"""
    id: int
    tenant_id: int
    is_active: bool
    is_closed: bool
    is_locked: bool
    closed_at: Optional[datetime]
    closed_by: Optional[int]
    locked_at: Optional[datetime]
    locked_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountingPeriodListResponse(BaseModel):
    """Schema for listing accounting periods"""
    periods: List[AccountingPeriodResponse]
    total: int


# ============================================================================
# Event-driven Accounting Schemas
# ============================================================================

class LoanDisbursementAccountingRequest(BaseModel):
    """Schema for loan disbursement accounting"""
    loan_account_id: int
    disbursement_amount: Decimal
    disbursement_date: date
    processing_fee: Decimal = Decimal("0.00")
    documentation_charges: Decimal = Decimal("0.00")
    insurance_premium: Decimal = Decimal("0.00")
    net_disbursement: Decimal


class LoanRepaymentAccountingRequest(BaseModel):
    """Schema for loan repayment accounting"""
    loan_account_id: int
    repayment_id: int
    payment_date: date
    principal_amount: Decimal
    interest_amount: Decimal
    penal_interest: Decimal = Decimal("0.00")
    charges: Decimal = Decimal("0.00")
    total_amount: Decimal


class InterestAccrualRequest(BaseModel):
    """Schema for interest accrual"""
    loan_account_id: int
    accrual_date: date
    interest_amount: Decimal


class DepositReceiptAccountingRequest(BaseModel):
    """Schema for deposit receipt accounting"""
    deposit_id: int
    deposit_amount: Decimal
    deposit_date: date
    customer_id: int


# ============================================================================
# Statistics and Dashboard Schemas
# ============================================================================

class AccountingStatistics(BaseModel):
    """Accounting module statistics"""
    total_accounts: int
    active_accounts: int
    total_journal_entries: int
    posted_entries: int
    draft_entries: int
    current_period: Optional[str]
    last_closing_date: Optional[date]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    total_income: Decimal
    total_expenses: Decimal
    net_position: Decimal


class DashboardMetrics(BaseModel):
    """Dashboard metrics"""
    assets_vs_liabilities: Dict[str, Decimal]
    income_vs_expenses: Dict[str, Decimal]
    account_type_distribution: Dict[str, int]
    monthly_transactions: Dict[str, int]
    profit_trend: List[Dict[str, Any]]


# Update forward references
AccountHierarchyResponse.update_forward_refs()
