"""
Compliance Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


# ============================================================================
# ENUMS (Mirror from models)
# ============================================================================

class BorrowerTypeEnum(str):
    INDIVIDUAL = "individual"
    SOLE_PROPRIETOR = "sole_proprietor"
    PARTNERSHIP = "partnership"
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    TRUST = "trust"
    SOCIETY = "society"
    GOVERNMENT = "government"
    HUF = "huf"


class SMAStatusEnum(str):
    STANDARD = "standard"
    SMA_0 = "sma_0"
    SMA_1 = "sma_1"
    SMA_2 = "sma_2"
    NPA_SUBSTANDARD = "npa_substandard"
    NPA_DOUBTFUL = "npa_doubtful"
    NPA_LOSS = "npa_loss"


class AssetClassificationEnum(str):
    STANDARD = "standard"
    SUB_STANDARD = "sub_standard"
    DOUBTFUL_1 = "doubtful_1"
    DOUBTFUL_2 = "doubtful_2"
    DOUBTFUL_3 = "doubtful_3"
    LOSS = "loss"


class FacilityTypeEnum(str):
    TERM_LOAN = "term_loan"
    CASH_CREDIT = "cash_credit"
    OVERDRAFT = "overdraft"
    WORKING_CAPITAL = "working_capital"
    BILL_DISCOUNTING = "bill_discounting"
    BANK_GUARANTEE = "bank_guarantee"
    LETTER_OF_CREDIT = "letter_of_credit"
    OTHER = "other"


# ============================================================================
# CRILC BORROWER SCHEMAS
# ============================================================================

class CRILCBorrowerCreate(BaseModel):
    borrower_name: str = Field(..., max_length=500)
    borrower_type: str
    pan_number: Optional[str] = Field(None, max_length=10)
    cin_number: Optional[str] = Field(None, max_length=21)
    gstin: Optional[str] = Field(None, max_length=15)
    registered_address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=200)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    industry_code: Optional[str] = Field(None, max_length=20)
    industry_name: Optional[str] = Field(None, max_length=200)
    nature_of_business: Optional[str] = Field(None, max_length=500)
    year_of_incorporation: Optional[int] = None
    annual_turnover: Optional[Decimal] = None
    net_worth: Optional[Decimal] = None
    financial_year: Optional[str] = Field(None, max_length=10)
    customer_id: Optional[UUID] = None
    is_part_of_group: bool = False
    group_name: Optional[str] = Field(None, max_length=300)
    internal_rating: Optional[str] = Field(None, max_length=20)
    external_rating: Optional[str] = Field(None, max_length=20)
    rating_agency: Optional[str] = Field(None, max_length=100)
    rating_date: Optional[date] = None


class CRILCBorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = Field(None, max_length=500)
    registered_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    annual_turnover: Optional[Decimal] = None
    net_worth: Optional[Decimal] = None
    financial_year: Optional[str] = None
    is_part_of_group: Optional[bool] = None
    group_name: Optional[str] = None
    internal_rating: Optional[str] = None
    external_rating: Optional[str] = None
    rating_agency: Optional[str] = None
    rating_date: Optional[date] = None


class CRILCBorrowerResponse(BaseModel):
    id: UUID
    tenant_id: str
    borrower_code: str
    borrower_name: str
    borrower_type: str
    pan_number: Optional[str]
    cin_number: Optional[str]
    gstin: Optional[str]
    city: Optional[str]
    state: Optional[str]
    industry_name: Optional[str]
    total_credit_exposure: Decimal
    funded_exposure: Optional[Decimal]
    non_funded_exposure: Optional[Decimal]
    is_large_credit: bool
    large_credit_since: Optional[date]
    current_sma_status: str
    current_asset_classification: str
    days_past_due: int
    is_active: bool
    last_reported_quarter: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CRILC FACILITY SCHEMAS
# ============================================================================

class CRILCFacilityCreate(BaseModel):
    borrower_id: UUID
    loan_account_id: Optional[UUID] = None
    facility_type: str
    exposure_type: str
    sanctioned_amount: Decimal = Field(..., gt=0)
    outstanding_amount: Decimal = Field(..., ge=0)
    overdue_amount: Decimal = Field(default=0, ge=0)
    sanction_date: date
    disbursement_date: Optional[date] = None
    maturity_date: Optional[date] = None
    security_type: Optional[str] = Field(None, max_length=100)
    security_value: Optional[Decimal] = None
    collateral_details: Optional[Dict[str, Any]] = None
    interest_rate: Optional[Decimal] = None


class CRILCFacilityUpdate(BaseModel):
    outstanding_amount: Optional[Decimal] = None
    overdue_amount: Optional[Decimal] = None
    days_past_due: Optional[int] = None
    asset_classification: Optional[str] = None
    interest_overdue: Optional[Decimal] = None
    is_active: Optional[bool] = None
    closure_date: Optional[date] = None


class CRILCFacilityResponse(BaseModel):
    id: UUID
    tenant_id: str
    borrower_id: UUID
    loan_account_id: Optional[UUID]
    facility_id: str
    facility_type: str
    exposure_type: str
    sanctioned_amount: Decimal
    outstanding_amount: Decimal
    overdue_amount: Decimal
    sanction_date: date
    maturity_date: Optional[date]
    days_past_due: int
    asset_classification: str
    interest_rate: Optional[Decimal]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SMA TRACKING SCHEMAS
# ============================================================================

class SMATrackingCreate(BaseModel):
    borrower_id: UUID
    loan_account_id: UUID
    as_on_date: date
    reporting_quarter: Optional[str] = Field(None, max_length=10)
    current_sma_status: str
    days_past_due: int = Field(default=0, ge=0)
    principal_outstanding: Decimal = Field(..., ge=0)
    interest_outstanding: Decimal = Field(default=0, ge=0)
    total_outstanding: Decimal = Field(..., ge=0)
    principal_overdue: Decimal = Field(default=0, ge=0)
    interest_overdue: Decimal = Field(default=0, ge=0)
    total_overdue: Decimal = Field(default=0, ge=0)
    installment_amount: Optional[Decimal] = None
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[Decimal] = None
    next_due_date: Optional[date] = None
    asset_classification: str = "standard"
    provision_required: Decimal = Field(default=0, ge=0)
    provision_percentage: Decimal = Field(default=0, ge=0, le=100)


class SMATrackingResponse(BaseModel):
    id: UUID
    tenant_id: str
    borrower_id: UUID
    loan_account_id: UUID
    as_on_date: date
    reporting_quarter: Optional[str]
    current_sma_status: str
    previous_sma_status: Optional[str]
    status_change_date: Optional[date]
    days_past_due: int
    days_in_current_status: int
    principal_outstanding: Decimal
    interest_outstanding: Decimal
    total_outstanding: Decimal
    principal_overdue: Decimal
    interest_overdue: Decimal
    total_overdue: Decimal
    asset_classification: str
    provision_required: Decimal
    alert_triggered: bool
    follow_up_required: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SMAStatusHistoryResponse(BaseModel):
    id: UUID
    tenant_id: str
    borrower_id: UUID
    loan_account_id: UUID
    from_status: str
    to_status: str
    change_date: date
    dpd_at_change: Optional[int]
    outstanding_at_change: Optional[Decimal]
    overdue_at_change: Optional[Decimal]
    change_reason: Optional[str]
    triggered_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# QUARTERLY RETURN SCHEMAS
# ============================================================================

class CRILCQuarterlyReturnCreate(BaseModel):
    reporting_quarter: str = Field(..., max_length=10)  # Q1FY24
    reporting_year: str = Field(..., max_length=10)  # FY2023-24
    as_on_date: date
    remarks: Optional[str] = None


class CRILCQuarterlyReturnResponse(BaseModel):
    id: UUID
    tenant_id: str
    return_number: str
    reporting_quarter: str
    reporting_year: str
    as_on_date: date
    status: str
    total_large_borrowers: int
    total_funded_exposure: Decimal
    total_non_funded_exposure: Decimal
    total_exposure: Decimal
    sma_0_count: int
    sma_0_amount: Decimal
    sma_1_count: int
    sma_1_amount: Decimal
    sma_2_count: int
    sma_2_amount: Decimal
    npa_count: int
    npa_amount: Decimal
    report_file_path: Optional[str]
    report_file_url: Optional[str]
    prepared_date: Optional[datetime]
    approved_date: Optional[datetime]
    submitted_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SMAQuarterlyReportCreate(BaseModel):
    reporting_quarter: str = Field(..., max_length=10)
    reporting_year: str = Field(..., max_length=10)
    as_on_date: date
    remarks: Optional[str] = None


class SMAQuarterlyReportResponse(BaseModel):
    id: UUID
    tenant_id: str
    report_number: str
    reporting_quarter: str
    reporting_year: str
    as_on_date: date
    status: str
    sma_0_accounts: int
    sma_0_amount: Decimal
    sma_1_accounts: int
    sma_1_amount: Decimal
    sma_2_accounts: int
    sma_2_amount: Decimal
    report_file_path: Optional[str]
    prepared_date: Optional[datetime]
    approved_date: Optional[datetime]
    submitted_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMPLIANCE ALERT SCHEMAS
# ============================================================================

class ComplianceAlertCreate(BaseModel):
    alert_type: str = Field(..., max_length=50)
    alert_category: str = Field(..., max_length=50)
    severity: str = Field(default="medium", max_length=20)
    borrower_id: Optional[UUID] = None
    loan_account_id: Optional[UUID] = None
    alert_message: str
    alert_details: Optional[Dict[str, Any]] = None
    due_date: Optional[date] = None


class ComplianceAlertResponse(BaseModel):
    id: UUID
    tenant_id: str
    alert_type: str
    alert_category: str
    severity: str
    borrower_id: Optional[UUID]
    loan_account_id: Optional[UUID]
    alert_message: str
    alert_details: Optional[Dict[str, Any]]
    status: str
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    due_date: Optional[date]
    is_overdue: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# FILTER & QUERY SCHEMAS
# ============================================================================

class LargeCreditFilter(BaseModel):
    sma_status: Optional[str] = None
    asset_classification: Optional[str] = None
    min_exposure: Optional[Decimal] = None
    max_exposure: Optional[Decimal] = None
    industry_code: Optional[str] = None
    state: Optional[str] = None
    is_active: Optional[bool] = True
    reporting_quarter: Optional[str] = None


class SMADashboardStats(BaseModel):
    total_accounts: int
    standard_count: int
    standard_amount: Decimal


# ============================================================================
# RBI RETURNS AUTOMATION SCHEMAS
# ============================================================================

# ============================================================================
# RBI RETURN MASTER SCHEMAS
# ============================================================================

class RBIReturnMasterCreate(BaseModel):
    return_code: str = Field(..., max_length=50)
    return_name: str = Field(..., max_length=300)
    return_type: str
    description: Optional[str] = None
    applicable_to: Optional[List[str]] = None
    is_mandatory: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    frequency: str
    due_day_of_month: Optional[int] = None
    due_days_after_period: Optional[int] = None
    grace_period_days: int = 0
    file_formats: Optional[List[str]] = None
    has_xbrl: bool = False
    xbrl_taxonomy: Optional[str] = None
    submission_portal: Optional[str] = None
    submission_method: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None


class RBIReturnMasterUpdate(BaseModel):
    return_name: Optional[str] = None
    description: Optional[str] = None
    applicable_to: Optional[List[str]] = None
    is_mandatory: Optional[bool] = None
    effective_to: Optional[date] = None
    frequency: Optional[str] = None
    due_day_of_month: Optional[int] = None
    due_days_after_period: Optional[int] = None
    grace_period_days: Optional[int] = None
    file_formats: Optional[List[str]] = None
    has_xbrl: Optional[bool] = None
    submission_portal: Optional[str] = None
    submission_method: Optional[str] = None
    is_active: Optional[bool] = None


class RBIReturnMasterResponse(BaseModel):
    id: UUID
    tenant_id: str
    return_code: str
    return_name: str
    return_type: str
    description: Optional[str]
    applicable_to: Optional[List[str]]
    is_mandatory: bool
    effective_from: Optional[date]
    effective_to: Optional[date]
    frequency: str
    due_day_of_month: Optional[int]
    due_days_after_period: Optional[int]
    grace_period_days: int
    file_formats: Optional[List[str]]
    has_xbrl: bool
    xbrl_taxonomy: Optional[str]
    submission_portal: Optional[str]
    submission_method: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# NBS-7 RETURN SCHEMAS
# ============================================================================

class NBS7ReturnCreate(BaseModel):
    return_master_id: Optional[UUID] = None
    reporting_period: str = Field(..., max_length=20)
    period_start_date: date
    period_end_date: date
    as_on_date: date
    financial_year: str = Field(..., max_length=10)
    quarter: Optional[str] = Field(None, max_length=5)
    
    # Asset Side Data
    term_loans: Decimal = Field(default=0, ge=0)
    hire_purchase: Decimal = Field(default=0, ge=0)
    leasing: Decimal = Field(default=0, ge=0)
    bills_discounted: Decimal = Field(default=0, ge=0)
    other_loans: Decimal = Field(default=0, ge=0)
    
    provision_standard_assets: Decimal = Field(default=0, ge=0)
    provision_npa: Decimal = Field(default=0, ge=0)
    
    government_securities: Decimal = Field(default=0, ge=0)
    corporate_bonds: Decimal = Field(default=0, ge=0)
    mutual_funds: Decimal = Field(default=0, ge=0)
    shares_equity: Decimal = Field(default=0, ge=0)
    other_investments: Decimal = Field(default=0, ge=0)
    
    fixed_assets_gross: Decimal = Field(default=0, ge=0)
    accumulated_depreciation: Decimal = Field(default=0, ge=0)
    
    cash_bank_balances: Decimal = Field(default=0, ge=0)
    other_assets: Decimal = Field(default=0, ge=0)
    
    # Liability Side Data
    share_capital: Decimal = Field(default=0, ge=0)
    reserves_surplus: Decimal = Field(default=0)
    
    bank_borrowings: Decimal = Field(default=0, ge=0)
    debentures: Decimal = Field(default=0, ge=0)
    commercial_paper: Decimal = Field(default=0, ge=0)
    subordinated_debt: Decimal = Field(default=0, ge=0)
    other_borrowings: Decimal = Field(default=0, ge=0)
    
    public_deposits: Decimal = Field(default=0, ge=0)
    
    other_liabilities: Decimal = Field(default=0, ge=0)
    provisions_liabilities: Decimal = Field(default=0, ge=0)
    
    # Income Statement Data
    interest_income: Decimal = Field(default=0, ge=0)
    other_income: Decimal = Field(default=0, ge=0)
    
    interest_expenditure: Decimal = Field(default=0, ge=0)
    operating_expenses: Decimal = Field(default=0, ge=0)
    provisions_write_offs: Decimal = Field(default=0, ge=0)
    
    tax_provision: Decimal = Field(default=0, ge=0)
    
    # NPA & Prudential Data
    gross_npa: Decimal = Field(default=0, ge=0)
    net_npa: Decimal = Field(default=0, ge=0)
    
    tier1_capital: Decimal = Field(default=0, ge=0)
    tier2_capital: Decimal = Field(default=0, ge=0)
    risk_weighted_assets: Decimal = Field(default=0, ge=0)
    
    sectoral_deployment: Optional[Dict[str, Any]] = None
    geographic_distribution: Optional[Dict[str, Any]] = None
    detailed_data: Optional[Dict[str, Any]] = None
    
    remarks: Optional[str] = None
    internal_notes: Optional[str] = None


class NBS7ReturnUpdate(BaseModel):
    term_loans: Optional[Decimal] = None
    hire_purchase: Optional[Decimal] = None
    leasing: Optional[Decimal] = None
    bills_discounted: Optional[Decimal] = None
    other_loans: Optional[Decimal] = None
    
    provision_standard_assets: Optional[Decimal] = None
    provision_npa: Optional[Decimal] = None
    
    government_securities: Optional[Decimal] = None
    corporate_bonds: Optional[Decimal] = None
    mutual_funds: Optional[Decimal] = None
    shares_equity: Optional[Decimal] = None
    other_investments: Optional[Decimal] = None
    
    fixed_assets_gross: Optional[Decimal] = None
    accumulated_depreciation: Optional[Decimal] = None
    
    cash_bank_balances: Optional[Decimal] = None
    other_assets: Optional[Decimal] = None
    
    share_capital: Optional[Decimal] = None
    reserves_surplus: Optional[Decimal] = None
    
    bank_borrowings: Optional[Decimal] = None
    debentures: Optional[Decimal] = None
    commercial_paper: Optional[Decimal] = None
    subordinated_debt: Optional[Decimal] = None
    other_borrowings: Optional[Decimal] = None
    
    public_deposits: Optional[Decimal] = None
    
    other_liabilities: Optional[Decimal] = None
    provisions_liabilities: Optional[Decimal] = None
    
    interest_income: Optional[Decimal] = None
    other_income: Optional[Decimal] = None
    
    interest_expenditure: Optional[Decimal] = None
    operating_expenses: Optional[Decimal] = None
    provisions_write_offs: Optional[Decimal] = None
    
    tax_provision: Optional[Decimal] = None
    
    gross_npa: Optional[Decimal] = None
    net_npa: Optional[Decimal] = None
    
    tier1_capital: Optional[Decimal] = None
    tier2_capital: Optional[Decimal] = None
    risk_weighted_assets: Optional[Decimal] = None
    
    sectoral_deployment: Optional[Dict[str, Any]] = None
    geographic_distribution: Optional[Dict[str, Any]] = None
    detailed_data: Optional[Dict[str, Any]] = None
    
    remarks: Optional[str] = None
    internal_notes: Optional[str] = None


class NBS7ReturnResponse(BaseModel):
    id: UUID
    tenant_id: str
    return_number: str
    return_master_id: Optional[UUID]
    reporting_period: str
    period_start_date: date
    period_end_date: date
    as_on_date: date
    financial_year: str
    quarter: Optional[str]
    status: str
    
    # Calculated Totals
    total_loans: Decimal
    total_provisions: Decimal
    net_loans_advances: Decimal
    total_investments: Decimal
    fixed_assets_net: Decimal
    total_assets: Decimal
    
    total_capital_reserves: Decimal
    total_borrowings: Decimal
    public_deposits: Decimal
    total_liabilities: Decimal
    
    total_income: Decimal
    total_expenditure: Decimal
    profit_before_tax: Decimal
    profit_after_tax: Decimal
    
    gross_npa: Decimal
    net_npa: Decimal
    npa_ratio: Decimal
    
    crar_percentage: Decimal
    tier1_capital: Decimal
    tier2_capital: Decimal
    total_capital: Decimal
    risk_weighted_assets: Decimal
    
    excel_file_url: Optional[str]
    pdf_file_url: Optional[str]
    
    prepared_date: Optional[datetime]
    reviewed_date: Optional[datetime]
    approved_date: Optional[datetime]
    submitted_date: Optional[datetime]
    
    due_date: date
    is_overdue: bool
    days_overdue: int
    
    submission_reference: Optional[str]
    acknowledgement_number: Optional[str]
    
    remarks: Optional[str]
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NBS7ReturnGenerateRequest(BaseModel):
    """Auto-generate NBS-7 return from system data"""
    reporting_period: str = Field(..., max_length=20)
    period_start_date: date
    period_end_date: date
    as_on_date: date
    financial_year: str = Field(..., max_length=10)
    quarter: Optional[str] = Field(None, max_length=5)
    include_sectoral: bool = True
    include_geographic: bool = True
    remarks: Optional[str] = None


# ============================================================================
# STATUTORY RETURN SCHEMAS
# ============================================================================

class StatutoryReturnCreate(BaseModel):
    return_master_id: UUID
    return_type: str
    reporting_period: str = Field(..., max_length=20)
    period_start_date: date
    period_end_date: date
    as_on_date: date
    financial_year: str = Field(..., max_length=10)
    return_data: Dict[str, Any]
    schedules: Optional[Dict[str, Any]] = None
    summary_data: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    internal_notes: Optional[str] = None


class StatutoryReturnUpdate(BaseModel):
    return_data: Optional[Dict[str, Any]] = None
    schedules: Optional[Dict[str, Any]] = None
    summary_data: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    internal_notes: Optional[str] = None


class StatutoryReturnResponse(BaseModel):
    id: UUID
    tenant_id: str
    return_number: str
    return_master_id: UUID
    return_type: str
    reporting_period: str
    period_start_date: date
    period_end_date: date
    as_on_date: date
    financial_year: str
    status: str
    
    return_data: Dict[str, Any]
    schedules: Optional[Dict[str, Any]]
    summary_data: Optional[Dict[str, Any]]
    
    validation_status: str
    validation_errors: Optional[List[Dict[str, Any]]]
    validation_warnings: Optional[List[Dict[str, Any]]]
    
    excel_file_url: Optional[str]
    pdf_file_url: Optional[str]
    
    prepared_date: Optional[datetime]
    reviewed_date: Optional[datetime]
    approved_date: Optional[datetime]
    submitted_date: Optional[datetime]
    
    due_date: date
    is_overdue: bool
    days_overdue: int
    
    submission_reference: Optional[str]
    acknowledgement_number: Optional[str]
    
    revision_number: int
    parent_return_id: Optional[UUID]
    
    remarks: Optional[str]
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# XBRL DOCUMENT SCHEMAS
# ============================================================================

class XBRLDocumentCreate(BaseModel):
    document_name: str = Field(..., max_length=300)
    return_type: str
    nbs7_return_id: Optional[UUID] = None
    statutory_return_id: Optional[UUID] = None
    taxonomy_version: str
    taxonomy_url: Optional[str] = None
    schema_version: Optional[str] = None
    reporting_period: str = Field(..., max_length=20)
    period_start_date: date
    period_end_date: date
    entity_identifier: Optional[str] = None
    entity_name: Optional[str] = None
    remarks: Optional[str] = None


class XBRLDocumentResponse(BaseModel):
    id: UUID
    tenant_id: str
    document_number: str
    document_name: str
    return_type: str
    nbs7_return_id: Optional[UUID]
    statutory_return_id: Optional[UUID]
    taxonomy_version: str
    taxonomy_url: Optional[str]
    schema_version: Optional[str]
    reporting_period: str
    period_start_date: date
    period_end_date: date
    is_valid: bool
    validation_errors: Optional[List[Dict[str, Any]]]
    validation_date: Optional[datetime]
    xbrl_file_url: Optional[str]
    xbrl_file_size: Optional[int]
    entity_identifier: Optional[str]
    entity_name: Optional[str]
    status: str
    generated_date: Optional[datetime]
    submitted_date: Optional[datetime]
    submission_reference: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class XBRLGenerateRequest(BaseModel):
    """Generate XBRL from return data"""
    return_type: str
    return_id: UUID  # Either NBS7 or Statutory Return ID
    taxonomy_version: str
    entity_identifier: str = Field(..., max_length=100)
    entity_name: str = Field(..., max_length=300)
    include_validation: bool = True


class XBRLValidationResponse(BaseModel):
    is_valid: bool
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    validation_date: datetime


# ============================================================================
# COMPLIANCE CALENDAR SCHEMAS
# ============================================================================

class ComplianceCalendarCreate(BaseModel):
    event_code: Optional[str] = Field(None, max_length=50)
    event_title: str = Field(..., max_length=300)
    event_type: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    event_date: date
    event_time: Optional[str] = None
    due_date: Optional[date] = None
    priority: str = "medium"
    category: Optional[str] = Field(None, max_length=100)
    return_master_id: Optional[UUID] = None
    nbs7_return_id: Optional[UUID] = None
    statutory_return_id: Optional[UUID] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    recurrence_day: Optional[int] = None
    assigned_to: Optional[UUID] = None
    reminder_enabled: bool = True
    reminder_days_before: Optional[List[int]] = Field(default=[30, 15, 7, 3, 1])
    notes: Optional[str] = None


class ComplianceCalendarUpdate(BaseModel):
    event_title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    reminder_enabled: Optional[bool] = None
    reminder_days_before: Optional[List[int]] = None
    notes: Optional[str] = None
    internal_comments: Optional[str] = None


class ComplianceCalendarResponse(BaseModel):
    id: UUID
    tenant_id: str
    event_code: Optional[str]
    event_title: str
    event_type: str
    description: Optional[str]
    requirements: Optional[str]
    event_date: date
    event_time: Optional[str]
    due_date: Optional[date]
    priority: str
    category: Optional[str]
    return_master_id: Optional[UUID]
    nbs7_return_id: Optional[UUID]
    statutory_return_id: Optional[UUID]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_day: Optional[int]
    status: str
    completion_date: Optional[datetime]
    completed_by: Optional[UUID]
    assigned_to: Optional[UUID]
    assigned_by: Optional[UUID]
    assigned_date: Optional[datetime]
    reminder_enabled: bool
    reminder_days_before: Optional[List[int]]
    last_reminder_sent: Optional[datetime]
    notification_sent: bool
    notification_date: Optional[datetime]
    attachments: Optional[List[str]]
    notes: Optional[str]
    internal_comments: Optional[str]
    start_date: Optional[datetime]
    estimated_effort_hours: Optional[Decimal]
    actual_effort_hours: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceCalendarCompleteRequest(BaseModel):
    completion_notes: Optional[str] = None
    actual_effort_hours: Optional[Decimal] = None


# ============================================================================
# DASHBOARD & ANALYTICS SCHEMAS
# ============================================================================

class RBIReturnsDashboardStats(BaseModel):
    total_returns_due: int
    overdue_returns: int
    submitted_this_month: int
    pending_approval: int
    draft_returns: int
    
    nbs7_monthly_status: Dict[str, int]
    nbs7_quarterly_status: Dict[str, int]
    statutory_returns_status: Dict[str, int]
    
    upcoming_deadlines: List[Dict[str, Any]]
    recent_submissions: List[Dict[str, Any]]
    
    compliance_score: float
    on_time_submission_rate: float


class ComplianceCalendarSummary(BaseModel):
    total_events: int
    upcoming_events: int
    overdue_events: int
    completed_events: int
    events_this_month: int
    events_this_quarter: int
    
    by_priority: Dict[str, int]
    by_category: Dict[str, int]
    by_status: Dict[str, int]
    
    upcoming_critical: List[ComplianceCalendarResponse]


class ReturnSubmissionHistoryResponse(BaseModel):
    id: UUID
    tenant_id: str
    return_type: str
    nbs7_return_id: Optional[UUID]
    statutory_return_id: Optional[UUID]
    xbrl_document_id: Optional[UUID]
    action: str
    previous_status: Optional[str]
    new_status: Optional[str]
    action_by: UUID
    action_date: datetime
    action_details: Optional[Dict[str, Any]]
    comments: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# FILTER & QUERY SCHEMAS
# ============================================================================

class RBIReturnsFilter(BaseModel):
    return_type: Optional[str] = None
    financial_year: Optional[str] = None
    quarter: Optional[str] = None
    status: Optional[str] = None
    is_overdue: Optional[bool] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class ComplianceCalendarFilter(BaseModel):
    event_type: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    is_overdue: Optional[bool] = None
    sma_0_count: int
    sma_0_amount: Decimal
    sma_1_count: int
    sma_1_amount: Decimal
    sma_2_count: int
    sma_2_amount: Decimal
    npa_count: int
    npa_amount: Decimal
    total_exposure: Decimal
    provision_required: Decimal
    alerts_open: int


class LargeCreditIdentificationRequest(BaseModel):
    threshold_amount: Decimal = Field(default=50000000, description="₹5 Crore default")
    as_on_date: date
    include_group_exposure: bool = True


class SMACalculationRequest(BaseModel):
    as_on_date: date
    loan_account_ids: Optional[List[UUID]] = None
    calculate_provisions: bool = True


class QuarterlyReturnGenerateRequest(BaseModel):
    reporting_quarter: str = Field(..., description="Format: Q1FY24")
    as_on_date: date
    auto_submit: bool = False
