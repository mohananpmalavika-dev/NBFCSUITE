"""
Eligibility Rules Models
Defines data models for customer, financial, and geographic eligibility rules
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator


# ============================================================================
# ENUMERATIONS
# ============================================================================

class EmploymentType(str, Enum):
    """Employment types"""
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    BUSINESS = "BUSINESS"
    PROFESSIONAL = "PROFESSIONAL"
    PENSIONER = "PENSIONER"
    UNEMPLOYED = "UNEMPLOYED"


class ResidencyStatus(str, Enum):
    """Residency status"""
    RESIDENT = "RESIDENT"
    NRI = "NRI"
    PIO = "PIO"  # Person of Indian Origin
    FOREIGN_NATIONAL = "FOREIGN_NATIONAL"


class IncomeVerificationMethod(str, Enum):
    """Income verification methods"""
    SALARY_SLIP = "SALARY_SLIP"
    BANK_STATEMENT = "BANK_STATEMENT"
    ITR = "ITR"  # Income Tax Return
    FORM_16 = "FORM_16"
    FINANCIALS = "FINANCIALS"  # For businesses
    GST_RETURNS = "GST_RETURNS"
    DECLARATION = "DECLARATION"


class RuleStatus(str, Enum):
    """Eligibility rule status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class EligibilityResult(str, Enum):
    """Eligibility check result"""
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    CONDITIONAL = "CONDITIONAL"  # Eligible with conditions
    MANUAL_REVIEW = "MANUAL_REVIEW"


# ============================================================================
# CUSTOMER ELIGIBILITY CONFIGURATION
# ============================================================================

class AgeCriteria(BaseModel):
    """Age criteria configuration"""
    min_age: int = Field(ge=18, le=100, description="Minimum age")
    max_age: int = Field(ge=18, le=100, description="Maximum age")
    
    @validator('max_age')
    def validate_age_range(cls, v, values):
        if 'min_age' in values and v < values['min_age']:
            raise ValueError('max_age must be greater than or equal to min_age')
        return v


class IncomeCriteria(BaseModel):
    """Income criteria configuration"""
    min_monthly_income: Optional[float] = Field(None, ge=0)
    min_annual_income: Optional[float] = Field(None, ge=0)
    verification_methods: List[IncomeVerificationMethod] = []
    require_proof: bool = True


class CreditScoreCriteria(BaseModel):
    """Credit score criteria"""
    min_credit_score: Optional[int] = Field(None, ge=300, le=900)
    bureau_name: Optional[str] = None  # CIBIL, Experian, Equifax, CRIF
    mandatory: bool = True
    allow_no_history: bool = False  # Allow customers with no credit history


class CoApplicantRules(BaseModel):
    """Co-applicant requirements"""
    required: bool = False
    min_count: int = Field(0, ge=0)
    max_count: int = Field(0, ge=0)
    relationship_types: List[str] = []  # Spouse, Parent, Sibling, etc.
    min_income: Optional[float] = None
    min_credit_score: Optional[int] = None


class GuarantorRules(BaseModel):
    """Guarantor requirements"""
    required: bool = False
    min_count: int = Field(0, ge=0)
    max_count: int = Field(0, ge=0)
    min_net_worth: Optional[float] = None
    min_income: Optional[float] = None
    relationship_allowed: List[str] = []


class CustomerEligibility(BaseModel):
    """Customer eligibility criteria"""
    age_criteria: AgeCriteria
    income_criteria: IncomeCriteria
    employment_types: List[EmploymentType] = []
    credit_score_criteria: Optional[CreditScoreCriteria] = None
    
    # Customer status
    existing_customer_required: bool = False
    negative_areas_check: bool = True  # Check negative areas list
    
    # Nationality and residency
    allowed_nationalities: List[str] = ["IN"]  # ISO country codes
    allowed_residency_status: List[ResidencyStatus] = [ResidencyStatus.RESIDENT]
    
    # Co-applicant and guarantor
    co_applicant_rules: Optional[CoApplicantRules] = None
    guarantor_rules: Optional[GuarantorRules] = None
    
    # Additional checks
    dedup_check: bool = True  # Check for duplicate applications
    blacklist_check: bool = True
    politically_exposed_person_check: bool = True


# ============================================================================
# FINANCIAL ELIGIBILITY CONFIGURATION
# ============================================================================

class FOIRCriteria(BaseModel):
    """Fixed Obligation to Income Ratio criteria"""
    max_foir_percentage: float = Field(ge=0, le=100, description="Maximum FOIR %")
    include_proposed_emi: bool = True
    calculation_method: str = "MONTHLY"  # MONTHLY, ANNUAL


class DTICriteria(BaseModel):
    """Debt-to-Income ratio criteria"""
    max_dti_percentage: float = Field(ge=0, le=100, description="Maximum DTI %")
    include_all_obligations: bool = True
    calculation_method: str = "ANNUAL"


class ExistingObligations(BaseModel):
    """Existing obligations criteria"""
    max_existing_loans: Optional[int] = None
    max_existing_emi: Optional[float] = None
    check_credit_card_dues: bool = True
    check_existing_nbfc_loans: bool = True


class BankingTurnoverCriteria(BaseModel):
    """Banking turnover requirements"""
    required: bool = False
    min_monthly_turnover: Optional[float] = None
    min_average_balance: Optional[float] = None
    months_to_consider: int = Field(6, ge=1, le=24)
    banking_relationship_months: Optional[int] = None


class ITRCriteria(BaseModel):
    """Income Tax Return requirements"""
    required: bool = False
    min_years: int = Field(2, ge=1, le=5)
    min_annual_income: Optional[float] = None
    must_be_filed: bool = True
    accept_provisional: bool = False


class FinancialEligibility(BaseModel):
    """Financial eligibility criteria"""
    foir_criteria: Optional[FOIRCriteria] = None
    dti_criteria: Optional[DTICriteria] = None
    existing_obligations: Optional[ExistingObligations] = None
    banking_turnover: Optional[BankingTurnoverCriteria] = None
    itr_criteria: Optional[ITRCriteria] = None
    
    # Additional financial checks
    min_net_worth: Optional[float] = None
    min_liquid_assets: Optional[float] = None
    debt_free_required: bool = False


# ============================================================================
# GEOGRAPHIC ELIGIBILITY CONFIGURATION
# ============================================================================

class PinCodeRestriction(BaseModel):
    """PIN code restrictions"""
    type: str = Field(description="INCLUDE or EXCLUDE")
    pin_codes: List[str] = []
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['INCLUDE', 'EXCLUDE']:
            raise ValueError('type must be INCLUDE or EXCLUDE')
        return v


class StateRestriction(BaseModel):
    """State restrictions"""
    type: str = Field(description="INCLUDE or EXCLUDE")
    states: List[str] = []  # State codes
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['INCLUDE', 'EXCLUDE']:
            raise ValueError('type must be INCLUDE or EXCLUDE')
        return v


class CityRestriction(BaseModel):
    """City restrictions"""
    type: str = Field(description="INCLUDE or EXCLUDE")
    cities: List[str] = []
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['INCLUDE', 'EXCLUDE']:
            raise ValueError('type must be INCLUDE or EXCLUDE')
        return v


class BranchAvailability(BaseModel):
    """Branch-wise product availability"""
    enabled: bool = False
    branch_codes: List[str] = []
    require_local_branch: bool = False
    max_distance_km: Optional[float] = None


class GeographicEligibility(BaseModel):
    """Geographic eligibility criteria"""
    pin_code_restriction: Optional[PinCodeRestriction] = None
    state_restriction: Optional[StateRestriction] = None
    city_restriction: Optional[CityRestriction] = None
    branch_availability: Optional[BranchAvailability] = None
    
    # Location-based checks
    serviceable_locations_only: bool = True
    check_negative_areas: bool = True
    allow_rural_areas: bool = True
    allow_semi_urban_areas: bool = True
    allow_urban_areas: bool = True
    allow_metro_areas: bool = True


# ============================================================================
# MAIN ELIGIBILITY RULE MODEL
# ============================================================================

class EligibilityRule(BaseModel):
    """Main eligibility rule model"""
    id: Optional[str] = None
    tenant_id: str
    
    # Basic information
    rule_code: str = Field(description="Unique rule code")
    rule_name: str
    description: str
    status: RuleStatus = RuleStatus.DRAFT
    
    # Product association
    product_id: Optional[str] = None
    product_code: Optional[str] = None
    apply_to_all_products: bool = False
    
    # Eligibility criteria
    customer_eligibility: CustomerEligibility
    financial_eligibility: FinancialEligibility
    geographic_eligibility: GeographicEligibility
    
    # Rule priority and conditions
    priority: int = Field(10, ge=1, le=100, description="Rule priority (1=highest)")
    effective_date: date
    expiry_date: Optional[date] = None
    
    # Override options
    allow_manual_override: bool = True
    override_approval_required: bool = True
    override_reason_mandatory: bool = True
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_code": "ELIG001",
                "rule_name": "Standard Personal Loan Eligibility",
                "description": "Eligibility criteria for standard personal loans",
                "status": "ACTIVE",
                "customer_eligibility": {
                    "age_criteria": {"min_age": 21, "max_age": 60},
                    "income_criteria": {"min_monthly_income": 25000},
                    "employment_types": ["SALARIED", "SELF_EMPLOYED"]
                }
            }
        }


# ============================================================================
# ELIGIBILITY CHECK MODELS
# ============================================================================

class CustomerData(BaseModel):
    """Customer data for eligibility check"""
    # Personal information
    date_of_birth: date
    nationality: str = "IN"
    residency_status: ResidencyStatus = ResidencyStatus.RESIDENT
    employment_type: EmploymentType
    
    # Income information
    monthly_income: Optional[float] = None
    annual_income: Optional[float] = None
    income_verification_method: Optional[IncomeVerificationMethod] = None
    
    # Credit information
    credit_score: Optional[int] = None
    credit_bureau: Optional[str] = None
    
    # Financial information
    existing_emi: Optional[float] = 0
    existing_loan_count: Optional[int] = 0
    monthly_obligations: Optional[float] = 0
    net_worth: Optional[float] = None
    liquid_assets: Optional[float] = None
    
    # Banking information
    average_banking_turnover: Optional[float] = None
    average_bank_balance: Optional[float] = None
    banking_months: Optional[int] = None
    
    # ITR information
    itr_filed_years: Optional[int] = None
    itr_annual_income: Optional[float] = None
    
    # Location information
    pin_code: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    branch_code: Optional[str] = None
    
    # Customer status
    is_existing_customer: bool = False
    is_blacklisted: bool = False
    is_pep: bool = False  # Politically Exposed Person
    
    # Co-applicant and guarantor
    has_co_applicant: bool = False
    co_applicant_count: int = 0
    co_applicant_income: Optional[float] = None
    has_guarantor: bool = False
    guarantor_count: int = 0
    guarantor_net_worth: Optional[float] = None


class EligibilityCheckRequest(BaseModel):
    """Request to check eligibility"""
    rule_id: Optional[str] = None
    rule_code: Optional[str] = None
    product_id: Optional[str] = None
    customer_data: CustomerData
    loan_amount: Optional[float] = None
    loan_tenure: Optional[int] = None
    proposed_emi: Optional[float] = None


class EligibilityCriteriaResult(BaseModel):
    """Individual criteria check result"""
    criteria_name: str
    passed: bool
    actual_value: Optional[Any] = None
    required_value: Optional[Any] = None
    message: str
    severity: str = "INFO"  # INFO, WARNING, ERROR


class EligibilityCheckResponse(BaseModel):
    """Response from eligibility check"""
    rule_id: str
    rule_code: str
    rule_name: str
    result: EligibilityResult
    overall_score: float = Field(ge=0, le=100, description="Eligibility score 0-100")
    
    # Detailed results by category
    customer_criteria_results: List[EligibilityCriteriaResult] = []
    financial_criteria_results: List[EligibilityCriteriaResult] = []
    geographic_criteria_results: List[EligibilityCriteriaResult] = []
    
    # Summary
    total_criteria_count: int
    passed_criteria_count: int
    failed_criteria_count: int
    warning_criteria_count: int
    
    # Recommendations
    recommendations: List[str] = []
    required_documents: List[str] = []
    
    # Override information
    can_override: bool
    override_approval_required: bool
    
    # Metadata
    checked_at: datetime
    checked_by: Optional[str] = None


# ============================================================================
# HELPER MODELS
# ============================================================================

class EligibilityRuleSummary(BaseModel):
    """Summary of eligibility rule"""
    id: str
    rule_code: str
    rule_name: str
    status: RuleStatus
    product_code: Optional[str] = None
    priority: int
    effective_date: date
    expiry_date: Optional[date] = None
    created_at: datetime


class EligibilityRuleFilter(BaseModel):
    """Filter for listing eligibility rules"""
    status: Optional[RuleStatus] = None
    product_id: Optional[str] = None
    product_code: Optional[str] = None
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None
    search_term: Optional[str] = None


class EligibilityStats(BaseModel):
    """Statistics for eligibility rules"""
    total_rules: int = 0
    active_rules: int = 0
    draft_rules: int = 0
    inactive_rules: int = 0
    archived_rules: int = 0
    rules_by_product: Dict[str, int] = {}
    total_checks_performed: int = 0
    eligible_count: int = 0
    not_eligible_count: int = 0
    conditional_count: int = 0


class EligibilityRuleClone(BaseModel):
    """Clone eligibility rule request"""
    new_rule_code: str
    new_rule_name: Optional[str] = None
    new_product_id: Optional[str] = None


class BulkEligibilityCheckRequest(BaseModel):
    """Bulk eligibility check request"""
    rule_id: str
    customer_data_list: List[CustomerData]
    loan_amount: Optional[float] = None
    loan_tenure: Optional[int] = None


class BulkEligibilityCheckResponse(BaseModel):
    """Bulk eligibility check response"""
    total_customers: int
    eligible_count: int
    not_eligible_count: int
    conditional_count: int
    manual_review_count: int
    results: List[EligibilityCheckResponse]
    summary: Dict[str, Any]
