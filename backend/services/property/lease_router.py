"""
Lease Management Router
API endpoints for lease agreements and tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from backend.shared.database.connection import get_db
from backend.shared.database.property_rent_models import Lease, Property, SpaceAllocation, PropertySpace, RentPayment
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/leases", tags=["Property Management - Leases"])


# ============================================
# PYDANTIC SCHEMAS
# ============================================

class LeaseCreate(BaseModel):
    property_id: int
    lease_type: str
    lessee_type: str
    lessee_name: str
    lessee_contact: str
    lessee_email: Optional[str] = None
    lessee_address: Optional[str] = None
    lessee_id_proof_type: Optional[str] = None
    lessee_id_proof_number: Optional[str] = None
    lease_start_date: date
    lease_duration_months: int
    monthly_rent: float
    maintenance_charges: Optional[float] = 0
    other_charges: Optional[float] = 0
    rent_due_day: int = 5
    payment_frequency: str = "monthly"
    advance_months: int = 0
    security_deposit: float
    escalation_applicable: bool = False
    escalation_percentage: Optional[float] = None
    escalation_frequency_months: Optional[int] = None
    agreement_date: date
    registration_number: Optional[str] = None
    registration_date: Optional[date] = None
    stamp_duty_paid: Optional[float] = None
    terms_conditions: Optional[str] = None
    special_clauses: Optional[str] = None
    lock_in_period_months: Optional[int] = None
    notice_period_days: int = 30
    electricity_included: bool = False
    water_included: bool = False
    gas_included: bool = False
    space_ids: List[int] = []


class LeaseUpdate(BaseModel):
    lessee_name: Optional[str] = None
    lessee_contact: Optional[str] = None
    lessee_email: Optional[str] = None
    lessee_address: Optional[str] = None
    monthly_rent: Optional[float] = None
    maintenance_charges: Optional[float] = None
    other_charges: Optional[float] = None
    security_deposit: Optional[float] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


# ============================================
# CRUD ENDPOINTS
# ============================================

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_lease(
    lease_data: LeaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lease agreement"""
    
    # Generate lease number
    count_result = await db.execute(
        select(func.count(Lease.id)).where(Lease.tenant_id == current_user.tenant_id)
    )
    count = count_result.scalar() or 0
    lease_number = f"LSE-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
    
    # Calculate lease end date
    lease_end_date = lease_data.lease_start_date + relativedelta(months=lease_data.lease_duration_months)
    
    # Calculate total monthly payment
    total_monthly = lease_data.monthly_rent + (lease_data.maintenance_charges or 0) + (lease_data.other_charges or 0)
    
    # Calculate lock-in end date
    lock_in_end_date = None
    if lease_data.lock_in_period_months:
        lock_in_end_date = lease_data.lease_start_date + relativedelta(months=lease_data.lock_in_period_months)
    
    # Calculate next escalation date
    next_escalation_date = None
    if lease_data.escalation_applicable and lease_data.escalation_frequency_months:
        next_escalation_date = lease_data.lease_start_date + relativedelta(months=lease_data.escalation_frequency_months)
    
    # Create lease
    lease_dict = lease_data.model_dump(exclude={'space_ids'})
    lease_obj = Lease(
        tenant_id=current_user.tenant_id,
        lease_number=lease_number,
        lease_end_date=lease_end_date,
        total_monthly_payment=total_monthly,
        lock_in_end_date=lock_in_end_date,
        next_escalation_date=next_escalation_date,
        created_by=current_user.id,
        **lease_dict
    )
    
    db.add(lease_obj)
    await db.flush()
    
    # Create space allocations
    if lease_data.space_ids:
        for space_id in lease_data.space_ids:
            allocation = SpaceAllocation(
                tenant_id=current_user.tenant_id,
                lease_id=lease_obj.id,
                space_id=space_id,
                allocation_date=lease_data.lease_start_date,
                created_by=current_user.id
            )
            db.add(allocation)
            
            # Update space status
            space_result = await db.execute(select(PropertySpace).where(PropertySpace.id == space_id))
            space = space_result.scalar_one_or_none()
            if space:
                space.status = 'occupied'
                space.current_lease_id = lease_obj.id
                space.occupancy_start_date = lease_data.lease_start_date
    
    await db.commit()
    await db.refresh(lease_obj)
    
    return {
        "success": True,
        "message": "Lease created successfully",
        "data": {
            "id": lease_obj.id,
            "lease_number": lease_obj.lease_number
        }
    }


@router.get("", response_model=dict)
async def get_leases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    property_id: Optional[int] = None,
    lease_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all leases with filtering and pagination"""
    
    query = select(Lease).where(
        and_(
            Lease.tenant_id == current_user.tenant_id,
            Lease.is_deleted == False
        )
    )
    
    if search:
        search_filter = or_(
            Lease.lease_number.ilike(f"%{search}%"),
            Lease.lessee_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if status:
        query = query.where(Lease.status == status)
    
    if property_id:
        query = query.where(Lease.property_id == property_id)
    
    if lease_type:
        query = query.where(Lease.lease_type == lease_type)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Lease.created_at.desc())
    
    result = await db.execute(query)
    leases = result.scalars().all()
    
    # Enrich with property names
    items = []
    for lease in leases:
        property_result = await db.execute(select(Property).where(Property.id == lease.property_id))
        property_obj = property_result.scalar_one_or_none()
        
        items.append({
            "id": lease.id,
            "lease_number": lease.lease_number,
            "lessee_name": lease.lessee_name,
            "lessee_contact": lease.lessee_contact,
            "property_name": property_obj.property_name if property_obj else None,
            "lease_type": lease.lease_type,
            "lease_start_date": lease.lease_start_date.isoformat(),
            "lease_end_date": lease.lease_end_date.isoformat(),
            "monthly_rent": float(lease.monthly_rent),
            "total_monthly_payment": float(lease.total_monthly_payment),
            "security_deposit": float(lease.security_deposit),
            "status": lease.status,
            "created_at": lease.created_at.isoformat()
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


@router.get("/{lease_id}", response_model=dict)
async def get_lease(
    lease_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lease details by ID"""
    
    result = await db.execute(
        select(Lease).where(
            and_(
                Lease.id == lease_id,
                Lease.tenant_id == current_user.tenant_id,
                Lease.is_deleted == False
            )
        )
    )
    lease = result.scalar_one_or_none()
    
    if not lease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found")
    
    # Get property
    property_result = await db.execute(select(Property).where(Property.id == lease.property_id))
    property_obj = property_result.scalar_one_or_none()
    
    # Get allocated spaces
    spaces_result = await db.execute(
        select(SpaceAllocation, PropertySpace)
        .join(PropertySpace, PropertySpace.id == SpaceAllocation.space_id)
        .where(
            and_(
                SpaceAllocation.lease_id == lease_id,
                SpaceAllocation.is_deleted == False
            )
        )
    )
    spaces = []
    for allocation, space in spaces_result.all():
        spaces.append({
            "id": space.id,
            "space_code": space.space_code,
            "space_name": space.space_name,
            "area": float(space.area),
            "allocation_date": allocation.allocation_date.isoformat()
        })
    
    # Get payment summary
    payment_result = await db.execute(
        select(
            func.count(RentPayment.id).label('total_payments'),
            func.sum(RentPayment.paid_amount).label('total_paid'),
            func.sum(RentPayment.outstanding_amount).label('total_outstanding')
        ).where(
            and_(
                RentPayment.lease_id == lease_id,
                RentPayment.is_deleted == False
            )
        )
    )
    payment_stats = payment_result.first()
    
    lease_dict = {
        "id": lease.id,
        "lease_number": lease.lease_number,
        "property_id": lease.property_id,
        "property_name": property_obj.property_name if property_obj else None,
        "lease_type": lease.lease_type,
        "lessee_type": lease.lessee_type,
        "lessee_name": lease.lessee_name,
        "lessee_contact": lease.lessee_contact,
        "lessee_email": lease.lessee_email,
        "lessee_address": lease.lessee_address,
        "lease_start_date": lease.lease_start_date.isoformat(),
        "lease_end_date": lease.lease_end_date.isoformat(),
        "lease_duration_months": lease.lease_duration_months,
        "monthly_rent": float(lease.monthly_rent),
        "maintenance_charges": float(lease.maintenance_charges) if lease.maintenance_charges else 0,
        "other_charges": float(lease.other_charges) if lease.other_charges else 0,
        "total_monthly_payment": float(lease.total_monthly_payment),
        "rent_due_day": lease.rent_due_day,
        "payment_frequency": lease.payment_frequency,
        "advance_months": lease.advance_months,
        "security_deposit": float(lease.security_deposit),
        "escalation_applicable": lease.escalation_applicable,
        "escalation_percentage": float(lease.escalation_percentage) if lease.escalation_percentage else None,
        "agreement_date": lease.agreement_date.isoformat(),
        "status": lease.status,
        "allocated_spaces": spaces,
        "payment_summary": {
            "total_payments": payment_stats.total_payments or 0,
            "total_paid": float(payment_stats.total_paid or 0),
            "total_outstanding": float(payment_stats.total_outstanding or 0)
        },
        "created_at": lease.created_at.isoformat()
    }
    
    return {
        "success": True,
        "data": lease_dict
    }


@router.put("/{lease_id}", response_model=dict)
async def update_lease(
    lease_id: int,
    lease_data: LeaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update lease details"""
    
    result = await db.execute(
        select(Lease).where(
            and_(
                Lease.id == lease_id,
                Lease.tenant_id == current_user.tenant_id,
                Lease.is_deleted == False
            )
        )
    )
    lease = result.scalar_one_or_none()
    
    if not lease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found")
    
    update_data = lease_data.model_dump(exclude_unset=True)
    
    # Recalculate total if rent components changed
    if any(k in update_data for k in ['monthly_rent', 'maintenance_charges', 'other_charges']):
        monthly_rent = update_data.get('monthly_rent', lease.monthly_rent)
        maintenance = update_data.get('maintenance_charges', lease.maintenance_charges or 0)
        other = update_data.get('other_charges', lease.other_charges or 0)
        update_data['total_monthly_payment'] = monthly_rent + maintenance + other
    
    for field, value in update_data.items():
        setattr(lease, field, value)
    
    lease.updated_by = current_user.id
    lease.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Lease updated successfully"
    }


@router.post("/{lease_id}/terminate", response_model=dict)
async def terminate_lease(
    lease_id: int,
    termination_reason: str,
    termination_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Terminate a lease"""
    
    result = await db.execute(
        select(Lease).where(
            and_(
                Lease.id == lease_id,
                Lease.tenant_id == current_user.tenant_id,
                Lease.is_deleted == False
            )
        )
    )
    lease = result.scalar_one_or_none()
    
    if not lease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found")
    
    if lease.status != 'active':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only active leases can be terminated")
    
    lease.status = 'terminated'
    lease.termination_date = termination_date
    lease.termination_reason = termination_reason
    lease.updated_by = current_user.id
    lease.updated_at = datetime.utcnow()
    
    # Update space allocations
    allocations_result = await db.execute(
        select(SpaceAllocation).where(
            and_(
                SpaceAllocation.lease_id == lease_id,
                SpaceAllocation.status == 'active'
            )
        )
    )
    for allocation in allocations_result.scalars().all():
        allocation.status = 'inactive'
        allocation.vacated_date = termination_date
        
        # Update space status
        space_result = await db.execute(select(PropertySpace).where(PropertySpace.id == allocation.space_id))
        space = space_result.scalar_one_or_none()
        if space:
            space.status = 'available'
            space.current_lease_id = None
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Lease terminated successfully"
    }


@router.get("/dashboard/statistics", response_model=dict)
async def get_lease_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lease dashboard statistics"""
    
    # Active leases
    active_result = await db.execute(
        select(func.count(Lease.id)).where(
            and_(
                Lease.tenant_id == current_user.tenant_id,
                Lease.status == 'active',
                Lease.is_deleted == False
            )
        )
    )
    active_leases = active_result.scalar()
    
    # Expiring soon (next 60 days)
    expiring_date = date.today() + relativedelta(days=60)
    expiring_result = await db.execute(
        select(func.count(Lease.id)).where(
            and_(
                Lease.tenant_id == current_user.tenant_id,
                Lease.status == 'active',
                Lease.lease_end_date <= expiring_date,
                Lease.is_deleted == False
            )
        )
    )
    expiring_soon = expiring_result.scalar()
    
    # Total monthly revenue
    revenue_result = await db.execute(
        select(func.sum(Lease.total_monthly_payment)).where(
            and_(
                Lease.tenant_id == current_user.tenant_id,
                Lease.status == 'active',
                Lease.is_deleted == False
            )
        )
    )
    total_revenue = revenue_result.scalar() or 0
    
    return {
        "success": True,
        "data": {
            "active_leases": active_leases,
            "expiring_soon": expiring_soon,
            "total_monthly_revenue": float(total_revenue)
        }
    }
