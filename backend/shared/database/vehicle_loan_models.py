"""
Vehicle Loan Models
Database models for vehicle loan specific features
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, 
    DateTime, ForeignKey, Enum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
import enum


class VehicleType(str, enum.Enum):
    """Vehicle types"""
    TWO_WHEELER = "two_wheeler"
    THREE_WHEELER = "three_wheeler"
    FOUR_WHEELER = "four_wheeler"
    COMMERCIAL = "commercial"
    LUXURY = "luxury"


class VehicleCondition(str, enum.Enum):
    """Vehicle condition"""
    NEW = "new"
    USED = "used"


class HypothecationStatus(str, enum.Enum):
    """Hypothecation status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    MARKED = "marked"
    NOC_ISSUED = "noc_issued"
    REMOVED = "removed"
    FAILED = "failed"


class InsuranceStatus(str, enum.Enum):
    """Insurance status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    CANCELLED = "cancelled"


class VehicleLoanDetails(Base):
    """Vehicle-specific loan details"""
    __tablename__ = "vehicle_loan_details"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, unique=True, index=True)
    
    # Vehicle Basic Info
    vehicle_type = Column(Enum(VehicleType), nullable=False, index=True)
    vehicle_condition = Column(Enum(VehicleCondition), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    variant = Column(String(100))
    manufacturing_year = Column(Integer)
    color = Column(String(50))
    fuel_type = Column(String(50))  # petrol, diesel, electric, hybrid, cng
    
    # Vehicle Identification
    chassis_number = Column(String(50), unique=True, index=True)
    engine_number = Column(String(50), unique=True, index=True)
    registration_number = Column(String(20), unique=True, index=True)
    registration_date = Column(Date)
    registration_state = Column(String(50))
    registration_rto = Column(String(100))
    
    # Pricing
    ex_showroom_price = Column(Numeric(15, 2), nullable=False)
    on_road_price = Column(Numeric(15, 2), nullable=False)
    down_payment = Column(Numeric(15, 2), nullable=False)
    financed_amount = Column(Numeric(15, 2), nullable=False)
    loan_to_value = Column(Numeric(5, 2))  # LTV percentage
    
    # Dealer Information
    dealer_id = Column(Integer, ForeignKey("vehicle_dealers.id"))
    dealer_name = Column(String(200))
    dealer_contact = Column(String(20))
    dealer_location = Column(String(200))
    dealer_invoice_number = Column(String(50))
    dealer_invoice_date = Column(Date)
    
    # Current Status
    is_registered = Column(Boolean, default=False)
    hypothecation_status = Column(Enum(HypothecationStatus), default=HypothecationStatus.PENDING)
    current_owner = Column(String(200))  # Customer name from RC
    
    # Additional Details
    seating_capacity = Column(Integer)
    gross_vehicle_weight = Column(Numeric(10, 2))  # in kg
    vehicle_class = Column(String(50))  # as per RTO
    body_type = Column(String(50))  # sedan, suv, hatchback, etc.
    
    # Documents
    rc_book_number = Column(String(50))
    rc_book_uploaded = Column(Boolean, default=False)
    invoice_uploaded = Column(Boolean, default=False)
    insurance_uploaded = Column(Boolean, default=False)
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    loan_application = relationship("LoanApplication", back_populates="vehicle_details")
    dealer = relationship("VehicleDealer", back_populates="vehicle_loans")
    rto_tracking = relationship("VehicleRTOTracking", back_populates="vehicle_loan", uselist=False)
    insurance_policies = relationship("VehicleInsurance", back_populates="vehicle_loan")
    
    # Indexes
    __table_args__ = (
        Index('idx_vehicle_tenant_loan', 'tenant_id', 'loan_application_id'),
        Index('idx_vehicle_chassis_engine', 'chassis_number', 'engine_number'),
        Index('idx_vehicle_registration', 'registration_number'),
    )


class VehicleDealer(Base):
    """Vehicle dealers/showrooms"""
    __tablename__ = "vehicle_dealers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Dealer Info
    dealer_code = Column(String(50), unique=True, nullable=False, index=True)
    dealer_name = Column(String(200), nullable=False)
    brand = Column(String(100))  # Honda, Maruti, etc.
    
    # Contact Info
    contact_person = Column(String(100))
    mobile = Column(String(20), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    
    # Address
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    pincode = Column(String(10))
    
    # Business Details
    gstin = Column(String(15))
    pan = Column(String(10))
    business_type = Column(String(50))  # authorized_dealer, multi_brand, etc.
    
    # Agreement
    agreement_start_date = Column(Date)
    agreement_end_date = Column(Date)
    commission_percentage = Column(Numeric(5, 2))
    payout_terms = Column(String(100))
    
    # Banking
    bank_name = Column(String(100))
    bank_account_number = Column(String(50))
    bank_ifsc = Column(String(11))
    bank_branch = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    vehicle_loans = relationship("VehicleLoanDetails", back_populates="dealer")
    
    # Indexes
    __table_args__ = (
        Index('idx_dealer_tenant_code', 'tenant_id', 'dealer_code'),
        Index('idx_dealer_active', 'tenant_id', 'is_active'),
    )


class VehicleRTOTracking(Base):
    """RTO hypothecation tracking"""
    __tablename__ = "vehicle_rto_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    vehicle_loan_id = Column(Integer, ForeignKey("vehicle_loan_details.id"), nullable=False, unique=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    
    # RTO Details
    rto_state = Column(String(50), nullable=False)
    rto_office = Column(String(100), nullable=False)
    rto_code = Column(String(20))
    
    # Hypothecation Details
    hypothecation_status = Column(Enum(HypothecationStatus), default=HypothecationStatus.PENDING, index=True)
    lender_name = Column(String(200))  # NBFC name
    
    # Form 35 (Hypothecation Addition)
    form35_submitted = Column(Boolean, default=False)
    form35_submission_date = Column(Date)
    form35_reference_number = Column(String(50))
    form35_fees_paid = Column(Numeric(10, 2))
    
    # Hypothecation Marking
    hypothecation_marked_date = Column(Date)
    hypothecation_endorsement_number = Column(String(50))
    rc_book_updated = Column(Boolean, default=False)
    physical_rc_received = Column(Boolean, default=False)
    
    # NOC & Removal (Form 35 for removal)
    loan_closed_date = Column(Date)
    noc_generated_date = Column(Date)
    noc_sent_to_customer = Column(Boolean, default=False)
    noc_reference_number = Column(String(50))
    
    form35_removal_submitted = Column(Boolean, default=False)
    form35_removal_date = Column(Date)
    form35_removal_reference = Column(String(50))
    
    hypothecation_removed_date = Column(Date)
    updated_rc_issued = Column(Boolean, default=False)
    
    # Tracking
    last_followup_date = Column(Date)
    next_followup_date = Column(Date)
    followup_comments = Column(Text)
    
    # Issues
    issues_encountered = Column(Text)
    resolution_notes = Column(Text)
    
    # Documents
    form35_document_path = Column(String(500))
    noc_document_path = Column(String(500))
    rc_copy_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    vehicle_loan = relationship("VehicleLoanDetails", back_populates="rto_tracking")
    loan_application = relationship("LoanApplication")
    
    # Indexes
    __table_args__ = (
        Index('idx_rto_tenant_status', 'tenant_id', 'hypothecation_status'),
        Index('idx_rto_followup', 'tenant_id', 'next_followup_date'),
    )


class VehicleInsurance(Base):
    """Vehicle insurance tracking"""
    __tablename__ = "vehicle_insurance"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    vehicle_loan_id = Column(Integer, ForeignKey("vehicle_loan_details.id"), nullable=False, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Policy Details
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    policy_type = Column(String(50), nullable=False)  # comprehensive, third_party, own_damage
    insurance_company = Column(String(200), nullable=False)
    insurance_provider_code = Column(String(50))
    
    # Coverage
    idv_amount = Column(Numeric(15, 2), nullable=False)  # Insured Declared Value
    coverage_amount = Column(Numeric(15, 2))
    is_zero_depreciation = Column(Boolean, default=False)
    is_engine_protection = Column(Boolean, default=False)
    is_return_to_invoice = Column(Boolean, default=False)
    
    # Premium
    premium_amount = Column(Numeric(15, 2), nullable=False)
    own_damage_premium = Column(Numeric(15, 2))
    third_party_premium = Column(Numeric(15, 2))
    gst_amount = Column(Numeric(15, 2))
    total_premium = Column(Numeric(15, 2), nullable=False)
    
    # Dates
    policy_start_date = Column(Date, nullable=False, index=True)
    policy_end_date = Column(Date, nullable=False, index=True)
    policy_issued_date = Column(Date)
    
    # Premium Payment
    premium_paid = Column(Boolean, default=False)
    premium_paid_date = Column(Date)
    premium_payment_mode = Column(String(50))
    premium_receipt_number = Column(String(50))
    
    # Renewal
    is_renewal = Column(Boolean, default=False)
    previous_policy_number = Column(String(50))
    renewal_notice_sent = Column(Boolean, default=False)
    renewal_notice_date = Column(Date)
    
    # Status
    status = Column(Enum(InsuranceStatus), default=InsuranceStatus.ACTIVE, index=True)
    cancellation_date = Column(Date)
    cancellation_reason = Column(Text)
    
    # Lien Marking (for insurance)
    lien_marked = Column(Boolean, default=False)
    lien_holder_name = Column(String(200))
    lien_marked_date = Column(Date)
    lien_removed_date = Column(Date)
    
    # Claims
    claims_count = Column(Integer, default=0)
    last_claim_date = Column(Date)
    total_claim_amount = Column(Numeric(15, 2), default=0)
    
    # Nominee
    nominee_name = Column(String(200))
    nominee_relationship = Column(String(50))
    
    # Documents
    policy_document_path = Column(String(500))
    premium_receipt_path = Column(String(500))
    
    # Alerts
    expiry_alert_sent = Column(Boolean, default=False)
    expiry_alert_date = Column(Date)
    days_to_expiry = Column(Integer)  # Computed field
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    vehicle_loan = relationship("VehicleLoanDetails", back_populates="insurance_policies")
    loan_application = relationship("LoanApplication")
    customer = relationship("Customer")
    claims = relationship("VehicleInsuranceClaim", back_populates="insurance_policy")
    
    # Indexes
    __table_args__ = (
        Index('idx_vehicle_insurance_customer', 'tenant_id', 'customer_id'),
        Index('idx_vehicle_insurance_tenant_vehicle', 'tenant_id', 'vehicle_loan_id'),
        Index('idx_vehicle_insurance_expiry', 'tenant_id', 'policy_end_date', 'status'),
    )


class VehicleInsuranceClaim(Base):
    """Insurance claim tracking"""
    __tablename__ = "vehicle_insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    insurance_id = Column(Integer, ForeignKey("vehicle_insurance.id"), nullable=False, index=True)
    
    # Claim Details
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    claim_date = Column(Date, nullable=False, index=True)
    incident_date = Column(Date, nullable=False)
    incident_location = Column(String(200))
    
    # Claim Type
    claim_type = Column(String(50), nullable=False)  # accident, theft, natural_calamity, fire
    claim_description = Column(Text)
    police_fir_number = Column(String(50))
    police_station = Column(String(200))
    
    # Claim Amount
    claimed_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2))
    settled_amount = Column(Numeric(15, 2))
    deductible_amount = Column(Numeric(15, 2))
    
    # Status
    claim_status = Column(String(50), default="submitted", index=True)
    # submitted, under_review, surveyor_appointed, approved, rejected, settled, closed
    
    # Surveyor
    surveyor_name = Column(String(200))
    surveyor_contact = Column(String(20))
    survey_date = Column(Date)
    survey_report_number = Column(String(50))
    survey_report_path = Column(String(500))
    
    # Settlement
    settlement_date = Column(Date)
    settlement_mode = Column(String(50))
    settlement_reference = Column(String(100))
    
    # Rejection
    rejection_date = Column(Date)
    rejection_reason = Column(Text)
    
    # Documents
    claim_form_path = Column(String(500))
    repair_estimate_path = Column(String(500))
    repair_invoice_path = Column(String(500))
    photos_path = Column(JSONB)  # Array of photo paths
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    insurance_policy = relationship("VehicleInsurance", back_populates="claims")
    
    # Indexes
    __table_args__ = (
        Index('idx_vehicle_insurance_claim_tenant_insurance', 'tenant_id', 'insurance_id'),
        Index('idx_vehicle_insurance_claim_status', 'tenant_id', 'claim_status'),
    )


class VehicleManufacturerModel(Base):
    """Master data for vehicle manufacturers and models"""
    __tablename__ = "vehicle_manufacturer_models"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Manufacturer
    manufacturer = Column(String(100), nullable=False, index=True)
    manufacturer_code = Column(String(50))
    
    # Model
    model = Column(String(100), nullable=False)
    model_code = Column(String(50))
    variant = Column(String(100))
    
    # Type
    vehicle_type = Column(Enum(VehicleType), nullable=False, index=True)
    body_type = Column(String(50))
    fuel_type = Column(String(50))
    
    # Specifications
    engine_capacity = Column(Integer)  # in CC
    seating_capacity = Column(Integer)
    mileage = Column(Numeric(5, 2))  # km/l
    power_bhp = Column(Integer)
    
    # Pricing (reference only)
    ex_showroom_price_min = Column(Numeric(15, 2))
    ex_showroom_price_max = Column(Numeric(15, 2))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_vehicle_model_tenant', 'tenant_id', 'manufacturer', 'model'),
        Index('idx_vehicle_model_type', 'tenant_id', 'vehicle_type', 'is_active'),
    )
