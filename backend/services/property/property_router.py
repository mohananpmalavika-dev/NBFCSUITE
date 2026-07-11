"""
Property Master Router
API endpoints for property management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime, date

from backend.shared.database.connection import get_db
from backend.shared.database.property_rent_models import Property, PropertySpace, Lease
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/properties", tags=["Property Management - Properties"])


# ============================================
# PYDANTIC SCHEMAS
# ============================================

class PropertyCreate(BaseModel):
    property_code: str
    property_name: str
    property_type: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    pincode: str
    landmark: Optional[str] = None
    total_area: float
    area_unit: str = "sq_ft"
    built_up_area: Optional[float] = None
    carpet_area: Optional[float] = None
    floors_count: Optional[int] = None
    year_built: Optional[int] = None
    ownership_type: str
    owner_name: Optional[str] = None
    owner_contact: Optional[str] = None
    owner_email: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_value: Optional[float] = None
    current_market_value: Optional[float] = None
    registration_number: Optional[str] = None
    survey_number: Optional[str] = None
    khata_number: Optional[str] = None
    electricity_connection: bool = False
    electricity_consumer_number: Optional[str] = None
    water_connection: bool = False
    water_consumer_number: Optional[str] = None
    gas_connection: bool = False
    gas_consumer_number: Optional[str] = None
    amenities: Optional[dict] = None
    features: Optional[dict] = None
    annual_property_tax: Optional[float] = None
    annual_maintenance: Optional[float] = None
    insurance_premium: Optional[float] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[date] = None
    caretaker_name: Optional[str] = None
    caretaker_contact: Optional[str] = None
    description: Optional[str] = None
    remarks: Optional[str] = None


class PropertyUpdate(BaseModel):
    property_name: Optional[str] = None
    property_type: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None
    total_area: Optional[float] = None
    built_up_area: Optional[float] = None
    carpet_area: Optional[float] = None
    floors_count: Optional[int] = None
    year_built: Optional[int] = None
    owner_name: Optional[str] = None
    owner_contact: Optional[str] = None
    owner_email: Optional[str] = None
    current_market_value: Optional[float] = None
    electricity_consumer_number: Optional[str] = None
    water_consumer_number: Optional[str] = None
    gas_consumer_number: Optional[str] = None
    amenities: Optional[dict] = None
    features: Optional[dict] = None
    annual_property_tax: Optional[float] = None
    annual_maintenance: Optional[float] = None
    insurance_premium: Optional[float] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[date] = None
    status: Optional[str] = None
    occupancy_status: Optional[str] = None
    caretaker_name: Optional[str] = None
    caretaker_contact: Optional[str] = None
    description: Optional[str] = None
    remarks: Optional[str] = None


class PropertyResponse(BaseModel):
    id: int
    property_code: str
    property_name: str
    property_type: str
    address_line1: str
    city: str
    state: str
    pincode: str
    total_area: float
    area_unit: str
    ownership_type: str
    status: str
    occupancy_status: str
    current_market_value: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# CRUD ENDPOINTS
# ============================================

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new property"""
    
    # Check if property code already exists
    result = await db.execute(
        select(Property).where(
            and_(
                Property.property_code == property_data.property_code,
                Property.is_deleted == False
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Property with code {property_data.property_code} already exists"
        )
    
    # Create property
    property_obj = Property(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **property_data.model_dump()
    )
    
    db.add(property_obj)
    await db.commit()
    await db.refresh(property_obj)
    
    return {
        "success": True,
        "message": "Property created successfully",
        "data": {
            "id": property_obj.id,
            "property_code": property_obj.property_code,
            "property_name": property_obj.property_name
        }
    }


@router.get("", response_model=dict)
async def get_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    property_type: Optional[str] = None,
    status: Optional[str] = None,
    occupancy_status: Optional[str] = None,
    city: Optional[str] = None,
    ownership_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all properties with filtering and pagination"""
    
    # Base query
    query = select(Property).where(
        and_(
            Property.tenant_id == current_user.tenant_id,
            Property.is_deleted == False
        )
    )
    
    # Apply filters
    if search:
        search_filter = or_(
            Property.property_code.ilike(f"%{search}%"),
            Property.property_name.ilike(f"%{search}%"),
            Property.address_line1.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if property_type:
        query = query.where(Property.property_type == property_type)
    
    if status:
        query = query.where(Property.status == status)
    
    if occupancy_status:
        query = query.where(Property.occupancy_status == occupancy_status)
    
    if city:
        query = query.where(Property.city.ilike(f"%{city}%"))
    
    if ownership_type:
        query = query.where(Property.ownership_type == ownership_type)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Property.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    properties = result.scalars().all()
    
    return {
        "success": True,
        "data": {
            "items": [PropertyResponse.model_validate(p) for p in properties],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/{property_id}", response_model=dict)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get property details by ID"""
    
    result = await db.execute(
        select(Property).where(
            and_(
                Property.id == property_id,
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False
            )
        )
    )
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Get spaces count
    spaces_result = await db.execute(
        select(func.count(PropertySpace.id)).where(
            and_(
                PropertySpace.property_id == property_id,
                PropertySpace.is_deleted == False
            )
        )
    )
    total_spaces = spaces_result.scalar()
    
    # Get active leases count
    leases_result = await db.execute(
        select(func.count(Lease.id)).where(
            and_(
                Lease.property_id == property_id,
                Lease.status == 'active',
                Lease.is_deleted == False
            )
        )
    )
    active_leases = leases_result.scalar()
    
    property_dict = {
        "id": property_obj.id,
        "tenant_id": property_obj.tenant_id,
        "property_code": property_obj.property_code,
        "property_name": property_obj.property_name,
        "property_type": property_obj.property_type,
        "address_line1": property_obj.address_line1,
        "address_line2": property_obj.address_line2,
        "city": property_obj.city,
        "state": property_obj.state,
        "country": property_obj.country,
        "pincode": property_obj.pincode,
        "landmark": property_obj.landmark,
        "total_area": float(property_obj.total_area) if property_obj.total_area else None,
        "area_unit": property_obj.area_unit,
        "built_up_area": float(property_obj.built_up_area) if property_obj.built_up_area else None,
        "carpet_area": float(property_obj.carpet_area) if property_obj.carpet_area else None,
        "floors_count": property_obj.floors_count,
        "year_built": property_obj.year_built,
        "ownership_type": property_obj.ownership_type,
        "owner_name": property_obj.owner_name,
        "owner_contact": property_obj.owner_contact,
        "owner_email": property_obj.owner_email,
        "purchase_date": property_obj.purchase_date.isoformat() if property_obj.purchase_date else None,
        "purchase_value": float(property_obj.purchase_value) if property_obj.purchase_value else None,
        "current_market_value": float(property_obj.current_market_value) if property_obj.current_market_value else None,
        "registration_number": property_obj.registration_number,
        "survey_number": property_obj.survey_number,
        "khata_number": property_obj.khata_number,
        "electricity_connection": property_obj.electricity_connection,
        "electricity_consumer_number": property_obj.electricity_consumer_number,
        "water_connection": property_obj.water_connection,
        "water_consumer_number": property_obj.water_consumer_number,
        "gas_connection": property_obj.gas_connection,
        "gas_consumer_number": property_obj.gas_consumer_number,
        "amenities": property_obj.amenities,
        "features": property_obj.features,
        "annual_property_tax": float(property_obj.annual_property_tax) if property_obj.annual_property_tax else None,
        "annual_maintenance": float(property_obj.annual_maintenance) if property_obj.annual_maintenance else None,
        "insurance_premium": float(property_obj.insurance_premium) if property_obj.insurance_premium else None,
        "insurance_policy_number": property_obj.insurance_policy_number,
        "insurance_expiry_date": property_obj.insurance_expiry_date.isoformat() if property_obj.insurance_expiry_date else None,
        "status": property_obj.status,
        "occupancy_status": property_obj.occupancy_status,
        "caretaker_name": property_obj.caretaker_name,
        "caretaker_contact": property_obj.caretaker_contact,
        "documents": property_obj.documents,
        "photos": property_obj.photos,
        "description": property_obj.description,
        "remarks": property_obj.remarks,
        "created_at": property_obj.created_at.isoformat(),
        "updated_at": property_obj.updated_at.isoformat() if property_obj.updated_at else None,
        "total_spaces": total_spaces,
        "active_leases": active_leases
    }
    
    return {
        "success": True,
        "data": property_dict
    }


@router.put("/{property_id}", response_model=dict)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update property details"""
    
    result = await db.execute(
        select(Property).where(
            and_(
                Property.id == property_id,
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False
            )
        )
    )
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Update fields
    update_data = property_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property_obj, field, value)
    
    property_obj.updated_by = current_user.id
    property_obj.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(property_obj)
    
    return {
        "success": True,
        "message": "Property updated successfully",
        "data": {
            "id": property_obj.id,
            "property_code": property_obj.property_code,
            "property_name": property_obj.property_name
        }
    }


@router.delete("/{property_id}", response_model=dict)
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a property"""
    
    result = await db.execute(
        select(Property).where(
            and_(
                Property.id == property_id,
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False
            )
        )
    )
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if property has active leases
    leases_result = await db.execute(
        select(func.count(Lease.id)).where(
            and_(
                Lease.property_id == property_id,
                Lease.status == 'active',
                Lease.is_deleted == False
            )
        )
    )
    active_leases = leases_result.scalar()
    
    if active_leases > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete property with {active_leases} active lease(s)"
        )
    
    # Soft delete
    property_obj.is_deleted = True
    property_obj.updated_by = current_user.id
    property_obj.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Property deleted successfully"
    }


# ============================================
# DASHBOARD & STATISTICS
# ============================================

@router.get("/dashboard/statistics", response_model=dict)
async def get_property_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get property management dashboard statistics"""
    
    # Total properties
    total_result = await db.execute(
        select(func.count(Property.id)).where(
            and_(
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False
            )
        )
    )
    total_properties = total_result.scalar()
    
    # Properties by status
    status_result = await db.execute(
        select(
            Property.status,
            func.count(Property.id)
        ).where(
            and_(
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False
            )
        ).group_by(Property.status)
    )
    properties_by_status = {row[0]: row[1] for row in status_result.all()}
    
    # Properties by occupancy
    occupancy_result = await db.execute(
        select(
            Property.occupancy_status,
            func.count(Property.id)
        ).where(
            and_(
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False
            )
        ).group_by(Property.occupancy_status)
    )
    properties_by_occupancy = {row[0]: row[1] for row in occupancy_result.all()}
    
    # Total property value
    value_result = await db.execute(
        select(func.sum(Property.current_market_value)).where(
            and_(
                Property.tenant_id == current_user.tenant_id,
                Property.is_deleted == False,
                Property.current_market_value.isnot(None)
            )
        )
    )
    total_value = value_result.scalar() or 0
    
    # Active leases
    leases_result = await db.execute(
        select(func.count(Lease.id)).where(
            and_(
                Lease.tenant_id == current_user.tenant_id,
                Lease.status == 'active',
                Lease.is_deleted == False
            )
        )
    )
    active_leases = leases_result.scalar()
    
    return {
        "success": True,
        "data": {
            "total_properties": total_properties,
            "properties_by_status": properties_by_status,
            "properties_by_occupancy": properties_by_occupancy,
            "total_property_value": float(total_value),
            "active_leases": active_leases
        }
    }
