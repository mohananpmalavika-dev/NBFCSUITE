"""
Rent Collection Router
API endpoints for rent payment tracking and collection
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from backend.shared.database.connection import get_db
from backend.shared.database.property_rent_models import RentPayment, Lease
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/rent-payments", tags=["Property Management - Rent Collection"])


class RentPaymentCreate(BaseModel):
    lease_id: int
    payment_month: str  # YYYY-MM
    rent_amount: float
    maintenance_amount: Optional[float] = 0
    other_charges: Optional[float] = 0
    late_fee: Optional[float] = 0
    discount_amount: Optional[float] = 0
    paid_amount: float
    payment_date: date
    payment_mode: str
    payment_reference: Optional[str] = None
    bank_name: Optional[str] = None
    tds_applicable: bool = False
    tds_amount: Optional[float] = 0
    remarks: Optional[str] = None


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_rent_payment(
    payment_data: RentPaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a rent payment"""
    
    # Generate payment number
    count_result = await db.execute(
        select(func.count(RentPayment.id)).where(RentPayment.tenant_id == current_user.tenant_id)
    )
    count = count_result.scalar() or 0
    payment_number = f"RENT-{datetime.now().strftime('%Y%m%d')}-{count + 1:04d}"
    
    # Get lease
    lease_result = await db.execute(select(Lease).where(Lease.id == payment_data.lease_id))
    lease = lease_result.scalar_one_or_none()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Calculate dates
    period_start = datetime.strptime(payment_data.payment_month, '%Y-%m').date()
    period_end = period_start + relativedelta(months=1, days=-1)
    due_date = period_start.replace(day=lease.rent_due_day)
    
    # Calculate total and outstanding
    total_amount = payment_data.rent_amount + payment_data.maintenance_amount + payment_data.other_charges + payment_data.late_fee - payment_data.discount_amount
    outstanding_amount = total_amount - payment_data.paid_amount
    
    # Determine status
    if payment_data.paid_amount >= total_amount:
        payment_status = 'paid'
    elif payment_data.paid_amount > 0:
        payment_status = 'partial'
    else:
        payment_status = 'pending'
    
    # Calculate days overdue
    days_overdue = max(0, (payment_data.payment_date - due_date).days) if payment_data.payment_date > due_date else 0
    
    payment = RentPayment(
        tenant_id=current_user.tenant_id,
        payment_number=payment_number,
        payment_period_start=period_start,
        payment_period_end=period_end,
        due_date=due_date,
        total_amount=total_amount,
        outstanding_amount=outstanding_amount,
        payment_status=payment_status,
        days_overdue=days_overdue,
        created_by=current_user.id,
        collected_by=current_user.id,
        **payment_data.model_dump()
    )
    
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    return {
        "success": True,
        "message": "Rent payment recorded successfully",
        "data": {"id": payment.id, "payment_number": payment.payment_number}
    }


@router.get("", response_model=dict)
async def get_rent_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    lease_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    payment_month: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rent payments with filtering"""
    
    query = select(RentPayment).where(
        and_(
            RentPayment.tenant_id == current_user.tenant_id,
            RentPayment.is_deleted == False
        )
    )
    
    if lease_id:
        query = query.where(RentPayment.lease_id == lease_id)
    if payment_status:
        query = query.where(RentPayment.payment_status == payment_status)
    if payment_month:
        query = query.where(RentPayment.payment_month == payment_month)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(RentPayment.created_at.desc())
    
    result = await db.execute(query)
    payments = result.scalars().all()
    
    items = []
    for payment in payments:
        lease_result = await db.execute(select(Lease).where(Lease.id == payment.lease_id))
        lease = lease_result.scalar_one_or_none()
        
        items.append({
            "id": payment.id,
            "payment_number": payment.payment_number,
            "lease_number": lease.lease_number if lease else None,
            "lessee_name": lease.lessee_name if lease else None,
            "payment_month": payment.payment_month,
            "due_date": payment.due_date.isoformat(),
            "total_amount": float(payment.total_amount),
            "paid_amount": float(payment.paid_amount),
            "outstanding_amount": float(payment.outstanding_amount),
            "payment_status": payment.payment_status,
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "days_overdue": payment.days_overdue
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


@router.get("/dashboard/statistics", response_model=dict)
async def get_rent_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rent collection statistics"""
    
    current_month = date.today().strftime('%Y-%m')
    
    # Current month collection
    current_result = await db.execute(
        select(
            func.sum(RentPayment.paid_amount).label('collected'),
            func.sum(RentPayment.total_amount).label('expected')
        ).where(
            and_(
                RentPayment.tenant_id == current_user.tenant_id,
                RentPayment.payment_month == current_month,
                RentPayment.is_deleted == False
            )
        )
    )
    current_stats = current_result.first()
    
    # Overdue payments
    overdue_result = await db.execute(
        select(
            func.count(RentPayment.id),
            func.sum(RentPayment.outstanding_amount)
        ).where(
            and_(
                RentPayment.tenant_id == current_user.tenant_id,
                RentPayment.payment_status.in_(['pending', 'partial']),
                RentPayment.due_date < date.today(),
                RentPayment.is_deleted == False
            )
        )
    )
    overdue_stats = overdue_result.first()
    
    return {
        "success": True,
        "data": {
            "current_month_collected": float(current_stats.collected or 0),
            "current_month_expected": float(current_stats.expected or 0),
            "overdue_count": overdue_stats[0] or 0,
            "overdue_amount": float(overdue_stats[1] or 0)
        }
    }
