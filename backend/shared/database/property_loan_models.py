"""
Property Loan Models (LAP/Home Loan)
Database models for property/mortgage loan specific features
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


class PropertyType(str, enum.Enum):
    """Property types"""
    RESIDENTIAL_FLAT = "residential_flat"
    RESIDENTIAL_HOUSE = "residential_house"
    RESIDENTIAL_PLOT = "residential_plot"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_SHOP = "commercial_shop"
    COMMERCIAL_PLOT = "commercial_plot"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"


class PropertyOwnershipType(str, enum.Enum):
    """Property ownership"""
    FREEHOLD = "freehold"
    LEASEHOLD = "leasehold"
    POWER_OF_ATTORNEY = "power_of_attorney"
    CO_OWNERSHIP = "co_ownership"


class PropertyStatus(str, enum.Enum):
    """Property status"""
    UNDER_CONSTRUCTION = "under_construction"
    READY_TO_MOVE = "ready_to_move"
    OCCUPIED = "occupied"
    VACANT = "vacant"


class LegalVerificationStatus(str, enum.Enum):
    """Legal verification status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CLEAR = "clear"
    ISSUES_FOUND = "issues_found"
    REJECTED = "rejected"


class TechnicalVerificationStatus(str, enum.Enum):
    """Technical verification status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class MortgageStatus(str, enum.Enum):
    """Mortgage status"""
    PENDING = "pending"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    REGISTERED = "registered"
    DISCHARGED = "discharged"


class PropertyLoanDetails(Base):
    """Property-specific loan details for LAP/Home Loan"""
    __tablename__ = "property_loan_details"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, unique=True, index=True)
    
    # Property Basic Info
    property_type = Column(Enum(PropertyType), nullable=False, index=True)
    property_ownership_type = Column(Enum(PropertyOwnershipType), nullable=False)
    property_status = Column(Enum(PropertyStatus), nullable=False)
    
    # Property Location
    address_line1 = Column(String(200), nullable=False)
    address_line2 = Column(String(200))
    city = Column(String(100), nullable=False)
    district = Column(String(100))
    state = Column(String(50), nullable=False)
    pincode = Column(String(10), nullable=False)
    landmark = Column(String(200))
    
    # Property Identification
    survey_number = Column(String(100))
    plot_number = Column(String(50))
    khata_number = Column(String(50))  # Karnataka
    khasra_number = Column(String(50))  # North India
    cts_number = Column(String(50))  # Maharashtra
    block_number = Column(String(50))
    flat_number = Column(String(50))
    building_name = Column(String(200))
    
    # Property Measurements
    plot_area = Column(Numeric(10, 2))  # in sq ft
    built_up_area = Column(Numeric(10, 2))  # in sq ft
    carpet_area = Column(Numeric(10, 2))  # in sq ft
    
    # Property Details
    construction_year = Column(Integer)
    property_age = Column(Integer)  # in years
    number_of_floors = Column(Integer)
    floor_number = Column(Integer)  # if flat/office
    number_of_rooms = Column(Integer)
    number_of_bathrooms = Column(Integer)
    
    # Boundaries
    boundary_north = Column(String(200))
    boundary_south = Column(String(200))
    boundary_east = Column(String(200))
    boundary_west = Column(String(200))
    
    # Valuation
    market_value = Column(Numeric(15, 2), nullable=False)
    distress_sale_value = Column(Numeric(15, 2))
    government_value = Column(Numeric(15, 2))  # guideline value
    bank_valuation = Column(Numeric(15, 2))
    loan_amount = Column(Numeric(15, 2), nullable=False)
    loan_to_value = Column(Numeric(5, 2))  # LTV percentage
    
    # Ownership
    current_owner_name = Column(String(200))
    previous_owner_name = Column(String(200))
    ownership_duration = Column(Integer)  # in years
    
    # Builder/Seller Info
    builder_name = Column(String(200))
    builder_contact = Column(String(20))
    builder_registration = Column(String(100))
    seller_name = Column(String(200))
    seller_contact = Column(String(20))
    
    # Legal Status
    is_disputed = Column(Boolean, default=False)
    has_clear_title = Column(Boolean, default=False)
    has_litigation = Column(Boolean, default=False)
    litigation_details = Column(Text)
    
    # Approvals
    has_building_approval = Column(Boolean, default=False)
    has_occupation_certificate = Column(Boolean, default=False)
    has_completion_certificate = Column(Boolean, default=False)
    
    # Utilities
    has_electricity = Column(Boolean, default=False)
    has_water_connection = Column(Boolean, default=False)
    has_drainage = Column(Boolean, default=False)
    
    # Status
    legal_verification_status = Column(Enum(LegalVerificationStatus), default=LegalVerificationStatus.PENDING)
    technical_verification_status = Column(Enum(TechnicalVerificationStatus), default=TechnicalVerificationStatus.PENDING)
    mortgage_status = Column(Enum(MortgageStatus), default=MortgageStatus.PENDING)
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    loan_application = relationship("LoanApplication", back_populates="property_details")
    legal_verification = relationship("PropertyLegalVerification", back_populates="property_loan", uselist=False)
    technical_verification = relationship("PropertyTechnicalVerification", back_populates="property_loan", uselist=False)
    documents = relationship("PropertyDocument", back_populates="property_loan")
    mortgage = relationship("PropertyMortgage", back_populates="property_loan", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_property_tenant_loan', 'tenant_id', 'loan_application_id'),
        Index('idx_property_type_status', 'tenant_id', 'property_type', 'property_status'),
        Index('idx_property_location', 'city', 'state', 'pincode'),
    )


class PropertyLegalVerification(Base):
    """Legal verification for property"""
    __tablename__ = "property_legal_verification"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_loan_id = Column(Integer, ForeignKey("property_loan_details.id"), nullable=False, unique=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    
    # Legal Firm/Advocate
    advocate_name = Column(String(200))
    advocate_contact = Column(String(20))
    advocate_bar_registration = Column(String(100))
    legal_firm_name = Column(String(200))
    
    # Verification Details
    verification_date = Column(Date)
    verification_reference = Column(String(100))
    verification_fees = Column(Numeric(10, 2))
    
    # Title Status
    title_clear = Column(Boolean, default=False)
    title_issues = Column(Text)
    title_chain_verified = Column(Boolean, default=False)
    previous_owners = Column(JSONB)  # Array of previous owner details
    
    # Encumbrance Certificate (EC)
    ec_obtained = Column(Boolean, default=False)
    ec_period_from = Column(Date)
    ec_period_to = Column(Date)
    ec_reference_number = Column(String(100))
    ec_issues_found = Column(Text)
    encumbrances_found = Column(Boolean, default=False)
    encumbrance_details = Column(Text)
    
    # Search Report
    search_report_available = Column(Boolean, default=False)
    search_report_date = Column(Date)
    search_years_covered = Column(Integer)  # typically 13/30 years
    
    # Property Tax
    property_tax_verified = Column(Boolean, default=False)
    property_tax_updated = Column(Boolean, default=False)
    property_tax_arrears = Column(Numeric(10, 2))
    
    # Ownership Documents
    sale_deed_verified = Column(Boolean, default=False)
    sale_deed_date = Column(Date)
    sale_deed_value = Column(Numeric(15, 2))
    gift_deed_applicable = Column(Boolean, default=False)
    inheritance_verified = Column(Boolean, default=False)
    
    # Power of Attorney (if applicable)
    poa_verified = Column(Boolean, default=False)
    poa_holder_name = Column(String(200))
    poa_registration_date = Column(Date)
    poa_valid = Column(Boolean, default=False)
    
    # Mother Deed
    mother_deed_verified = Column(Boolean, default=False)
    mother_deed_date = Column(Date)
    
    # Legal Opinion
    legal_opinion_given = Column(Boolean, default=False)
    legal_opinion_date = Column(Date)
    legal_opinion_summary = Column(Text)
    legal_opinion_status = Column(Enum(LegalVerificationStatus), default=LegalVerificationStatus.PENDING)
    
    # Issues & Risks
    litigation_pending = Column(Boolean, default=False)
    litigation_details = Column(Text)
    legal_risks_identified = Column(Text)
    recommendations = Column(Text)
    
    # Approval
    approved = Column(Boolean, default=False)
    approved_date = Column(Date)
    rejection_reason = Column(Text)
    
    # Documents
    legal_report_path = Column(String(500))
    ec_document_path = Column(String(500))
    search_report_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    property_loan = relationship("PropertyLoanDetails", back_populates="legal_verification")
    loan_application = relationship("LoanApplication")
    
    # Indexes
    __table_args__ = (
        Index('idx_legal_tenant_property', 'tenant_id', 'property_loan_id'),
        Index('idx_legal_status', 'tenant_id', 'legal_opinion_status'),
    )


class PropertyTechnicalVerification(Base):
    """Technical/engineering verification for property"""
    __tablename__ = "property_technical_verification"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_loan_id = Column(Integer, ForeignKey("property_loan_details.id"), nullable=False, unique=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    
    # Engineer/Valuer
    engineer_name = Column(String(200))
    engineer_contact = Column(String(20))
    engineer_license = Column(String(100))
    valuer_empaneled = Column(Boolean, default=False)
    
    # Inspection Details
    inspection_date = Column(Date)
    inspection_time = Column(String(20))
    inspection_reference = Column(String(100))
    inspection_fees = Column(Numeric(10, 2))
    
    # Site Visit
    site_visited = Column(Boolean, default=False)
    site_accessible = Column(Boolean, default=True)
    site_location_verified = Column(Boolean, default=False)
    boundaries_verified = Column(Boolean, default=False)
    
    # Measurements
    plot_area_verified = Column(Numeric(10, 2))
    built_up_area_verified = Column(Numeric(10, 2))
    carpet_area_verified = Column(Numeric(10, 2))
    measurement_variance = Column(Numeric(5, 2))  # percentage variance
    
    # Construction Details
    construction_type = Column(String(50))  # RCC, load_bearing, etc.
    construction_quality = Column(String(50))  # excellent, good, average, poor
    construction_stage = Column(String(50))  # if under construction
    construction_completion = Column(Integer)  # percentage
    
    # Property Condition
    property_condition = Column(String(50))  # excellent, good, average, poor
    property_age_verified = Column(Integer)
    property_maintenance = Column(String(50))
    structural_issues = Column(Text)
    repair_required = Column(Boolean, default=False)
    repair_cost_estimate = Column(Numeric(10, 2))
    
    # Amenities
    floor_type = Column(String(50))  # tiles, marble, etc.
    roof_type = Column(String(50))
    window_type = Column(String(50))
    door_type = Column(String(50))
    
    # Utilities Verification
    electricity_verified = Column(Boolean, default=False)
    water_supply_verified = Column(Boolean, default=False)
    drainage_verified = Column(Boolean, default=False)
    road_access = Column(Boolean, default=True)
    road_width = Column(Numeric(5, 2))  # in feet
    
    # Approvals Verification
    building_plan_approved = Column(Boolean, default=False)
    building_plan_number = Column(String(100))
    building_plan_authority = Column(String(200))
    
    occupation_certificate_verified = Column(Boolean, default=False)
    oc_number = Column(String(100))
    oc_date = Column(Date)
    
    completion_certificate_verified = Column(Boolean, default=False)
    cc_number = Column(String(100))
    cc_date = Column(Date)
    
    # Neighborhood
    locality_type = Column(String(50))  # prime, good, average
    neighborhood_development = Column(String(50))
    distance_to_main_road = Column(Numeric(5, 2))  # in km
    public_transport_available = Column(Boolean, default=True)
    
    # Valuation
    market_value_assessed = Column(Numeric(15, 2))
    distress_sale_value_assessed = Column(Numeric(15, 2))
    forced_sale_value = Column(Numeric(15, 2))
    realizable_value = Column(Numeric(15, 2))
    valuation_method = Column(String(50))  # market_comparison, cost, income
    
    # Recommendations
    recommended_loan_amount = Column(Numeric(15, 2))
    recommended_ltv = Column(Numeric(5, 2))
    property_marketable = Column(Boolean, default=True)
    remarks = Column(Text)
    risks_identified = Column(Text)
    
    # Approval
    status = Column(Enum(TechnicalVerificationStatus), default=TechnicalVerificationStatus.PENDING)
    approved = Column(Boolean, default=False)
    approved_date = Column(Date)
    rejection_reason = Column(Text)
    
    # Documents
    valuation_report_path = Column(String(500))
    site_photos = Column(JSONB)  # Array of photo paths
    video_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    property_loan = relationship("PropertyLoanDetails", back_populates="technical_verification")
    loan_application = relationship("LoanApplication")
    
    # Indexes
    __table_args__ = (
        Index('idx_technical_tenant_property', 'tenant_id', 'property_loan_id'),
        Index('idx_technical_status', 'tenant_id', 'status'),
    )


class PropertyDocument(Base):
    """Property documents"""
    __tablename__ = "property_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_loan_id = Column(Integer, ForeignKey("property_loan_details.id"), nullable=False, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    
    # Document Details
    document_type = Column(String(100), nullable=False)
    # sale_deed, mother_deed, ec, property_card, tax_receipt, building_plan, 
    # oc, cc, poa, search_report, legal_opinion, valuation_report
    document_name = Column(String(200), nullable=False)
    document_number = Column(String(100))
    document_date = Column(Date)
    
    # File Info
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200))
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True))
    verified_date = Column(Date)
    verification_remarks = Column(Text)
    
    # Status
    is_original = Column(Boolean, default=False)
    is_certified_copy = Column(Boolean, default=False)
    issuing_authority = Column(String(200))
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    uploaded_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    property_loan = relationship("PropertyLoanDetails", back_populates="documents")
    loan_application = relationship("LoanApplication")
    
    # Indexes
    __table_args__ = (
        Index('idx_document_tenant_property', 'tenant_id', 'property_loan_id'),
        Index('idx_document_type', 'tenant_id', 'document_type'),
    )


class PropertyMortgage(Base):
    """Property mortgage/lien tracking"""
    __tablename__ = "property_mortgages"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_loan_id = Column(Integer, ForeignKey("property_loan_details.id"), nullable=False, unique=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    
    # Mortgage Details
    mortgage_type = Column(String(50), nullable=False)  # equitable, registered
    mortgage_deed_number = Column(String(100))
    mortgage_amount = Column(Numeric(15, 2), nullable=False)
    
    # Registration
    sub_registrar_office = Column(String(200))
    sub_registrar_district = Column(String(100))
    registration_date = Column(Date)
    registration_number = Column(String(100))
    registration_fees = Column(Numeric(10, 2))
    stamp_duty_paid = Column(Numeric(10, 2))
    
    # Lien Details
    lien_marked = Column(Boolean, default=False)
    lien_marked_date = Column(Date)
    lien_holder_name = Column(String(200))
    lien_amount = Column(Numeric(15, 2))
    
    # Status
    mortgage_status = Column(Enum(MortgageStatus), default=MortgageStatus.PENDING, index=True)
    
    # Documents Submitted
    original_documents_submitted = Column(Boolean, default=False)
    documents_submission_date = Column(Date)
    documents_received_from = Column(String(200))
    
    # Original Documents List
    sale_deed_original = Column(Boolean, default=False)
    property_card_original = Column(Boolean, default=False)
    building_plan_original = Column(Boolean, default=False)
    other_documents = Column(JSONB)  # List of other original documents
    
    # Discharge (on loan closure)
    loan_closed_date = Column(Date)
    discharge_initiated = Column(Boolean, default=False)
    discharge_initiated_date = Column(Date)
    
    discharge_deed_executed = Column(Boolean, default=False)
    discharge_deed_date = Column(Date)
    discharge_deed_number = Column(String(100))
    
    discharge_registered = Column(Boolean, default=False)
    discharge_registration_date = Column(Date)
    discharge_registration_number = Column(String(100))
    
    documents_returned = Column(Boolean, default=False)
    documents_return_date = Column(Date)
    documents_returned_to = Column(String(200))
    
    # Tracking
    last_followup_date = Column(Date)
    next_followup_date = Column(Date)
    followup_remarks = Column(Text)
    
    # Documents
    mortgage_deed_path = Column(String(500))
    discharge_deed_path = Column(String(500))
    acknowledgement_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    property_loan = relationship("PropertyLoanDetails", back_populates="mortgage")
    loan_application = relationship("LoanApplication")
    
    # Indexes
    __table_args__ = (
        Index('idx_mortgage_tenant_property', 'tenant_id', 'property_loan_id'),
        Index('idx_mortgage_status', 'tenant_id', 'mortgage_status'),
    )
