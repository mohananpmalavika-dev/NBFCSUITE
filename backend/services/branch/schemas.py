"""
Branch & Operations Management Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# ============================================
# ORGANIZATION SCHEMAS
# ============================================

class OrganizationBase(BaseModel):
    """Base organization schema"""
    code: str = Field(..., description="Organization code")
    name: str = Field(..., description="Organization name")
    display_name: str = Field(..., description="Display name")
    level: str = Field(..., description="Organization level (HEAD_OFFICE, ZONE, REGION, AREA, BRANCH)")
    parent_id: Optional[UUID] = Field(None, description="Parent organization ID")
    manager_id: Optional[UUID] = Field(None, description="Manager user ID")
    manager_name: Optional[str] = Field(None, description="Manager name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"
    status: str = "ACTIVE"
    is_operational: bool = True
    opening_date: Optional[datetime] = None
    cash_limit: Decimal = Field(default=Decimal("0"), description="Cash limit")
    daily_transaction_limit: Decimal = Field(default=Decimal("0"), description="Daily transaction limit")
    settings: Optional[Dict[str, Any]] = None


class OrganizationCreate(OrganizationBase):
    """Create organization schema"""
    pass


class OrganizationUpdate(BaseModel):
    """Update organization schema"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    manager_id: Optional[UUID] = None
    manager_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    status: Optional[str] = None
    is_operational: Optional[bool] = None
    cash_limit: Optional[Decimal] = None
    daily_transaction_limit: Optional[Decimal] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(OrganizationBase):
    """Organization response schema"""
    id: UUID
    tenant_id: str
    hierarchy_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OrganizationHierarchy(BaseModel):
    """Organization hierarchy tree"""
    id: UUID
    code: str
    name: str
    level: str
    parent_id: Optional[UUID] = None
    children: List["OrganizationHierarchy"] = []
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# BRANCH SCHEMAS
# ============================================

class BranchBase(BaseModel):
    """Base branch schema"""
    organization_id: UUID = Field(..., description="Organization ID")
    branch_code: str = Field(..., description="Branch code")
    branch_name: str = Field(..., description="Branch name")
    branch_type: str = "FULL_SERVICE"
    ifsc_code: Optional[str] = None
    micr_code: Optional[str] = None
    swift_code: Optional[str] = None
    working_days: Optional[List[str]] = None
    working_hours_start: str = "09:00"
    working_hours_end: str = "17:00"
    branch_manager_id: Optional[UUID] = None
    branch_manager_name: Optional[str] = None
    branch_manager_phone: Optional[str] = None
    branch_manager_email: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_head_office: bool = False
    is_regional_office: bool = False


class BranchCreate(BranchBase):
    """Create branch schema"""
    pass


class BranchUpdate(BaseModel):
    """Update branch schema"""
    branch_name: Optional[str] = None
    branch_type: Optional[str] = None
    ifsc_code: Optional[str] = None
    working_days: Optional[List[str]] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    branch_manager_id: Optional[UUID] = None
    branch_manager_name: Optional[str] = None
    branch_manager_phone: Optional[str] = None
    branch_manager_email: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class BranchResponse(BranchBase):
    """Branch response schema"""
    id: UUID
    tenant_id: str
    staff_count: int = 0
    customer_count: int = 0
    active_loan_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# DAY OPERATION SCHEMAS
# ============================================

class DayBeginRequest(BaseModel):
    """Day begin request"""
    branch_id: UUID = Field(..., description="Branch ID")
    business_date: datetime = Field(..., description="Business date")
    opening_cash_balance: Decimal = Field(..., description="Opening cash balance")
    opening_bank_balance: Decimal = Field(default=Decimal("0"), description="Opening bank balance")
    remarks: Optional[str] = None
    checklist: Optional[Dict[str, Any]] = None


class DayEndRequest(BaseModel):
    """Day end request"""
    branch_id: UUID = Field(..., description="Branch ID")
    business_date: datetime = Field(..., description="Business date")
    closing_cash_balance: Decimal = Field(..., description="Closing cash balance")
    closing_bank_balance: Decimal = Field(default=Decimal("0"), description="Closing bank balance")
    remarks: Optional[str] = None
    checklist: Optional[Dict[str, Any]] = None


class BranchDayOperationResponse(BaseModel):
    """Day operation response"""
    id: UUID
    tenant_id: str
    branch_id: UUID
    branch_code: str
    business_date: datetime
    day_begin_time: Optional[datetime] = None
    day_begin_by: Optional[UUID] = None
    day_end_time: Optional[datetime] = None
    day_end_by: Optional[UUID] = None
    opening_cash_balance: Decimal
    opening_bank_balance: Decimal
    closing_cash_balance: Decimal
    closing_bank_balance: Decimal
    total_receipts: Decimal
    total_payments: Decimal
    total_transfers: Decimal
    transaction_count: int
    status: str
    is_holiday: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# COUNTER SCHEMAS
# ============================================

class CounterBase(BaseModel):
    """Base counter schema"""
    branch_id: UUID
    counter_number: str
    counter_name: str
    counter_type: str = "REGULAR"
    assigned_user_id: Optional[UUID] = None
    assigned_user_name: Optional[str] = None


class CounterCreate(CounterBase):
    """Create counter schema"""
    pass


class CounterOpenRequest(BaseModel):
    """Counter open request"""
    opening_balance: Decimal = Field(..., description="Opening balance")


class CounterCloseRequest(BaseModel):
    """Counter close request"""
    closing_balance: Decimal = Field(..., description="Closing balance")
    physical_count: Optional[Decimal] = None


class CounterResponse(CounterBase):
    """Counter response"""
    id: UUID
    tenant_id: str
    opened_at: Optional[datetime] = None
    opened_by: Optional[UUID] = None
    opening_balance: Decimal
    closed_at: Optional[datetime] = None
    closed_by: Optional[UUID] = None
    closing_balance: Decimal
    current_balance: Decimal
    total_receipts: Decimal
    total_payments: Decimal
    transaction_count: int
    is_active: bool
    is_open: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# CASH TRANSACTION SCHEMAS
# ============================================

class CashTransactionBase(BaseModel):
    """Base cash transaction schema"""
    transaction_date: datetime = Field(..., description="Transaction date")
    transaction_type: str = Field(..., description="Transaction type")
    branch_id: UUID = Field(..., description="Branch ID")
    counter_id: Optional[UUID] = None
    amount: Decimal = Field(..., description="Transaction amount")
    from_party_type: Optional[str] = None
    from_party_id: Optional[str] = None
    from_party_name: Optional[str] = None
    to_party_type: Optional[str] = None
    to_party_id: Optional[str] = None
    to_party_name: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    reference_number: Optional[str] = None
    payment_mode: str = "CASH"
    instrument_number: Optional[str] = None
    instrument_date: Optional[datetime] = None
    narration: Optional[str] = None
    remarks: Optional[str] = None


class CashTransactionCreate(CashTransactionBase):
    """Create cash transaction schema"""
    pass


class CashTransactionResponse(CashTransactionBase):
    """Cash transaction response"""
    id: UUID
    tenant_id: str
    transaction_number: str
    processed_by: UUID
    processed_by_name: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    status: str
    is_cancelled: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CashDenominationDetail(BaseModel):
    """Cash denomination detail"""
    note_2000: int = 0
    note_500: int = 0
    note_200: int = 0
    note_100: int = 0
    note_50: int = 0
    note_20: int = 0
    note_10: int = 0
    coin_10: int = 0
    coin_5: int = 0
    coin_2: int = 0
    coin_1: int = 0


class CashDenominationCreate(CashDenominationDetail):
    """Create cash denomination"""
    reference_type: str
    reference_id: UUID
    branch_id: UUID


class CashDenominationResponse(CashDenominationDetail):
    """Cash denomination response"""
    id: UUID
    tenant_id: str
    reference_type: str
    reference_id: UUID
    branch_id: UUID
    total_amount: Decimal
    recorded_by: Optional[UUID] = None
    recorded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# CASH POSITION SCHEMAS
# ============================================

class CashPositionResponse(BaseModel):
    """Cash position response"""
    id: UUID
    tenant_id: str
    reference_type: str
    reference_id: UUID
    position_date: datetime
    opening_balance: Decimal
    receipts: Decimal
    payments: Decimal
    closing_balance: Decimal
    physical_count: Optional[Decimal] = None
    variance: Decimal
    is_reconciled: bool
    reconciled_at: Optional[datetime] = None
    reconciled_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# PERFORMANCE SCHEMAS
# ============================================

class BranchPerformanceResponse(BaseModel):
    """Branch performance response"""
    id: UUID
    tenant_id: str
    branch_id: UUID
    branch_code: str
    period_type: str
    period_start: datetime
    period_end: datetime
    loans_disbursed: int
    loans_disbursed_amount: Decimal
    loans_collected: Decimal
    loans_overdue: Decimal
    npa_amount: Decimal
    deposits_opened: int
    deposits_amount: Decimal
    deposits_closed: int
    deposits_matured: int
    new_customers: int
    active_customers: int
    total_customers: int
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    total_transactions: int
    cash_transactions: int
    digital_transactions: int
    avg_processing_time: Decimal
    customer_satisfaction: Decimal
    target_disbursement: Decimal
    target_collection: Decimal
    target_achievement: Decimal
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BranchTargetBase(BaseModel):
    """Base branch target schema"""
    branch_id: UUID
    target_period: str
    target_month: Optional[int] = None
    target_quarter: Optional[int] = None
    target_year: int
    loan_disbursement_target: Decimal = Decimal("0")
    loan_collection_target: Decimal = Decimal("0")
    loan_count_target: int = 0
    deposit_mobilization_target: Decimal = Decimal("0")
    deposit_count_target: int = 0
    new_customer_target: int = 0
    revenue_target: Decimal = Decimal("0")


class BranchTargetCreate(BranchTargetBase):
    """Create branch target"""
    pass


class BranchTargetUpdate(BaseModel):
    """Update branch target"""
    loan_disbursement_target: Optional[Decimal] = None
    loan_collection_target: Optional[Decimal] = None
    loan_count_target: Optional[int] = None
    deposit_mobilization_target: Optional[Decimal] = None
    deposit_count_target: Optional[int] = None
    new_customer_target: Optional[int] = None
    revenue_target: Optional[Decimal] = None


class BranchTargetResponse(BranchTargetBase):
    """Branch target response"""
    id: UUID
    tenant_id: str
    branch_code: str
    set_by: Optional[UUID] = None
    set_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# AUDIT LOG SCHEMAS
# ============================================

class BranchAuditLogResponse(BaseModel):
    """Branch audit log response"""
    id: UUID
    tenant_id: str
    branch_id: UUID
    event_type: str
    event_category: str
    event_description: str
    user_id: UUID
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    event_timestamp: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# DASHBOARD SCHEMAS
# ============================================

class BranchDashboard(BaseModel):
    """Branch dashboard summary"""
    branch_id: UUID
    branch_code: str
    branch_name: str
    day_status: str
    business_date: datetime
    cash_balance: Decimal
    total_transactions_today: int
    total_receipts_today: Decimal
    total_payments_today: Decimal
    pending_approvals: int
    active_counters: int
    staff_present: int
    
    model_config = ConfigDict(from_attributes=True)
