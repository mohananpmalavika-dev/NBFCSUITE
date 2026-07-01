from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AssetCategoryCreate(BaseModel):
    tenant_id: str
    category_code: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class AssetCategoryResponse(AssetCategoryCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AssetCreate(BaseModel):
    tenant_id: str
    asset_code: str
    asset_name: str
    asset_category: Optional[str] = None
    asset_class: Optional[str] = None
    asset_type: Optional[str] = None
    serial_number: Optional[str] = None
    qr_code: Optional[str] = None
    barcode: Optional[str] = None
    location: Optional[str] = None
    branch_id: Optional[str] = None
    department_id: Optional[str] = None
    custodian: Optional[str] = None
    assigned_to: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    acquisition_cost: Optional[float] = 0.0
    book_value: Optional[float] = 0.0
    currency: Optional[str] = "INR"
    lifecycle_stage: Optional[str] = "planning"
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_category: Optional[str] = None
    asset_class: Optional[str] = None
    asset_type: Optional[str] = None
    location: Optional[str] = None
    branch_id: Optional[str] = None
    department_id: Optional[str] = None
    custodian: Optional[str] = None
    assigned_to: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetResponse(AssetCreate):
    id: str
    status: str
    book_value: float
    accumulated_depreciation: float
    net_book_value: float
    capitalization_date: Optional[datetime] = None
    commissioning_date: Optional[datetime] = None
    disposal_date: Optional[datetime] = None
    disposal_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetCapitalizeRequest(BaseModel):
    capitalization_date: Optional[datetime] = None


class AssetDepreciationRequest(BaseModel):
    depreciation_amount: float
    depreciation_method: Optional[str] = None
    book_type: Optional[str] = "primary"
    period: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetTransferRequest(BaseModel):
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_department_id: Optional[str] = None
    to_department_id: Optional[str] = None
    transfer_date: Optional[datetime] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetDisposeRequest(BaseModel):
    disposal_reason: Optional[str] = None
    disposal_date: Optional[datetime] = None
    disposal_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetVerifyRequest(BaseModel):
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    remarks: Optional[str] = None
    status: Optional[str] = "verified"
    metadata: Optional[Dict[str, Any]] = None


class AssetDashboardResponse(BaseModel):
    tenant_id: str
    total_assets: int
    total_gross_block: float
    total_accumulated_depreciation: float
    total_net_book_value: float
    total_cwip: float
    assets_by_status: Dict[str, int]

    class Config:
        from_attributes = True
