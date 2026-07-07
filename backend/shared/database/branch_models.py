"""
Branch & Operations Management Models
Organizational hierarchy, branch operations, day begin/end, cash management
"""

from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Numeric, 
    Text, ForeignKey, Index, Enum as SQLEnum, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from backend.shared.database.connection import Base
from backend.shared.database.models import BaseModel


# ============================================
# ENUMS
# ============================================

class OrganizationLevelEnum(str, enum.Enum):
    """Organization hierarchy levels"""
    HEAD_OFFICE = "HEAD_OFFICE"
    ZONE = "ZONE"
    REGION = "REGION"
    AREA = "AREA"
    BRANCH = "BRANCH"


class BranchTypeEnum(str, enum.Enum):
    """Branch types"""
    FULL_SERVICE = "FULL_SERVICE"
    SATELLITE = "SATELLITE"
    COLLECTION_CENTER = "COLLECTION_CENTER"
    SERVICE_CENTER = "SERVICE_CENTER"


class BranchStatusEnum(str, enum.Enum):
    """Branch operational status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class DayStatusEnum(str, enum.Enum):
    """Day begin/end status"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"


class TransactionTypeEnum(str, enum.Enum):
    """Transaction types"""
    CASH_RECEIPT = "CASH_RECEIPT"
    CASH_PAYMENT = "CASH_PAYMENT"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    BANK_DEPOSIT = "BANK_DEPOSIT"
    BANK_WITHDRAWAL = "BANK_WITHDRAWAL"
    COUNTER_OPENING = "COUNTER_OPENING"
    COUNTER_CLOSING = "COUNTER_CLOSING"


class CashDenominationEnum(str, enum.Enum):
    """Cash denominations"""
    NOTE_2000 = "NOTE_2000"
    NOTE_500 = "NOTE_500"
    NOTE_200 = "NOTE_200"
    NOTE_100 = "NOTE_100"
    NOTE_50 = "NOTE_50"
    NOTE_20 = "NOTE_20"
    NOTE_10 = "NOTE_10"
    COIN_10 = "COIN_10"
    COIN_5 = "COIN_5"
    COIN_2 = "COIN_2"
    COIN_1 = "COIN_1"


# ============================================
# ORGANIZATIONAL HIERARCHY MODELS
# ============================================

class Organization(BaseModel):
    """
    Organization / Organizational Unit
    Represents HO → Zone → Region → Area → Branch hierarchy
    """
    __tablename__ = "organizations"
    
    # Basic Information
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    
    # Hierarchy
    level = Column(SQLEnum(OrganizationLevelEnum), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    hierarchy_path = Column(String(500), nullable=True)  # /HO/Zone/Region/Area/Branch
    
    # Manager
    manager_id = Column(UUID(as_uuid=True), nullable=True)
    manager_name = Column(String(200), nullable=True)
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Status
    status = Column(SQLEnum(BranchStatusEnum), default=BranchStatusEnum.ACTIVE, nullable=False)
    is_operational = Column(Boolean, default=True, nullable=False)
    
    # Operational Details
    opening_date = Column(DateTime(timezone=True), nullable=True)
    closing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Limits & Configuration
    cash_limit = Column(Numeric(15, 2), default=0)
    daily_transaction_limit = Column(Numeric(15, 2), default=0)
    settings = Column(JSONB, nullable=True)
    
    __table_args__ = (
        Index('idx_org_code', 'tenant_id', 'code', unique=True),
        Index('idx_org_level', 'tenant_id', 'level'),
        Index('idx_org_parent', 'tenant_id', 'parent_id'),
    )


class Branch(BaseModel):
    """
    Branch Details
    Extended information for branches (leaf nodes in hierarchy)
    """
    __tablename__ = "branches"
    
    # Link to Organization
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Branch Information
    branch_code = Column(String(50), nullable=False, index=True)
    branch_name = Column(String(200), nullable=False)
    branch_type = Column(SQLEnum(BranchTypeEnum), default=BranchTypeEnum.FULL_SERVICE)
    
    # IFSC and Banking
    ifsc_code = Column(String(11), nullable=True)
    micr_code = Column(String(9), nullable=True)
    swift_code = Column(String(11), nullable=True)
    
    # Operational Information
    working_days = Column(JSONB, nullable=True)  # ["Monday", "Tuesday", ...]
    working_hours_start = Column(String(5), default="09:00")  # HH:MM
    working_hours_end = Column(String(5), default="17:00")  # HH:MM
    
    # Branch Manager
    branch_manager_id = Column(UUID(as_uuid=True), nullable=True)
    branch_manager_name = Column(String(200), nullable=True)
    branch_manager_phone = Column(String(20), nullable=True)
    branch_manager_email = Column(String(100), nullable=True)
    
    # Geographic Information
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    
    # Operational Metrics
    staff_count = Column(Integer, default=0)
    customer_count = Column(Integer, default=0)
    active_loan_count = Column(Integer, default=0)
    
    # Status
    is_head_office = Column(Boolean, default=False)
    is_regional_office = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_branch_code', 'tenant_id', 'branch_code', unique=True),
        Index('idx_branch_org', 'tenant_id', 'organization_id'),
    )


# ============================================
# DAY BEGIN/END OPERATIONS
# ============================================

class BranchDayOperation(BaseModel):
    """
    Branch Day Operations
    Tracks day begin and day end processes
    """
    __tablename__ = "branch_day_operations"
    
    # Branch Reference
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_code = Column(String(50), nullable=False)
    
    # Business Date
    business_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Day Begin
    day_begin_time = Column(DateTime(timezone=True), nullable=True)
    day_begin_by = Column(UUID(as_uuid=True), nullable=True)
    day_begin_remarks = Column(Text, nullable=True)
    
    # Day End
    day_end_time = Column(DateTime(timezone=True), nullable=True)
    day_end_by = Column(UUID(as_uuid=True), nullable=True)
    day_end_remarks = Column(Text, nullable=True)
    
    # Opening Balances
    opening_cash_balance = Column(Numeric(15, 2), default=0)
    opening_bank_balance = Column(Numeric(15, 2), default=0)
    
    # Closing Balances
    closing_cash_balance = Column(Numeric(15, 2), default=0)
    closing_bank_balance = Column(Numeric(15, 2), default=0)
    
    # Transaction Summary
    total_receipts = Column(Numeric(15, 2), default=0)
    total_payments = Column(Numeric(15, 2), default=0)
    total_transfers = Column(Numeric(15, 2), default=0)
    transaction_count = Column(Integer, default=0)
    
    # Status
    status = Column(SQLEnum(DayStatusEnum), default=DayStatusEnum.NOT_STARTED, nullable=False)
    is_holiday = Column(Boolean, default=False)
    
    # Checklist
    pre_day_checklist = Column(JSONB, nullable=True)
    post_day_checklist = Column(JSONB, nullable=True)
    
    __table_args__ = (
        Index('idx_branch_day', 'tenant_id', 'branch_id', 'business_date', unique=True),
        Index('idx_day_status', 'tenant_id', 'business_date', 'status'),
    )


class BranchCounter(BaseModel):
    """
    Branch Counter/Teller
    Individual counter at branch for cash transactions
    """
    __tablename__ = "branch_counters"
    
    # Branch Reference
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Counter Information
    counter_number = Column(String(20), nullable=False)
    counter_name = Column(String(100), nullable=False)
    counter_type = Column(String(50), default="REGULAR")  # REGULAR, CASH, SUPERVISOR
    
    # Assigned User
    assigned_user_id = Column(UUID(as_uuid=True), nullable=True)
    assigned_user_name = Column(String(200), nullable=True)
    
    # Opening Details
    opened_at = Column(DateTime(timezone=True), nullable=True)
    opened_by = Column(UUID(as_uuid=True), nullable=True)
    opening_balance = Column(Numeric(15, 2), default=0)
    
    # Closing Details
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(UUID(as_uuid=True), nullable=True)
    closing_balance = Column(Numeric(15, 2), default=0)
    
    # Current Balance
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Transaction Summary
    total_receipts = Column(Numeric(15, 2), default=0)
    total_payments = Column(Numeric(15, 2), default=0)
    transaction_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_open = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_counter_branch', 'tenant_id', 'branch_id', 'counter_number', unique=True),
        Index('idx_counter_user', 'tenant_id', 'assigned_user_id'),
    )


# ============================================
# CASH MANAGEMENT
# ============================================

class CashTransaction(BaseModel):
    """
    Cash Transactions
    All cash movements at branch level
    """
    __tablename__ = "cash_transactions"
    
    # Transaction Details
    transaction_number = Column(String(50), nullable=False, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionTypeEnum), nullable=False)
    
    # Branch & Counter
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    counter_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Party Details
    from_party_type = Column(String(50), nullable=True)  # CUSTOMER, BRANCH, BANK, VENDOR
    from_party_id = Column(String(50), nullable=True)
    from_party_name = Column(String(200), nullable=True)
    
    to_party_type = Column(String(50), nullable=True)
    to_party_id = Column(String(50), nullable=True)
    to_party_name = Column(String(200), nullable=True)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # LOAN, DEPOSIT, EXPENSE
    reference_id = Column(String(50), nullable=True)
    reference_number = Column(String(50), nullable=True)
    
    # Payment Details
    payment_mode = Column(String(50), default="CASH")
    instrument_number = Column(String(50), nullable=True)
    instrument_date = Column(DateTime(timezone=True), nullable=True)
    
    # Processed By
    processed_by = Column(UUID(as_uuid=True), nullable=False)
    processed_by_name = Column(String(200), nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Narration
    narration = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="COMPLETED")
    is_cancelled = Column(Boolean, default=False)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_cash_txn_number', 'tenant_id', 'transaction_number', unique=True),
        Index('idx_cash_txn_date', 'tenant_id', 'transaction_date'),
        Index('idx_cash_txn_branch', 'tenant_id', 'branch_id', 'transaction_date'),
        Index('idx_cash_txn_reference', 'tenant_id', 'reference_type', 'reference_id'),
    )


class CashDenomination(BaseModel):
    """
    Cash Denomination Details
    Break-up of cash by denominations
    """
    __tablename__ = "cash_denominations"
    
    # Reference (Transaction or Counter)
    reference_type = Column(String(50), nullable=False)  # TRANSACTION, COUNTER, DAY_OPERATION
    reference_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Branch
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Denominations
    note_2000 = Column(Integer, default=0)
    note_500 = Column(Integer, default=0)
    note_200 = Column(Integer, default=0)
    note_100 = Column(Integer, default=0)
    note_50 = Column(Integer, default=0)
    note_20 = Column(Integer, default=0)
    note_10 = Column(Integer, default=0)
    coin_10 = Column(Integer, default=0)
    coin_5 = Column(Integer, default=0)
    coin_2 = Column(Integer, default=0)
    coin_1 = Column(Integer, default=0)
    
    # Total
    total_amount = Column(Numeric(15, 2), default=0)
    
    # Recorded By
    recorded_by = Column(UUID(as_uuid=True), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_denom_reference', 'tenant_id', 'reference_type', 'reference_id'),
        Index('idx_denom_branch', 'tenant_id', 'branch_id'),
    )


class CashPosition(BaseModel):
    """
    Cash Position
    Real-time cash position at branch/counter level
    """
    __tablename__ = "cash_positions"
    
    # Reference
    reference_type = Column(String(50), nullable=False)  # BRANCH, COUNTER
    reference_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Date
    position_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Balances
    opening_balance = Column(Numeric(15, 2), default=0)
    receipts = Column(Numeric(15, 2), default=0)
    payments = Column(Numeric(15, 2), default=0)
    closing_balance = Column(Numeric(15, 2), default=0)
    
    # Physical Count
    physical_count = Column(Numeric(15, 2), nullable=True)
    variance = Column(Numeric(15, 2), default=0)
    
    # Status
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)
    reconciled_by = Column(UUID(as_uuid=True), nullable=True)
    
    __table_args__ = (
        Index('idx_cash_pos_ref', 'tenant_id', 'reference_type', 'reference_id', 'position_date', unique=True),
    )


# ============================================
# BRANCH PERFORMANCE
# ============================================

class BranchPerformance(BaseModel):
    """
    Branch Performance Metrics
    Daily/Monthly/Yearly performance tracking
    """
    __tablename__ = "branch_performance"
    
    # Branch Reference
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_code = Column(String(50), nullable=False)
    
    # Period
    period_type = Column(String(20), nullable=False)  # DAILY, MONTHLY, QUARTERLY, YEARLY
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Loan Metrics
    loans_disbursed = Column(Integer, default=0)
    loans_disbursed_amount = Column(Numeric(15, 2), default=0)
    loans_collected = Column(Numeric(15, 2), default=0)
    loans_overdue = Column(Numeric(15, 2), default=0)
    npa_amount = Column(Numeric(15, 2), default=0)
    
    # Deposit Metrics
    deposits_opened = Column(Integer, default=0)
    deposits_amount = Column(Numeric(15, 2), default=0)
    deposits_closed = Column(Integer, default=0)
    deposits_matured = Column(Integer, default=0)
    
    # Customer Metrics
    new_customers = Column(Integer, default=0)
    active_customers = Column(Integer, default=0)
    total_customers = Column(Integer, default=0)
    
    # Financial Metrics
    total_revenue = Column(Numeric(15, 2), default=0)
    total_expenses = Column(Numeric(15, 2), default=0)
    net_profit = Column(Numeric(15, 2), default=0)
    
    # Transaction Metrics
    total_transactions = Column(Integer, default=0)
    cash_transactions = Column(Integer, default=0)
    digital_transactions = Column(Integer, default=0)
    
    # Productivity Metrics
    avg_processing_time = Column(Numeric(10, 2), default=0)  # minutes
    customer_satisfaction = Column(Numeric(5, 2), default=0)  # out of 5
    
    # Targets
    target_disbursement = Column(Numeric(15, 2), default=0)
    target_collection = Column(Numeric(15, 2), default=0)
    target_achievement = Column(Numeric(5, 2), default=0)  # percentage
    
    # Calculated Fields
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_branch_perf', 'tenant_id', 'branch_id', 'period_type', 'period_start', unique=True),
        Index('idx_branch_perf_period', 'tenant_id', 'period_type', 'period_start'),
    )


class BranchTarget(BaseModel):
    """
    Branch Targets
    Monthly/Quarterly/Yearly targets for branches
    """
    __tablename__ = "branch_targets"
    
    # Branch Reference
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_code = Column(String(50), nullable=False)
    
    # Period
    target_period = Column(String(20), nullable=False)  # MONTHLY, QUARTERLY, YEARLY
    target_month = Column(Integer, nullable=True)
    target_quarter = Column(Integer, nullable=True)
    target_year = Column(Integer, nullable=False)
    
    # Loan Targets
    loan_disbursement_target = Column(Numeric(15, 2), default=0)
    loan_collection_target = Column(Numeric(15, 2), default=0)
    loan_count_target = Column(Integer, default=0)
    
    # Deposit Targets
    deposit_mobilization_target = Column(Numeric(15, 2), default=0)
    deposit_count_target = Column(Integer, default=0)
    
    # Customer Targets
    new_customer_target = Column(Integer, default=0)
    
    # Revenue Targets
    revenue_target = Column(Numeric(15, 2), default=0)
    
    # Set By
    set_by = Column(UUID(as_uuid=True), nullable=True)
    set_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_branch_target', 'tenant_id', 'branch_id', 'target_period', 'target_year', 'target_month', unique=True),
    )


class BranchAuditLog(BaseModel):
    """
    Branch Audit Log
    Tracks all important operations at branch level
    """
    __tablename__ = "branch_audit_logs"
    
    # Branch Reference
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Event Details
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(50), nullable=False)
    event_description = Column(Text, nullable=False)
    
    # User
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_name = Column(String(200), nullable=True)
    user_role = Column(String(100), nullable=True)
    
    # Reference
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(String(50), nullable=True)
    
    # Before/After Data
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    
    # IP & Session
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Timestamp
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_audit_branch', 'tenant_id', 'branch_id', 'event_timestamp'),
        Index('idx_audit_event', 'tenant_id', 'event_type', 'event_timestamp'),
        Index('idx_audit_user', 'tenant_id', 'user_id', 'event_timestamp'),
    )
