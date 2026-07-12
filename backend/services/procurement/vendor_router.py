"""
Vendor Management API Router
FastAPI endpoints for vendor operations
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user
from backend.services.procurement.vendor_service import VendorService
from backend.services.procurement import schemas
from backend.shared.database.procurement_models import VendorStatus, VendorType


router = APIRouter(prefix="/vendors", tags=["Vendors"])


def get_vendor_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> VendorService:
    """Dependency to get vendor service"""
    return VendorService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=uuid.UUID(current_user["id"])
    )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: schemas.VendorCreate,
    service: VendorService = Depends(get_vendor_service)
):
    """Create new vendor"""
    try:
        vendor = await service.create_vendor(vendor_data)
        return success_response(
            data=schemas.VendorResponse.from_orm(vendor),
            message="Vendor created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vendor: {str(e)}")


@router.get("/{vendor_id}", response_model=dict)
async def get_vendor(
    vendor_id: uuid.UUID,
    service: VendorService = Depends(get_vendor_service)
):
    """Get vendor by ID"""
    try:
        vendor = await service.get_vendor(vendor_id)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return success_response(data=schemas.VendorResponse.from_orm(vendor))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("", response_model=dict)
async def list_vendors(
    status: Optional[VendorStatus] = None,
    vendor_type: Optional[VendorType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: VendorService = Depends(get_vendor_service)
):
    """List vendors with filters"""
    try:
        skip = (page - 1) * page_size
        vendors, total = await service.list_vendors(
            status=status,
            vendor_type=vendor_type,
            search=search,
            skip=skip,
            limit=page_size
        )
        
        return success_response(
            data=schemas.VendorListResponse(
                vendors=[schemas.VendorResponse.from_orm(v) for v in vendors],
                total=total,
                page=page,
                page_size=page_size
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{vendor_id}", response_model=dict)
async def update_vendor(
    vendor_id: uuid.UUID,
    vendor_data: schemas.VendorUpdate,
    service: VendorService = Depends(get_vendor_service)
):
    """Update vendor"""
    try:
        vendor = await service.update_vendor(vendor_id, vendor_data)
        return success_response(
            data=schemas.VendorResponse.from_orm(vendor),
            message="Vendor updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{vendor_id}", response_model=dict)
async def delete_vendor(
    vendor_id: uuid.UUID,
    service: VendorService = Depends(get_vendor_service)
):
    """Delete vendor"""
    try:
        await service.delete_vendor(vendor_id)
        return success_response(message="Vendor deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{vendor_id}/ratings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vendor_rating(
    vendor_id: uuid.UUID,
    rating_data: schemas.VendorRatingCreate,
    service: VendorService = Depends(get_vendor_service),
    current_user: dict = Depends(get_current_user)
):
    """Create vendor rating"""
    try:
        rating = await service.create_vendor_rating(
            rating_data,
            rated_by_name=current_user.get("name", "Unknown")
        )
        return success_response(
            data=schemas.VendorRatingResponse.from_orm(rating),
            message="Vendor rating created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/dashboard", response_model=dict)
async def get_vendor_statistics(
    service: VendorService = Depends(get_vendor_service)
):
    """Get vendor statistics for dashboard"""
    try:
        stats = await service.get_vendor_statistics()
        return success_response(data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
