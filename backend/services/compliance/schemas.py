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
