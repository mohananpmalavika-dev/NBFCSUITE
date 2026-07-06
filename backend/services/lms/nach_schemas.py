"""
NACH/eNACH Schemas
Pydantic models for NACH mandate and debit operations
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================
# Enums
# ============================================

class MandateTypeEnum(str, Enum):
    PHYSICAL = "physical"
    ENACH = "enach"


class MandateFrequencyEnum(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"
    AS_PRESENTED = "as_presented"


class MandateStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_CUSTOMER = "pending_customer"
    PENDING_BANK = "pending_bank"
    ACTIVE = "active"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class DebitStatusEnum(str, Enum):
    INITIATED = "initiated"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REVERSED = "reversed"


class DebitFailureReasonEnum(str, Enum):
    INSUFFICIENT_FUNDS = "insufficient_funds"
    ACCOUNT_CLOSED = "account_closed"
    MANDATE_CANCELLED = "mandate_cancelled"
    STOP_PAYMENT = "stop_payment"
    TECHNICAL_ERROR = "technical_error"
    AMOUNT_EXCEEDED = "amount_exceeded"
    OTHER = "other"


# ============================================
# NACH Mandate Schemas
# ============================================

class MandateCreateBase(BaseModel):
    """Base schema for mandate creation"""
    loan_account_id: int = Field(..., description="Loan account ID")
    mandate_type: MandateTypeEnum = Field(..., description="Type of mandate")
    bank_account_id: int = Field(..., description="Customer bank account ID")
    frequency: MandateFrequencyEnum = Field(..., description="Debit frequency")
    max_amount: Decimal = Field(..., gt=0, description="Maximum debit amount per transaction")
    start_date: date = Field(..., description="Mandate start date")
    end_date: date = Field(..., description="Mandate end date")
    
    # Optional fields
    debit_type: Optional[str] = Field(None, description="Fixed/Maximum debit type")
    utility_code: Optional[str] = Field(None, description="Utility code from NPCI")
    category_code: Optional[str] = Field(None, description="Category code")
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v


class PhysicalMandateCreate(MandateCreateBase):
    """Schema for physical NACH mandate creation"""
    mandate_type: MandateTypeEnum = Field(default=MandateTypeEnum.PHYSICAL, description="Type must be physical")
    physical_form_received: bool = Field(default=False, description="Physical form received")
    physical_form_number: Optional[str] = Field(None, description="Physical form reference number")


class ENACHMandateCreate(MandateCreateBase):
    """Schema for eNACH mandate creation"""
    mandate_type: MandateTypeEnum = Field(default=MandateTypeEnum.ENACH, description="Type must be enach")
    redirect_url: Optional[str] = Field(None, description="URL to redirect after authentication")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for status updates")


class MandateUpdate(BaseModel):
    """Schema for mandate updates"""
    status: Optional[MandateStatusEnum] = None
    max_amount: Optional[Decimal] = Field(None, gt=0)
    end_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    suspension_reason: Optional[str] = None
    
    class Config:
        extra = "forbid"


class MandateResponse(BaseModel):
    """Schema for mandate response"""
    id: int
    loan_account_id: int
    mandate_number: str
    mandate_type: MandateTypeEnum
    bank_account_id: int
    status: MandateStatusEnum
    frequency: MandateFrequencyEnum
    max_amount: Decimal
    start_date: date
    end_date: date
    
    # Physical NACH fields
    physical_form_received: Optional[bool] = None
    physical_form_number: Optional[str] = None
    
    # eNACH fields
    enach_request_id: Optional[str] = None
    enach_authentication_url: Optional[str] = None
    enach_authenticated_at: Optional[datetime] = None
    
    # Bank details
    umrn: Optional[str] = None
    sponsor_bank_code: Optional[str] = None
    utility_code: Optional[str] = None
    category_code: Optional[str] = None
    
    # Status fields
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    suspension_reason: Optional[str] = None
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class ENACHAuthenticationResponse(BaseModel):
    """Response for eNACH authentication initiation"""
    mandate_id: int
    mandate_number: str
    enach_request_id: str
    authentication_url: str
    message: str


class MandateListFilter(BaseModel):
    """Filters for mandate list"""
    loan_account_id: Optional[int] = None
    status: Optional[MandateStatusEnum] = None
    mandate_type: Optional[MandateTypeEnum] = None
    expiring_before: Optional[date] = None


class MandateStatistics(BaseModel):
    """Mandate statistics"""
    total_mandates: int
    active_mandates: int
    pending_mandates: int
    expired_mandates: int
    cancelled_mandates: int
    physical_mandates: int
    enach_mandates: int
    total_max_debit_amount: Decimal
    mandates_expiring_30_days: int
    mandates_expiring_60_days: int


# ============================================
# NACH Debit Transaction Schemas
# ============================================

class DebitInitiateRequest(BaseModel):
    """Schema for initiating debit transaction"""
    mandate_id: int = Field(..., description="NACH mandate ID")
    repayment_schedule_id: int = Field(..., description="Repayment schedule ID")
    debit_amount: Decimal = Field(..., gt=0, description="Amount to debit")
    debit_date: date = Field(..., description="Scheduled debit date")
    purpose: str = Field(..., description="Purpose of debit (e.g., EMI Payment)")
    
    @field_validator('debit_date')
    @classmethod
    def validate_debit_date(cls, v):
        if v < date.today():
            raise ValueError('Debit date cannot be in the past')
        return v


class DebitResponseUpdate(BaseModel):
    """Schema for updating debit response from bank"""
    transaction_reference: str = Field(..., description="Transaction reference number")
    status: DebitStatusEnum = Field(..., description="Debit status")
    bank_reference: Optional[str] = Field(None, description="Bank reference number")
    utr_number: Optional[str] = Field(None, description="UTR number for successful debits")
    failure_reason: Optional[DebitFailureReasonEnum] = None
    failure_remarks: Optional[str] = None
    processed_date: Optional[date] = None
    
    class Config:
        extra = "forbid"


class DebitRetryRequest(BaseModel):
    """Schema for retry request"""
    retry_date: date = Field(..., description="New retry date")
    retry_reason: str = Field(..., description="Reason for retry")
    
    @field_validator('retry_date')
    @classmethod
    def validate_retry_date(cls, v):
        if v < date.today():
            raise ValueError('Retry date cannot be in the past')
        return v


class DebitTransactionResponse(BaseModel):
    """Schema for debit transaction response"""
    id: int
    mandate_id: int
    loan_account_id: int
    repayment_schedule_id: int
    transaction_reference: str
    debit_amount: Decimal
    debit_date: date
    status: DebitStatusEnum
    
    # Bank response fields
    bank_reference: Optional[str] = None
    utr_number: Optional[str] = None
    processed_date: Optional[date] = None
    
    # Failure fields
    failure_reason: Optional[DebitFailureReasonEnum] = None
    failure_remarks: Optional[str] = None
    retry_count: int
    max_retry_attempts: int
    next_retry_date: Optional[date] = None
    
    # NPCI fields
    npci_transaction_id: Optional[str] = None
    settlement_date: Optional[date] = None
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    initiated_by: int
    
    class Config:
        from_attributes = True


class DebitTransactionListFilter(BaseModel):
    """Filters for debit transaction list"""
    mandate_id: Optional[int] = None
    loan_account_id: Optional[int] = None
    status: Optional[DebitStatusEnum] = None
    debit_date_from: Optional[date] = None
    debit_date_to: Optional[date] = None
    failure_reason: Optional[DebitFailureReasonEnum] = None


class BulkDebitInitiateRequest(BaseModel):
    """Schema for bulk debit initiation"""
    debit_requests: List[DebitInitiateRequest] = Field(..., min_length=1, max_length=1000)
    batch_reference: Optional[str] = Field(None, description="Batch reference for tracking")


class BulkDebitResponse(BaseModel):
    """Response for bulk debit initiation"""
    total_requests: int
    successful: int
    failed: int
    batch_reference: str
    debit_transactions: List[DebitTransactionResponse]
    errors: List[dict]


class DebitStatistics(BaseModel):
    """Debit transaction statistics"""
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    total_debit_amount: Decimal
    total_success_amount: Decimal
    total_failed_amount: Decimal
    success_rate: float
    average_debit_amount: Decimal
    pending_retry_count: int


# ============================================
# NACH Dashboard Schemas
# ============================================

class NACHDashboard(BaseModel):
    """Combined NACH dashboard data"""
    mandate_statistics: MandateStatistics
    debit_statistics: DebitStatistics
    recent_failures: List[DebitTransactionResponse]
    expiring_mandates: List[MandateResponse]
    pending_approvals: List[MandateResponse]


# ============================================
# NACH Webhook Schemas
# ============================================

class ENACHWebhookPayload(BaseModel):
    """Schema for eNACH webhook payload from NPCI"""
    enach_request_id: str
    mandate_number: str
    status: str
    umrn: Optional[str] = None
    bank_reference: Optional[str] = None
    rejection_reason: Optional[str] = None
    timestamp: datetime


class DebitWebhookPayload(BaseModel):
    """Schema for NACH debit webhook payload"""
    transaction_reference: str
    npci_transaction_id: str
    status: str
    bank_reference: Optional[str] = None
    utr_number: Optional[str] = None
    failure_reason: Optional[str] = None
    processed_date: Optional[date] = None
    timestamp: datetime
