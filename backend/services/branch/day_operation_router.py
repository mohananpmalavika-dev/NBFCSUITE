"""
Day Operation Router
API endpoints for day begin/end operations
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.shared.database.branch_models import (
    BranchDayOperation, Branch, BranchCounter, CashTransaction
)
from backend.services.branch.schemas import (
    DayBeginRequest,
    DayEndRequest,
    BranchDayOperationResponse,
    CounterCreate,
    CounterOpenRequest,
    CounterCloseRequest,
    CounterResponse
)
from backend.services.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/branch/day-operations", tags=["Branch - Day Operations"])


@router.post(
    "/day-begin",
    response_model=dict,
    summary="Begin day operations"
)
async def day_begin(
    request: DayBeginRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Start day operations for a branch"""
    
    # Check if day already started
    business_date = request.business_date.date()
    stmt = select(BranchDayOperation).where(
        and_(
            BranchDayOperation.branch_id == request.branch_id,
            BranchDayOperation.tenant_id == current_user.tenant_id,
            func.date(BranchDayOperation.business_date) == business_date,
            BranchDayOperation.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing and existing.status != "NOT_STARTED":
        return error_response(
            message="Day operations already started",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Get branch
    branch_stmt = select(Branch).where(
        and_(
            Branch.id == request.branch_id,
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    branch_result = await db.execute(branch_stmt)
    branch = branch_result.scalar_one_or_none()
    
    if not branch:
        return error_response(
            message="Branch not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if existing:
        # Update existing record
        existing.day_begin_time = datetime.now()
        existing.day_begin_by = current_user.id
        existing.day_begin_remarks = request.remarks
        existing.opening_cash_balance = request.opening_cash_balance
        existing.opening_bank_balance = request.opening_bank_balance
        existing.pre_day_checklist = request.checklist
        existing.status = "IN_PROGRESS"
        existing.updated_by = current_user.id
        day_operation = existing
    else:
        # Create new day operation
        day_operation = BranchDayOperation(
            tenant_id=current_user.tenant_id,
            branch_id=request.branch_id,
            branch_code=branch.branch_code,
            business_date=request.business_date,
            day_begin_time=datetime.now(),
            day_begin_by=current_user.id,
            day_begin_remarks=request.remarks,
            opening_cash_balance=request.opening_cash_balance,
            opening_bank_balance=request.opening_bank_balance,
            pre_day_checklist=request.checklist,
            status="IN_PROGRESS",
            created_by=current_user.id
        )
        db.add(day_operation)
    
    await db.commit()
    await db.refresh(day_operation)
    
    return success_response(
        data=BranchDayOperationResponse.model_validate(day_operation).model_dump(mode='json'),
        message="Day operations started successfully"
    )


@router.post(
    "/day-end",
    response_model=dict,
    summary="End day operations"
)
async def day_end(
    request: DayEndRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """End day operations for a branch"""
    
    # Get day operation
    business_date = request.business_date.date()
    stmt = select(BranchDayOperation).where(
        and_(
            BranchDayOperation.branch_id == request.branch_id,
            BranchDayOperation.tenant_id == current_user.tenant_id,
            func.date(BranchDayOperation.business_date) == business_date,
            BranchDayOperation.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    day_operation = result.scalar_one_or_none()
    
    if not day_operation:
        return error_response(
            message="Day operations not started",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if day_operation.status == "COMPLETED":
        return error_response(
            message="Day operations already completed",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if all counters are closed
    counter_stmt = select(func.count()).where(
        and_(
            BranchCounter.branch_id == request.branch_id,
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_open == True,
            BranchCounter.is_deleted == False
        )
    )
    counter_result = await db.execute(counter_stmt)
    open_counters = counter_result.scalar()
    
    if open_counters > 0:
        return error_response(
            message=f"Cannot end day. {open_counters} counter(s) still open",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate transaction summary
    txn_stmt = select(
        func.count(CashTransaction.id).label('count'),
        func.sum(func.case(
            (CashTransaction.transaction_type.in_(['CASH_RECEIPT', 'BANK_DEPOSIT']), CashTransaction.amount),
            else_=0
        )).label('receipts'),
        func.sum(func.case(
            (CashTransaction.transaction_type.in_(['CASH_PAYMENT', 'BANK_WITHDRAWAL']), CashTransaction.amount),
            else_=0
        )).label('payments'),
        func.sum(func.case(
            (CashTransaction.transaction_type == 'INTERNAL_TRANSFER', CashTransaction.amount),
            else_=0
        )).label('transfers')
    ).where(
        and_(
            CashTransaction.branch_id == request.branch_id,
            CashTransaction.tenant_id == current_user.tenant_id,
            func.date(CashTransaction.transaction_date) == business_date,
            CashTransaction.is_cancelled == False,
            CashTransaction.is_deleted == False
        )
    )
    txn_result = await db.execute(txn_stmt)
    txn_summary = txn_result.first()
    
    # Update day operation
    day_operation.day_end_time = datetime.now()
    day_operation.day_end_by = current_user.id
    day_operation.day_end_remarks = request.remarks
    day_operation.closing_cash_balance = request.closing_cash_balance
    day_operation.closing_bank_balance = request.closing_bank_balance
    day_operation.post_day_checklist = request.checklist
    day_operation.total_receipts = txn_summary.receipts or 0
    day_operation.total_payments = txn_summary.payments or 0
    day_operation.total_transfers = txn_summary.transfers or 0
    day_operation.transaction_count = txn_summary.count or 0
    day_operation.status = "COMPLETED"
    day_operation.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(day_operation)
    
    return success_response(
        data=BranchDayOperationResponse.model_validate(day_operation).model_dump(mode='json'),
        message="Day operations completed successfully"
    )


@router.get(
    "",
    response_model=dict,
    summary="List day operations"
)
async def list_day_operations(
    branch_id: Optional[UUID] = Query(None, description="Filter by branch"),
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of day operations"""
    
    stmt = select(BranchDayOperation).where(
        and_(
            BranchDayOperation.tenant_id == current_user.tenant_id,
            BranchDayOperation.is_deleted == False
        )
    )
    
    if branch_id:
        stmt = stmt.where(BranchDayOperation.branch_id == branch_id)
    if from_date:
        stmt = stmt.where(func.date(BranchDayOperation.business_date) >= from_date)
    if to_date:
        stmt = stmt.where(func.date(BranchDayOperation.business_date) <= to_date)
    if status:
        stmt = stmt.where(BranchDayOperation.status == status)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated results
    stmt = stmt.order_by(BranchDayOperation.business_date.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    operations = result.scalars().all()
    
    return success_response(
        data={
            "items": [BranchDayOperationResponse.model_validate(op).model_dump(mode='json') for op in operations],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get(
    "/{operation_id}",
    response_model=dict,
    summary="Get day operation by ID"
)
async def get_day_operation(
    operation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get day operation details"""
    
    stmt = select(BranchDayOperation).where(
        and_(
            BranchDayOperation.id == operation_id,
            BranchDayOperation.tenant_id == current_user.tenant_id,
            BranchDayOperation.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    operation = result.scalar_one_or_none()
    
    if not operation:
        return error_response(
            message="Day operation not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=BranchDayOperationResponse.model_validate(operation).model_dump(mode='json')
    )


# ============================================
# COUNTER OPERATIONS
# ============================================

@router.post(
    "/counters",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create counter"
)
async def create_counter(
    request: CounterCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new counter"""
    
    # Check if counter number already exists for branch
    stmt = select(BranchCounter).where(
        and_(
            BranchCounter.branch_id == request.branch_id,
            BranchCounter.counter_number == request.counter_number,
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return error_response(
            message="Counter number already exists for this branch",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    counter = BranchCounter(
        tenant_id=current_user.tenant_id,
        branch_id=request.branch_id,
        counter_number=request.counter_number,
        counter_name=request.counter_name,
        counter_type=request.counter_type,
        assigned_user_id=request.assigned_user_id,
        assigned_user_name=request.assigned_user_name,
        created_by=current_user.id
    )
    
    db.add(counter)
    await db.commit()
    await db.refresh(counter)
    
    return success_response(
        data=CounterResponse.model_validate(counter).model_dump(mode='json'),
        message="Counter created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/counters/{counter_id}/open",
    response_model=dict,
    summary="Open counter"
)
async def open_counter(
    counter_id: UUID,
    request: CounterOpenRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Open a counter for transactions"""
    
    stmt = select(BranchCounter).where(
        and_(
            BranchCounter.id == counter_id,
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    counter = result.scalar_one_or_none()
    
    if not counter:
        return error_response(
            message="Counter not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if counter.is_open:
        return error_response(
            message="Counter is already open",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    counter.is_open = True
    counter.opened_at = datetime.now()
    counter.opened_by = current_user.id
    counter.opening_balance = request.opening_balance
    counter.current_balance = request.opening_balance
    counter.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(counter)
    
    return success_response(
        data=CounterResponse.model_validate(counter).model_dump(mode='json'),
        message="Counter opened successfully"
    )


@router.post(
    "/counters/{counter_id}/close",
    response_model=dict,
    summary="Close counter"
)
async def close_counter(
    counter_id: UUID,
    request: CounterCloseRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Close a counter"""
    
    stmt = select(BranchCounter).where(
        and_(
            BranchCounter.id == counter_id,
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    counter = result.scalar_one_or_none()
    
    if not counter:
        return error_response(
            message="Counter not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if not counter.is_open:
        return error_response(
            message="Counter is not open",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    counter.is_open = False
    counter.closed_at = datetime.now()
    counter.closed_by = current_user.id
    counter.closing_balance = request.closing_balance
    counter.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(counter)
    
    return success_response(
        data=CounterResponse.model_validate(counter).model_dump(mode='json'),
        message="Counter closed successfully"
    )


@router.get(
    "/counters",
    response_model=dict,
    summary="List counters"
)
async def list_counters(
    branch_id: Optional[UUID] = Query(None, description="Filter by branch"),
    is_open: Optional[bool] = Query(None, description="Filter by open status"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of counters"""
    
    stmt = select(BranchCounter).where(
        and_(
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_deleted == False
        )
    )
    
    if branch_id:
        stmt = stmt.where(BranchCounter.branch_id == branch_id)
    if is_open is not None:
        stmt = stmt.where(BranchCounter.is_open == is_open)
    
    stmt = stmt.order_by(BranchCounter.counter_number)
    result = await db.execute(stmt)
    counters = result.scalars().all()
    
    return success_response(
        data=[CounterResponse.model_validate(c).model_dump(mode='json') for c in counters]
    )
