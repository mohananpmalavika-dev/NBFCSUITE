"""
Space Allocation Router
API endpoints for property space management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.shared.database.property_rent_models import PropertySpace, Property, SpaceAllocation
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/property-spaces", tags=["Property Management - Spaces"])


class PropertySpaceCreate(BaseModel):
    property_id: int
    space_code: str
    space_name: str
    space_type: str
    floor_number: Optional[int] = None
    unit_number: Optional[str] = None
    area: float
    area_unit: str = "sq_ft"
    base_rent: float
    maintenance_charges: Optional[float] = 0
    security_deposit: float
    furnishing_status: Optional[str] = None
    amenities: Optional[dict] = None
    description: Optional[str] = None


class PropertySpaceUpdate(BaseModel):
    space_name: Optional[str] = None
    base_rent: Optional[float] = None
    maintenance_charges: Optional[float] = None
    security_deposit: Optional[float] = None
    furnishing_status: Optional[str] = None
    amenities: Optional[dict] = None
    status: Optional[str] = None
    description: Optional[str] = None


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_property_space(
    space_data: PropertySpaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new property space/unit"""
    
    # Check if space code already exists
    result = await db.execute(
        select(PropertySpace).where(
            and_(
                PropertySpace.space_code == space_data.space_code,
                PropertySpace.is_deleted == False
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Space with code {space_data.space_code} already exists"
        )
    
    space = PropertySpace(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **space_data.model_dump()
    )
    
    db.add(space)
    await db.commit()
    await db.refresh(space)
    
    return {
        "success": True,
        "message": "Property space created successfully",
        "data": {"id": space.id, "space_code": space.space_code}
    }


@router.get("", response_model=dict)
async def get_property_spaces(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    property_id: Optional[int] = None,
    status: Optional[str] = None,
    space_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get property spaces with filtering"""
    
    query = select(PropertySpace).where(
        and_(
            PropertySpace.tenant_id == current_user.tenant_id,
            PropertySpace.is_deleted == False
        )
    )
    
    if property_id:
        query = query.where(PropertySpace.property_id == property_id)
    if status:
        query = query.where(PropertySpace.status == status)
    if space_type:
        query = query.where(PropertySpace.space_type == space_type)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(PropertySpace.created_at.desc())
    
    result = await db.execute(query)
    spaces = result.scalars().all()
    
    items = []
    for space in spaces:
        property_result = await db.execute(select(Property).where(Property.id == space.property_id))
        property_obj = property_result.scalar_one_or_none()
        
        items.append({
            "id": space.id,
            "space_code": space.space_code,
            "space_name": space.space_name,
            "property_name": property_obj.property_name if property_obj else None,
            "space_type": space.space_type,
            "floor_number": space.floor_number,
            "area": float(space.area),
            "area_unit": space.area_unit,
            "base_rent": float(space.base_rent),
            "status": space.status,
            "furnishing_status": space.furnishing_status
        })
    
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/{space_id}", response_model=dict)
async def get_property_space(
    space_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get property space details"""
    
    result = await db.execute(
        select(PropertySpace).where(
            and_(
                PropertySpace.id == space_id,
                PropertySpace.tenant_id == current_user.tenant_id,
                PropertySpace.is_deleted == False
            )
        )
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(status_code=404, detail="Property space not found")
    
    property_result = await db.execute(select(Property).where(Property.id == space.property_id))
    property_obj = property_result.scalar_one_or_none()
    
    return {
        "success": True,
        "data": {
            "id": space.id,
            "space_code": space.space_code,
            "space_name": space.space_name,
            "property_id": space.property_id,
            "property_name": property_obj.property_name if property_obj else None,
            "space_type": space.space_type,
            "floor_number": space.floor_number,
            "unit_number": space.unit_number,
            "area": float(space.area),
            "area_unit": space.area_unit,
            "base_rent": float(space.base_rent),
            "maintenance_charges": float(space.maintenance_charges) if space.maintenance_charges else 0,
            "security_deposit": float(space.security_deposit),
            "furnishing_status": space.furnishing_status,
            "amenities": space.amenities,
            "status": space.status,
            "description": space.description,
            "created_at": space.created_at.isoformat()
        }
    }


@router.put("/{space_id}", response_model=dict)
async def update_property_space(
    space_id: int,
    space_data: PropertySpaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update property space details"""
    
    result = await db.execute(
        select(PropertySpace).where(
            and_(
                PropertySpace.id == space_id,
                PropertySpace.tenant_id == current_user.tenant_id,
                PropertySpace.is_deleted == False
            )
        )
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(status_code=404, detail="Property space not found")
    
    update_data = space_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(space, field, value)
    
    space.updated_by = current_user.id
    space.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Property space updated successfully"
    }


@router.get("/dashboard/statistics", response_model=dict)
async def get_space_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get space allocation statistics"""
    
    # Total spaces
    total_result = await db.execute(
        select(func.count(PropertySpace.id)).where(
            and_(
                PropertySpace.tenant_id == current_user.tenant_id,
                PropertySpace.is_deleted == False
            )
        )
    )
    total_spaces = total_result.scalar()
    
    # Spaces by status
    status_result = await db.execute(
        select(
            PropertySpace.status,
            func.count(PropertySpace.id)
        ).where(
            and_(
                PropertySpace.tenant_id == current_user.tenant_id,
                PropertySpace.is_deleted == False
            )
        ).group_by(PropertySpace.status)
    )
    spaces_by_status = {row[0]: row[1] for row in status_result.all()}
    
    # Occupancy rate
    occupied = spaces_by_status.get('occupied', 0)
    occupancy_rate = (occupied / total_spaces * 100) if total_spaces > 0 else 0
    
    return {
        "success": True,
        "data": {
            "total_spaces": total_spaces,
            "spaces_by_status": spaces_by_status,
            "occupancy_rate": round(occupancy_rate, 2)
        }
    }
