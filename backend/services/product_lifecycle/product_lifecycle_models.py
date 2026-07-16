"""
Product Lifecycle Management Models
Product variants, promotional products, seasonal products, and product sunset
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from backend.core.database import Base


# =====================================================================
# ENUMS
# =====================================================================

class VariantType(str, Enum):
    """Product variant types"""
    STANDARD = "STANDARD"
    PROMOTIONAL = "PROMOTIONAL"
    SEASONAL = "SEASONAL"
    GEOGRAPHY_SPECIFIC = "GEOGRAPHY_SPECIFIC"
    SEGMENT_SPECIFIC = "SEGMENT_SPECIFIC"
    LIMITED_EDITION = "LIMITED_EDITION"
    EMPLOYEE_SPECIAL = "EMPLOYEE_SPECIAL"


class VariantStatus(str, Enum):
    """Variant status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    DISCONTINUED = "DISCONTINUED"


class Season(str, Enum):
    """Seasonal periods"""
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    MONSOON = "MONSOON"
    AUTUMN = "AUTUMN"
    WINTER = "WINTER"
    FESTIVE = "FESTIVE"
    YEAR_END = "YEAR_END"
    NEW_YEAR = "NEW_YEAR"


class CustomerSegment(str, Enum):
    """Customer segments"""
    RETAIL = "RETAIL"
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    PROFESSIONAL = "PROFESSIONAL"
    STUDENT = "STUDENT"
    SENIOR_CITIZEN = "SENIOR_CITIZEN"
    WOMEN = "WOMEN"
    RURAL = "RURAL"
    URBAN = "URBAN"
    PREMIUM = "PREMIUM"
    MASS_MARKET = "MASS_MARKET"


class SunsetStatus(str, Enum):
    """Product sunset status"""
    ACTIVE = "ACTIVE"
    ANNOUNCED = "ANNOUNCED"
    NO_NEW_APPLICATIONS = "NO_NEW_APPLICATIONS"
    CLOSED_FOR_NEW = "CLOSED_FOR_NEW"
    GRANDFATHERED_ONLY = "GRANDFATHERED_ONLY"
    FULLY_DISCONTINUED = "FULLY_DISCONTINUED"


class MigrationStatus(str, Enum):
    """Customer migration status"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    MIGRATED = "MIGRATED"
    DECLINED = "DECLINED"
    FAILED = "FAILED"


# =====================================================================
# DATABASE MODELS
# =====================================================================

class ProductVariant(Base):
    """Product variants with different configurations"""
    __tablename__ = "product_variants"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    base_product_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Variant information
    variant_code = Column(String(50), nullable=False, unique=True)
    variant_name = Column(String(255), nullable=False)
    variant_type = Column(SQLEnum(VariantType), nullable=False)
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(VariantStatus), default=VariantStatus.DRAFT)
    is_active = Column(Boolean, default=False)
    
    # Validity period
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date)
    
    # Configuration overrides (JSON for flexibility)
    interest_rate_override = Column(JSON)  # {"base": 10.5, "min": 10.0, "max": 12.0}
    tenure_override = Column(JSON)  # {"min": 12, "max": 60}
    amount_override = Column(JSON)  # {"min": 50000, "max": 500000}
    fee_override = Column(JSON)  # {"processing_fee": 1.5, "prepayment_fee": 2.0}
    eligibility_override = Column(JSON)  # Custom eligibility criteria
    
    # Priority (higher priority variants shown first)
    priority = Column(Integer, default=0)
    
    # Marketing
    marketing_name = Column(String(255))
    tagline = Column(String(500))
    promotional_message = Column(Text)
    banner_image_url = Column(String(500))
    terms_and_conditions = Column(Text)
    
    # Usage tracking
    application_count = Column(Integer, default=0)
    disbursement_count = Column(Integer, default=0)
    total_disbursed_amount = Column(Float, default=0.0)
    
    # Relationships
    promotional_config = relationship("PromotionalProduct", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    seasonal_config = relationship("SeasonalProduct", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    geography_config = relationship("GeographySpecificProduct", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    segment_config = relationship("SegmentSpecificProduct", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    updated_by = Column(PGUUID(as_uuid=True))


class PromotionalProduct(Base):
    """Promotional product configuration (limited period offers)"""
    __tablename__ = "promotional_products"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    variant_id = Column(PGUUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Promotion details
    promotion_code = Column(String(50), unique=True)
    promotion_name = Column(String(255), nullable=False)
    campaign_name = Column(String(255))
    
    # Promotion period
    promotion_start_date = Column(Date, nullable=False)
    promotion_end_date = Column(Date, nullable=False)
    
    # Offer details
    special_rate_discount = Column(Float)  # Discount on interest rate (e.g., 0.5% off)
    fee_waiver = Column(JSON)  # {"processing_fee": 100, "prepayment_fee": 50}
    cashback_amount = Column(Float)
    cashback_percentage = Column(Float)
    
    # Limits
    max_applications = Column(Integer)  # Max applications allowed
    max_disbursement_amount = Column(Float)  # Max total disbursement
    applications_per_customer = Column(Integer, default=1)
    
    # Current usage
    current_applications = Column(Integer, default=0)
    current_disbursement_amount = Column(Float, default=0.0)
    
    # Conditions
    min_credit_score = Column(Integer)
    min_loan_amount = Column(Float)
    requires_referral_code = Column(Boolean, default=False)
    auto_approve_eligible = Column(Boolean, default=False)
    
    # Partner integration
    partner_code = Column(String(100))
    partner_commission_percentage = Column(Float)
    
    # Relationship
    variant = relationship("ProductVariant", back_populates="promotional_config")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SeasonalProduct(Base):
    """Seasonal product configuration"""
    __tablename__ = "seasonal_products"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    variant_id = Column(PGUUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Season information
    season = Column(SQLEnum(Season), nullable=False)
    season_year = Column(Integer, nullable=False)
    
    # Season dates
    season_start_date = Column(Date, nullable=False)
    season_end_date = Column(Date, nullable=False)
    
    # Seasonal adjustments
    seasonal_rate_adjustment = Column(Float)  # +/- adjustment to base rate
    seasonal_amount_boost = Column(Float)  # Additional amount limit for season
    seasonal_tenure_extension = Column(Integer)  # Additional months allowed
    
    # Seasonal features
    festive_bonus = Column(Float)
    holiday_moratorium = Column(Boolean, default=False)  # EMI holiday during season
    moratorium_months = Column(Integer)
    
    # Target metrics
    target_applications = Column(Integer)
    target_disbursement = Column(Float)
    
    # Auto-renewal
    auto_renew_next_year = Column(Boolean, default=False)
    
    # Relationship
    variant = relationship("ProductVariant", back_populates="seasonal_config")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GeographySpecificProduct(Base):
    """Geography-specific product variants"""
    __tablename__ = "geography_specific_products"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    variant_id = Column(PGUUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Geography targeting
    allowed_states = Column(JSON)  # List of state codes
    allowed_cities = Column(JSON)  # List of city names
    allowed_pincodes = Column(JSON)  # List of pincode ranges
    excluded_areas = Column(JSON)  # Excluded areas
    
    # Geography type
    is_metro = Column(Boolean)
    is_tier1 = Column(Boolean)
    is_tier2 = Column(Boolean)
    is_tier3 = Column(Boolean)
    is_rural = Column(Boolean)
    
    # Regional adjustments
    regional_rate_adjustment = Column(Float)
    regional_amount_adjustment = Column(Float)
    regional_ltv_adjustment = Column(Float)
    
    # Local compliance
    local_regulations = Column(JSON)
    requires_local_verification = Column(Boolean, default=False)
    local_documentation = Column(JSON)
    
    # Branch availability
    requires_branch_presence = Column(Boolean, default=False)
    available_branch_codes = Column(JSON)
    
    # Relationship
    variant = relationship("ProductVariant", back_populates="geography_config")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SegmentSpecificProduct(Base):
    """Customer segment-specific product variants"""
    __tablename__ = "segment_specific_products"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    variant_id = Column(PGUUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Target segments
    target_segments = Column(JSON, nullable=False)  # List of CustomerSegment values
    
    # Segment criteria
    min_age = Column(Integer)
    max_age = Column(Integer)
    min_income = Column(Float)
    max_income = Column(Float)
    employment_types = Column(JSON)  # ["SALARIED", "SELF_EMPLOYED"]
    
    # Industry/profession targeting
    allowed_industries = Column(JSON)
    allowed_professions = Column(JSON)
    excluded_industries = Column(JSON)
    
    # Segment benefits
    segment_rate_benefit = Column(Float)  # Rate discount for segment
    segment_fee_waiver = Column(JSON)
    priority_processing = Column(Boolean, default=False)
    dedicated_relationship_manager = Column(Boolean, default=False)
    
    # Additional features
    special_features = Column(JSON)  # {"top_up": true, "overdraft": true}
    loyalty_benefits = Column(JSON)
    referral_bonus = Column(Float)
    
    # Segment limits
    max_segment_exposure = Column(Float)  # Max total exposure to segment
    current_segment_exposure = Column(Float, default=0.0)
    
    # Relationship
    variant = relationship("ProductVariant", back_populates="segment_config")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductSunset(Base):
    """Product sunset/discontinuation management"""
    __tablename__ = "product_sunsets"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Sunset information
    sunset_reason = Column(String(255), nullable=False)
    sunset_description = Column(Text)
    sunset_category = Column(String(50))  # REGULATORY, BUSINESS, PERFORMANCE, etc.
    
    # Timeline
    announcement_date = Column(Date, nullable=False)
    no_new_applications_date = Column(Date, nullable=False)
    existing_customers_cutoff_date = Column(Date)
    full_discontinuation_date = Column(Date)
    
    # Status
    sunset_status = Column(SQLEnum(SunsetStatus), default=SunsetStatus.ANNOUNCED)
    
    # Grandfathering
    grandfather_existing_customers = Column(Boolean, default=True)
    grandfather_in_pipeline = Column(Boolean, default=True)
    pipeline_cutoff_stage = Column(String(50))  # e.g., "APPROVED", "DISBURSED"
    
    # Impact assessment
    total_active_accounts = Column(Integer, default=0)
    total_outstanding_amount = Column(Float, default=0.0)
    applications_in_pipeline = Column(Integer, default=0)
    
    # Migration plan
    has_migration_plan = Column(Boolean, default=False)
    target_product_id = Column(PGUUID(as_uuid=True))  # Replacement product
    auto_migrate_eligible = Column(Boolean, default=False)
    migration_deadline = Column(Date)
    migration_incentive = Column(JSON)  # {"rate_benefit": 0.25, "fee_waiver": true}
    
    # Customer communication
    customer_notification_sent = Column(Boolean, default=False)
    notification_date = Column(Date)
    notification_channels = Column(JSON)  # ["EMAIL", "SMS", "LETTER"]
    customer_support_info = Column(Text)
    faq_document_url = Column(String(500))
    
    # Metrics
    customers_notified = Column(Integer, default=0)
    customers_migrated = Column(Integer, default=0)
    customers_remaining = Column(Integer, default=0)
    
    # Regulatory compliance
    regulatory_approval_required = Column(Boolean, default=False)
    regulatory_approval_date = Column(Date)
    regulatory_reference_number = Column(String(100))
    
    # Relationships
    migrations = relationship("CustomerMigration", back_populates="sunset", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    approved_by = Column(PGUUID(as_uuid=True))


class CustomerMigration(Base):
    """Track customer migration to new products"""
    __tablename__ = "customer_migrations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sunset_id = Column(PGUUID(as_uuid=True), ForeignKey("product_sunsets.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Customer information
    customer_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    old_account_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Migration details
    from_product_id = Column(PGUUID(as_uuid=True), nullable=False)
    to_product_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Migration status
    migration_status = Column(SQLEnum(MigrationStatus), default=MigrationStatus.NOT_STARTED)
    
    # Dates
    eligible_from = Column(Date, nullable=False)
    migration_deadline = Column(Date)
    customer_contacted_date = Column(Date)
    customer_consent_date = Column(Date)
    migration_completed_date = Column(Date)
    
    # Migration terms
    outstanding_balance = Column(Float)
    new_account_id = Column(PGUUID(as_uuid=True))
    migration_terms = Column(JSON)  # Terms offered for migration
    customer_accepted_terms = Column(Boolean, default=False)
    
    # Benefits offered
    rate_benefit_offered = Column(Float)
    fee_waiver_offered = Column(JSON)
    special_conditions = Column(JSON)
    
    # Communication
    communication_log = Column(JSON)  # Log of all communications
    customer_response = Column(Text)
    decline_reason = Column(String(255))
    
    # Approvals
    migration_approved_by = Column(PGUUID(as_uuid=True))
    approval_date = Column(Date)
    
    # Relationship
    sunset = relationship("ProductSunset", back_populates="migrations")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =====================================================================
# PYDANTIC SCHEMAS
# =====================================================================

class ProductVariantBase(BaseModel):
    """Base variant schema"""
    base_product_id: UUID
    variant_code: str
    variant_name: str
    variant_type: VariantType
    description: Optional[str] = None
    valid_from: date
    valid_to: Optional[date] = None
    interest_rate_override: Optional[Dict[str, Any]] = None
    tenure_override: Optional[Dict[str, Any]] = None
    amount_override: Optional[Dict[str, Any]] = None
    fee_override: Optional[Dict[str, Any]] = None
    eligibility_override: Optional[Dict[str, Any]] = None
    priority: int = 0
    marketing_name: Optional[str] = None
    tagline: Optional[str] = None
    promotional_message: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class ProductVariantCreate(ProductVariantBase):
    """Create variant schema"""
    pass


class ProductVariantUpdate(BaseModel):
    """Update variant schema"""
    variant_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[VariantStatus] = None
    valid_to: Optional[date] = None
    interest_rate_override: Optional[Dict[str, Any]] = None
    tenure_override: Optional[Dict[str, Any]] = None
    amount_override: Optional[Dict[str, Any]] = None
    fee_override: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    marketing_name: Optional[str] = None
    tagline: Optional[str] = None
    promotional_message: Optional[str] = None


class PromotionalProductSchema(BaseModel):
    """Promotional product schema"""
    promotion_code: Optional[str] = None
    promotion_name: str
    campaign_name: Optional[str] = None
    promotion_start_date: date
    promotion_end_date: date
    special_rate_discount: Optional[float] = None
    fee_waiver: Optional[Dict[str, float]] = None
    cashback_amount: Optional[float] = None
    cashback_percentage: Optional[float] = None
    max_applications: Optional[int] = None
    max_disbursement_amount: Optional[float] = None
    applications_per_customer: int = 1
    min_credit_score: Optional[int] = None
    min_loan_amount: Optional[float] = None
    requires_referral_code: bool = False
    auto_approve_eligible: bool = False
    partner_code: Optional[str] = None
    partner_commission_percentage: Optional[float] = None


class SeasonalProductSchema(BaseModel):
    """Seasonal product schema"""
    season: Season
    season_year: int
    season_start_date: date
    season_end_date: date
    seasonal_rate_adjustment: Optional[float] = None
    seasonal_amount_boost: Optional[float] = None
    seasonal_tenure_extension: Optional[int] = None
    festive_bonus: Optional[float] = None
    holiday_moratorium: bool = False
    moratorium_months: Optional[int] = None
    target_applications: Optional[int] = None
    target_disbursement: Optional[float] = None
    auto_renew_next_year: bool = False


class GeographySpecificProductSchema(BaseModel):
    """Geography-specific product schema"""
    allowed_states: Optional[List[str]] = None
    allowed_cities: Optional[List[str]] = None
    allowed_pincodes: Optional[List[str]] = None
    excluded_areas: Optional[List[str]] = None
    is_metro: Optional[bool] = None
    is_tier1: Optional[bool] = None
    is_tier2: Optional[bool] = None
    is_tier3: Optional[bool] = None
    is_rural: Optional[bool] = None
    regional_rate_adjustment: Optional[float] = None
    regional_amount_adjustment: Optional[float] = None
    regional_ltv_adjustment: Optional[float] = None
    local_regulations: Optional[Dict[str, Any]] = None
    requires_local_verification: bool = False
    local_documentation: Optional[List[str]] = None
    requires_branch_presence: bool = False
    available_branch_codes: Optional[List[str]] = None


class SegmentSpecificProductSchema(BaseModel):
    """Segment-specific product schema"""
    target_segments: List[str]
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    min_income: Optional[float] = None
    max_income: Optional[float] = None
    employment_types: Optional[List[str]] = None
    allowed_industries: Optional[List[str]] = None
    allowed_professions: Optional[List[str]] = None
    excluded_industries: Optional[List[str]] = None
    segment_rate_benefit: Optional[float] = None
    segment_fee_waiver: Optional[Dict[str, float]] = None
    priority_processing: bool = False
    dedicated_relationship_manager: bool = False
    special_features: Optional[Dict[str, bool]] = None
    loyalty_benefits: Optional[Dict[str, Any]] = None
    referral_bonus: Optional[float] = None
    max_segment_exposure: Optional[float] = None


class ProductSunsetCreate(BaseModel):
    """Create sunset schema"""
    product_id: UUID
    sunset_reason: str
    sunset_description: Optional[str] = None
    sunset_category: Optional[str] = None
    announcement_date: date
    no_new_applications_date: date
    existing_customers_cutoff_date: Optional[date] = None
    full_discontinuation_date: Optional[date] = None
    grandfather_existing_customers: bool = True
    grandfather_in_pipeline: bool = True
    pipeline_cutoff_stage: Optional[str] = None
    has_migration_plan: bool = False
    target_product_id: Optional[UUID] = None
    auto_migrate_eligible: bool = False
    migration_deadline: Optional[date] = None
    migration_incentive: Optional[Dict[str, Any]] = None
    notification_channels: Optional[List[str]] = None
    customer_support_info: Optional[str] = None
    regulatory_approval_required: bool = False


class ProductSunsetUpdate(BaseModel):
    """Update sunset schema"""
    sunset_status: Optional[SunsetStatus] = None
    no_new_applications_date: Optional[date] = None
    existing_customers_cutoff_date: Optional[date] = None
    full_discontinuation_date: Optional[date] = None
    migration_deadline: Optional[date] = None
    customer_notification_sent: Optional[bool] = None
    notification_date: Optional[date] = None
    regulatory_approval_date: Optional[date] = None
    regulatory_reference_number: Optional[str] = None


class ProductVariantResponse(ProductVariantBase):
    """Variant response schema"""
    id: UUID
    tenant_id: UUID
    status: VariantStatus
    is_active: bool
    application_count: int
    disbursement_count: int
    total_disbursed_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductSunsetResponse(BaseModel):
    """Sunset response schema"""
    id: UUID
    tenant_id: UUID
    product_id: UUID
    sunset_reason: str
    sunset_description: Optional[str]
    sunset_category: Optional[str]
    announcement_date: date
    no_new_applications_date: date
    existing_customers_cutoff_date: Optional[date]
    full_discontinuation_date: Optional[date]
    sunset_status: SunsetStatus
    grandfather_existing_customers: bool
    total_active_accounts: int
    total_outstanding_amount: float
    applications_in_pipeline: int
    customers_notified: int
    customers_migrated: int
    customers_remaining: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
