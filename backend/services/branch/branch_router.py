"""
Branch Router
API endpoints for branch management
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.shared.database.branch_models import Branch, Organization
from backend.services.branch.schemas import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    BranchDashboard
)
from backend.services.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/branch/branches", tags=["Branch - Branches"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create branch"
)
async def create_branch(
    request: BranchCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new branch"""
    
    # Check if branch code already exists
    stmt = select(Branch).where(
        and_(
            Branch.tenant_id == current_user.tenant_id,
            Branch.branch_code == request.branch_code,
            Branch.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return error_response(
            message="Branch code already exists",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify organization exists
    org_stmt = select(Organization).where(
        and_(
            Organization.id == request.organization_id,
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    )
    org_result = await db.execute(org_stmt)
    organization = org_result.scalar_one_or_none()
    
    if not organization:
        return error_response(
            message="Organization not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Create branch
    branch = Branch(
        tenant_id=current_user.tenant_id,
        organization_id=request.organization_id,
        branch_code=request.branch_code,
        branch_name=request.branch_name,
        branch_type=request.branch_type,
        ifsc_code=request.ifsc_code,
        micr_code=request.micr_code,
        swift_code=request.swift_code,
        working_days=request.working_days,
        working_hours_start=request.working_hours_start,
        working_hours_end=request.working_hours_end,
        branch_manager_id=request.branch_manager_id,
        branch_manager_name=request.branch_manager_name,
        branch_manager_phone=request.branch_manager_phone,
        branch_manager_email=request.branch_manager_email,
        latitude=request.latitude,
        longitude=request.longitude,
        is_head_office=request.is_head_office,
        is_regional_office=request.is_regional_office,
        created_by=current_user.id
    )
    
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    
    return success_response(
        data=BranchResponse.model_validate(branch).model_dump(mode='json'),
        message="Branch created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "",
    response_model=dict,
    summary="List branches"
)
async def list_branches(
    organization_id: Optional[UUID] = Query(None, description="Filter by organization"),
    branch_type: Optional[str] = Query(None, description="Filter by branch type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of branches"""
    
    stmt = select(Branch).where(
        and_(
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    
    if organization_id:
        stmt = stmt.where(Branch.organization_id == organization_id)
    if branch_type:
        stmt = stmt.where(Branch.branch_type == branch_type)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated results
    stmt = stmt.order_by(Branch.branch_code).offset(skip).limit(limit)
    result = await db.execute(stmt)
    branches = result.scalars().all()
    
    return success_response(
        data={
            "items": [BranchResponse.model_validate(b).model_dump(mode='json') for b in branches],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get(
    "/{branch_id}",
    response_model=dict,
    summary="Get branch by ID"
)
async def get_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get branch details"""
    
    stmt = select(Branch).where(
        and_(
            Branch.id == branch_id,
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return error_response(
            message="Branch not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=BranchResponse.model_validate(branch).model_dump(mode='json')
    )


@router.get(
    "/code/{branch_code}",
    response_model=dict,
    summary="Get branch by code"
)
async def get_branch_by_code(
    branch_code: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get branch details by code"""
    
    stmt = select(Branch).where(
        and_(
            Branch.branch_code == branch_code,
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return error_response(
            message="Branch not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=BranchResponse.model_validate(branch).model_dump(mode='json')
    )


@router.put(
    "/{branch_id}",
    response_model=dict,
    summary="Update branch"
)
async def update_branch(
    branch_id: UUID,
    request: BranchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update branch details"""
    
    stmt = select(Branch).where(
        and_(
            Branch.id == branch_id,
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return error_response(
            message="Branch not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    
    branch.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(branch)
    
    return success_response(
        data=BranchResponse.model_validate(branch).model_dump(mode='json'),
        message="Branch updated successfully"
    )


@router.delete(
    "/{branch_id}",
    response_model=dict,
    summary="Delete branch"
)
async def delete_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Soft delete branch"""
    
    stmt = select(Branch).where(
        and_(
            Branch.id == branch_id,
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return error_response(
            message="Branch not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    branch.is_deleted = True
    branch.deleted_by = current_user.id
    branch.deleted_at = func.now()
    
    await db.commit()
    
    return success_response(message="Branch deleted successfully")


@router.get(
    "/{branch_id}/dashboard",
    response_model=dict,
    summary="Get branch dashboard"
)
async def get_branch_dashboard(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get branch dashboard with key metrics"""
    
    from backend.shared.database.branch_models import BranchDayOperation, BranchCounter
    from datetime import datetime, date
    
    # Get branch
    stmt = select(Branch).where(
        and_(
            Branch.id == branch_id,
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return error_response(
            message="Branch not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Get today's day operation
    today = datetime.now().date()
    day_stmt = select(BranchDayOperation).where(
        and_(
            BranchDayOperation.branch_id == branch_id,
            BranchDayOperation.tenant_id == current_user.tenant_id,
            func.date(BranchDayOperation.business_date) == today,
            BranchDayOperation.is_deleted == False
        )
    )
    day_result = await db.execute(day_stmt)
    day_operation = day_result.scalar_one_or_none()
    
    # Get active counters count
    counter_stmt = select(func.count()).where(
        and_(
            BranchCounter.branch_id == branch_id,
            BranchCounter.tenant_id == current_user.tenant_id,
            BranchCounter.is_open == True,
            BranchCounter.is_deleted == False
        )
    )
    counter_result = await db.execute(counter_stmt)
    active_counters = counter_result.scalar()
    
    dashboard = {
        "branch_id": branch.id,
        "branch_code": branch.branch_code,
        "branch_name": branch.branch_name,
        "day_status": day_operation.status if day_operation else "NOT_STARTED",
        "business_date": day_operation.business_date if day_operation else datetime.now(),
        "cash_balance": day_operation.closing_cash_balance if day_operation else 0,
        "total_transactions_today": day_operation.transaction_count if day_operation else 0,
        "total_receipts_today": day_operation.total_receipts if day_operation else 0,
        "total_payments_today": day_operation.total_payments if day_operation else 0,
        "pending_approvals": 0,  # TODO: Calculate from actual pending items
        "active_counters": active_counters,
        "staff_present": branch.staff_count
    }
    
    return success_response(data=dashboard)
