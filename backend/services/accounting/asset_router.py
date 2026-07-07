"""
Asset Management Router
Fixed Assets, Depreciation, Transfers, Disposal, Maintenance
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from backend.services.accounting.asset_service import AssetService
from backend.shared.database.accounting_extended_models import (
    AssetCategory,
    DepreciationMethod,
    AssetStatus
)

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class AssetCreate(BaseModel):
    asset_name: str = Field(..., min_length=1, max_length=200)
    category: AssetCategory
    purchase_date: date
    purchase_cost: Decimal = Field(..., gt=0)
    depreciation_method: DepreciationMethod
    depreciation_rate: Decimal = Field(..., ge=0, le=100)
    useful_life_years: int = Field(..., gt=0)
    useful_life_months: int = Field(default=0, ge=0, lt=12)
    salvage_value: Decimal = Field(default=Decimal("0.00"), ge=0)
    description: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    custodian: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    custodian: Optional[str] = None
    status: Optional[AssetStatus] = None


class AssetResponse(BaseModel):
    id: int
    asset_code: str
    asset_name: str
    category: str
    purchase_date: date
    purchase_cost: Decimal
    depreciation_method: str
    depreciation_rate: Decimal
    accumulated_depreciation: Decimal
    written_down_value: Decimal
    status: str
    location: Optional[str]
    department: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DepreciationPostRequest(BaseModel):
    asset_id: int
    depreciation_date: date
    journal_entry_id: Optional[int] = None


class DepreciationScheduleResponse(BaseModel):
    id: int
    asset_id: int
    depreciation_date: date
    opening_wdv: Decimal
    depreciation_amount: Decimal
    accumulated_depreciation: Decimal
    closing_wdv: Decimal
    is_posted: bool
    
    class Config:
        from_attributes = True


class AssetTransferRequest(BaseModel):
    asset_id: int
    to_location: Optional[str] = None
    to_department: Optional[str] = None
    to_custodian: Optional[str] = None
    transfer_reason: Optional[str] = None


class AssetDisposalRequest(BaseModel):
    asset_id: int
    disposal_date: date
    disposal_amount: Decimal = Field(..., ge=0)
    disposal_reason: str


class MaintenanceRequest(BaseModel):
    asset_id: int
    maintenance_date: date
    maintenance_type: str
    description: str
    cost: Decimal = Field(..., ge=0)
    vendor_name: Optional[str] = None


class MaintenanceResponse(BaseModel):
    id: int
    asset_id: int
    maintenance_date: date
    maintenance_type: str
    description: str
    maintenance_cost: Decimal
    vendor_name: Optional[str]
    is_completed: bool
    
    class Config:
        from_attributes = True


# ============================================
# ENDPOINTS
# ============================================

@router.post("/assets", response_model=AssetResponse, tags=["Assets"])
async def create_asset(
    data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new fixed asset"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    asset = await service.create_asset(
        asset_name=data.asset_name,
        category=data.category,
        purchase_date=data.purchase_date,
        purchase_cost=data.purchase_cost,
        depreciation_method=data.depreciation_method,
        depreciation_rate=data.depreciation_rate,
        useful_life_years=data.useful_life_years,
        salvage_value=data.salvage_value,
        description=data.description,
        location=data.location,
        department=data.department,
        vendor_name=data.vendor_name,
        invoice_number=data.invoice_number
    )
    
    return asset


@router.get("/assets", tags=["Assets"])
async def list_assets(
    category: Optional[AssetCategory] = None,
    status: Optional[AssetStatus] = None,
    location: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all assets with filters"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    assets, total = await service.list_assets(
        category=category,
        status=status,
        location=location,
        skip=skip,
        limit=limit
    )
    
    return {
        "assets": assets,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get asset by ID"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset


@router.put("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
async def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update asset details"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update fields
    if data.asset_name is not None:
        asset.asset_name = data.asset_name
    if data.location is not None:
        asset.location = data.location
    if data.department is not None:
        asset.department = data.department
    if data.custodian is not None:
        asset.custodian = data.custodian
    if data.status is not None:
        asset.status = data.status
    
    await db.commit()
    await db.refresh(asset)
    
    return asset


@router.post("/assets/depreciation/post", response_model=DepreciationScheduleResponse, tags=["Depreciation"])
async def post_depreciation(
    data: DepreciationPostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post depreciation for an asset"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    try:
        schedule = await service.post_depreciation(
            asset_id=data.asset_id,
            depreciation_date=data.depreciation_date,
            journal_entry_id=data.journal_entry_id
        )
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assets/depreciation/schedule", tags=["Depreciation"])
async def get_depreciation_schedule(
    asset_id: Optional[int] = None,
    financial_year: Optional[int] = None,
    month: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get depreciation schedule"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    schedule = await service.get_depreciation_schedule(
        asset_id=asset_id,
        financial_year=financial_year,
        month=month
    )
    
    return {"schedule": schedule, "count": len(schedule)}


@router.post("/assets/depreciation/calculate/{asset_id}", tags=["Depreciation"])
async def calculate_depreciation(
    asset_id: int,
    depreciation_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate depreciation for an asset (preview only)"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    depreciation_amount = await service.calculate_monthly_depreciation(asset, depreciation_date)
    
    return {
        "asset_id": asset_id,
        "asset_name": asset.asset_name,
        "depreciation_date": depreciation_date,
        "opening_wdv": asset.written_down_value,
        "depreciation_amount": depreciation_amount,
        "closing_wdv": asset.written_down_value - depreciation_amount,
        "method": asset.depreciation_method.value
    }


@router.post("/assets/transfer", tags=["Assets"])
async def transfer_asset(
    data: AssetTransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transfer asset to new location/department"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    try:
        transfer = await service.transfer_asset(
            asset_id=data.asset_id,
            to_location=data.to_location,
            to_department=data.to_department,
            to_custodian=data.to_custodian,
            transfer_reason=data.transfer_reason
        )
        return transfer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assets/dispose", tags=["Assets"])
async def dispose_asset(
    data: AssetDisposalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dispose/sell asset"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    try:
        asset = await service.dispose_asset(
            asset_id=data.asset_id,
            disposal_date=data.disposal_date,
            disposal_amount=data.disposal_amount,
            disposal_reason=data.disposal_reason
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assets/maintenance", response_model=MaintenanceResponse, tags=["Maintenance"])
async def record_maintenance(
    data: MaintenanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record asset maintenance"""
    service = AssetService(db, current_user.tenant_id, current_user.id)
    
    maintenance = await service.record_maintenance(
        asset_id=data.asset_id,
        maintenance_date=data.maintenance_date,
        maintenance_type=data.maintenance_type,
        description=data.description,
        cost=data.cost,
        vendor_name=data.vendor_name
    )
    
    return maintenance


@router.get("/assets/{asset_id}/maintenance", tags=["Maintenance"])
async def get_asset_maintenance(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance history for an asset"""
    from sqlalchemy import select, and_
    from backend.shared.database.accounting_extended_models import AssetMaintenance
    
    query = select(AssetMaintenance).where(
        and_(
            AssetMaintenance.tenant_id == current_user.tenant_id,
            AssetMaintenance.asset_id == asset_id
        )
    ).order_by(AssetMaintenance.maintenance_date.desc())
    
    result = await db.execute(query)
    maintenance_records = result.scalars().all()
    
    return {"maintenance": maintenance_records, "count": len(maintenance_records)}


@router.get("/assets/summary/dashboard", tags=["Assets"])
async def get_asset_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get asset dashboard summary"""
    from sqlalchemy import select, func, and_
    from backend.shared.database.accounting_extended_models import FixedAsset
    
    # Total assets
    total_query = select(func.count(FixedAsset.id)).where(
        and_(
            FixedAsset.tenant_id == current_user.tenant_id,
            FixedAsset.is_deleted == False
        )
    )
    total_result = await db.execute(total_query)
    total_assets = total_result.scalar()
    
    # Total value
    value_query = select(func.sum(FixedAsset.purchase_cost)).where(
        and_(
            FixedAsset.tenant_id == current_user.tenant_id,
            FixedAsset.is_deleted == False
        )
    )
    value_result = await db.execute(value_query)
    total_value = value_result.scalar() or Decimal("0.00")
    
    # Total WDV
    wdv_query = select(func.sum(FixedAsset.written_down_value)).where(
        and_(
            FixedAsset.tenant_id == current_user.tenant_id,
            FixedAsset.is_deleted == False,
            FixedAsset.status == AssetStatus.ACTIVE
        )
    )
    wdv_result = await db.execute(wdv_query)
    total_wdv = wdv_result.scalar() or Decimal("0.00")
    
    # Total depreciation
    dep_query = select(func.sum(FixedAsset.accumulated_depreciation)).where(
        and_(
            FixedAsset.tenant_id == current_user.tenant_id,
            FixedAsset.is_deleted == False
        )
    )
    dep_result = await db.execute(dep_query)
    total_depreciation = dep_result.scalar() or Decimal("0.00")
    
    # Assets by status
    status_query = select(
        FixedAsset.status,
        func.count(FixedAsset.id)
    ).where(
        and_(
            FixedAsset.tenant_id == current_user.tenant_id,
            FixedAsset.is_deleted == False
        )
    ).group_by(FixedAsset.status)
    
    status_result = await db.execute(status_query)
    status_breakdown = {str(status): count for status, count in status_result.all()}
    
    # Assets by category
    category_query = select(
        FixedAsset.category,
        func.count(FixedAsset.id),
        func.sum(FixedAsset.written_down_value)
    ).where(
        and_(
            FixedAsset.tenant_id == current_user.tenant_id,
            FixedAsset.is_deleted == False
        )
    ).group_by(FixedAsset.category)
    
    category_result = await db.execute(category_query)
    category_breakdown = [
        {
            "category": str(category),
            "count": count,
            "value": float(value or 0)
        }
        for category, count, value in category_result.all()
    ]
    
    return {
        "total_assets": total_assets,
        "total_value": float(total_value),
        "total_wdv": float(total_wdv),
        "total_depreciation": float(total_depreciation),
        "status_breakdown": status_breakdown,
        "category_breakdown": category_breakdown
    }

