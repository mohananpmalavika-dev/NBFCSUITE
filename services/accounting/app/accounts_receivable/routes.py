from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.accounts_receivable.models import (
    ARReceipt,
    ARSettlement,
    ARWriteOff,
    CustomerReceivable,
    ReceiptAllocation,
)


def _get_db():
    from app.main import get_db

    return get_db()
from app.accounts_receivable.schemas import (
    AllocationRequest,
    AllocationResponse,
    ARDashboardResponse,
    AgingBucket,
    AgingResponse,
    CustomerReceivableCreate,
    CustomerReceivableResponse,
    CustomerSummaryResponse,
    LedgerSummaryResponse,
    ReceiptCreate,
    ReceiptResponse,
    SettlementRequest,
    SettlementResponse,
    WriteOffRequest,
    WriteOffResponse,
)

router = APIRouter(tags=["accounts receivable"])


def _receivable_response(receivable: CustomerReceivable) -> CustomerReceivableResponse:
    return CustomerReceivableResponse(
        id=receivable.id,
        tenant_id=receivable.tenant_id,
        customer_id=receivable.customer_id,
        receivable_number=receivable.receivable_number,
        product_type=receivable.product_type,
        amount=receivable.amount,
        currency=receivable.currency,
        due_date=receivable.due_date,
        status=receivable.status,
        posted_to_accounting=receivable.posted_to_accounting,
        metadata=receivable.metadata_json,
        created_by=receivable.created_by,
        created_at=receivable.created_at,
        updated_at=receivable.updated_at,
    )


def _receipt_response(receipt: ARReceipt) -> ReceiptResponse:
    return ReceiptResponse(
        id=receipt.id,
        tenant_id=receipt.tenant_id,
        customer_id=receipt.customer_id,
        receipt_number=receipt.receipt_number,
        payment_method=receipt.payment_method,
        amount=receipt.amount,
        currency=receipt.currency,
        receipt_date=receipt.receipt_date,
        status=receipt.status,
        metadata=receipt.metadata_json,
        created_at=receipt.created_at,
    )


@router.get("/customers", response_model=List[CustomerSummaryResponse])
async def list_ar_customers(
    tenant_id: str = Query(...),
    branch_id: Optional[str] = Query(None),
    product_type: Optional[str] = Query(None),
    db: Session = Depends(_get_db),
):
    receivables = db.query(CustomerReceivable).filter(CustomerReceivable.tenant_id == tenant_id)
    if product_type:
        receivables = receivables.filter(CustomerReceivable.product_type == product_type)
    records = receivables.all()

    summary_map: Dict[str, Dict[str, object]] = {}
    for rec in records:
        bucket = summary_map.setdefault(rec.customer_id, {"outstanding_balance": 0.0, "total_receivables": 0, "customer_name": None})
        bucket["outstanding_balance"] += rec.amount
        bucket["total_receivables"] += 1
        bucket["customer_name"] = bucket["customer_name"] or getattr(rec, "customer_name", None)

    return [
        CustomerSummaryResponse(
            customer_id=customer_id,
            customer_name=summary["customer_name"],
            outstanding_balance=round(summary["outstanding_balance"], 2),
            total_receivables=summary["total_receivables"],
        )
        for customer_id, summary in summary_map.items()
    ]


@router.get("/receivables", response_model=Dict[str, object])
async def list_receivables(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(_get_db),
):
    query = db.query(CustomerReceivable).filter(CustomerReceivable.tenant_id == tenant_id)
    if status:
        query = query.filter(CustomerReceivable.status == status)
    if customer_id:
        query = query.filter(CustomerReceivable.customer_id == customer_id)

    total = query.count()
    items = query.order_by(CustomerReceivable.due_date.asc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_receivable_response(item) for item in items]}


@router.post("/receivables", response_model=CustomerReceivableResponse)
async def create_receivable(receivable: CustomerReceivableCreate, db: Session = Depends(_get_db)):
    if receivable.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than zero")

    new_receivable = CustomerReceivable(
        id=str(uuid4()),
        tenant_id=receivable.tenant_id,
        customer_id=receivable.customer_id,
        receivable_number=receivable.receivable_number,
        product_type=receivable.product_type,
        amount=round(receivable.amount, 2),
        currency=receivable.currency or "INR",
        due_date=receivable.due_date,
        status=receivable.status or "pending",
        metadata_json=receivable.metadata,
        created_by=receivable.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_receivable)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(new_receivable)
    return _receivable_response(new_receivable)


@router.post("/receipts", response_model=ReceiptResponse)
async def create_receipt(receipt: ReceiptCreate, db: Session = Depends(_get_db)):
    if receipt.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than zero")

    new_receipt = ARReceipt(
        id=str(uuid4()),
        tenant_id=receipt.tenant_id,
        customer_id=receipt.customer_id,
        receipt_number=receipt.receipt_number,
        payment_method=receipt.payment_method,
        amount=round(receipt.amount, 2),
        currency=receipt.currency or "INR",
        receipt_date=receipt.receipt_date or datetime.utcnow(),
        status="received",
        metadata_json=receipt.metadata,
        created_by=receipt.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(new_receipt)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(new_receipt)
    return _receipt_response(new_receipt)


@router.post("/allocate", response_model=AllocationResponse)
async def allocate_receipt(allocation: AllocationRequest, db: Session = Depends(_get_db)):
    total_allocated = 0.0
    created_count = 0

    for item in allocation.items:
        receipt = db.query(ARReceipt).filter(ARReceipt.id == item.receipt_id, ARReceipt.tenant_id == allocation.tenant_id).first()
        receivable = db.query(CustomerReceivable).filter(CustomerReceivable.id == item.receivable_id, CustomerReceivable.tenant_id == allocation.tenant_id).first()
        if not receipt or not receivable:
            raise HTTPException(status_code=404, detail="receipt or receivable not found")

        allocation_record = ReceiptAllocation(
            id=str(uuid4()),
            tenant_id=allocation.tenant_id,
            receipt_id=receipt.id,
            receivable_id=receivable.id,
            amount=round(item.amount, 2),
            created_at=datetime.utcnow(),
        )
        db.add(allocation_record)
        total_allocated += item.amount
        created_count += 1

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    return AllocationResponse(allocations_created=created_count, allocated_amount=round(total_allocated, 2))


@router.get("/ledger", response_model=LedgerSummaryResponse)
async def get_customer_ledger(
    tenant_id: str = Query(...),
    customer_id: str = Query(...),
    db: Session = Depends(_get_db),
):
    receivables = db.query(CustomerReceivable).filter(CustomerReceivable.tenant_id == tenant_id, CustomerReceivable.customer_id == customer_id).all()
    receipts = db.query(ARReceipt).filter(ARReceipt.tenant_id == tenant_id, ARReceipt.customer_id == customer_id).all()

    total_receipts = sum(receipt.amount for receipt in receipts)
    outstanding = sum(receivable.amount for receivable in receivables) - total_receipts

    return LedgerSummaryResponse(
        tenant_id=tenant_id,
        customer_id=customer_id,
        outstanding_balance=round(outstanding, 2),
        total_receivables=len(receivables),
        total_receipts=round(total_receipts, 2),
        receivables=[_receivable_response(receivable) for receivable in receivables],
        receipts=[_receipt_response(receipt) for receipt in receipts],
    )


@router.get("/aging", response_model=AgingResponse)
async def get_aging(tenant_id: str = Query(...), db: Session = Depends(_get_db)):
    receivables = db.query(CustomerReceivable).filter(CustomerReceivable.tenant_id == tenant_id).all()
    buckets: Dict[str, Dict[str, object]] = {
        "current": {"amount": 0.0, "receivables": 0},
        "1-30": {"amount": 0.0, "receivables": 0},
        "31-60": {"amount": 0.0, "receivables": 0},
        "61-90": {"amount": 0.0, "receivables": 0},
        "90+": {"amount": 0.0, "receivables": 0},
    }
    now = datetime.utcnow()

    for rec in receivables:
        if not rec.due_date:
            buckets["current"]["amount"] += rec.amount
            buckets["current"]["receivables"] += 1
            continue

        age = (now - rec.due_date).days
        if age <= 0:
            bucket = "current"
        elif age <= 30:
            bucket = "1-30"
        elif age <= 60:
            bucket = "31-60"
        elif age <= 90:
            bucket = "61-90"
        else:
            bucket = "90+"
        buckets[bucket]["amount"] += rec.amount
        buckets[bucket]["receivables"] += 1

    return AgingResponse(
        tenant_id=tenant_id,
        aging_buckets=[AgingBucket(bucket=bucket, amount=round(data["amount"], 2), receivables=data["receivables"]) for bucket, data in buckets.items()],
    )


@router.post("/settlement", response_model=SettlementResponse)
async def create_settlement(settlement: SettlementRequest, db: Session = Depends(_get_db)):
    if settlement.settlement_amount <= 0:
        raise HTTPException(status_code=400, detail="settlement_amount must be greater than zero")

    new_settlement = ARSettlement(
        id=str(uuid4()),
        tenant_id=settlement.tenant_id,
        customer_id=settlement.customer_id,
        receivable_id=settlement.receivable_id,
        settlement_amount=round(settlement.settlement_amount, 2),
        settlement_date=settlement.settlement_date or datetime.utcnow(),
        status="approved",
        metadata_json=settlement.metadata,
        created_by=settlement.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(new_settlement)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(new_settlement)
    return SettlementResponse(
        id=new_settlement.id,
        tenant_id=new_settlement.tenant_id,
        customer_id=new_settlement.customer_id,
        receivable_id=new_settlement.receivable_id,
        settlement_amount=new_settlement.settlement_amount,
        settlement_date=new_settlement.settlement_date,
        status=new_settlement.status,
        created_by=new_settlement.created_by,
        metadata=new_settlement.metadata_json,
        created_at=new_settlement.created_at,
    )


@router.post("/writeoff", response_model=WriteOffResponse)
async def create_writeoff(writeoff: WriteOffRequest, db: Session = Depends(_get_db)):
    if writeoff.write_off_amount <= 0:
        raise HTTPException(status_code=400, detail="write_off_amount must be greater than zero")

    new_writeoff = ARWriteOff(
        id=str(uuid4()),
        tenant_id=writeoff.tenant_id,
        customer_id=writeoff.customer_id,
        receivable_id=writeoff.receivable_id,
        write_off_amount=round(writeoff.write_off_amount, 2),
        reason=writeoff.reason,
        status="approved",
        metadata_json=writeoff.metadata,
        created_by=writeoff.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(new_writeoff)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(new_writeoff)
    return WriteOffResponse(
        id=new_writeoff.id,
        tenant_id=new_writeoff.tenant_id,
        customer_id=new_writeoff.customer_id,
        receivable_id=new_writeoff.receivable_id,
        write_off_amount=new_writeoff.write_off_amount,
        reason=new_writeoff.reason,
        status=new_writeoff.status,
        created_by=new_writeoff.created_by,
        metadata=new_writeoff.metadata_json,
        created_at=new_writeoff.created_at,
    )


@router.get("/dashboard", response_model=ARDashboardResponse)
async def ar_dashboard(tenant_id: str = Query(...), db: Session = Depends(_get_db)):
    receivables = db.query(CustomerReceivable).filter(CustomerReceivable.tenant_id == tenant_id).all()
    receipts = db.query(ARReceipt).filter(ARReceipt.tenant_id == tenant_id).all()

    total_receivables = len(receivables)
    total_outstanding = sum(rec.amount for rec in receivables) - sum(rc.amount for rc in receipts)
    overdue_count = sum(1 for rec in receivables if rec.due_date and rec.due_date < datetime.utcnow())
    current_count = total_receivables - overdue_count

    return ARDashboardResponse(
        tenant_id=tenant_id,
        total_receivables=total_receivables,
        total_outstanding=round(total_outstanding, 2),
        total_receipts=round(sum(rc.amount for rc in receipts), 2),
        overdue_receivables=overdue_count,
        current_receivables=current_count,
    )
