"""
NPA Management Schemas
Pydantic models for NPA classification, provisioning, and reporting
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from backend.services.accounting.npa_service import NPACategory


# ============================================================================
# NPA Classification Schemas
# ============================================================================

class NPAClassificationRequest(BaseModel):
    """Request for classifying a loan"""
    days_past_due: int = Field(..., ge=0, description="Days past due")
    is_restructured: bool = Field(False, description="Is loan restructured")
    is_written_off: bool = Field(False, description="Is loan written off")


class NPAClassificationResponse(BaseModel):
    """Response with NPA classification"""
    npa_category: NPACategory
    days_past_due: int
    is_npa: bool
    is_sma: bool
    classification_date: date


class LoanClassificationResponse(BaseModel):
    """Loan classification details"""
    loan_account_id: int
    customer_id: Optional[int]
    loan_account_number: Optional[str]
    outstanding_principal: Decimal
    days_past_due: int
    npa_category: NPACategory
    is_secured: bool
    security_value: Optional[Decimal]
    security_coverage_ratio: Optional[Decimal]
    provisioning_rate: Decimal
    required_provision: Decimal
    existing_provision: Decimal
    additional_provision: Decimal
    classification_date: date


# ============================================================================
# Provisioning Schemas
# ============================================================================

class ProvisioningCalculationRequest(BaseModel):
    """Request for calculating provisioning"""
    outstanding_principal: Decimal = Field(..., gt=0)
    npa_category: NPACategory
    is_secured: bool = Field(True)
    security_coverage_ratio: Decimal = Field(Decimal("100.00"), ge=0, le=100)
    existing_provision: Decimal = Field(Decimal("0.00"), ge=0)


class ProvisioningCalculationResponse(BaseModel):
    """Response with provisioning calculation"""
    outstanding_principal: Decimal
    provisioning_rate: Decimal
    required_provision: Decimal
    existing_provision: Decimal
    additional_provision: Decimal
    npa_category: NPACategory


class CreateProvisionRequest(BaseModel):
    """Request to create provisioning entry"""
    loan_account_id: int
    provision_amount: Decimal = Field(..., gt=0)
    npa_category: NPACategory
    as_of_date: date
    narration: Optional[str] = None


class ReverseProvisionRequest(BaseModel):
    """Request to reverse provisioning"""
    loan_account_id: int
    provision_amount: Decimal = Field(..., gt=0)
    as_of_date: date
    narration: Optional[str] = None


class WriteOffRequest(BaseModel):
    """Request to write off loan"""
    loan_account_id: int
    write_off_amount: Decimal = Field(..., gt=0)
    provision_available: Decimal = Field(Decimal("0.00"), ge=0)
    as_of_date: date
    narration: Optional[str] = None


# ============================================================================
# Asset Classification Register Schemas
# ============================================================================

class AssetClassificationRegisterRequest(BaseModel):
    """Request for asset classification register"""
    as_of_date: date
    category_filter: Optional[NPACategory] = None


class AssetClassificationEntry(BaseModel):
    """Single entry in asset classification register"""
    loan_account_id: int
    loan_account_number: str
    customer_name: str
    outstanding_principal: Decimal
    days_past_due: int
    npa_category: NPACategory
    provisioning_rate: Decimal
    required_provision: Decimal
    existing_provision: Decimal
    last_payment_date: Optional[date]
    classification_date: date


class AssetClassificationCategorySummary(BaseModel):
    """Summary for a specific NPA category"""
    category: NPACategory
    account_count: int
    total_outstanding: Decimal
    total_provision: Decimal
    provisioning_rate: Decimal
    accounts: List[AssetClassificationEntry]



class AssetClassificationRegisterResponse(BaseModel):
    """Complete asset classification register"""
    as_of_date: date
    generated_at: datetime
    summary: Dict[str, Any]
    categories: Dict[str, AssetClassificationCategorySummary]


class NPASummaryResponse(BaseModel):
    """Summary of NPA statistics"""
    as_of_date: date
    total_portfolio: Dict[str, Any]
    standard_assets: Dict[str, Any]
    sma_assets: Dict[str, Any]
    npa_assets: Dict[str, Any]
    gross_npa_ratio: Decimal
    net_npa_ratio: Decimal
    total_provision: Decimal


# ============================================================================
# NPA Movement Report Schemas
# ============================================================================

class NPAMovementReportRequest(BaseModel):
    """Request for NPA movement report"""
    from_date: date
    to_date: date


class NPAMovementAccount(BaseModel):
    """Account details in movement report"""
    loan_account_id: int
    loan_account_number: str
    customer_name: str
    outstanding_amount: Decimal
    previous_category: Optional[NPACategory]
    current_category: NPACategory
    movement_date: date


class NPAMovementAdditions(BaseModel):
    """NPA additions during period"""
    fresh_npa: Dict[str, Any]
    increased_provision: Dict[str, Any]


class NPAMovementReductions(BaseModel):
    """NPA reductions during period"""
    upgrades: Dict[str, Any]
    recoveries: Dict[str, Any]
    write_offs: Dict[str, Any]


class NPAMovementReportResponse(BaseModel):
    """Complete NPA movement report"""
    from_date: date
    to_date: date
    generated_at: datetime
    opening_balance: Dict[str, Any]
    additions: NPAMovementAdditions
    reductions: NPAMovementReductions
    closing_balance: Dict[str, Any]
    movements_by_category: Dict[str, Dict[str, int]]


# ============================================================================
# Vintage Analysis Schemas
# ============================================================================

class VintageAnalysisRequest(BaseModel):
    """Request for vintage analysis"""
    as_of_date: date
    cohort_by: str = Field("month", description="month, quarter, or year")


class VintageCohort(BaseModel):
    """Vintage cohort data"""
    cohort_period: str
    loans_originated: int
    original_amount: Decimal
    current_outstanding: Decimal
    npa_amount: Decimal
    npa_percentage: Decimal
    age_buckets: Dict[str, Any]


class VintageAnalysisResponse(BaseModel):
    """Vintage analysis report"""
    as_of_date: date
    cohort_by: str
    cohorts: List[VintageCohort]


# ============================================================================
# Regulatory Report Schemas
# ============================================================================

class RBINPAReturnRequest(BaseModel):
    """Request for RBI NPA return"""
    as_of_date: date


class RBINPAReturnResponse(BaseModel):
    """RBI NPA return format"""
    reporting_date: date
    reporting_entity: str
    gross_advances: Decimal
    gross_npa: Decimal
    gross_npa_ratio: Decimal
    provisions_held: Decimal
    net_npa: Decimal
    net_npa_ratio: Decimal
    category_wise_npa: Dict[str, Decimal]
    sector_wise_npa: Dict[str, Decimal]
    security_wise_npa: Dict[str, Decimal]


class ProvisioningCoverageRatioRequest(BaseModel):
    """Request for PCR calculation"""
    as_of_date: date


class ProvisioningCoverageRatioResponse(BaseModel):
    """Provisioning Coverage Ratio report"""
    as_of_date: date
    gross_npa: Decimal
    provisions_held: Decimal
    pcr_percentage: Decimal
    category_wise_pcr: Dict[str, Decimal]
    required_provision: Decimal
    shortfall: Decimal


# ============================================================================
# Batch Processing Schemas
# ============================================================================

class MonthlyNPAClassificationRequest(BaseModel):
    """Request for monthly NPA classification run"""
    as_of_date: date


class MonthlyNPAClassificationResponse(BaseModel):
    """Response from monthly NPA classification"""
    as_of_date: date
    processed_at: datetime
    total_accounts_processed: int
    classifications: Dict[str, int]
    provisions_created: Decimal
    journal_entries: List[int]
    summary: Dict[str, Any]
