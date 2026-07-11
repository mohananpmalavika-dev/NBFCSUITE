"""
Utility Management Router
API endpoints for utility bill tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime, date

from backend.shared.database.connection import get_db
from backend.shared.database.property_rent_models import UtilityBill, Property
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/utility-bills", tags=["Property Management - Utilities"])


class UtilityBillCreate(BaseModel):
    property_id: int
    lease_id: Optional[int] = None
    utility_type: str
    bill_period_start: date
    bill_period_end: date
    bill_date: date
    due_date: date
    provider_name: Optional[str] = None
    consumer_number: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    fixed_charges: float = 0
    consumption_charges: float = 0
    tax_amount: float = 0
    other_charges: float = 0
    allocated_to_tenant: bool = False
    tenant_share_percentage: Optional[float] = None
    remarks: Optional[str] = None


class UtilityBillPayment(BaseModel):
    paid_amount: float
    payment_date: date
    payment_mode: str
    payment_reference: Optional[str] = None


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_utility_bill(
    bill_data: UtilityBillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a utility bill record"""
    
    count_result = await db.execute(
        select(func.count(UtilityBill.id)).where(UtilityBill.tenant_id == current_user.tenant_id)
    )
    count = count_result.scalar() or 0
    bill_number = f"UTIL-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
    
    # Calculate consumption units
    consumption_units = None
    if bill_data.current_reading and bill_data.previous_reading:
        consumption_units = bill_data.current_reading - bill_data.previous_reading
    
    # Calculate total amount
    total_amount = bill_data.fixed_charges + bill_data.consumption_charges + bill_data.tax_amount + bill_data.other_charges
    
    # Calculate tenant share
    tenant_share_amount = None
    if bill_data.allocated_to_tenant and bill_data.tenant_share_percentage:
        tenant_share_amount = total_amount * (bill_data.tenant_share_percentage / 100)
    
    bill_month = bill_data.bill_date.strftime('%Y-%m')
    
    bill = UtilityBill(
        tenant_id=current_user.tenant_id,
        bill_number=bill_number,
        bill_month=bill_month,
        consumption_units=consumption_units,
        total_amount=total_amount,
        tenant_share_amount=tenant_share_amount,
        created_by=current_user.id,
        **bill_data.model_dump()
    )
    
    db.add(bill)
    await db.commit()
    await db.refresh(bill)
    
    return {
        "success": True,
        "message": "Utility bill created successfully",
        "data": {"id": bill.id, "bill_number": bill.bill_number}
    }


@router.get("", response_model=dict)
async def get_utility_bills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    property_id: Optional[int] = None,
    utility_type: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get utility bills with filtering"""
    
    query = select(UtilityBill).where(
        and_(
            UtilityBill.tenant_id == current_user.tenant_id,
            UtilityBill.is_deleted == False
        )
    )
    
    if property_id:
        query = query.where(UtilityBill.property_id == property_id)
    if utility_type:
        query = query.where(UtilityBill.utility_type == utility_type)
    if payment_status:
        query = query.where(UtilityBill.payment_status == payment_status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(UtilityBill.bill_date.desc())
    
    result = await db.execute(query)
    bills = result.scalars().all()
    
    items = []
    for bill in bills:
        property_result = await db.execute(select(Property).where(Property.id == bill.property_id))
        property_obj = property_result.scalar_one_or_none()
        
        items.append({
            "id": bill.id,
            "bill_number": bill.bill_number,
            "property_name": property_obj.property_name if property_obj else None,
            "utility_type": bill.utility_type,
            "bill_month": bill.bill_month,
            "bill_date": bill.bill_date.isoformat(),
            "due_date": bill.due_date.isoformat(),
            "total_amount": float(bill.total_amount),
            "paid_amount": float(bill.paid_amount),
            "payment_status": bill.payment_status,
            "consumption_units": float(bill.consumption_units) if bill.consumption_units else None
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


@router.post("/{bill_id}/pay", response_model=dict)
async def record_payment(
    bill_id: int,
    payment_data: UtilityBillPayment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record payment for a utility bill"""
    
    result = await db.execute(
        select(UtilityBill).where(
            and_(
                UtilityBill.id == bill_id,
                UtilityBill.tenant_id == current_user.tenant_id,
                UtilityBill.is_deleted == False
            )
        )
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(status_code=404, detail="Utility bill not found")
    
    bill.paid_amount = payment_data.paid_amount
    bill.payment_date = payment_data.payment_date
    bill.payment_mode = payment_data.payment_mode
    bill.payment_reference = payment_data.payment_reference
    
    if bill.paid_amount >= bill.total_amount:
        bill.payment_status = 'paid'
    elif bill.paid_amount > 0:
        bill.payment_status = 'partial'
    
    bill.updated_by = current_user.id
    bill.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Payment recorded successfully"
    }
