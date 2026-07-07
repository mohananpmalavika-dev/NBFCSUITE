"""
Cash Management Router
API endpoints for cash transactions and management
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.shared.database.branch_models import (
    CashTransaction, CashDenomination, CashPosition, BranchCounter, Branch
)
from backend.services.branch.schemas import (
    CashTransactionCreate,
    CashTransactionResponse,
    CashDenominationCreate,
    CashDenominationResponse,
    CashPositionResponse
)
from backend.services.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/branch/cash", tags=["Branch - Cash Management"])


@router.post(
    "/transactions",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create cash transaction"
)
async def create_cash_transaction(
    request: CashTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Record a cash transaction"""
    
    # Generate transaction number
    today = datetime.now().strftime("%Y%m%d")
    count_stmt = select(func.count()).where(
        and_(
            CashTransaction.tenant_id == current_user.tenant_id,
            CashTransaction.transaction_number.like(f"CASH{today}%")
        )
    )
    count_result = await db.execute(count_stmt)
    count = count_result.scalar()
    transaction_number = f"CASH{today}{str(count + 1).zfill(6)}"
    
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
    
    # If counter specified, check if it's open
    if request.counter_id:
        counter_stmt = select(BranchCounter).where(
            and_(
                BranchCounter.id == request.counter_id,
                BranchCounter.tenant_id == current_user.tenant_id,
                BranchCounter.is_deleted == False
            )
        )
        counter_result = await db.execute(counter_stmt)
        counter = counter_result.scalar_one_or_none()
        
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
        
        # Update counter balance
        if request.transaction_type in ["CASH_RECEIPT", "BANK_DEPOSIT"]:
            counter.current_balance += request.amount
            counter.total_receipts += request.amount
        elif request.transaction_type in ["CASH_PAYMENT", "BANK_WITHDRAWAL"]:
            if counter.current_balance < request.amount:
                return error_response(
                    message="Insufficient cash balance in counter",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            counter.current_balance -= request.amount
            counter.total_payments += request.amount
        
        counter.transaction_count += 1
    
    # Create transaction
    transaction = CashTransaction(
        tenant_id=current_user.tenant_id,
        transaction_number=transaction_number,
        transaction_date=request.transaction_date,
        transaction_type=request.transaction_type,
        branch_id=request.branch_id,
        counter_id=request.counter_id,
        amount=request.amount,
        from_party_type=request.from_party_type,
        from_party_id=request.from_party_id,
        from_party_name=request.from_party_name,
        to_party_type=request.to_party_type,
        to_party_id=request.to_party_id,
        to_party_name=request.to_party_name,
        reference_type=request.reference_type,
        reference_id=request.reference_id,
        reference_number=request.reference_number,
        payment_mode=request.payment_mode,
        instrument_number=request.instrument_number,
        instrument_date=request.instrument_date,
        narration=request.narration,
        remarks=request.remarks,
        processed_by=current_user.id,
        processed_by_name=f"{current_user.first_name} {current_user.last_name}",
        status="COMPLETED",
        created_by=current_user.id
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return success_response(
        data=CashTransactionResponse.model_validate(transaction).model_dump(mode='json'),
        message="Cash transaction recorded successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/transactions",
    response_model=dict,
    summary="List cash transactions"
)
async def list_cash_transactions(
    branch_id: Optional[UUID] = Query(None, description="Filter by branch"),
    counter_id: Optional[UUID] = Query(None, description="Filter by counter"),
    transaction_type: Optional[str] = Query(None, description="Filter by type"),
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of cash transactions"""
    
    stmt = select(CashTransaction).where(
        and_(
            CashTransaction.tenant_id == current_user.tenant_id,
            CashTransaction.is_deleted == False
        )
    )
    
    if branch_id:
        stmt = stmt.where(CashTransaction.branch_id == branch_id)
    if counter_id:
        stmt = stmt.where(CashTransaction.counter_id == counter_id)
    if transaction_type:
        stmt = stmt.where(CashTransaction.transaction_type == transaction_type)
    if from_date:
        stmt = stmt.where(func.date(CashTransaction.transaction_date) >= from_date)
    if to_date:
        stmt = stmt.where(func.date(CashTransaction.transaction_date) <= to_date)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated results
    stmt = stmt.order_by(CashTransaction.transaction_date.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    return success_response(
        data={
            "items": [CashTransactionResponse.model_validate(t).model_dump(mode='json') for t in transactions],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=dict,
    summary="Get cash transaction by ID"
)
async def get_cash_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get cash transaction details"""
    
    stmt = select(CashTransaction).where(
        and_(
            CashTransaction.id == transaction_id,
            CashTransaction.tenant_id == current_user.tenant_id,
            CashTransaction.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        return error_response(
            message="Transaction not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=CashTransactionResponse.model_validate(transaction).model_dump(mode='json')
    )


@router.post(
    "/transactions/{transaction_id}/cancel",
    response_model=dict,
    summary="Cancel cash transaction"
)
async def cancel_cash_transaction(
    transaction_id: UUID,
    reason: str = Query(..., description="Cancellation reason"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Cancel a cash transaction"""
    
    stmt = select(CashTransaction).where(
        and_(
            CashTransaction.id == transaction_id,
            CashTransaction.tenant_id == current_user.tenant_id,
            CashTransaction.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        return error_response(
            message="Transaction not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if transaction.is_cancelled:
        return error_response(
            message="Transaction already cancelled",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Reverse counter balance if applicable
    if transaction.counter_id:
        counter_stmt = select(BranchCounter).where(
            and_(
                BranchCounter.id == transaction.counter_id,
                BranchCounter.tenant_id == current_user.tenant_id,
                BranchCounter.is_deleted == False
            )
        )
        counter_result = await db.execute(counter_stmt)
        counter = counter_result.scalar_one_or_none()
        
        if counter:
            if transaction.transaction_type in ["CASH_RECEIPT", "BANK_DEPOSIT"]:
                counter.current_balance -= transaction.amount
                counter.total_receipts -= transaction.amount
            elif transaction.transaction_type in ["CASH_PAYMENT", "BANK_WITHDRAWAL"]:
                counter.current_balance += transaction.amount
                counter.total_payments -= transaction.amount
            
            counter.transaction_count -= 1
    
    transaction.is_cancelled = True
    transaction.cancelled_by = current_user.id
    transaction.cancelled_at = datetime.now()
    transaction.cancellation_reason = reason
    transaction.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(transaction)
    
    return success_response(
        data=CashTransactionResponse.model_validate(transaction).model_dump(mode='json'),
        message="Transaction cancelled successfully"
    )


# ============================================
# CASH DENOMINATIONS
# ============================================

@router.post(
    "/denominations",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Record cash denominations"
)
async def create_cash_denomination(
    request: CashDenominationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Record cash denomination details"""
    
    # Calculate total
    total_amount = (
        request.note_2000 * 2000 +
        request.note_500 * 500 +
        request.note_200 * 200 +
        request.note_100 * 100 +
        request.note_50 * 50 +
        request.note_20 * 20 +
        request.note_10 * 10 +
        request.coin_10 * 10 +
        request.coin_5 * 5 +
        request.coin_2 * 2 +
        request.coin_1 * 1
    )
    
    denomination = CashDenomination(
        tenant_id=current_user.tenant_id,
        reference_type=request.reference_type,
        reference_id=request.reference_id,
        branch_id=request.branch_id,
        note_2000=request.note_2000,
        note_500=request.note_500,
        note_200=request.note_200,
        note_100=request.note_100,
        note_50=request.note_50,
        note_20=request.note_20,
        note_10=request.note_10,
        coin_10=request.coin_10,
        coin_5=request.coin_5,
        coin_2=request.coin_2,
        coin_1=request.coin_1,
        total_amount=total_amount,
        recorded_by=current_user.id,
        created_by=current_user.id
    )
    
    db.add(denomination)
    await db.commit()
    await db.refresh(denomination)
    
    return success_response(
        data=CashDenominationResponse.model_validate(denomination).model_dump(mode='json'),
        message="Cash denomination recorded successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/denominations",
    response_model=dict,
    summary="Get cash denominations"
)
async def get_cash_denominations(
    reference_type: str = Query(..., description="Reference type"),
    reference_id: UUID = Query(..., description="Reference ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get cash denomination details"""
    
    stmt = select(CashDenomination).where(
        and_(
            CashDenomination.reference_type == reference_type,
            CashDenomination.reference_id == reference_id,
            CashDenomination.tenant_id == current_user.tenant_id,
            CashDenomination.is_deleted == False
        )
    ).order_by(CashDenomination.recorded_at.desc())
    
    result = await db.execute(stmt)
    denominations = result.scalars().all()
    
    return success_response(
        data=[CashDenominationResponse.model_validate(d).model_dump(mode='json') for d in denominations]
    )


# ============================================
# CASH POSITION
# ============================================

@router.get(
    "/position",
    response_model=dict,
    summary="Get cash position"
)
async def get_cash_position(
    reference_type: str = Query(..., description="Reference type (BRANCH or COUNTER)"),
    reference_id: UUID = Query(..., description="Reference ID"),
    position_date: Optional[date] = Query(None, description="Position date"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get cash position for branch or counter"""
    
    if not position_date:
        position_date = datetime.now().date()
    
    stmt = select(CashPosition).where(
        and_(
            CashPosition.reference_type == reference_type,
            CashPosition.reference_id == reference_id,
            func.date(CashPosition.position_date) == position_date,
            CashPosition.tenant_id == current_user.tenant_id,
            CashPosition.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()
    
    if not position:
        return error_response(
            message="Cash position not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=CashPositionResponse.model_validate(position).model_dump(mode='json')
    )


@router.get(
    "/summary",
    response_model=dict,
    summary="Get cash summary"
)
async def get_cash_summary(
    branch_id: UUID = Query(..., description="Branch ID"),
    summary_date: Optional[date] = Query(None, description="Summary date"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get cash summary for a branch"""
    
    if not summary_date:
        summary_date = datetime.now().date()
    
    # Get total cash in all counters
    counter_stmt = select(
        func.sum(BranchCounter.current_balance).label('total_counter_cash'),
        func.count(BranchCounter.id).label('counter_count')
    ).where(
        and_(
            BranchCounter.branch_id == branch_id,
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_deleted == False
        )
    )
    counter_result = await db.execute(counter_stmt)
    counter_summary = counter_result.first()
    
    # Get transaction summary for the day
    txn_stmt = select(
        func.count(CashTransaction.id).label('transaction_count'),
        func.sum(func.case(
            (CashTransaction.transaction_type.in_(['CASH_RECEIPT']), CashTransaction.amount),
            else_=0
        )).label('total_receipts'),
        func.sum(func.case(
            (CashTransaction.transaction_type.in_(['CASH_PAYMENT']), CashTransaction.amount),
            else_=0
        )).label('total_payments')
    ).where(
        and_(
            CashTransaction.branch_id == branch_id,
            func.date(CashTransaction.transaction_date) == summary_date,
            CashTransaction.is_cancelled == False,
            CashTransaction.tenant_id == current_user.tenant_id,
            CashTransaction.is_deleted == False
        )
    )
    txn_result = await db.execute(txn_stmt)
    txn_summary = txn_result.first()
    
    summary = {
        "branch_id": str(branch_id),
        "summary_date": summary_date.isoformat(),
        "total_counter_cash": float(counter_summary.total_counter_cash or 0),
        "counter_count": counter_summary.counter_count or 0,
        "transaction_count": txn_summary.transaction_count or 0,
        "total_receipts": float(txn_summary.total_receipts or 0),
        "total_payments": float(txn_summary.total_payments or 0),
        "net_cash_flow": float((txn_summary.total_receipts or 0) - (txn_summary.total_payments or 0))
    }
    
    return success_response(data=summary)
