"""
Property Maintenance Router
API endpoints for property maintenance tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional
from datetime import datetime, date

from backend.shared.database.connection import get_db
from backend.shared.database.property_rent_models import PropertyMaintenance, Property
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/property-maintenance", tags=["Property Management - Maintenance"])


class MaintenanceCreate(BaseModel):
    property_id: int
    space_id: Optional[int] = None
    maintenance_type: str
    issue_description: str
    category: Optional[str] = None
    priority: str = "medium"
    requested_by: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    estimated_cost: Optional[float] = None
    scheduled_date: Optional[date] = None
    remarks: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    issue_description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    vendor_amount: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    resolution_notes: Optional[str] = None
    customer_satisfaction: Optional[int] = None
    remarks: Optional[str] = None


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
    maintenance_data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a maintenance request"""
    
    count_result = await db.execute(
        select(func.count(PropertyMaintenance.id)).where(PropertyMaintenance.tenant_id == current_user.tenant_id)
    )
    count = count_result.scalar() or 0
    ticket_number = f"MAINT-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
    
    maintenance = PropertyMaintenance(
        tenant_id=current_user.tenant_id,
        ticket_number=ticket_number,
        request_date=date.today(),
        created_by=current_user.id,
        **maintenance_data.model_dump()
    )
    
    db.add(maintenance)
    await db.commit()
    await db.refresh(maintenance)
    
    return {
        "success": True,
        "message": "Maintenance request created successfully",
        "data": {"id": maintenance.id, "ticket_number": maintenance.ticket_number}
    }


@router.get("", response_model=dict)
async def get_maintenance_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    property_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    maintenance_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance requests with filtering"""
    
    query = select(PropertyMaintenance).where(
        and_(
            PropertyMaintenance.tenant_id == current_user.tenant_id,
            PropertyMaintenance.is_deleted == False
        )
    )
    
    if property_id:
        query = query.where(PropertyMaintenance.property_id == property_id)
    if status:
        query = query.where(PropertyMaintenance.status == status)
    if priority:
        query = query.where(PropertyMaintenance.priority == priority)
    if maintenance_type:
        query = query.where(PropertyMaintenance.maintenance_type == maintenance_type)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(PropertyMaintenance.request_date.desc())
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    items = []
    for req in requests:
        property_result = await db.execute(select(Property).where(Property.id == req.property_id))
        property_obj = property_result.scalar_one_or_none()
        
        items.append({
            "id": req.id,
            "ticket_number": req.ticket_number,
            "property_name": property_obj.property_name if property_obj else None,
            "maintenance_type": req.maintenance_type,
            "issue_description": req.issue_description,
            "priority": req.priority,
            "status": req.status,
            "request_date": req.request_date.isoformat(),
            "scheduled_date": req.scheduled_date.isoformat() if req.scheduled_date else None,
            "estimated_cost": float(req.estimated_cost) if req.estimated_cost else None
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


@router.get("/{maintenance_id}", response_model=dict)
async def get_maintenance_request(
    maintenance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance request details"""
    
    result = await db.execute(
        select(PropertyMaintenance).where(
            and_(
                PropertyMaintenance.id == maintenance_id,
                PropertyMaintenance.tenant_id == current_user.tenant_id,
                PropertyMaintenance.is_deleted == False
            )
        )
    )
    maintenance = result.scalar_one_or_none()
    
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    property_result = await db.execute(select(Property).where(Property.id == maintenance.property_id))
    property_obj = property_result.scalar_one_or_none()
    
    return {
        "success": True,
        "data": {
            "id": maintenance.id,
            "ticket_number": maintenance.ticket_number,
            "property_id": maintenance.property_id,
            "property_name": property_obj.property_name if property_obj else None,
            "maintenance_type": maintenance.maintenance_type,
            "issue_description": maintenance.issue_description,
            "category": maintenance.category,
            "priority": maintenance.priority,
            "request_date": maintenance.request_date.isoformat(),
            "requested_by": maintenance.requested_by,
            "status": maintenance.status,
            "vendor_name": maintenance.vendor_name,
            "vendor_contact": maintenance.vendor_contact,
            "vendor_amount": float(maintenance.vendor_amount) if maintenance.vendor_amount else None,
            "estimated_cost": float(maintenance.estimated_cost) if maintenance.estimated_cost else None,
            "actual_cost": float(maintenance.actual_cost) if maintenance.actual_cost else None,
            "scheduled_date": maintenance.scheduled_date.isoformat() if maintenance.scheduled_date else None,
            "completed_date": maintenance.completed_date.isoformat() if maintenance.completed_date else None,
            "resolution_notes": maintenance.resolution_notes,
            "customer_satisfaction": maintenance.customer_satisfaction,
            "remarks": maintenance.remarks,
            "created_at": maintenance.created_at.isoformat()
        }
    }


@router.put("/{maintenance_id}", response_model=dict)
async def update_maintenance_request(
    maintenance_id: int,
    maintenance_data: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance request"""
    
    result = await db.execute(
        select(PropertyMaintenance).where(
            and_(
                PropertyMaintenance.id == maintenance_id,
                PropertyMaintenance.tenant_id == current_user.tenant_id,
                PropertyMaintenance.is_deleted == False
            )
        )
    )
    maintenance = result.scalar_one_or_none()
    
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    update_data = maintenance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(maintenance, field, value)
    
    maintenance.updated_by = current_user.id
    maintenance.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Maintenance request updated successfully"
    }


@router.get("/dashboard/statistics", response_model=dict)
async def get_maintenance_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance statistics"""
    
    # Total requests
    total_result = await db.execute(
        select(func.count(PropertyMaintenance.id)).where(
            and_(
                PropertyMaintenance.tenant_id == current_user.tenant_id,
                PropertyMaintenance.is_deleted == False
            )
        )
    )
    total_requests = total_result.scalar()
    
    # By status
    status_result = await db.execute(
        select(
            PropertyMaintenance.status,
            func.count(PropertyMaintenance.id)
        ).where(
            and_(
                PropertyMaintenance.tenant_id == current_user.tenant_id,
                PropertyMaintenance.is_deleted == False
            )
        ).group_by(PropertyMaintenance.status)
    )
    requests_by_status = {row[0]: row[1] for row in status_result.all()}
    
    # Urgent requests
    urgent_result = await db.execute(
        select(func.count(PropertyMaintenance.id)).where(
            and_(
                PropertyMaintenance.tenant_id == current_user.tenant_id,
                PropertyMaintenance.priority == 'urgent',
                PropertyMaintenance.status.in_(['open', 'assigned', 'in_progress']),
                PropertyMaintenance.is_deleted == False
            )
        )
    )
    urgent_requests = urgent_result.scalar()
    
    return {
        "success": True,
        "data": {
            "total_requests": total_requests,
            "requests_by_status": requests_by_status,
            "urgent_requests": urgent_requests
        }
    }
