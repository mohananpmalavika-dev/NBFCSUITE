"""
Treasury - Fund Transfer Schemas
Pydantic models for internal and external fund transfers
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Enums
class FundTransferType(str, Enum):
    """Fund transfer types"""
    INTERNAL = "internal"  # Branch to branch
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CHEQUE = "cheque"
    DEMAND_DRAFT = "demand_draft"


class FundTransferStatus(str, Enum):
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


# Fund Transfer Schemas
class FundTransferCreate(BaseModel):
    """Create fund transfer"""
    transfer_type: FundTransferType = Field(..., description="Transfer type")
    source_account_id: int = Field(..., description="Source bank account ID")
    
    # For internal transfers
    destination_account_id: Optional[int] = Field(None, description="Destination account ID (internal)")
    
    # For external transfers
    destination_account_number: Optional[str] = Field(None, max_length=50)
    destination_bank_name: Optional[str] = Field(None, max_length=200)
    destination_ifsc: Optional[str] = Field(None, max_length=20)
    destination_account_holder: Optional[str] = Field(None, max_length=200)
    
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    currency: str = Field(default="INR", max_length=3)
    purpose: str = Field(..., max_length=500, description="Transfer purpose")
    reference_number: Optional[str] = Field(None, max_length=100)
    
    # Scheduling
    is_scheduled: bool = Field(default=False)
    scheduled_date: Optional[date] = Field(None, description="Scheduled execution date")
    
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than zero')
        return v

    @field_validator('destination_account_id', 'destination_account_number')
    @classmethod
    def validate_destination(cls, v, info):
        transfer_type = info.data.get('transfer_type')
        if transfer_type == FundTransferType.INTERNAL and not info.data.get('destination_account_id'):
            raise ValueError('Destination account ID required for internal transfers')
        if transfer_type != FundTransferType.INTERNAL and not info.data.get('destination_account_number'):
            raise ValueError('Destination account number required for external transfers')
        return v


class FundTransferUpdate(BaseModel):
    """Update fund transfer (draft only)"""
    transfer_type: Optional[FundTransferType] = None
    destination_account_id: Optional[int] = None
    destination_account_number: Optional[str] = Field(None, max_length=50)
    destination_bank_name: Optional[str] = Field(None, max_length=200)
    destination_ifsc: Optional[str] = Field(None, max_length=20)
    destination_account_holder: Optional[str] = Field(None, max_length=200)
    amount: Optional[Decimal] = Field(None, gt=0)
    purpose: Optional[str] = Field(None, max_length=500)
    reference_number: Optional[str] = Field(None, max_length=100)
    is_scheduled: Optional[bool] = None
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None


class FundTransferResponse(BaseModel):
    """Fund transfer response"""
    id: int
    tenant_id: int
    transfer_number: str
    transfer_date: date
    transfer_type: FundTransferType
    
    source_account_id: int
    source_account_number: Optional[str]
    
    destination_account_id: Optional[int]
    destination_account_number: Optional[str]
    destination_bank_name: Optional[str]
    destination_ifsc: Optional[str]
    destination_account_holder: Optional[str]
    
    amount: Decimal
    currency: str
    purpose: str
    reference_number: Optional[str]
    
    is_scheduled: bool
    scheduled_date: Optional[date]
    
    status: FundTransferStatus
    
    requested_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]
    
    rejected_by: Optional[int]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    
    executed_by: Optional[int]
    executed_at: Optional[datetime]
    transaction_reference: Optional[str]
    
    failure_reason: Optional[str]
    retry_count: int
    
    journal_entry_id: Optional[int]
    
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class FundTransferApprove(BaseModel):
    """Approve fund transfer"""
    approval_notes: Optional[str] = None


class FundTransferReject(BaseModel):
    """Reject fund transfer"""
    rejection_reason: str = Field(..., description="Reason for rejection")


class FundTransferExecute(BaseModel):
    """Execute fund transfer"""
    transaction_reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class FundTransferCancel(BaseModel):
    """Cancel fund transfer"""
    cancellation_reason: str = Field(..., description="Reason for cancellation")


# Statistics and Reports
class FundTransferStatistics(BaseModel):
    """Fund transfer statistics"""
    total_transfers: int
    draft_count: int
    pending_approval_count: int
    approved_count: int
    rejected_count: int
    scheduled_count: int
    in_progress_count: int
    completed_count: int
    failed_count: int
    cancelled_count: int
    
    total_amount_transferred: Decimal
    total_amount_pending: Decimal
    total_amount_completed: Decimal
    total_amount_failed: Decimal
    
    avg_transfer_amount: Decimal
    largest_transfer: Decimal
    
    by_type: dict = Field(default_factory=dict)
    today_transfers: int
    this_month_transfers: int


class FundTransferSummary(BaseModel):
    """Fund transfer summary by account"""
    account_id: int
    total_transfers: int
    total_sent: Decimal
    total_received: Decimal
    net_position: Decimal
    pending_transfers: int
    pending_amount: Decimal


class FundTransferSchedule(BaseModel):
    """Scheduled transfers summary"""
    total_scheduled: int
    due_today: int
    due_this_week: int
    due_this_month: int
    overdue: int
    scheduled_amount: Decimal


# List request/response
class FundTransferListRequest(BaseModel):
    """Request filters for listing transfers"""
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    transfer_type: Optional[FundTransferType] = None
    status: Optional[FundTransferStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_scheduled: Optional[bool] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    total: int
    items: List
    skip: int
    limit: int
