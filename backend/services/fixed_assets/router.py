"""
Fixed Asset Management API Router
Complete REST API for asset management
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user
from backend.services.fixed_assets.schemas import *
from backend.services.fixed_assets.asset_service import AssetService
from backend.services.fixed_assets.depreciation_service import DepreciationService
from backend.services.fixed_assets.maintenance_service import MaintenanceService
from backend.services.fixed_assets.transfer_service import TransferService
from backend.services.fixed_assets.verification_service import VerificationService


router = APIRouter(prefix="/fixed-assets", tags=["Fixed Assets"])


# ============================================================================
# FIXED ASSET ENDPOINTS
# ============================================================================

@router.post("/assets", response_model=FixedAssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_data: FixedAssetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new fixed asset"""
    return AssetService.create_asset(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        asset_data=asset_data
    )


@router.get("/assets/{asset_id}", response_model=FixedAssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get asset by ID"""
    asset = AssetService.get_asset(
        db=db,
        tenant_id=current_user["tenant_id"],
        asset_id=asset_id
    )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.put("/assets/{asset_id}", response_model=FixedAssetResponse)
def update_asset(
    asset_id: int,
    asset_data: FixedAssetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing asset"""
    return AssetService.update_asset(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        asset_id=asset_id,
        asset_data=asset_data
    )


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an asset (soft delete)"""
    AssetService.delete_asset(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        asset_id=asset_id
    )


@router.get("/assets", response_model=PaginatedResponse)
def list_assets(
    category: Optional[AssetCategoryEnum] = None,
    status: Optional[AssetStatusEnum] = None,
    location_id: Optional[int] = None,
    department_id: Optional[int] = None,
    custodian_id: Optional[int] = None,
    acquisition_date_from: Optional[date] = None,
    acquisition_date_to: Optional[date] = None,
    purchase_cost_min: Optional[float] = None,
    purchase_cost_max: Optional[float] = None,
    search_query: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    sort_by: Optional[str] = "asset_code",
    sort_order: Optional[str] = "asc",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List assets with filtering and pagination"""
    from decimal import Decimal
    
    filters = AssetFilterParams(
        category=category,
        status=status,
        location_id=location_id,
        department_id=department_id,
        custodian_id=custodian_id,
        acquisition_date_from=acquisition_date_from,
        acquisition_date_to=acquisition_date_to,
        purchase_cost_min=Decimal(purchase_cost_min) if purchase_cost_min else None,
        purchase_cost_max=Decimal(purchase_cost_max) if purchase_cost_max else None,
        search_query=search_query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    assets, total = AssetService.list_assets(
        db=db,
        tenant_id=current_user["tenant_id"],
        filters=filters
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": assets,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.post("/assets/{asset_id}/dispose", response_model=AssetDisposalResponse)
def dispose_asset(
    asset_id: int,
    disposal_data: AssetDisposalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Dispose an asset"""
    disposal_data.asset_id = asset_id
    return AssetService.dispose_asset(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        disposal_data=disposal_data
    )


@router.get("/assets/summary/statistics")
def get_asset_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get asset summary statistics"""
    return AssetService.get_asset_summary(
        db=db,
        tenant_id=current_user["tenant_id"]
    )


# ============================================================================
# DEPRECIATION ENDPOINTS
# ============================================================================

@router.post("/depreciation/calculate", response_model=DepreciationCalculationResponse)
def calculate_depreciation(
    request: DepreciationCalculationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Calculate and post depreciation"""
    return DepreciationService.calculate_and_post_depreciation(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        request=request
    )


@router.get("/depreciation/asset/{asset_id}", response_model=List[AssetDepreciationResponse])
def get_depreciation_schedule(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get depreciation schedule for an asset"""
    return DepreciationService.get_depreciation_schedule(
        db=db,
        tenant_id=current_user["tenant_id"],
        asset_id=asset_id
    )


@router.post("/depreciation/{depreciation_id}/reverse")
def reverse_depreciation(
    depreciation_id: int,
    reason: str = Query(..., description="Reason for reversal"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reverse a depreciation entry"""
    result = DepreciationService.reverse_depreciation(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        depreciation_id=depreciation_id,
        reason=reason
    )
    return {"message": "Depreciation reversed successfully", "success": result}


@router.get("/depreciation/report/{financial_year}", response_model=DepreciationReport)
def get_depreciation_report(
    financial_year: int,
    financial_month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate depreciation report"""
    return DepreciationService.get_depreciation_report(
        db=db,
        tenant_id=current_user["tenant_id"],
        financial_year=financial_year,
        financial_month=financial_month
    )


# ============================================================================
# MAINTENANCE ENDPOINTS
# ============================================================================

@router.post("/maintenance", response_model=AssetMaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    maintenance_data: AssetMaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a maintenance record"""
    return MaintenanceService.create_maintenance(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        maintenance_data=maintenance_data
    )


@router.get("/maintenance/{maintenance_id}", response_model=AssetMaintenanceResponse)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get maintenance record by ID"""
    maintenance = MaintenanceService.get_maintenance(
        db=db,
        tenant_id=current_user["tenant_id"],
        maintenance_id=maintenance_id
    )
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    return maintenance


@router.put("/maintenance/{maintenance_id}", response_model=AssetMaintenanceResponse)
def update_maintenance(
    maintenance_id: int,
    maintenance_data: AssetMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update maintenance record"""
    return MaintenanceService.update_maintenance(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        maintenance_id=maintenance_id,
        maintenance_data=maintenance_data
    )


@router.post("/maintenance/{maintenance_id}/approve", response_model=AssetMaintenanceResponse)
def approve_maintenance(
    maintenance_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve a maintenance request"""
    return MaintenanceService.approve_maintenance(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        maintenance_id=maintenance_id,
        approval_notes=approval_notes
    )


@router.get("/maintenance", response_model=PaginatedResponse)
def list_maintenance(
    asset_id: Optional[int] = None,
    status: Optional[MaintenanceStatusEnum] = None,
    maintenance_type: Optional[MaintenanceTypeEnum] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List maintenance records"""
    maintenance_records, total = MaintenanceService.list_maintenance(
        db=db,
        tenant_id=current_user["tenant_id"],
        asset_id=asset_id,
        status=status,
        maintenance_type=maintenance_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": maintenance_records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/maintenance/upcoming/schedule", response_model=List[AssetMaintenanceResponse])
def get_upcoming_maintenance(
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get upcoming scheduled maintenance"""
    return MaintenanceService.get_upcoming_maintenance(
        db=db,
        tenant_id=current_user["tenant_id"],
        days_ahead=days_ahead
    )


@router.get("/maintenance/report/period", response_model=MaintenanceReport)
def get_maintenance_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate maintenance report"""
    return MaintenanceService.get_maintenance_report(
        db=db,
        tenant_id=current_user["tenant_id"],
        from_date=from_date,
        to_date=to_date
    )


# ============================================================================
# TRANSFER ENDPOINTS
# ============================================================================

@router.post("/transfers", response_model=AssetTransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    transfer_data: AssetTransferCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create an asset transfer"""
    return TransferService.create_transfer(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        transfer_data=transfer_data
    )


@router.get("/transfers/{transfer_id}", response_model=AssetTransferResponse)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get transfer by ID"""
    transfer = TransferService.get_transfer(
        db=db,
        tenant_id=current_user["tenant_id"],
        transfer_id=transfer_id
    )
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    return transfer


@router.put("/transfers/{transfer_id}", response_model=AssetTransferResponse)
def update_transfer(
    transfer_id: int,
    transfer_data: AssetTransferUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update transfer details"""
    return TransferService.update_transfer(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        transfer_id=transfer_id,
        transfer_data=transfer_data
    )


@router.post("/transfers/{transfer_id}/approve", response_model=AssetTransferResponse)
def approve_transfer(
    transfer_id: int,
    approval: AssetTransferApproval,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject a transfer"""
    return TransferService.approve_transfer(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        transfer_id=transfer_id,
        approval=approval
    )


@router.post("/transfers/{transfer_id}/in-transit", response_model=AssetTransferResponse)
def mark_transfer_in_transit(
    transfer_id: int,
    handover_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark transfer as in transit"""
    return TransferService.mark_in_transit(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        transfer_id=transfer_id,
        handover_date=handover_date
    )


@router.post("/transfers/{transfer_id}/complete", response_model=AssetTransferResponse)
def complete_transfer(
    transfer_id: int,
    received_date: date = Query(...),
    condition_at_receipt: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Complete a transfer"""
    return TransferService.complete_transfer(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        transfer_id=transfer_id,
        received_date=received_date,
        condition_at_receipt=condition_at_receipt,
        notes=notes
    )


@router.post("/transfers/{transfer_id}/cancel", response_model=AssetTransferResponse)
def cancel_transfer(
    transfer_id: int,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel a transfer"""
    return TransferService.cancel_transfer(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        transfer_id=transfer_id,
        reason=reason
    )


@router.get("/transfers", response_model=PaginatedResponse)
def list_transfers(
    asset_id: Optional[int] = None,
    status: Optional[TransferStatusEnum] = None,
    from_location_id: Optional[int] = None,
    to_location_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List transfers"""
    transfers, total = TransferService.list_transfers(
        db=db,
        tenant_id=current_user["tenant_id"],
        asset_id=asset_id,
        status=status,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": transfers,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


# ============================================================================
# VERIFICATION ENDPOINTS
# ============================================================================

@router.post("/verification/cycles", response_model=VerificationCycleResponse, status_code=status.HTTP_201_CREATED)
def create_verification_cycle(
    cycle_data: VerificationCycleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a verification cycle"""
    return VerificationService.create_verification_cycle(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        cycle_data=cycle_data
    )


@router.post("/verification/cycles/{cycle_id}/start", response_model=VerificationCycleResponse)
def start_verification_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start a verification cycle"""
    return VerificationService.start_verification_cycle(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        cycle_id=cycle_id
    )


@router.post("/verification/cycles/{cycle_id}/complete", response_model=VerificationCycleResponse)
def complete_verification_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Complete a verification cycle"""
    return VerificationService.complete_verification_cycle(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        cycle_id=cycle_id
    )


@router.get("/verification/cycles/{cycle_id}", response_model=VerificationCycleResponse)
def get_verification_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get verification cycle by ID"""
    cycle = VerificationService.get_cycle(
        db=db,
        tenant_id=current_user["tenant_id"],
        cycle_id=cycle_id
    )
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification cycle not found"
        )
    return cycle


@router.get("/verification/cycles", response_model=PaginatedResponse)
def list_verification_cycles(
    financial_year: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List verification cycles"""
    cycles, total = VerificationService.list_cycles(
        db=db,
        tenant_id=current_user["tenant_id"],
        financial_year=financial_year,
        status=status,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": cycles,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.post("/verification", response_model=AssetVerificationResponse, status_code=status.HTTP_201_CREATED)
def create_verification(
    verification_data: AssetVerificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a verification record"""
    return VerificationService.create_verification(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"],
        verification_data=verification_data
    )


@router.get("/verification", response_model=PaginatedResponse)
def list_verifications(
    cycle_id: Optional[int] = None,
    asset_id: Optional[int] = None,
    verification_status: Optional[VerificationStatusEnum] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List verification records"""
    verifications, total = VerificationService.list_verifications(
        db=db,
        tenant_id=current_user["tenant_id"],
        cycle_id=cycle_id,
        asset_id=asset_id,
        verification_status=verification_status,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": verifications,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/verification/cycles/{cycle_id}/unverified-assets", response_model=PaginatedResponse)
def get_unverified_assets(
    cycle_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get unverified assets in a cycle"""
    assets, total = VerificationService.get_unverified_assets(
        db=db,
        tenant_id=current_user["tenant_id"],
        cycle_id=cycle_id,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": assets,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/verification/cycles/{cycle_id}/report")
def get_verification_report(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate verification report"""
    return VerificationService.get_verification_report(
        db=db,
        tenant_id=current_user["tenant_id"],
        cycle_id=cycle_id
    )
