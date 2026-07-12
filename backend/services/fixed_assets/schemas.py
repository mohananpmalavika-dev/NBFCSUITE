"""
Fixed Asset Management Schemas
Pydantic models for request/response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class AssetCategoryEnum(str, Enum):
    LAND = "land"
    BUILDING = "building"
    PLANT_MACHINERY = "plant_machinery"
    FURNITURE_FIXTURES = "furniture_fixtures"
    VEHICLES = "vehicles"
    COMPUTER_EQUIPMENT = "computer_equipment"
    OFFICE_EQUIPMENT = "office_equipment"
    LEASEHOLD_IMPROVEMENTS = "leasehold_improvements"
    INTANGIBLE_ASSETS = "intangible_assets"
    OTHER = "other"


class DepreciationMethodEnum(str, Enum):
    STRAIGHT_LINE = "straight_line"
    WRITTEN_DOWN_VALUE = "written_down_value"
    DOUBLE_DECLINING = "double_declining"
    SUM_OF_YEARS = "sum_of_years"
    UNITS_OF_PRODUCTION = "units_of_production"
    NO_DEPRECIATION = "no_depreciation"


class AssetStatusEnum(str, Enum):
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    UNDER_REPAIR = "under_repair"
    IDLE = "idle"
    DISPOSED = "disposed"
    SOLD = "sold"
    WRITTEN_OFF = "written_off"
    TRANSFERRED = "transferred"
    LOST = "lost"
    STOLEN = "stolen"


class MaintenanceTypeEnum(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    BREAKDOWN = "breakdown"
    SCHEDULED = "scheduled"
    INSPECTION = "inspection"


class MaintenanceStatusEnum(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransferStatusEnum(str, Enum):
    INITIATED = "initiated"
    APPROVED = "approved"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DisposalMethodEnum(str, Enum):
    SALE = "sale"
    SCRAP = "scrap"
    DONATION = "donation"
    TRADE_IN = "trade_in"
    WRITE_OFF = "write_off"
    DESTRUCTION = "destruction"


class VerificationStatusEnum(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    DAMAGED = "damaged"
    NEEDS_REPAIR = "needs_repair"
    DISCREPANCY = "discrepancy"


# ============================================================================
# Fixed Asset Schemas
# ============================================================================

class FixedAssetBase(BaseModel):
    """Base schema for Fixed Asset"""
    asset_code: str = Field(..., max_length=50, description="Unique asset code")
    asset_name: str = Field(..., max_length=200, description="Asset name")
    asset_description: Optional[str] = Field(None, description="Detailed description")
    
    # Classification
    asset_category: AssetCategoryEnum
    sub_category: Optional[str] = Field(None, max_length=100)
    asset_type: Optional[str] = Field(None, max_length=100)
    asset_class: Optional[str] = Field(None, max_length=50)
    
    # Acquisition
    acquisition_date: date
    purchase_date: Optional[date] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    invoice_date: Optional[date] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = Field(None, max_length=200)
    
    # Financial
    purchase_cost: Decimal = Field(..., ge=0)
    installation_cost: Decimal = Field(default=0, ge=0)
    transportation_cost: Decimal = Field(default=0, ge=0)
    other_costs: Decimal = Field(default=0, ge=0)
    
    # Depreciation configuration
    depreciation_method: DepreciationMethodEnum = DepreciationMethodEnum.STRAIGHT_LINE
    depreciation_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    useful_life_years: Optional[int] = Field(None, ge=0)
    useful_life_units: Optional[int] = Field(None, ge=0)
    salvage_value: Decimal = Field(default=0, ge=0)
    residual_value: Decimal = Field(default=0, ge=0)
    depreciation_start_date: Optional[date] = None
    
    # Location and custodian
    location_id: Optional[int] = None
    location_name: Optional[str] = Field(None, max_length=200)
    department_id: Optional[int] = None
    department_name: Optional[str] = Field(None, max_length=100)
    custodian_id: Optional[int] = None
    custodian_name: Optional[str] = Field(None, max_length=200)
    
    # Physical details
    serial_number: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    year_of_manufacture: Optional[int] = None
    
    # Warranty and insurance
    warranty_expiry_date: Optional[date] = None
    warranty_provider: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[date] = None
    insurance_company: Optional[str] = Field(None, max_length=200)
    insurance_value: Optional[Decimal] = Field(None, ge=0)
    
    # Status
    asset_status: AssetStatusEnum = AssetStatusEnum.ACTIVE
    in_use: bool = True
    
    # Accounting
    asset_account_id: Optional[int] = None
    depreciation_account_id: Optional[int] = None
    expense_account_id: Optional[int] = None
    
    # Additional
    barcode: Optional[str] = Field(None, max_length=100)
    qr_code: Optional[str] = Field(None, max_length=200)
    rfid_tag: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    document_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None


class FixedAssetCreate(FixedAssetBase):
    """Schema for creating a fixed asset"""
    pass


class FixedAssetUpdate(BaseModel):
    """Schema for updating a fixed asset"""
    asset_name: Optional[str] = Field(None, max_length=200)
    asset_description: Optional[str] = None
    sub_category: Optional[str] = Field(None, max_length=100)
    asset_type: Optional[str] = Field(None, max_length=100)
    asset_class: Optional[str] = Field(None, max_length=50)
    
    location_id: Optional[int] = None
    location_name: Optional[str] = Field(None, max_length=200)
    department_id: Optional[int] = None
    department_name: Optional[str] = Field(None, max_length=100)
    custodian_id: Optional[int] = None
    custodian_name: Optional[str] = Field(None, max_length=200)
    
    asset_status: Optional[AssetStatusEnum] = None
    in_use: Optional[bool] = None
    
    warranty_expiry_date: Optional[date] = None
    warranty_provider: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[date] = None
    insurance_company: Optional[str] = Field(None, max_length=200)
    insurance_value: Optional[Decimal] = Field(None, ge=0)
    
    image_url: Optional[str] = Field(None, max_length=500)
    document_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None


class FixedAssetResponse(FixedAssetBase):
    """Schema for fixed asset response"""
    id: int
    tenant_id: int
    total_cost: Decimal
    accumulated_depreciation: Decimal
    net_book_value: Decimal
    current_value: Optional[Decimal] = None
    last_depreciation_date: Optional[date] = None
    
    is_verified: bool
    last_verification_date: Optional[date] = None
    
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class FixedAssetListItem(BaseModel):
    """Simplified schema for asset list"""
    id: int
    asset_code: str
    asset_name: str
    asset_category: AssetCategoryEnum
    asset_status: AssetStatusEnum
    purchase_cost: Decimal
    total_cost: Decimal
    accumulated_depreciation: Decimal
    net_book_value: Decimal
    location_name: Optional[str] = None
    custodian_name: Optional[str] = None
    acquisition_date: date
    depreciation_method: DepreciationMethodEnum
    last_verification_date: Optional[date] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Asset Depreciation Schemas
# ============================================================================

class AssetDepreciationBase(BaseModel):
    """Base schema for asset depreciation"""
    asset_id: int
    financial_year: int
    financial_month: Optional[int] = Field(None, ge=1, le=12)
    period_start_date: date
    period_end_date: date
    depreciation_date: date
    depreciation_method: DepreciationMethodEnum
    depreciation_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class AssetDepreciationCreate(AssetDepreciationBase):
    """Schema for creating depreciation entry"""
    pass


class AssetDepreciationResponse(AssetDepreciationBase):
    """Schema for depreciation response"""
    id: int
    tenant_id: int
    opening_wdv: Decimal
    depreciation_amount: Decimal
    accumulated_depreciation: Decimal
    closing_wdv: Decimal
    days_in_period: Optional[int] = None
    is_partial_year: bool
    is_posted: bool
    posted_at: Optional[datetime] = None
    journal_entry_id: Optional[int] = None
    is_reversed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DepreciationCalculationRequest(BaseModel):
    """Request for depreciation calculation"""
    asset_ids: Optional[List[int]] = None  # If None, calculate for all assets
    financial_year: int
    financial_month: Optional[int] = Field(None, ge=1, le=12)
    calculation_date: date
    auto_post: bool = False


class DepreciationCalculationResponse(BaseModel):
    """Response from depreciation calculation"""
    total_assets: int
    assets_depreciated: int
    total_depreciation: Decimal
    posted_entries: int
    errors: List[Dict[str, Any]]


# ============================================================================
# Asset Maintenance Schemas
# ============================================================================

class AssetMaintenanceBase(BaseModel):
    """Base schema for asset maintenance"""
    asset_id: int
    maintenance_type: MaintenanceTypeEnum
    maintenance_category: Optional[str] = Field(None, max_length=100)
    
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[str] = Field(None, max_length=20)
    next_maintenance_date: Optional[date] = None
    
    priority: str = Field(default="medium", max_length=20)
    
    is_internal: bool = True
    service_provider_id: Optional[int] = None
    service_provider_name: Optional[str] = Field(None, max_length=200)
    technician_name: Optional[str] = Field(None, max_length=200)
    technician_contact: Optional[str] = Field(None, max_length=50)
    
    problem_description: Optional[str] = None
    work_performed: Optional[str] = None
    parts_replaced: Optional[str] = None
    recommendations: Optional[str] = None
    
    labor_cost: Decimal = Field(default=0, ge=0)
    parts_cost: Decimal = Field(default=0, ge=0)
    other_charges: Decimal = Field(default=0, ge=0)
    
    downtime_hours: Optional[Decimal] = Field(None, ge=0)
    
    warranty_claim: bool = False
    warranty_claim_number: Optional[str] = Field(None, max_length=100)
    
    invoice_number: Optional[str] = Field(None, max_length=100)
    invoice_date: Optional[date] = None
    invoice_amount: Optional[Decimal] = Field(None, ge=0)
    
    document_urls: Optional[List[str]] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    """Schema for creating maintenance record"""
    pass


class AssetMaintenanceUpdate(BaseModel):
    """Schema for updating maintenance record"""
    status: Optional[MaintenanceStatusEnum] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    
    work_performed: Optional[str] = None
    parts_replaced: Optional[str] = None
    recommendations: Optional[str] = None
    
    labor_cost: Optional[Decimal] = Field(None, ge=0)
    parts_cost: Optional[Decimal] = Field(None, ge=0)
    other_charges: Optional[Decimal] = Field(None, ge=0)
    
    downtime_hours: Optional[Decimal] = Field(None, ge=0)
    
    invoice_number: Optional[str] = Field(None, max_length=100)
    invoice_date: Optional[date] = None
    invoice_amount: Optional[Decimal] = Field(None, ge=0)
    
    document_urls: Optional[List[str]] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None


class AssetMaintenanceResponse(AssetMaintenanceBase):
    """Schema for maintenance response"""
    id: int
    tenant_id: int
    maintenance_number: str
    status: MaintenanceStatusEnum
    
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    
    total_cost: Decimal
    downtime_cost: Optional[Decimal] = None
    
    requested_by: Optional[int] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Asset Transfer Schemas
# ============================================================================

class AssetTransferBase(BaseModel):
    """Base schema for asset transfer"""
    asset_id: int
    transfer_date: date
    transfer_type: str = Field(default="internal", max_length=50)
    
    from_location_id: Optional[int] = None
    from_location_name: Optional[str] = Field(None, max_length=200)
    from_department_id: Optional[int] = None
    from_department_name: Optional[str] = Field(None, max_length=100)
    from_custodian_id: Optional[int] = None
    from_custodian_name: Optional[str] = Field(None, max_length=200)
    
    to_location_id: Optional[int] = None
    to_location_name: Optional[str] = Field(None, max_length=200)
    to_department_id: Optional[int] = None
    to_department_name: Optional[str] = Field(None, max_length=100)
    to_custodian_id: Optional[int] = None
    to_custodian_name: Optional[str] = Field(None, max_length=200)
    
    reason: Optional[str] = None
    transfer_mode: Optional[str] = Field(None, max_length=50)
    transport_details: Optional[str] = None
    estimated_arrival_date: Optional[date] = None
    
    condition_at_transfer: Optional[str] = Field(None, max_length=50)
    condition_notes: Optional[str] = None
    
    transfer_cost: Decimal = Field(default=0, ge=0)
    insurance_cost: Decimal = Field(default=0, ge=0)
    other_charges: Decimal = Field(default=0, ge=0)
    
    document_urls: Optional[List[str]] = None
    remarks: Optional[str] = None
    notes: Optional[str] = None


class AssetTransferCreate(AssetTransferBase):
    """Schema for creating transfer"""
    pass


class AssetTransferUpdate(BaseModel):
    """Schema for updating transfer"""
    status: Optional[TransferStatusEnum] = None
    status_notes: Optional[str] = None
    
    actual_arrival_date: Optional[date] = None
    handover_date: Optional[date] = None
    received_date: Optional[date] = None
    
    condition_at_receipt: Optional[str] = Field(None, max_length=50)
    condition_notes: Optional[str] = None
    
    remarks: Optional[str] = None
    notes: Optional[str] = None


class AssetTransferResponse(AssetTransferBase):
    """Schema for transfer response"""
    id: int
    tenant_id: int
    transfer_number: str
    status: TransferStatusEnum
    status_notes: Optional[str] = None
    
    actual_arrival_date: Optional[date] = None
    handover_date: Optional[date] = None
    handover_by: Optional[int] = None
    received_date: Optional[date] = None
    received_by: Optional[int] = None
    
    condition_at_receipt: Optional[str] = None
    total_cost: Decimal
    
    initiated_by: Optional[int] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class AssetTransferApproval(BaseModel):
    """Schema for transfer approval/rejection"""
    approve: bool
    notes: Optional[str] = None


# ============================================================================
# Asset Disposal Schemas
# ============================================================================

class AssetDisposalRequest(BaseModel):
    """Schema for asset disposal"""
    asset_id: int
    disposal_date: date
    disposal_method: DisposalMethodEnum
    disposal_value: Decimal = Field(default=0, ge=0)
    disposal_cost: Decimal = Field(default=0, ge=0)
    disposal_notes: Optional[str] = None
    reason: Optional[str] = None


class AssetDisposalResponse(BaseModel):
    """Response for asset disposal"""
    asset_id: int
    disposal_date: date
    disposal_method: DisposalMethodEnum
    net_book_value: Decimal
    disposal_value: Decimal
    disposal_cost: Decimal
    disposal_gain_loss: Decimal
    journal_entry_id: Optional[int] = None
    message: str


# ============================================================================
# Asset Verification Schemas
# ============================================================================

class AssetVerificationBase(BaseModel):
    """Base schema for asset verification"""
    asset_id: int
    verification_date: date
    verification_status: VerificationStatusEnum
    is_found: bool = True
    condition: Optional[str] = Field(None, max_length=50)
    
    location_verified: bool = True
    location_remarks: Optional[str] = None
    custodian_verified: bool = True
    custodian_remarks: Optional[str] = None
    
    functional_status: Optional[str] = Field(None, max_length=50)
    requires_repair: bool = False
    requires_maintenance: bool = False
    recommended_action: Optional[str] = None
    
    has_discrepancy: bool = False
    discrepancy_type: Optional[str] = Field(None, max_length=100)
    discrepancy_description: Optional[str] = None
    
    actual_location_id: Optional[int] = None
    actual_location_name: Optional[str] = Field(None, max_length=200)
    actual_custodian_id: Optional[int] = None
    actual_custodian_name: Optional[str] = Field(None, max_length=200)
    
    image_urls: Optional[List[str]] = None
    document_urls: Optional[List[str]] = None
    
    gps_latitude: Optional[str] = Field(None, max_length=50)
    gps_longitude: Optional[str] = Field(None, max_length=50)
    gps_accuracy: Optional[str] = Field(None, max_length=20)
    
    notes: Optional[str] = None
    remarks: Optional[str] = None


class AssetVerificationCreate(AssetVerificationBase):
    """Schema for creating verification record"""
    verification_cycle_id: Optional[int] = None


class AssetVerificationResponse(AssetVerificationBase):
    """Schema for verification response"""
    id: int
    tenant_id: int
    verification_cycle_id: Optional[int] = None
    verification_number: str
    asset_code: str
    
    expected_location_id: Optional[int] = None
    expected_location_name: Optional[str] = None
    expected_custodian_id: Optional[int] = None
    expected_custodian_name: Optional[str] = None
    
    verified_by: int
    verified_by_name: Optional[str] = None
    verification_team: Optional[List[int]] = None
    
    discrepancy_resolved: bool = False
    resolution_notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Verification Cycle Schemas
# ============================================================================

class VerificationCycleBase(BaseModel):
    """Base schema for verification cycle"""
    cycle_name: str = Field(..., max_length=200)
    financial_year: int
    planned_start_date: date
    planned_end_date: date
    
    scope: str = Field(default="all", max_length=50)
    category_filter: Optional[List[str]] = None
    location_filter: Optional[List[int]] = None
    department_filter: Optional[List[int]] = None
    
    team_lead_id: Optional[int] = None
    team_lead_name: Optional[str] = Field(None, max_length=200)
    team_members: Optional[List[int]] = None
    
    description: Optional[str] = None
    notes: Optional[str] = None


class VerificationCycleCreate(VerificationCycleBase):
    """Schema for creating verification cycle"""
    pass


class VerificationCycleUpdate(BaseModel):
    """Schema for updating verification cycle"""
    cycle_name: Optional[str] = Field(None, max_length=200)
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    team_members: Optional[List[int]] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None


class VerificationCycleResponse(VerificationCycleBase):
    """Schema for verification cycle response"""
    id: int
    tenant_id: int
    cycle_number: str
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    
    total_assets: int
    verified_assets: int
    pending_assets: int
    found_assets: int
    not_found_assets: int
    discrepancy_count: int
    
    status: str
    completion_percentage: Decimal
    
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    
    report_generated: bool
    report_url: Optional[str] = None
    report_generated_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Report and Analytics Schemas
# ============================================================================

class AssetRegisterReport(BaseModel):
    """Asset register report"""
    filters: Dict[str, Any]
    total_assets: int
    total_cost: Decimal
    total_depreciation: Decimal
    total_net_book_value: Decimal
    assets_by_category: List[Dict[str, Any]]
    assets_by_location: List[Dict[str, Any]]
    assets_by_status: List[Dict[str, Any]]


class DepreciationReport(BaseModel):
    """Depreciation report"""
    financial_year: int
    financial_month: Optional[int] = None
    total_depreciation: Decimal
    assets_depreciated: int
    depreciation_by_category: List[Dict[str, Any]]
    depreciation_by_method: List[Dict[str, Any]]


class MaintenanceReport(BaseModel):
    """Maintenance report"""
    period_start: date
    period_end: date
    total_maintenance_cost: Decimal
    total_maintenance_requests: int
    maintenance_by_type: List[Dict[str, Any]]
    maintenance_by_status: List[Dict[str, Any]]
    top_maintained_assets: List[Dict[str, Any]]


class AssetUtilizationReport(BaseModel):
    """Asset utilization report"""
    total_assets: int
    active_assets: int
    idle_assets: int
    under_maintenance: int
    utilization_percentage: Decimal
    assets_by_age: List[Dict[str, Any]]


# ============================================================================
# Filter and Search Schemas
# ============================================================================

class AssetFilterParams(BaseModel):
    """Parameters for filtering assets"""
    category: Optional[AssetCategoryEnum] = None
    status: Optional[AssetStatusEnum] = None
    location_id: Optional[int] = None
    department_id: Optional[int] = None
    custodian_id: Optional[int] = None
    acquisition_date_from: Optional[date] = None
    acquisition_date_to: Optional[date] = None
    purchase_cost_min: Optional[Decimal] = None
    purchase_cost_max: Optional[Decimal] = None
    search_query: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)
    sort_by: Optional[str] = Field(default="asset_code")
    sort_order: Optional[str] = Field(default="asc")


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
