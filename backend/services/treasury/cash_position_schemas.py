"""
Treasury Cash Position - Pydantic Schemas
Validation models for cash position management
"""

from datetime import date, datetime
from typing import Optional, Dict, List
from decimal import Decimal
from pydantic import BaseModel, Field, validator


# ============================================
# Base Schemas
# ============================================

class CashPositionBase(BaseModel):
    """Base schema for cash position"""
    position_date: date = Field(..., description="Date of cash position")
    branch_id: Optional[int] = Field(None, description="Branch ID (null for HO)")
    account_id: Optional[int] = Field(None, description="Bank account ID if deposited")
    opening_balance: Decimal = Field(default=0, ge=0, description="Opening cash balance")
    cash_received: Decimal = Field(default=0, ge=0, description="Cash received during day")
    cash_paid: Decimal = Field(default=0, ge=0, description="Cash paid during day")
    bank_deposit: Decimal = Field(default=0, ge=0, description="Amount deposited to bank")
    bank_withdrawal: Decimal = Field(default=0, ge=0, description="Amount withdrawn from bank")
    closing_balance: Decimal = Field(default=0, ge=0, description="Closing cash balance")
    denomination_details: Optional[Dict] = Field(None, description="Denomination-wise breakup")
    vault_location: Optional[str] = Field(None, max_length=100, description="Vault location")
    recorded_by: Optional[int] = Field(None, description="User who recorded position")
    verified_by: Optional[int] = Field(None, description="User who verified position")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    discrepancy_amount: Decimal = Field(default=0, description="Physical vs system difference")
    discrepancy_reason: Optional[str] = Field(None, max_length=500, description="Reason for discrepancy")
    notes: Optional[str] = Field(None, description="Additional notes")
    status: str = Field(default="draft", description="Status: draft, verified, finalized")


class TreasuryCashPositionCreate(CashPositionBase):
    """Schema for creating cash position"""
    pass


class TreasuryCashPositionUpdate(BaseModel):
    """Schema for updating cash position"""
    opening_balance: Optional[Decimal] = Field(None, ge=0)
    cash_received: Optional[Decimal] = Field(None, ge=0)
    cash_paid: Optional[Decimal] = Field(None, ge=0)
    bank_deposit: Optional[Decimal] = Field(None, ge=0)
    bank_withdrawal: Optional[Decimal] = Field(None, ge=0)
    closing_balance: Optional[Decimal] = Field(None, ge=0)
    denomination_details: Optional[Dict] = None
    vault_location: Optional[str] = Field(None, max_length=100)
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    discrepancy_amount: Optional[Decimal] = None
    discrepancy_reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    status: Optional[str] = None


class TreasuryCashPositionResponse(CashPositionBase):
    """Schema for cash position response"""
    id: int
    tenant_id: int
    branch_name: Optional[str] = None
    account_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TreasuryCashPositionListResponse(BaseModel):
    """Schema for paginated cash position list"""
    items: List[TreasuryCashPositionResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================
# Denomination Schemas
# ============================================

class DenominationBreakup(BaseModel):
    """Schema for denomination breakup"""
    notes_2000: int = Field(default=0, ge=0, description="Count of ₹2000 notes")
    notes_500: int = Field(default=0, ge=0, description="Count of ₹500 notes")
    notes_200: int = Field(default=0, ge=0, description="Count of ₹200 notes")
    notes_100: int = Field(default=0, ge=0, description="Count of ₹100 notes")
    notes_50: int = Field(default=0, ge=0, description="Count of ₹50 notes")
    notes_20: int = Field(default=0, ge=0, description="Count of ₹20 notes")
    notes_10: int = Field(default=0, ge=0, description="Count of ₹10 notes")
    coins_10: int = Field(default=0, ge=0, description="Count of ₹10 coins")
    coins_5: int = Field(default=0, ge=0, description="Count of ₹5 coins")
    coins_2: int = Field(default=0, ge=0, description="Count of ₹2 coins")
    coins_1: int = Field(default=0, ge=0, description="Count of ₹1 coins")
    
    @validator('*', pre=True, always=True)
    def default_zero(cls, v):
        return v if v is not None else 0
    
    def calculate_total(self) -> Decimal:
        """Calculate total amount from denomination"""
        total = (
            self.notes_2000 * 2000 +
            self.notes_500 * 500 +
            self.notes_200 * 200 +
            self.notes_100 * 100 +
            self.notes_50 * 50 +
            self.notes_20 * 20 +
            self.notes_10 * 10 +
            self.coins_10 * 10 +
            self.coins_5 * 5 +
            self.coins_2 * 2 +
            self.coins_1 * 1
        )
        return Decimal(total)


# ============================================
# Cash Transfer Schemas
# ============================================

class CashTransferCreate(BaseModel):
    """Schema for creating cash transfer between branches"""
    transfer_date: date = Field(..., description="Date of transfer")
    from_branch_id: int = Field(..., description="Source branch ID")
    to_branch_id: int = Field(..., description="Destination branch ID")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    denomination_details: Optional[Dict] = Field(None, description="Denomination breakup")
    courier_name: Optional[str] = Field(None, max_length=200, description="Courier/person name")
    courier_contact: Optional[str] = Field(None, max_length=20, description="Contact number")
    vehicle_number: Optional[str] = Field(None, max_length=50, description="Vehicle number")
    dispatch_time: Optional[datetime] = Field(None, description="Dispatch time")
    received_time: Optional[datetime] = Field(None, description="Received time")
    received_by: Optional[int] = Field(None, description="Receiver user ID")
    notes: Optional[str] = Field(None, description="Transfer notes")


class CashTransferResponse(BaseModel):
    """Schema for cash transfer response"""
    id: int
    tenant_id: int
    transfer_date: date
    from_branch_id: int
    from_branch_name: Optional[str] = None
    to_branch_id: int
    to_branch_name: Optional[str] = None
    amount: Decimal
    denomination_details: Optional[Dict] = None
    courier_name: Optional[str] = None
    courier_contact: Optional[str] = None
    vehicle_number: Optional[str] = None
    dispatch_time: Optional[datetime] = None
    received_time: Optional[datetime] = None
    received_by: Optional[int] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Statistics & Reports Schemas
# ============================================

class TreasuryCashPositionStatistics(BaseModel):
    """Schema for cash position statistics"""
    total_cash_on_hand: Decimal
    total_branches: int
    branches_with_low_cash: int
    branches_with_high_cash: int
    total_cash_received_today: Decimal
    total_cash_paid_today: Decimal
    total_bank_deposits_today: Decimal
    positions_pending_verification: int
    cash_by_branch: Dict[str, Decimal]
    denomination_summary: Optional[Dict] = None


class BranchCashSummary(BaseModel):
    """Schema for branch-wise cash summary"""
    branch_id: int
    branch_name: str
    current_cash: Decimal
    opening_balance: Decimal
    closing_balance: Decimal
    last_updated: datetime
    status: str
    low_cash_alert: bool


class CashMovementSummary(BaseModel):
    """Schema for cash movement summary"""
    date: date
    opening_balance: Decimal
    cash_received: Decimal
    cash_paid: Decimal
    bank_deposit: Decimal
    bank_withdrawal: Decimal
    closing_balance: Decimal
    net_movement: Decimal


class CashAlertResponse(BaseModel):
    """Schema for cash alerts"""
    alert_type: str  # low_cash, high_cash, discrepancy, pending_verification
    severity: str  # info, warning, critical
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None
    message: str
    amount: Optional[Decimal] = None
    created_at: datetime


# ============================================
# Bulk Operations Schemas
# ============================================

class BulkCashPositionCreate(BaseModel):
    """Schema for bulk cash position creation"""
    positions: List[TreasuryCashPositionCreate] = Field(..., min_items=1, max_items=100)


class BulkCashPositionResponse(BaseModel):
    """Schema for bulk creation response"""
    success_count: int
    failure_count: int
    created_ids: List[int]
    errors: List[Dict]
