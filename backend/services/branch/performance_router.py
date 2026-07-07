"""
Branch Performance Router
API endpoints for branch performance tracking and targets
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
    BranchPerformance, BranchTarget, Branch, BranchAuditLog
)
from backend.services.branch.schemas import (
    BranchPerformanceResponse,
    BranchTargetCreate,
    BranchTargetUpdate,
    BranchTargetResponse,
    BranchAuditLogResponse
)
from backend.services.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/branch/performance", tags=["Branch - Performance"])


@router.get(
    "",
    response_model=dict,
    summary="Get branch performance"
)
async def get_branch_performance(
    branch_id: UUID = Query(..., description="Branch ID"),
    period_type: str = Query(..., description="Period type (DAILY, MONTHLY, QUARTERLY, YEARLY)"),
    period_start: date = Query(..., description="Period start date"),
    period_end: date = Query(..., description="Period end date"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get branch performance metrics"""
    
    stmt = select(BranchPerformance).where(
        and_(
            BranchPerformance.branch_id == branch_id,
            BranchPerformance.period_type == period_type,
            BranchPerformance.period_start == period_start,
            BranchPerformance.period_end == period_end,
            BranchPerformance.tenant_id == current_user.tenant_id,
            BranchPerformance.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    performance = result.scalar_one_or_none()
    
    if not performance:
        return error_response(
            message="Performance data not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=BranchPerformanceResponse.model_validate(performance).model_dump(mode='json')
    )


@router.get(
    "/list",
    response_model=dict,
    summary="List branch performance records"
)
async def list_branch_performance(
    branch_id: Optional[UUID] = Query(None, description="Filter by branch"),
    period_type: Optional[str] = Query(None, description="Filter by period type"),
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of branch performance records"""
    
    stmt = select(BranchPerformance).where(
        and_(
            BranchPerformance.tenant_id == current_user.tenant_id,
            BranchPerformance.is_deleted == False
        )
    )
    
    if branch_id:
        stmt = stmt.where(BranchPerformance.branch_id == branch_id)
    if period_type:
        stmt = stmt.where(BranchPerformance.period_type == period_type)
    if from_date:
        stmt = stmt.where(BranchPerformance.period_start >= from_date)
    if to_date:
        stmt = stmt.where(BranchPerformance.period_end <= to_date)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated results
    stmt = stmt.order_by(BranchPerformance.period_start.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    performances = result.scalars().all()
    
    return success_response(
        data={
            "items": [BranchPerformanceResponse.model_validate(p).model_dump(mode='json') for p in performances],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.post(
    "/calculate",
    response_model=dict,
    summary="Calculate branch performance"
)
async def calculate_branch_performance(
    branch_id: UUID = Query(..., description="Branch ID"),
    period_type: str = Query(..., description="Period type (DAILY, MONTHLY, QUARTERLY, YEARLY)"),
    period_start: date = Query(..., description="Period start date"),
    period_end: date = Query(..., description="Period end date"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Calculate and store branch performance metrics"""
    
    # Get branch
    branch_stmt = select(Branch).where(
        and_(
            Branch.id == branch_id,
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
    
    # Calculate metrics (simplified - in production, query actual data)
    # TODO: Calculate from actual loan, deposit, customer tables
    
    # Check if performance record already exists
    stmt = select(BranchPerformance).where(
        and_(
            BranchPerformance.branch_id == branch_id,
            BranchPerformance.period_type == period_type,
            BranchPerformance.period_start == period_start,
            BranchPerformance.period_end == period_end,
            BranchPerformance.tenant_id == current_user.tenant_id,
            BranchPerformance.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    performance = result.scalar_one_or_none()
    
    if performance:
        # Update existing record
        performance.calculated_at = datetime.now()
        performance.updated_by = current_user.id
    else:
        # Create new record
        performance = BranchPerformance(
            tenant_id=current_user.tenant_id,
            branch_id=branch_id,
            branch_code=branch.branch_code,
            period_type=period_type,
            period_start=datetime.combine(period_start, datetime.min.time()),
            period_end=datetime.combine(period_end, datetime.max.time()),
            loans_disbursed=0,
            loans_disbursed_amount=Decimal("0"),
            loans_collected=Decimal("0"),
            loans_overdue=Decimal("0"),
            npa_amount=Decimal("0"),
            deposits_opened=0,
            deposits_amount=Decimal("0"),
            deposits_closed=0,
            deposits_matured=0,
            new_customers=0,
            active_customers=branch.customer_count,
            total_customers=branch.customer_count,
            total_revenue=Decimal("0"),
            total_expenses=Decimal("0"),
            net_profit=Decimal("0"),
            total_transactions=0,
            cash_transactions=0,
            digital_transactions=0,
            avg_processing_time=Decimal("0"),
            customer_satisfaction=Decimal("4.5"),
            target_disbursement=Decimal("0"),
            target_collection=Decimal("0"),
            target_achievement=Decimal("0"),
            created_by=current_user.id
        )
        db.add(performance)
    
    await db.commit()
    await db.refresh(performance)
    
    return success_response(
        data=BranchPerformanceResponse.model_validate(performance).model_dump(mode='json'),
        message="Branch performance calculated successfully"
    )


# ============================================
# BRANCH TARGETS
# ============================================

@router.post(
    "/targets",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create branch target"
)
async def create_branch_target(
    request: BranchTargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Set targets for a branch"""
    
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
    
    # Check if target already exists
    stmt = select(BranchTarget).where(
        and_(
            BranchTarget.branch_id == request.branch_id,
            BranchTarget.target_period == request.target_period,
            BranchTarget.target_year == request.target_year,
            BranchTarget.target_month == request.target_month,
            BranchTarget.target_quarter == request.target_quarter,
            BranchTarget.tenant_id == current_user.tenant_id,
            BranchTarget.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return error_response(
            message="Target already exists for this period",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    target = BranchTarget(
        tenant_id=current_user.tenant_id,
        branch_id=request.branch_id,
        branch_code=branch.branch_code,
        target_period=request.target_period,
        target_month=request.target_month,
        target_quarter=request.target_quarter,
        target_year=request.target_year,
        loan_disbursement_target=request.loan_disbursement_target,
        loan_collection_target=request.loan_collection_target,
        loan_count_target=request.loan_count_target,
        deposit_mobilization_target=request.deposit_mobilization_target,
        deposit_count_target=request.deposit_count_target,
        new_customer_target=request.new_customer_target,
        revenue_target=request.revenue_target,
        set_by=current_user.id,
        created_by=current_user.id
    )
    
    db.add(target)
    await db.commit()
    await db.refresh(target)
    
    return success_response(
        data=BranchTargetResponse.model_validate(target).model_dump(mode='json'),
        message="Branch target created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/targets",
    response_model=dict,
    summary="List branch targets"
)
async def list_branch_targets(
    branch_id: Optional[UUID] = Query(None, description="Filter by branch"),
    target_period: Optional[str] = Query(None, description="Filter by period"),
    target_year: Optional[int] = Query(None, description="Filter by year"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of branch targets"""
    
    stmt = select(BranchTarget).where(
        and_(
            BranchTarget.tenant_id == current_user.tenant_id,
            BranchTarget.is_active == True,
            BranchTarget.is_deleted == False
        )
    )
    
    if branch_id:
        stmt = stmt.where(BranchTarget.branch_id == branch_id)
    if target_period:
        stmt = stmt.where(BranchTarget.target_period == target_period)
    if target_year:
        stmt = stmt.where(BranchTarget.target_year == target_year)
    
    stmt = stmt.order_by(BranchTarget.target_year.desc(), BranchTarget.target_month.desc())
    result = await db.execute(stmt)
    targets = result.scalars().all()
    
    return success_response(
        data=[BranchTargetResponse.model_validate(t).model_dump(mode='json') for t in targets]
    )


@router.get(
    "/targets/{target_id}",
    response_model=dict,
    summary="Get branch target by ID"
)
async def get_branch_target(
    target_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get branch target details"""
    
    stmt = select(BranchTarget).where(
        and_(
            BranchTarget.id == target_id,
            BranchTarget.tenant_id == current_user.tenant_id,
            BranchTarget.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    target = result.scalar_one_or_none()
    
    if not target:
        return error_response(
            message="Target not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=BranchTargetResponse.model_validate(target).model_dump(mode='json')
    )


@router.put(
    "/targets/{target_id}",
    response_model=dict,
    summary="Update branch target"
)
async def update_branch_target(
    target_id: UUID,
    request: BranchTargetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update branch target"""
    
    stmt = select(BranchTarget).where(
        and_(
            BranchTarget.id == target_id,
            BranchTarget.tenant_id == current_user.tenant_id,
            BranchTarget.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    target = result.scalar_one_or_none()
    
    if not target:
        return error_response(
            message="Target not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target, field, value)
    
    target.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(target)
    
    return success_response(
        data=BranchTargetResponse.model_validate(target).model_dump(mode='json'),
        message="Branch target updated successfully"
    )


@router.delete(
    "/targets/{target_id}",
    response_model=dict,
    summary="Delete branch target"
)
async def delete_branch_target(
    target_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Soft delete branch target"""
    
    stmt = select(BranchTarget).where(
        and_(
            BranchTarget.id == target_id,
            BranchTarget.tenant_id == current_user.tenant_id,
            BranchTarget.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    target = result.scalar_one_or_none()
    
    if not target:
        return error_response(
            message="Target not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    target.is_deleted = True
    target.deleted_by = current_user.id
    target.deleted_at = func.now()
    
    await db.commit()
    
    return success_response(message="Branch target deleted successfully")


# ============================================
# AUDIT LOGS
# ============================================

@router.get(
    "/audit-logs",
    response_model=dict,
    summary="Get branch audit logs"
)
async def get_branch_audit_logs(
    branch_id: UUID = Query(..., description="Branch ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    from_date: Optional[datetime] = Query(None, description="From date"),
    to_date: Optional[datetime] = Query(None, description="To date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get audit logs for a branch"""
    
    stmt = select(BranchAuditLog).where(
        and_(
            BranchAuditLog.branch_id == branch_id,
            BranchAuditLog.tenant_id == current_user.tenant_id,
            BranchAuditLog.is_deleted == False
        )
    )
    
    if event_type:
        stmt = stmt.where(BranchAuditLog.event_type == event_type)
    if from_date:
        stmt = stmt.where(BranchAuditLog.event_timestamp >= from_date)
    if to_date:
        stmt = stmt.where(BranchAuditLog.event_timestamp <= to_date)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated results
    stmt = stmt.order_by(BranchAuditLog.event_timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return success_response(
        data={
            "items": [BranchAuditLogResponse.model_validate(log).model_dump(mode='json') for log in logs],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get(
    "/comparison",
    response_model=dict,
    summary="Compare branch performance"
)
async def compare_branch_performance(
    period_type: str = Query(..., description="Period type (MONTHLY, QUARTERLY, YEARLY)"),
    period_start: date = Query(..., description="Period start date"),
    period_end: date = Query(..., description="Period end date"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Compare performance across all branches"""
    
    stmt = select(BranchPerformance).where(
        and_(
            BranchPerformance.period_type == period_type,
            BranchPerformance.period_start == datetime.combine(period_start, datetime.min.time()),
            BranchPerformance.period_end == datetime.combine(period_end, datetime.max.time()),
            BranchPerformance.tenant_id == current_user.tenant_id,
            BranchPerformance.is_deleted == False
        )
    ).order_by(BranchPerformance.loans_disbursed_amount.desc())
    
    result = await db.execute(stmt)
    performances = result.scalars().all()
    
    # Calculate rankings
    comparison = []
    for idx, perf in enumerate(performances, 1):
        comparison.append({
            "rank": idx,
            "branch_id": str(perf.branch_id),
            "branch_code": perf.branch_code,
            "loans_disbursed_amount": float(perf.loans_disbursed_amount),
            "loans_collected": float(perf.loans_collected),
            "deposits_amount": float(perf.deposits_amount),
            "new_customers": perf.new_customers,
            "total_revenue": float(perf.total_revenue),
            "net_profit": float(perf.net_profit),
            "target_achievement": float(perf.target_achievement)
        })
    
    return success_response(data={
        "period_type": period_type,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "branches": comparison,
        "total_branches": len(comparison)
    })
