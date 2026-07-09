"""
Insurance & Bancassurance Database Models

Includes:
- Insurance Policy Management
- Premium Collection
- Claims Processing
- Commission Tracking
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Integer, ForeignKey, Text, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.shared.database.models import BaseModel


# ==================== ENUMS ====================

class PolicyStatus(str, enum.Enum):
    """Policy status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    LAPSED = "lapsed"
    SURRENDERED = "surrendered"
    MATURED = "matured"
    CANCELLED = "cancelled"


class PolicyType(str, enum.Enum):
    """Insurance policy types"""
    LIFE = "life"
    HEALTH = "health"
    GENERAL = "general"
    MOTOR = "motor"
    ENDOWMENT = "endowment"
    TERM = "term"
    ULIP = "ulip"
    PENSION = "pension"


class PremiumFrequency(str, enum.Enum):
    """Premium payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUALLY = "annually"
    SINGLE = "single"


class PremiumStatus(str, enum.Enum):
    """Premium payment status"""
    DUE = "due"
    PAID = "paid"
    OVERDUE = "overdue"
    WAIVED = "waived"
    CANCELLED = "cancelled"


class ClaimStatus(str, enum.Enum):
    """Claim processing status"""
    REGISTERED = "registered"
    UNDER_REVIEW = "under_review"
    DOCUMENTS_PENDING = "documents_pending"
    ASSESSMENT_COMPLETE = "assessment_complete"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class ClaimType(str, enum.Enum):
    """Types of insurance claims"""
    DEATH = "death"
    MATURITY = "maturity"
    SURRENDER = "surrender"
    HEALTH = "health"
    ACCIDENT = "accident"
    DAMAGE = "damage"
    THEFT = "theft"
    OTHER = "other"


class CommissionStatus(str, enum.Enum):
    """Commission payment status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


# ==================== MODELS ====================

class InsurancePolicy(BaseModel):
    """
    Insurance Policy Model
    Stores policy information and lifecycle
    """
    __tablename__ = "insurance_policies"
    
    # Policy identification
    policy_number = Column(String(50), nullable=False, index=True, unique=True)
    policy_type = Column(SQLEnum(PolicyType), nullable=False, index=True)
    policy_status = Column(SQLEnum(PolicyStatus), nullable=False, default=PolicyStatus.DRAFT, index=True)
    
    # Customer information
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    
    # Insured information
    insured_name = Column(String(200), nullable=False)
    insured_dob = Column(DateTime(timezone=True), nullable=False)
    insured_age = Column(Integer, nullable=False)
    insured_gender = Column(String(20), nullable=True)
    
    # Insurance provider
    insurance_company = Column(String(200), nullable=False)
    insurance_company_code = Column(String(50), nullable=True)
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(50), nullable=True)
    
    # Policy details
    sum_assured = Column(Numeric(15, 2), nullable=False)
    policy_term_years = Column(Integer, nullable=False)  # Policy term in years
    premium_paying_term_years = Column(Integer, nullable=False)  # Premium payment term
    
    # Premium details
    premium_amount = Column(Numeric(12, 2), nullable=False)
    premium_frequency = Column(SQLEnum(PremiumFrequency), nullable=False)
    premium_mode = Column(String(50), nullable=True)  # online, cheque, cash, etc.
    
    # Dates
    policy_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    policy_end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    first_premium_date = Column(DateTime(timezone=True), nullable=False)
    next_premium_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Agent/Bancassurance details
    agent_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    agent_name = Column(String(200), nullable=True)
    agent_code = Column(String(50), nullable=True)
    channel = Column(String(50), nullable=False, default="bancassurance")  # bancassurance, direct, broker
    
    # Branch information
    branch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    branch_name = Column(String(200), nullable=True)
    
    # Nominee information
    nominee_name = Column(String(200), nullable=True)
    nominee_relationship = Column(String(100), nullable=True)
    nominee_dob = Column(DateTime(timezone=True), nullable=True)
    nominee_percentage = Column(Numeric(5, 2), nullable=True, default=100.00)
    
    # Financial tracking
    total_premium_paid = Column(Numeric(15, 2), nullable=False, default=0)
    total_premium_due = Column(Numeric(15, 2), nullable=False, default=0)
    outstanding_premium = Column(Numeric(15, 2), nullable=False, default=0)
    premiums_paid_count = Column(Integer, nullable=False, default=0)
    premiums_due_count = Column(Integer, nullable=False, default=0)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_lapsed = Column(Boolean, default=False, nullable=False)
    lapsed_date = Column(DateTime(timezone=True), nullable=True)
    grace_period_days = Column(Integer, default=30)
    
    # Documents and remarks
    documents = Column(JSONB, nullable=True)  # List of document references
    remarks = Column(Text, nullable=True)
    policy_conditions = Column(Text, nullable=True)
    
    # Surrender and maturity
    surrender_value = Column(Numeric(15, 2), nullable=True)
    maturity_value = Column(Numeric(15, 2), nullable=True)
    maturity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional details
    medical_examination_required = Column(Boolean, default=False)
    medical_examination_status = Column(String(50), nullable=True)
    rider_details = Column(JSONB, nullable=True)  # Additional riders
    additional_data = Column(JSONB, nullable=True)  # Flexible field for extra data
    
    # Indexes
    __table_args__ = (
        Index('idx_insurance_policy_customer', 'tenant_id', 'customer_id'),
        Index('idx_insurance_policy_agent', 'tenant_id', 'agent_id'),
        Index('idx_insurance_policy_status', 'tenant_id', 'policy_status', 'is_active'),
        Index('idx_insurance_policy_dates', 'tenant_id', 'policy_start_date', 'policy_end_date'),
        Index('idx_insurance_policy_company', 'tenant_id', 'insurance_company'),
    )
    
    # Relationships
    premiums = relationship("InsurancePremium", back_populates="policy", cascade="all, delete-orphan")
    claims = relationship("InsuranceClaim", back_populates="policy", cascade="all, delete-orphan")
    commissions = relationship("InsuranceCommission", back_populates="policy", cascade="all, delete-orphan")


class InsurancePremium(BaseModel):
    """
    Insurance Premium Model
    Tracks premium collection and due dates
    """
    __tablename__ = "insurance_premiums"
    
    # Reference to policy
    policy_id = Column(UUID(as_uuid=True), ForeignKey('insurance_policies.id'), nullable=False, index=True)
    policy_number = Column(String(50), nullable=False, index=True)
    
    # Premium details
    premium_number = Column(String(50), nullable=False, index=True, unique=True)
    premium_amount = Column(Numeric(12, 2), nullable=False)
    premium_due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    premium_frequency = Column(SQLEnum(PremiumFrequency), nullable=False)
    installment_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    
    # Payment details
    premium_status = Column(SQLEnum(PremiumStatus), nullable=False, default=PremiumStatus.DUE, index=True)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    payment_amount = Column(Numeric(12, 2), nullable=True)
    payment_method = Column(String(50), nullable=True)  # cash, cheque, online, etc.
    payment_reference = Column(String(100), nullable=True)
    
    # Transaction tracking
    transaction_id = Column(String(100), nullable=True, index=True)
    receipt_number = Column(String(50), nullable=True)
    
    # Late payment tracking
    grace_period_end_date = Column(DateTime(timezone=True), nullable=True)
    late_fee = Column(Numeric(10, 2), nullable=True, default=0)
    late_days = Column(Integer, nullable=True, default=0)
    
    # Waiver/discount
    discount_amount = Column(Numeric(10, 2), nullable=True, default=0)
    discount_reason = Column(String(200), nullable=True)
    waived_amount = Column(Numeric(10, 2), nullable=True, default=0)
    waived_reason = Column(String(200), nullable=True)
    
    # Collection details
    collected_by = Column(UUID(as_uuid=True), nullable=True)
    collected_by_name = Column(String(200), nullable=True)
    collection_branch = Column(String(200), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    additional_data = Column(JSONB, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_insurance_premium_policy', 'tenant_id', 'policy_id'),
        Index('idx_insurance_premium_status', 'tenant_id', 'premium_status'),
        Index('idx_insurance_premium_due_date', 'tenant_id', 'premium_due_date'),
        Index('idx_premium_payment_date', 'tenant_id', 'payment_date'),
    )
    
    # Relationship
    policy = relationship("InsurancePolicy", back_populates="premiums")


class InsuranceClaim(BaseModel):
    """
    Insurance Claim Model
    Handles claim processing and settlement
    """
    __tablename__ = "insurance_claims"
    
    # Reference to policy
    policy_id = Column(UUID(as_uuid=True), ForeignKey('insurance_policies.id'), nullable=False, index=True)
    policy_number = Column(String(50), nullable=False, index=True)
    
    # Claim identification
    claim_number = Column(String(50), nullable=False, index=True, unique=True)
    claim_type = Column(SQLEnum(ClaimType), nullable=False, index=True)
    claim_status = Column(SQLEnum(ClaimStatus), nullable=False, default=ClaimStatus.REGISTERED, index=True)
    
    # Claim details
    claim_amount = Column(Numeric(15, 2), nullable=False)
    claimed_date = Column(DateTime(timezone=True), nullable=False, index=True)
    incident_date = Column(DateTime(timezone=True), nullable=False)
    incident_description = Column(Text, nullable=False)
    incident_location = Column(String(500), nullable=True)
    
    # Claimant details
    claimant_name = Column(String(200), nullable=False)
    claimant_relationship = Column(String(100), nullable=False)
    claimant_contact = Column(String(20), nullable=True)
    claimant_address = Column(Text, nullable=True)
    
    # Assessment
    assessed_by = Column(UUID(as_uuid=True), nullable=True)
    assessed_by_name = Column(String(200), nullable=True)
    assessment_date = Column(DateTime(timezone=True), nullable=True)
    assessed_amount = Column(Numeric(15, 2), nullable=True)
    assessment_remarks = Column(Text, nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_by_name = Column(String(200), nullable=True)
    approval_date = Column(DateTime(timezone=True), nullable=True)
    approved_amount = Column(Numeric(15, 2), nullable=True)
    approval_remarks = Column(Text, nullable=True)
    
    # Rejection (if applicable)
    rejection_reason = Column(Text, nullable=True)
    rejection_date = Column(DateTime(timezone=True), nullable=True)
    
    # Settlement
    settlement_date = Column(DateTime(timezone=True), nullable=True, index=True)
    settlement_amount = Column(Numeric(15, 2), nullable=True)
    settlement_method = Column(String(50), nullable=True)
    settlement_reference = Column(String(100), nullable=True)
    settlement_remarks = Column(Text, nullable=True)
    
    # Documents
    documents_submitted = Column(JSONB, nullable=True)  # List of document references
    documents_verified = Column(Boolean, default=False)
    documents_verification_date = Column(DateTime(timezone=True), nullable=True)
    
    # Investigation
    investigation_required = Column(Boolean, default=False)
    investigation_status = Column(String(50), nullable=True)
    investigation_remarks = Column(Text, nullable=True)
    
    # Financial tracking
    deductions = Column(Numeric(15, 2), nullable=True, default=0)
    deduction_details = Column(JSONB, nullable=True)
    net_payable = Column(Numeric(15, 2), nullable=True)
    
    # Processing timeline
    target_settlement_date = Column(DateTime(timezone=True), nullable=True)
    processing_days = Column(Integer, nullable=True)
    
    # Additional information
    remarks = Column(Text, nullable=True)
    additional_data = Column(JSONB, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_insurance_claim_policy', 'tenant_id', 'policy_id'),
        Index('idx_insurance_claim_status', 'tenant_id', 'claim_status'),
        Index('idx_insurance_claim_type', 'tenant_id', 'claim_type'),
        Index('idx_insurance_claim_dates', 'tenant_id', 'claimed_date'),
    )
    
    # Relationship
    policy = relationship("InsurancePolicy", back_populates="claims")


class InsuranceCommission(BaseModel):
    """
    Insurance Commission Model
    Tracks commission for agents and bancassurance partners
    """
    __tablename__ = "insurance_commissions"
    
    # Reference to policy
    policy_id = Column(UUID(as_uuid=True), ForeignKey('insurance_policies.id'), nullable=False, index=True)
    policy_number = Column(String(50), nullable=False, index=True)
    
    # Commission identification
    commission_number = Column(String(50), nullable=False, index=True, unique=True)
    commission_status = Column(SQLEnum(CommissionStatus), nullable=False, default=CommissionStatus.PENDING, index=True)
    
    # Agent/Partner details
    agent_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_name = Column(String(200), nullable=False)
    agent_code = Column(String(50), nullable=True)
    agent_type = Column(String(50), nullable=True)  # employee, external, partner
    
    # Commission calculation
    commission_type = Column(String(50), nullable=False)  # first_year, renewal, performance
    base_amount = Column(Numeric(15, 2), nullable=False)  # Amount on which commission is calculated
    commission_rate = Column(Numeric(5, 2), nullable=False)  # Commission percentage
    commission_amount = Column(Numeric(12, 2), nullable=False)
    
    # Period
    commission_period = Column(String(50), nullable=True)  # Q1-2024, Jan-2024, etc.
    calculation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Premium reference (if renewal commission)
    premium_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    premium_number = Column(String(50), nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_by_name = Column(String(200), nullable=True)
    approval_date = Column(DateTime(timezone=True), nullable=True)
    
    # Payment
    payment_date = Column(DateTime(timezone=True), nullable=True, index=True)
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    paid_amount = Column(Numeric(12, 2), nullable=True)
    
    # Deductions
    tds_amount = Column(Numeric(12, 2), nullable=True, default=0)
    tds_percentage = Column(Numeric(5, 2), nullable=True, default=0)
    other_deductions = Column(Numeric(12, 2), nullable=True, default=0)
    deduction_details = Column(JSONB, nullable=True)
    net_payable = Column(Numeric(12, 2), nullable=True)
    
    # Branch and hierarchy
    branch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    branch_name = Column(String(200), nullable=True)
    team_id = Column(UUID(as_uuid=True), nullable=True)
    team_name = Column(String(200), nullable=True)
    
    # Performance metrics
    target_achievement_percentage = Column(Numeric(5, 2), nullable=True)
    bonus_amount = Column(Numeric(12, 2), nullable=True, default=0)
    penalty_amount = Column(Numeric(12, 2), nullable=True, default=0)
    
    # Clawback (if policy is cancelled)
    is_clawback = Column(Boolean, default=False)
    clawback_reason = Column(String(200), nullable=True)
    clawback_amount = Column(Numeric(12, 2), nullable=True)
    
    # Additional information
    remarks = Column(Text, nullable=True)
    additional_data = Column(JSONB, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_commission_policy', 'tenant_id', 'policy_id'),
        Index('idx_commission_agent', 'tenant_id', 'agent_id'),
        Index('idx_commission_status', 'tenant_id', 'commission_status'),
        Index('idx_commission_dates', 'tenant_id', 'calculation_date'),
        Index('idx_commission_payment', 'tenant_id', 'payment_date'),
    )
    
    # Relationship
    policy = relationship("InsurancePolicy", back_populates="commissions")


class InsuranceAgent(BaseModel):
    """
    Insurance Agent Model
    Manages agent/partner information
    """
    __tablename__ = "insurance_agents"
    
    # Agent identification
    agent_code = Column(String(50), nullable=False, index=True, unique=True)
    agent_name = Column(String(200), nullable=False)
    agent_type = Column(String(50), nullable=False)  # employee, external, partner, bancassurance
    
    # Contact information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    
    # License and certification
    license_number = Column(String(100), nullable=True)
    license_valid_from = Column(DateTime(timezone=True), nullable=True)
    license_valid_till = Column(DateTime(timezone=True), nullable=True)
    certifications = Column(JSONB, nullable=True)
    
    # Organization details
    branch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    branch_name = Column(String(200), nullable=True)
    team_id = Column(UUID(as_uuid=True), nullable=True)
    team_name = Column(String(200), nullable=True)
    reporting_manager_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Commission structure
    commission_structure = Column(JSONB, nullable=True)  # Commission rates by product
    default_commission_rate = Column(Numeric(5, 2), nullable=True)
    
    # Bank details for payout
    bank_name = Column(String(200), nullable=True)
    account_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(20), nullable=True)
    account_holder_name = Column(String(200), nullable=True)
    
    # Tax details
    pan_number = Column(String(20), nullable=True)
    gst_number = Column(String(20), nullable=True)
    tds_applicable = Column(Boolean, default=True)
    
    # Performance tracking
    total_policies_sold = Column(Integer, default=0)
    total_premium_collected = Column(Numeric(15, 2), default=0)
    total_commission_earned = Column(Numeric(15, 2), default=0)
    active_policies_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    joining_date = Column(DateTime(timezone=True), nullable=True)
    exit_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    remarks = Column(Text, nullable=True)
    additional_data = Column(JSONB, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_type', 'tenant_id', 'agent_type'),
        Index('idx_agent_branch', 'tenant_id', 'branch_id'),
        Index('idx_agent_status', 'tenant_id', 'is_active'),
    )
