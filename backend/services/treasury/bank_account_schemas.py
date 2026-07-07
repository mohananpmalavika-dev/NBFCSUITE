"""
Treasury Bank Accounts Schemas
Pydantic models for API request/response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from backend.shared.database.treasury_models import (
    BankAccountType,
    BankAccountPurpose,
    BankAccountStatus
)


# ============================================================================
# Treasury Bank Account Schemas
# ============================================================================

class TreasuryBankAccountBase(BaseModel):
    """Base schema for Treasury Bank Account"""
    bank_name: str = Field(..., max_length=200, description="Bank name")
    branch_name: Optional[str] = Field(None, max_length=200, description="Branch name")
    ifsc_code: Optional[str] = Field(None, max_length=20, description="IFSC code")
    swift_code: Optional[str] = Field(None, max_length=20, description="SWIFT code")
    account_number: str = Field(..., max_length=50, description="Account number")
    account_name: str = Field(..., max_length=200, description="Account holder name")
    account_type: BankAccountType = Field(..., description="Account type")
    account_purpose: BankAccountPurpose = Field(..., description="Account purpose")
    currency: str = Field("INR", max_length=3, description="Currency code")
    branch_id: Optional[int] = Field(None, description="Branch ID")
    location: Optional[str] = Field(None, max_length=200, description="Location")
    opening_balance: Decimal = Field(Decimal("0.00"), description="Opening balance")
    minimum_balance: Decimal = Field(Decimal("0.00"), description="Minimum balance requirement")
    maximum_balance: Optional[Decimal] = Field(None, description="Maximum balance limit")
    daily_withdrawal_limit: Optional[Decimal] = Field(None, description="Daily withdrawal limit")
    monthly_withdrawal_limit: Optional[Decimal] = Field(None, description="Monthly withdrawal limit")
    gl_account_id: Optional[int] = Field(None, description="GL account ID for integration")
    gl_account_code: Optional[str] = Field(None, max_length=20, description="GL account code")
    contact_person: Optional[str] = Field(None, max_length=200, description="Contact person")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    contact_email: Optional[str] = Field(None, max_length=200, description="Contact email")
    documentation: Optional[Dict[str, Any]] = Field(None, description="Documentation details")
    opening_date: Optional[date] = Field(None, description="Account opening date")


class TreasuryBankAccountCreate(TreasuryBankAccountBase):
    """Schema for creating new bank account"""
    pass


class TreasuryBankAccountUpdate(BaseModel):
    """Schema for updating bank account"""
    bank_name: Optional[str] = Field(None, max_length=200)
    branch_name: Optional[str] = Field(None, max_length=200)
    account_name: Optional[str] = Field(None, max_length=200)
    account_purpose: Optional[BankAccountPurpose] = None
    branch_id: Optional[int] = None
    location: Optional[str] = None
    minimum_balance: Optional[Decimal] = None
    maximum_balance: Optional[Decimal] = None
    daily_withdrawal_limit: Optional[Decimal] = None
    monthly_withdrawal_limit: Optional[Decimal] = None
    gl_account_id: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    documentation: Optional[Dict[str, Any]] = None
    status: Optional[BankAccountStatus] = None


class TreasuryBankAccountResponse(TreasuryBankAccountBase):
    """Schema for bank account response"""
    id: int
    tenant_id: int
    current_balance: Decimal
    available_balance: Decimal
    last_updated_at: Optional[datetime]
    status: BankAccountStatus
    closing_date: Optional[date]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class TreasuryBankAccountListResponse(BaseModel):
    """Schema for listing bank accounts"""
    accounts: List[TreasuryBankAccountResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BankAccountBalanceUpdate(BaseModel):
    """Schema for updating bank account balance"""
    new_balance: Decimal = Field(..., description="New account balance")
    transaction_date: date = Field(..., description="Transaction date")
    description: Optional[str] = Field(None, description="Description of update")
    create_journal_entry: bool = Field(True, description="Create GL journal entry")


class BankAccountBalanceResponse(BaseModel):
    """Schema for bank account balance response"""
    account_id: int
    account_number: str
    account_name: str
    current_balance: Decimal
    available_balance: Decimal
    minimum_balance: Decimal
    last_updated_at: Optional[datetime]
    status: BankAccountStatus


class BankAccountStatistics(BaseModel):
    """Schema for bank account statistics"""
    total_accounts: int
    active_accounts: int
    inactive_accounts: int
    total_balance: Decimal
    accounts_below_minimum: int
    accounts_by_type: Dict[str, int]
    accounts_by_purpose: Dict[str, int]


class BankAccountTransactionSummary(BaseModel):
    """Schema for account transaction summary"""
    account_id: int
    account_number: str
    period_start: date
    period_end: date
    opening_balance: Decimal
    total_receipts: Decimal
    total_payments: Decimal
    closing_balance: Decimal
    transaction_count: int


class BankAccountBulkCreate(BaseModel):
    """Schema for bulk account creation"""
    accounts: List[TreasuryBankAccountCreate]


class BankAccountBulkCreateResponse(BaseModel):
    """Schema for bulk creation response"""
    created_count: int
    failed_count: int
    created_accounts: List[TreasuryBankAccountResponse]
    errors: List[Dict[str, Any]]
