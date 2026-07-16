"""
Product Configuration Models

Models for defining loan and deposit products with complete configuration
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ==================== ENUMS ====================

class ProductCategory(str, Enum):
    """Product category types"""
    PERSONAL_LOAN = "personal_loan"
    HOME_LOAN = "home_loan"
    VEHICLE_LOAN = "vehicle_loan"
    GOLD_LOAN = "gold_loan"
    BUSINESS_LOAN = "business_loan"
    EDUCATION_LOAN = "education_loan"
    FIXED_DEPOSIT = "fixed_deposit"
    RECURRING_DEPOSIT = "recurring_deposit"
    SAVINGS_ACCOUNT = "savings_account"
    CREDIT_CARD = "credit_card"
    OVERDRAFT = "overdraft"
    LAP = "loan_against_property"
    MSME_LOAN = "msme_loan"


class ProductStatus(str, Enum):
    """Product status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMING_SOON = "coming_soon"
    DISCONTINUED = "discontinued"


class InterestCalculationMethod(str, Enum):
    """Interest calculation methods"""
    FLAT_RATE = "flat_rate"
    REDUCING_BALANCE = "reducing_balance"
    SIMPLE_INTEREST = "simple_interest"
    COMPOUND_INTEREST = "compound_interest"
    DAILY_REDUCING = "daily_reducing"
    MONTHLY_REDUCING = "monthly_reducing"


class InterestRateType(str, Enum):
    """Interest rate type"""
    FIXED = "fixed"
    FLOATING = "floating"
    HYBRID = "hybrid"


class RateRevisionFrequency(str, Enum):
    """Rate revision frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"
    AS_PER_RBI = "as_per_rbi"
    FIXED = "fixed"


class ChargeType(str, Enum):
    """Charge type"""
    FLAT = "flat"
    PERCENTAGE = "percentage"
    SLAB_BASED = "slab_based"


class EMIStartDateOption(str, Enum):
    """EMI start date options"""
    SAME_DAY = "same_day"
    NEXT_MONTH = "next_month"
    AFTER_GRACE_PERIOD = "after_grace_period"
    CUSTOM = "custom"


class EMIType(str, Enum):
    """EMI type"""
    STANDARD = "standard"
    STEP_UP = "step_up"
    STEP_DOWN = "step_down"
    BULLET = "bullet"
    BALLOON = "balloon"


# ==================== CONFIGURATION MODELS ====================

class RateCardEntry(BaseModel):
    """Rate card entry for segment/amount-wise rates"""
    entry_id: str
    segment_name: Optional[str] = None  # e.g., "Salaried", "Self-Employed"
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    tenure_min: Optional[int] = None  # months
    tenure_max: Optional[int] = None  # months
    credit_score_min: Optional[int] = None
    credit_score_max: Optional[int] = None
    interest_rate: float
    description: Optional[str] = None
    is_active: bool = True


class InterestConfig(BaseModel):
    """Interest configuration for product"""
    calculation_method: InterestCalculationMethod
    base_rate: float = Field(..., ge=0, le=100, description="Base interest rate %")
    min_rate: float = Field(..., ge=0, le=100, description="Minimum interest rate %")
    max_rate: float = Field(..., ge=0, le=100, description="Maximum interest rate %")
    rate_type: InterestRateType = InterestRateType.FIXED
    rate_revision_frequency: Optional[RateRevisionFrequency] = None
    rate_card: List[RateCardEntry] = Field(default_factory=list)
    benchmark_rate: Optional[str] = None  # e.g., "RBI Repo Rate"
    spread: Optional[float] = None  # Spread over benchmark
    compounding_frequency: Optional[str] = None  # daily, monthly, quarterly, yearly
    day_count_convention: str = "actual_365"  # actual/365, actual/360, 30/360
    interest_free_period_days: int = 0
    
    class Config:
        use_enum_values = True


class TenureConfig(BaseModel):
    """Tenure configuration for product"""
    min_tenure_months: int = Field(..., ge=0, description="Minimum tenure in months")
    max_tenure_months: int = Field(..., ge=0, description="Maximum tenure in months")
    allowed_tenures: List[int] = Field(default_factory=list, description="Specific allowed tenures")
    tenure_multiplier: int = 1  # tenure must be multiple of this (e.g., 6 for half-yearly)
    default_tenure_months: Optional[int] = None
    tenure_based_pricing: Dict[int, float] = Field(default_factory=dict)  # tenure -> rate adjustment
    lock_in_period_months: int = 0
    
    class Config:
        use_enum_values = True


class AmountConfig(BaseModel):
    """Amount configuration for product"""
    min_amount: float = Field(..., ge=0, description="Minimum loan/deposit amount")
    max_amount: float = Field(..., ge=0, description="Maximum loan/deposit amount")
    default_amount: Optional[float] = None
    amount_rounding: int = 1000  # round to nearest
    amount_multiples: Optional[int] = None  # amount must be multiple of this
    ticket_size_validation: bool = True
    ltv_ratio_max: Optional[float] = None  # Loan-to-Value ratio for secured loans
    income_multiplier_max: Optional[float] = None  # Max loan as multiple of income
    amount_slabs: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class FeeChargeConfig(BaseModel):
    """Individual fee/charge configuration"""
    charge_id: str
    charge_name: str
    charge_type: ChargeType
    flat_amount: Optional[float] = None
    percentage: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    slabs: List[Dict[str, Any]] = Field(default_factory=list)
    is_mandatory: bool = True
    is_refundable: bool = False
    gst_applicable: bool = True
    gst_percentage: float = 18.0
    collection_stage: str = "disbursal"  # disbursal, monthly, closure
    description: Optional[str] = None
    is_active: bool = True
    
    class Config:
        use_enum_values = True


class FeesConfig(BaseModel):
    """Fees and charges configuration"""
    processing_fee: Optional[FeeChargeConfig] = None
    documentation_charges: Optional[FeeChargeConfig] = None
    valuation_charges: Optional[FeeChargeConfig] = None
    legal_charges: Optional[FeeChargeConfig] = None
    stamp_duty: Optional[FeeChargeConfig] = None
    prepayment_charges: Optional[FeeChargeConfig] = None
    foreclosure_charges: Optional[FeeChargeConfig] = None
    part_payment_charges: Optional[FeeChargeConfig] = None
    penal_charges: Optional[FeeChargeConfig] = None
    bounce_charges: Optional[FeeChargeConfig] = None
    late_payment_charges: Optional[FeeChargeConfig] = None
    commitment_charges: Optional[FeeChargeConfig] = None
    switching_charges: Optional[FeeChargeConfig] = None
    custom_charges: List[FeeChargeConfig] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class EMIConfig(BaseModel):
    """EMI configuration for loan products"""
    emi_type: EMIType = EMIType.STANDARD
    calculation_formula: str = "standard"  # standard, custom
    rounding_rule: str = "round_up"  # round_up, round_down, round_nearest
    rounding_to: int = 1  # round to nearest
    start_date_option: EMIStartDateOption = EMIStartDateOption.NEXT_MONTH
    grace_period_months: int = 0
    moratorium_period_months: int = 0
    interest_during_moratorium: str = "capitalized"  # capitalized, paid_separately, waived
    
    # Bullet/Balloon payment
    bullet_payment_enabled: bool = False
    balloon_payment_enabled: bool = False
    balloon_percentage: Optional[float] = None  # % of principal
    
    # Step-up/Step-down
    step_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    step_increase_percentage: Optional[float] = None
    step_frequency_months: Optional[int] = None
    
    # Advanced options
    prepayment_allowed: bool = True
    prepayment_min_amount: Optional[float] = None
    part_payment_allowed: bool = True
    part_payment_min_amount: Optional[float] = None
    foreclosure_allowed: bool = True
    foreclosure_lock_in_months: int = 0
    
    # EMI due date
    emi_due_day: int = 5  # day of month
    allow_due_date_change: bool = False
    auto_debit_enabled: bool = True
    grace_days_for_payment: int = 3
    
    class Config:
        use_enum_values = True


class EligibilityCriteria(BaseModel):
    """Eligibility criteria for product"""
    min_age: int = 18
    max_age: int = 70
    min_income: Optional[float] = None
    employment_types: List[str] = Field(default_factory=list)  # salaried, self_employed, etc.
    min_credit_score: Optional[int] = None
    min_employment_months: Optional[int] = None
    min_business_vintage_months: Optional[int] = None
    residence_type: List[str] = Field(default_factory=list)  # owned, rented, etc.
    citizenship: List[str] = Field(default_factory=list)
    blacklist_check: bool = True
    cibil_check: bool = True
    


class DocumentRequirement(BaseModel):
    """Document requirements for product"""
    document_id: str
    document_name: str
    document_type: str  # identity, address, income, property, etc.
    is_mandatory: bool = True
    applicable_for: List[str] = Field(default_factory=list)  # salaried, self_employed, etc.
    description: Optional[str] = None
    verification_required: bool = True


# ==================== MAIN PRODUCT MODEL ====================

class Product(BaseModel):
    """Main product configuration model"""
    # Basic Information
    product_id: str
    product_code: str = Field(..., description="Unique product code")
    product_name: str
    product_category: ProductCategory
    product_description: Optional[str] = None
    product_status: ProductStatus = ProductStatus.DRAFT
    
    # Dates
    effective_date: date
    expiry_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    # Configuration sections
    interest_config: InterestConfig
    tenure_config: TenureConfig
    amount_config: AmountConfig
    fees_config: FeesConfig
    emi_config: Optional[EMIConfig] = None  # Only for loan products
    
    # Eligibility & Documents
    eligibility_criteria: EligibilityCriteria = Field(default_factory=EligibilityCriteria)
    document_requirements: List[DocumentRequirement] = Field(default_factory=list)
    
    # Additional settings
    target_segments: List[str] = Field(default_factory=list)
    sales_channels: List[str] = Field(default_factory=list)  # branch, online, dsa, etc.
    max_applications_per_customer: Optional[int] = None
    cooling_period_days: int = 0  # days between applications
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    terms_and_conditions: Optional[str] = None
    
    # System fields
    version: str = "1.0"
    is_featured: bool = False
    display_order: int = 0
    tenant_id: Optional[int] = None
    
    class Config:
        use_enum_values = True


class ProductSummary(BaseModel):
    """Product summary for list views"""
    product_id: str
    product_code: str
    product_name: str
    product_category: ProductCategory
    product_status: ProductStatus
    base_rate: float
    min_amount: float
    max_amount: float
    min_tenure_months: int
    max_tenure_months: int
    effective_date: date
    is_featured: bool
    created_at: datetime
    
    class Config:
        use_enum_values = True


class ProductClone(BaseModel):
    """Product clone request"""
    source_product_id: str
    new_product_code: str
    new_product_name: str
    modifications: Dict[str, Any] = Field(default_factory=dict)
    cloned_by: Optional[int] = None
    cloned_at: datetime = Field(default_factory=datetime.utcnow)


class ProductCalculation(BaseModel):
    """Product calculation request"""
    product_id: str
    principal_amount: float
    tenure_months: int
    interest_rate: Optional[float] = None  # If None, use product's base rate
    calculation_date: Optional[date] = None
    
    
class ProductCalculationResult(BaseModel):
    """Product calculation result"""
    product_id: str
    principal_amount: float
    tenure_months: int
    interest_rate: float
    emi_amount: float
    total_interest: float
    total_amount: float
    processing_fee: float
    total_charges: float
    net_disbursal_amount: float
    emi_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    calculation_date: datetime = Field(default_factory=datetime.utcnow)


# ==================== HELPER MODELS ====================

class ProductFilter(BaseModel):
    """Filter options for product listing"""
    category: Optional[ProductCategory] = None
    status: Optional[ProductStatus] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    target_segment: Optional[str] = None
    sales_channel: Optional[str] = None
    search_query: Optional[str] = None
    is_featured: Optional[bool] = None
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True
