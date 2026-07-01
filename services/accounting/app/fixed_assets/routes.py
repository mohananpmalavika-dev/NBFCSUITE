from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.fixed_assets.models import (
    Asset,
    AssetCategory,
    AssetDepreciation,
    AssetDisposal,
    AssetTransfer,
    AssetVerification,
)
from app.fixed_assets.schemas import (
    AssetCapitalizeRequest,
    AssetCreate,
    AssetDashboardResponse,
    AssetDepreciationRequest,
    AssetDisposeRequest,
    AssetResponse,
    AssetTransferRequest,
    AssetUpdate,
    AssetVerifyRequest,
)


router = APIRouter(prefix="/api/v1/assets", tags=["fixed assets"])


def _asset_response(asset: Asset) -> AssetResponse:
    return AssetResponse(
        id=asset.id,
        tenant_id=asset.tenant_id,
        asset_code=asset.asset_code,
        asset_name=asset.asset_name,
        asset_category=asset.asset_category,
        asset_class=asset.asset_class,
        asset_type=asset.asset_type,
        serial_number=asset.serial_number,
        qr_code=asset.qr_code,
        barcode=asset.barcode,
        location=asset.location,
        branch_id=asset.branch_id,
        department_id=asset.department_id,
        custodian=asset.custodian,
        assigned_to=asset.assigned_to,
        acquisition_date=asset.acquisition_date,
        acquisition_cost=asset.acquisition_cost,
        book_value=asset.book_value,
        accumulated_depreciation=asset.accumulated_depreciation,
        net_book_value=asset.net_book_value,
        capitalization_date=asset.capitalization_date,
        commissioning_date=asset.commissioning_date,
        disposal_date=asset.disposal_date,
        disposal_reason=asset.disposal_reason,
        status=asset.status,
        lifecycle_stage=asset.lifecycle_stage,
        currency=asset.currency,
        metadata=asset.metadata_json,
        created_by=asset.created_by,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.post("/", response_model=AssetResponse)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    existing = db.query(Asset).filter(
        Asset.tenant_id == asset.tenant_id,
        Asset.asset_code == asset.asset_code,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Asset code already exists")

    entity = Asset(
        id=str(uuid4()),
        tenant_id=asset.tenant_id,
        asset_code=asset.asset_code,
        asset_name=asset.asset_name,
        asset_category=asset.asset_category,
        asset_class=asset.asset_class,
        asset_type=asset.asset_type,
        serial_number=asset.serial_number,
        qr_code=asset.qr_code,
        barcode=asset.barcode,
        location=asset.location,
        branch_id=asset.branch_id,
        department_id=asset.department_id,
        custodian=asset.custodian,
        assigned_to=asset.assigned_to,
        acquisition_date=asset.acquisition_date,
        acquisition_cost=round(asset.acquisition_cost or 0.0, 2),
        book_value=round(asset.book_value or asset.acquisition_cost or 0.0, 2),
        accumulated_depreciation=0.0,
        net_book_value=round((asset.book_value or asset.acquisition_cost or 0.0), 2),
        lifecycle_stage=asset.lifecycle_stage or "planning",
        status="draft",
        currency=asset.currency or "INR",
        metadata_json=asset.metadata,
        created_by=asset.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return _asset_response(entity)


@router.get("/", response_model=Dict[str, object])
async def list_assets(
    tenant_id: str = Query(...),
    asset_category: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    query = db.query(Asset).filter(Asset.tenant_id == tenant_id)
    if asset_category:
        query = query.filter(Asset.asset_category == asset_category)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)

    total = query.count()
    items = query.order_by(Asset.asset_name.asc()).offset(skip).limit(limit).all()

    return {"total": total, "items": [_asset_response(item) for item in items]}


@router.get("/dashboard", response_model=AssetDashboardResponse)
async def asset_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    assets = db.query(Asset).filter(Asset.tenant_id == tenant_id).all()
    total_assets = len(assets)
    total_gross_block = round(sum(asset.acquisition_cost or 0.0 for asset in assets), 2)
    total_accumulated_depreciation = round(sum(asset.accumulated_depreciation or 0.0 for asset in assets), 2)
    total_net_book_value = round(sum(asset.net_book_value or 0.0 for asset in assets), 2)
    total_cwip = round(sum((asset.acquisition_cost or 0.0) for asset in assets if asset.lifecycle_stage == "cwip" or asset.status == "cwip"), 2)

    status_counts: Dict[str, int] = {}
    for asset in assets:
        status_counts[asset.status] = status_counts.get(asset.status, 0) + 1

    return AssetDashboardResponse(
        tenant_id=tenant_id,
        total_assets=total_assets,
        total_gross_block=total_gross_block,
        total_accumulated_depreciation=total_accumulated_depreciation,
        total_net_book_value=total_net_book_value,
        total_cwip=total_cwip,
        assets_by_status=status_counts,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _asset_response(asset)


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: str, payload: AssetUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(asset, field, value)
    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return _asset_response(asset)


@router.post("/{asset_id}/capitalize", response_model=AssetResponse)
async def capitalize_asset(
    asset_id: str,
    payload: AssetCapitalizeRequest,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset.capitalization_date = payload.capitalization_date or datetime.utcnow()
    asset.status = "capitalized"
    asset.lifecycle_stage = "capitalized"
    asset.book_value = round(asset.acquisition_cost or asset.book_value or 0.0, 2)
    asset.net_book_value = round((asset.book_value or 0.0) - (asset.accumulated_depreciation or 0.0), 2)
    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return _asset_response(asset)


@router.post("/{asset_id}/depreciate", response_model=AssetResponse)
async def depreciate_asset(
    asset_id: str,
    payload: AssetDepreciationRequest,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if payload.depreciation_amount <= 0:
        raise HTTPException(status_code=400, detail="depreciation_amount must be greater than zero")

    new_accumulated = round((asset.accumulated_depreciation or 0.0) + payload.depreciation_amount, 2)
    asset.accumulated_depreciation = new_accumulated
    asset.net_book_value = round((asset.book_value or 0.0) - new_accumulated, 2)
    asset.status = "depreciated"
    asset.updated_at = datetime.utcnow()

    depreciation_record = AssetDepreciation(
        id=str(uuid4()),
        tenant_id=tenant_id,
        asset_id=asset.id,
        book_type=payload.book_type or "primary",
        depreciation_method=payload.depreciation_method,
        depreciation_amount=round(payload.depreciation_amount, 2),
        accumulated_depreciation=asset.accumulated_depreciation,
        period=payload.period,
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(depreciation_record)
    db.commit()
    db.refresh(asset)
    return _asset_response(asset)


@router.post("/{asset_id}/transfer", response_model=AssetResponse)
async def transfer_asset(
    asset_id: str,
    payload: AssetTransferRequest,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    transfer_record = AssetTransfer(
        id=str(uuid4()),
        tenant_id=tenant_id,
        asset_id=asset.id,
        from_location=asset.location,
        to_location=payload.to_location or asset.location,
        from_department_id=asset.department_id,
        to_department_id=payload.to_department_id or asset.department_id,
        transfer_date=payload.transfer_date or datetime.utcnow(),
        reason=payload.reason,
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    asset.location = payload.to_location or asset.location
    asset.department_id = payload.to_department_id or asset.department_id
    asset.updated_at = datetime.utcnow()

    db.add(transfer_record)
    db.commit()
    db.refresh(asset)
    return _asset_response(asset)


@router.post("/{asset_id}/dispose", response_model=AssetResponse)
async def dispose_asset(
    asset_id: str,
    payload: AssetDisposeRequest,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    disposal_record = AssetDisposal(
        id=str(uuid4()),
        tenant_id=tenant_id,
        asset_id=asset.id,
        disposal_date=payload.disposal_date or datetime.utcnow(),
        disposal_reason=payload.disposal_reason,
        disposal_value=payload.disposal_value,
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )

    asset.status = "disposed"
    asset.disposal_date = disposal_record.disposal_date
    asset.disposal_reason = payload.disposal_reason
    asset.updated_at = datetime.utcnow()

    db.add(disposal_record)
    db.commit()
    db.refresh(asset)
    return _asset_response(asset)


@router.post("/{asset_id}/verify", response_model=AssetResponse)
async def verify_asset(
    asset_id: str,
    payload: AssetVerifyRequest,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    verification_record = AssetVerification(
        id=str(uuid4()),
        tenant_id=tenant_id,
        asset_id=asset.id,
        verified_by=payload.verified_by,
        verification_date=payload.verification_date or datetime.utcnow(),
        remarks=payload.remarks,
        status=payload.status or "verified",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )

    asset.status = payload.status or "verified"
    asset.updated_at = datetime.utcnow()

    db.add(verification_record)
    db.commit()
    db.refresh(asset)
    return _asset_response(asset)


@router.get("/dashboard", response_model=AssetDashboardResponse)
async def asset_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    assets = db.query(Asset).filter(Asset.tenant_id == tenant_id).all()
    total_assets = len(assets)
    total_gross_block = round(sum(asset.acquisition_cost or 0.0 for asset in assets), 2)
    total_accumulated_depreciation = round(sum(asset.accumulated_depreciation or 0.0 for asset in assets), 2)
    total_net_book_value = round(sum(asset.net_book_value or 0.0 for asset in assets), 2)
    total_cwip = round(sum((asset.acquisition_cost or 0.0) for asset in assets if asset.lifecycle_stage == "cwip" or asset.status == "cwip"), 2)

    status_counts: Dict[str, int] = {}
    for asset in assets:
        status_counts[asset.status] = status_counts.get(asset.status, 0) + 1

    return AssetDashboardResponse(
        tenant_id=tenant_id,
        total_assets=total_assets,
        total_gross_block=total_gross_block,
        total_accumulated_depreciation=total_accumulated_depreciation,
        total_net_book_value=total_net_book_value,
        total_cwip=total_cwip,
        assets_by_status=status_counts,
    )
