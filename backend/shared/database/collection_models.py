"""
Collection Management Models
Complete collection workflow from strategies to settlement
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, 
    DateTime, ForeignKey, Enum as SQLEnum, Index, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from .connection import Base


# ============================================================================
# ENUMS
# ============================================================================

class ActionType(str, Enum):
    """Collection action types"""
    CALL = "call"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    FIELD_VISIT = "field_visit"
    LEGAL_NOTICE = "legal_notice"
    LEGAL_ACTION = "legal_action"


class ActionStatus(str, Enum):
    """Action execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TemplateType(str, Enum):
    """Communication template types"""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    LETTER = "letter"
    NOTICE = "notice"


class VisitStatus(str, Enum):
    """Field visit status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CUSTOMER_NOT_FOUND = "customer_not_found"
    REFUSED_TO_MEET = "refused_to_meet"


class VisitDisposition(str, Enum):
    """Visit outcome disposition"""
    MET_CUSTOMER = "met_customer"
    NOT_HOME = "not_home"
    REFUSED_TO_MEET = "refused_to_meet"
    PAID = "paid"
    PROMISED_TO_PAY = "promised_to_pay"
    REQUESTED_SETTLEMENT = "requested_settlement"
    CUSTOMER_RELOCATED = "customer_relocated"
    HOSTILE = "hostile"


class PromiseStatus(str, Enum):
    """Payment promise status"""
    PENDING = "pending"
    KEPT = "kept"
    PARTIALLY_KEPT = "partially_kept"
    BROKEN = "broken"
    RESCHEDULED = "rescheduled"


class PromiseSource(str, Enum):
    """Where promise was made"""
    CALL = "call"
    FIELD_VISIT = "field_visit"
    EMAIL = "email"
    CUSTOMER_PORTAL = "customer_portal"
    BRANCH_VISIT = "branch_visit"


class LegalNoticeType(str, Enum):
    """Legal notice types"""
    DEMAND_NOTICE = "demand_notice"
    SECTION_13 = "section_13"
    SARFAESI_NOTICE = "sarfaesi_notice"
    FINAL_NOTICE = "final_notice"
    LEGAL_NOTICE = "legal_notice"


class NoticeStage(str, Enum):
    """Notice stage"""
    FIRST = "first"
    SECOND = "second"
    FINAL = "final"


class DeliveryStatus(str, Enum):
    """Notice delivery status"""
    PENDING = "pending"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    RETURNED = "returned"
    UNCLAIMED = "unclaimed"


class CaseType(str, Enum):
    """Legal case types"""
    CIVIL_SUIT = "civil_suit"
    ARBITRATION = "arbitration"
    DRT = "drt"
    SARFAESI = "sarfaesi"
    CRIMINAL = "criminal"


class CaseStatus(str, Enum):
    """Legal case status"""
    FILED = "filed"
    PENDING = "pending"
    HEARING = "hearing"
    JUDGEMENT = "judgement"
    CLOSED = "closed"
    WITHDRAWN = "withdrawn"


class CaseOutcome(str, Enum):
    """Legal case outcome"""
    WON = "won"
    LOST = "lost"
    SETTLED = "settled"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"


class RecoveryActionType(str, Enum):
    """Recovery action types"""
    REPOSSESSION = "repossession"
    AUCTION = "auction"
    SETTLEMENT = "settlement"
    WRITE_OFF = "write_off"
    LOAN_SALE = "loan_sale"


class SettlementType(str, Enum):
    """Settlement types"""
    ONE_TIME_SETTLEMENT = "one_time_settlement"
    COMPROMISE_SETTLEMENT = "compromise_settlement"
    COURT_SETTLEMENT = "court_settlement"
    PRE_CLOSURE = "pre_closure"
    NEGOTIATED = "negotiated"


class SettlementStatus(str, Enum):
    """Settlement proposal status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CUSTOMER_ACCEPTED = "customer_accepted"
    CUSTOMER_REJECTED = "customer_rejected"
    COMPLETED = "completed"
    BREACHED = "breached"


class PaymentTerms(str, Enum):
    """Settlement payment terms"""
    LUMP_SUM = "lump_sum"
    INSTALLMENTS = "installments"


# ============================================================================
# COLLECTION STRATEGY MODELS
# ============================================================================

class CollectionStrategy(Base):
    """
    Collection Strategy Configuration
    Defines actions to take based on DPD buckets
    """
    __tablename__ = "collection_strategies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Strategy Details
    strategy_name = Column(String(200), nullable=False)
    strategy_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # DPD Range
    dpd_min = Column(Integer, nullable=False)
    dpd_max = Column(Integer, nullable=False)
    
    # Action Configuration
    action_type = Column(SQLEnum(ActionType), nullable=False)
    frequency_days = Column(Integer, default=1)  # How often to repeat action
    max_attempts = Column(Integer, default=3)  # Maximum attempts
    
    # Template
    template_id = Column(Integer, ForeignKey("communication_templates.id"), nullable=True)
    
    # Escalation
    escalation_rules = Column(JSON)  # Rules for escalation
    escalate_after_days = Column(Integer)
    escalate_to_strategy_id = Column(Integer, ForeignKey("collection_strategies.id"))
    
    # Settings
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # Lower number = higher priority
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    template = relationship("CommunicationTemplate", foreign_keys=[template_id])


class CommunicationTemplate(Base):
    """
    Communication Templates for SMS, Email, WhatsApp, Letters
    """
    __tablename__ = "communication_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Template Details
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    template_type = Column(SQLEnum(TemplateType), nullable=False)
    
    # Content
    language = Column(String(10), default="en")  # en, hi, ta, ml, etc.
    subject = Column(String(500))  # For email
    content = Column(Text, nullable=False)  # Template body with variables
    
    # Variables
    variables = Column(JSON)  # List of available variables
    # Example: ["customer_name", "loan_account_number", "overdue_amount", "dpd"]
    
    # Categorization
    dpd_bucket = Column(String(50))  # Which DPD bucket this is for
    category = Column(String(50))  # reminder, warning, final_notice, legal
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


class CollectionAction(Base):
    """
    Collection Actions Log
    Records all collection activities
    """
    __tablename__ = "collection_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey("collection_strategies.id"))
    template_id = Column(Integer, ForeignKey("communication_templates.id"))
    
    # Action Details
    action_type = Column(SQLEnum(ActionType), nullable=False)
    action_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_date = Column(DateTime(timezone=True))
    
    # Status
    status = Column(SQLEnum(ActionStatus), nullable=False, default=ActionStatus.PENDING)
    
    # Execution Details
    contact_number = Column(String(20))  # Phone/mobile used
    email_address = Column(String(200))  # Email used
    
    # Response
    response_received = Column(Boolean, default=False)
    response_details = Column(Text)
    response_time = Column(DateTime(timezone=True))
    
    # Follow-up
    next_action_date = Column(DateTime(timezone=True))
    next_action_type = Column(SQLEnum(ActionType))
    
    # Assignment
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_agent_id = Column(Integer, ForeignKey("field_agents.id"))
    
    # Notes
    notes = Column(Text)
    internal_remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    strategy = relationship("CollectionStrategy", foreign_keys=[strategy_id])
    template = relationship("CommunicationTemplate", foreign_keys=[template_id])


# ============================================================================
# FIELD AGENT MODELS
# ============================================================================

class Territory(Base):
    """
    Geographical Territory for field operations
    """
    __tablename__ = "territories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Territory Details
    territory_code = Column(String(50), unique=True, nullable=False, index=True)
    territory_name = Column(String(200), nullable=False)
    parent_territory_id = Column(Integer, ForeignKey("territories.id"))
    
    # Geography
    state = Column(String(100))
    district = Column(String(100))
    city = Column(String(100))
    pincode_list = Column(JSON)  # List of pincodes
    
    # Assignment
    branch_id = Column(Integer, ForeignKey("branches.id"))
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


class FieldAgent(Base):
    """
    Field Collection Agents
    """
    __tablename__ = "field_agents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Agent Details
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    agent_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    mobile = Column(String(20), nullable=False)
    email = Column(String(200))
    
    # Assignment
    territory_id = Column(Integer, ForeignKey("territories.id"), index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    reporting_manager_id = Column(Integer, ForeignKey("users.id"))
    
    # Employment
    employment_type = Column(String(50))  # permanent, contract, outsourced
    joining_date = Column(Date)
    
    # Targets
    monthly_collection_target = Column(Numeric(15, 2))
    monthly_visit_target = Column(Integer)
    
    # Performance
    total_collection_amount = Column(Numeric(15, 2), default=0)
    total_visits_completed = Column(Integer, default=0)
    success_rate = Column(Numeric(5, 2), default=0)  # Percentage
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    territory = relationship("Territory", foreign_keys=[territory_id])


class FieldVisit(Base):
    """
    Field Visit Records
    """
    __tablename__ = "field_visits"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("field_agents.id"), nullable=False, index=True)
    
    # Visit Details
    visit_date = Column(Date, nullable=False, index=True)
    scheduled_time = Column(DateTime(timezone=True))
    actual_visit_time = Column(DateTime(timezone=True))
    
    # Status
    visit_status = Column(SQLEnum(VisitStatus), nullable=False, default=VisitStatus.SCHEDULED)
    visit_type = Column(String(50))  # routine, urgent, legal_notice_delivery
    
    # Outcome
    disposition = Column(SQLEnum(VisitDisposition))
    amount_collected = Column(Numeric(15, 2), default=0)
    payment_mode = Column(String(50))  # cash, cheque, upi
    receipt_number = Column(String(100))
    
    # Location
    location_lat = Column(Numeric(10, 8))
    location_lng = Column(Numeric(11, 8))
    address_visited = Column(Text)
    
    # Documentation
    visit_notes = Column(Text)
    customer_remarks = Column(Text)
    photo_urls = Column(JSON)  # List of photo URLs
    
    # Follow-up
    next_visit_date = Column(Date)
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    agent = relationship("FieldAgent", foreign_keys=[agent_id])


class VisitTarget(Base):
    """
    Monthly Visit Targets for Field Agents
    """
    __tablename__ = "visit_targets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Assignment
    agent_id = Column(Integer, ForeignKey("field_agents.id"), nullable=False, index=True)
    
    # Period
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    
    # Targets
    target_collection_amount = Column(Numeric(15, 2), nullable=False)
    target_visit_count = Column(Integer, nullable=False)
    
    # Achievement
    achieved_collection_amount = Column(Numeric(15, 2), default=0)
    achieved_visit_count = Column(Integer, default=0)
    
    # Performance
    achievement_percentage = Column(Numeric(5, 2), default=0)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    agent = relationship("FieldAgent", foreign_keys=[agent_id])
    
    # Unique constraint
    __table_args__ = (
        Index('idx_agent_month_year', 'agent_id', 'month', 'year', unique=True),
    )


# ============================================================================
# PAYMENT PROMISE MODELS
# ============================================================================

class PaymentPromise(Base):
    """
    Payment Promises (PTP) from customers
    """
    __tablename__ = "payment_promises"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Promise Details
    promise_amount = Column(Numeric(15, 2), nullable=False)
    promise_date = Column(Date, nullable=False, index=True)
    promised_on_date = Column(Date, nullable=False)
    
    # Source
    promised_by = Column(SQLEnum(PromiseSource), nullable=False)
    recorded_by_user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("field_agents.id"))
    field_visit_id = Column(Integer, ForeignKey("field_visits.id"))
    collection_action_id = Column(Integer, ForeignKey("collection_actions.id"))
    
    # Status
    promise_status = Column(SQLEnum(PromiseStatus), nullable=False, default=PromiseStatus.PENDING)
    
    # Fulfillment
    actual_payment_amount = Column(Numeric(15, 2))
    actual_payment_date = Column(Date)
    payment_transaction_id = Column(Integer, ForeignKey("loan_transactions.id"))
    
    # Rescheduling
    rescheduled_promise_id = Column(Integer, ForeignKey("payment_promises.id"))
    broken_reason = Column(Text)
    
    # Notes
    notes = Column(Text)
    customer_remarks = Column(Text)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_date = Column(DateTime(timezone=True))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    agent = relationship("FieldAgent", foreign_keys=[agent_id])
    field_visit = relationship("FieldVisit", foreign_keys=[field_visit_id])


class PromiseHistory(Base):
    """
    Payment Promise Status Change History
    """
    __tablename__ = "promise_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Reference
    promise_id = Column(Integer, ForeignKey("payment_promises.id"), nullable=False, index=True)
    
    # Status Change
    status_changed_from = Column(SQLEnum(PromiseStatus))
    status_changed_to = Column(SQLEnum(PromiseStatus), nullable=False)
    changed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    changed_by = Column(Integer, ForeignKey("users.id"))
    
    # Details
    remarks = Column(Text)
    
    # Relationships
    promise = relationship("PaymentPromise", foreign_keys=[promise_id])


# ============================================================================
# LEGAL & RECOVERY MODELS
# ============================================================================

class LegalNotice(Base):
    """
    Legal Notices sent to customers
    """
    __tablename__ = "legal_notices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Notice Details
    notice_type = Column(SQLEnum(LegalNoticeType), nullable=False)
    notice_stage = Column(SQLEnum(NoticeStage), nullable=False)
    notice_number = Column(String(100), unique=True, nullable=False, index=True)
    notice_date = Column(Date, nullable=False)
    notice_amount_demanded = Column(Numeric(15, 2), nullable=False)
    
    # Template & Generation
    template_id = Column(Integer, ForeignKey("communication_templates.id"))
    generated_pdf_url = Column(String(500))
    
    # Dispatch
    dispatch_mode = Column(String(50))  # courier, email, registered_post, hand_delivery
    dispatch_date = Column(Date)
    tracking_number = Column(String(100))
    courier_name = Column(String(200))
    
    # Delivery
    delivery_status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING)
    delivery_date = Column(Date)
    delivered_to = Column(String(200))
    
    # Response
    response_received = Column(Boolean, default=False)
    response_date = Column(Date)
    response_details = Column(Text)
    
    # Next Action
    next_action = Column(String(200))
    next_action_date = Column(Date)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    template = relationship("CommunicationTemplate", foreign_keys=[template_id])


class LegalCase(Base):
    """
    Legal Cases filed for recovery
    """
    __tablename__ = "legal_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Case Details
    case_number = Column(String(100), unique=True, nullable=False, index=True)
    case_type = Column(SQLEnum(CaseType), nullable=False)
    court_name = Column(String(300))
    filing_date = Column(Date, nullable=False)
    claim_amount = Column(Numeric(15, 2), nullable=False)
    
    # Legal Team
    lawyer_id = Column(Integer, ForeignKey("users.id"))
    lawyer_name = Column(String(200))
    lawyer_contact = Column(String(20))
    
    # Status
    case_status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.FILED)
    
    # Hearings
    next_hearing_date = Column(Date)
    total_hearings = Column(Integer, default=0)
    
    # Judgement
    judgement_details = Column(Text)
    judgement_date = Column(Date)
    judgement_amount = Column(Numeric(15, 2))
    case_outcome = Column(SQLEnum(CaseOutcome))
    
    # Costs
    total_legal_cost = Column(Numeric(15, 2), default=0)
    
    # Notes
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])


class CaseHearing(Base):
    """
    Court Hearing Records
    """
    __tablename__ = "case_hearings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Reference
    case_id = Column(Integer, ForeignKey("legal_cases.id"), nullable=False, index=True)
    
    # Hearing Details
    hearing_date = Column(Date, nullable=False)
    hearing_time = Column(String(20))
    judge_name = Column(String(200))
    
    # Attendance
    lawyer_present = Column(Boolean, default=True)
    defendant_present = Column(Boolean, default=False)
    
    # Outcome
    hearing_notes = Column(Text)
    next_hearing_date = Column(Date)
    order_passed = Column(Boolean, default=False)
    order_details = Column(Text)
    
    # Documents
    documents_submitted = Column(JSON)  # List of document names/URLs
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    case = relationship("LegalCase", foreign_keys=[case_id])


class RecoveryAgency(Base):
    """
    External Recovery Agencies
    """
    __tablename__ = "recovery_agencies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Agency Details
    agency_code = Column(String(50), unique=True, nullable=False, index=True)
    agency_name = Column(String(200), nullable=False)
    contact_person = Column(String(200))
    mobile = Column(String(20), nullable=False)
    email = Column(String(200))
    address = Column(Text)
    
    # Terms
    commission_percentage = Column(Numeric(5, 2), nullable=False)
    contract_start_date = Column(Date)
    contract_end_date = Column(Date)
    
    # Performance
    total_cases_assigned = Column(Integer, default=0)
    total_amount_recovered = Column(Numeric(15, 2), default=0)
    performance_rating = Column(Numeric(3, 2))  # Out of 5.00
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


class AgencyAssignment(Base):
    """
    Recovery Agency Assignments
    """
    __tablename__ = "agency_assignments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    agency_id = Column(Integer, ForeignKey("recovery_agencies.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Assignment Details
    assigned_date = Column(Date, nullable=False)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    commission_agreed = Column(Numeric(5, 2), nullable=False)
    
    # Status
    status = Column(String(50), nullable=False, default="assigned")
    # assigned, in_progress, recovered, closed
    
    # Recovery
    recovery_amount = Column(Numeric(15, 2), default=0)
    recovery_date = Column(Date)
    commission_amount = Column(Numeric(15, 2))
    commission_paid = Column(Boolean, default=False)
    commission_paid_date = Column(Date)
    
    # Closure
    closure_date = Column(Date)
    closure_reason = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    agency = relationship("RecoveryAgency", foreign_keys=[agency_id])
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])


class RecoveryAction(Base):
    """
    Recovery Actions (Repo, Auction, Write-off)
    """
    __tablename__ = "recovery_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Action Details
    action_type = Column(SQLEnum(RecoveryActionType), nullable=False)
    action_date = Column(Date, nullable=False)
    
    # Assignment
    assigned_to_internal = Column(Boolean, default=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    assigned_agency_id = Column(Integer, ForeignKey("recovery_agencies.id"))
    
    # Status
    action_status = Column(String(50), nullable=False, default="initiated")
    # initiated, in_progress, completed, failed
    
    # Financial
    recovery_amount = Column(Numeric(15, 2), default=0)
    recovery_cost = Column(Numeric(15, 2), default=0)
    net_recovery = Column(Numeric(15, 2), default=0)
    
    # Details
    remarks = Column(Text)
    documents = Column(JSON)  # Document URLs
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])


# ============================================================================
# SETTLEMENT/OTS MODELS
# ============================================================================

class WaiverPolicy(Base):
    """
    Waiver Policies for Settlements
    """
    __tablename__ = "waiver_policies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Policy Details
    policy_code = Column(String(50), unique=True, nullable=False, index=True)
    policy_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Applicability
    min_dpd = Column(Integer, nullable=False)
    max_dpd = Column(Integer, nullable=False)
    loan_product_ids = Column(JSON)  # Applicable loan products
    
    # Waiver Limits
    max_waiver_percentage_interest = Column(Numeric(5, 2), nullable=False)
    max_waiver_percentage_penal = Column(Numeric(5, 2), nullable=False)
    min_recovery_percentage = Column(Numeric(5, 2), nullable=False)  # Minimum % of principal
    
    # Approval
    approval_required = Column(Boolean, default=True)
    approval_authority = Column(String(100))  # role or user level
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


class SettlementProposal(Base):
    """
    Settlement/OTS Proposals
    """
    __tablename__ = "settlement_proposals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # References
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    waiver_policy_id = Column(Integer, ForeignKey("waiver_policies.id"))
    
    # Proposal Details
    proposal_number = Column(String(100), unique=True, nullable=False, index=True)
    proposal_type = Column(SQLEnum(SettlementType), nullable=False)
    requested_by = Column(String(50), nullable=False)  # customer, bank, agency
    request_date = Column(Date, nullable=False)
    
    # Outstanding Amounts
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    outstanding_principal = Column(Numeric(15, 2), nullable=False)
    outstanding_interest = Column(Numeric(15, 2), nullable=False)
    penal_charges = Column(Numeric(15, 2), default=0)
    other_charges = Column(Numeric(15, 2), default=0)
    
    # Proposed Settlement
    proposed_settlement_amount = Column(Numeric(15, 2), nullable=False)
    waiver_on_interest = Column(Numeric(15, 2), default=0)
    waiver_on_penal = Column(Numeric(15, 2), default=0)
    waiver_percentage = Column(Numeric(5, 2))
    
    # Payment Terms
    payment_terms = Column(SQLEnum(PaymentTerms), nullable=False, default=PaymentTerms.LUMP_SUM)
    installment_count = Column(Integer)
    installment_amount = Column(Numeric(15, 2))
    
    # Justification
    justification = Column(Text)
    financial_hardship_details = Column(Text)
    
    # Status
    proposal_status = Column(SQLEnum(SettlementStatus), nullable=False, default=SettlementStatus.SUBMITTED)
    
    # Approval Workflow
    current_approval_level = Column(Integer, default=1)
    total_approval_levels = Column(Integer, default=1)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    waiver_policy = relationship("WaiverPolicy", foreign_keys=[waiver_policy_id])


class SettlementApproval(Base):
    """
    Settlement Approval Workflow
    """
    __tablename__ = "settlement_approvals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Reference
    proposal_id = Column(Integer, ForeignKey("settlement_proposals.id"), nullable=False, index=True)
    
    # Approval Level
    approval_level = Column(Integer, nullable=False)
    approver_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    approval_status = Column(String(50), nullable=False, default="pending")
    # pending, approved, rejected
    approval_date = Column(DateTime(timezone=True))
    approval_remarks = Column(Text)
    
    # Forwarding
    forwarded_to_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    proposal = relationship("SettlementProposal", foreign_keys=[proposal_id])


class SettlementAgreement(Base):
    """
    Approved Settlement Agreements
    """
    __tablename__ = "settlement_agreements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Reference
    proposal_id = Column(Integer, ForeignKey("settlement_proposals.id"), nullable=False, unique=True)
    
    # Agreement Details
    agreement_number = Column(String(100), unique=True, nullable=False, index=True)
    agreement_date = Column(Date, nullable=False)
    settlement_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment
    payment_deadline = Column(Date, nullable=False)
    payment_schedule = Column(JSON)  # For installments
    
    # Terms
    terms_and_conditions = Column(Text)
    breach_clause = Column(Text)
    breach_penalty = Column(Numeric(15, 2))
    
    # Signing
    customer_signed_date = Column(Date)
    bank_signed_date = Column(Date)
    agreement_pdf_url = Column(String(500))
    
    # Status
    agreement_status = Column(String(50), nullable=False, default="active")
    # active, completed, breached, cancelled
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    proposal = relationship("SettlementProposal", foreign_keys=[proposal_id])


class SettlementPayment(Base):
    """
    Settlement Payment Tracking
    """
    __tablename__ = "settlement_payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Reference
    agreement_id = Column(Integer, ForeignKey("settlement_agreements.id"), nullable=False, index=True)
    
    # Installment Details
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    due_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment
    paid_amount = Column(Numeric(15, 2), default=0)
    payment_date = Column(Date)
    payment_status = Column(String(50), nullable=False, default="pending")
    # pending, paid, partially_paid, overdue, breached
    
    # Transaction
    transaction_id = Column(Integer, ForeignKey("loan_transactions.id"))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    agreement = relationship("SettlementAgreement", foreign_keys=[agreement_id])


# ============================================================================
# INDEXES FOR PERFORMANCE
# ============================================================================

# Collection Actions - Composite indexes
Index('idx_collection_actions_loan_date', 
      CollectionAction.loan_account_id, 
      CollectionAction.action_date)

Index('idx_collection_actions_status_date', 
      CollectionAction.status, 
      CollectionAction.scheduled_date)

# Field Visits - Composite indexes
Index('idx_field_visits_agent_date', 
      FieldVisit.agent_id, 
      FieldVisit.visit_date)

Index('idx_field_visits_loan_status', 
      FieldVisit.loan_account_id, 
      FieldVisit.visit_status)

# Payment Promises - Composite indexes
Index('idx_payment_promises_loan_status', 
      PaymentPromise.loan_account_id, 
      PaymentPromise.promise_status)

Index('idx_payment_promises_date_status', 
      PaymentPromise.promise_date, 
      PaymentPromise.promise_status)

# Legal Cases - Composite indexes
Index('idx_legal_cases_loan_status', 
      LegalCase.loan_account_id, 
      LegalCase.case_status)

# Settlement Proposals - Composite indexes
Index('idx_settlement_proposals_loan_status', 
      SettlementProposal.loan_account_id, 
      SettlementProposal.proposal_status)
