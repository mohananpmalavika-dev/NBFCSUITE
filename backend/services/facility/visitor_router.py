"""
Visitor Management API Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas import SuccessResponse, PaginatedResponse
from .visitor_service import VisitorService
from .schemas import (
    VisitorCreate, VisitorResponse, VisitorCheckIn
)

router = APIRouter(prefix="/facility/visitors", tags=["Facility - Visitor Management"])


@router.post("", response_model=SuccessResponse[VisitorResponse])
async def create_visitor(
    visitor: VisitorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new visitor entry"""
    result = await VisitorService.create_visitor(
        db, tenant_id, visitor.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("", response_model=SuccessResponse[PaginatedResponse[VisitorResponse]])
async def list_visitors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    visitor_type: Optional[str] = None,
    status: Optional[str] = None,
    host_employee_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List visitors with filters"""
    visitors, total = await VisitorService.list_visitors(
        db, tenant_id, skip, limit, visitor_type, status,
        host_employee_id, from_date, to_date, search
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=visitors,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.get("/{visitor_id}", response_model=SuccessResponse[VisitorResponse])
async def get_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get visitor by ID"""
    visitor = await VisitorService.get_visitor(db, tenant_id, visitor_id)
    return SuccessResponse(data=visitor)


@router.post("/{visitor_id}/check-in", response_model=SuccessResponse[VisitorResponse])
async def check_in_visitor(
    visitor_id: int,
    check_in: VisitorCheckIn,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check in a visitor"""
    result = await VisitorService.check_in_visitor(
        db, tenant_id, visitor_id, check_in.badge_number, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.post("/{visitor_id}/check-out", response_model=SuccessResponse[VisitorResponse])
async def check_out_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check out a visitor"""
    result = await VisitorService.check_out_visitor(
        db, tenant_id, visitor_id, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/active/current", response_model=SuccessResponse[List[VisitorResponse]])
async def get_active_visitors(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all currently checked-in visitors"""
    visitors = await VisitorService.get_active_visitors(db, tenant_id)
    return SuccessResponse(data=visitors)


@router.get("/expected/today", response_model=SuccessResponse[List[VisitorResponse]])
async def get_expected_visitors_today(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get visitors expected today"""
    visitors = await VisitorService.get_expected_visitors_today(db, tenant_id)
    return SuccessResponse(data=visitors)


@router.post("/{visitor_id}/approve", response_model=SuccessResponse[VisitorResponse])
async def approve_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve a visitor entry"""
    result = await VisitorService.approve_visitor(
        db, tenant_id, visitor_id, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/statistics/range", response_model=SuccessResponse[dict])
async def get_visitor_statistics(
    from_date: date,
    to_date: date,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get visitor statistics for a date range"""
    stats = await VisitorService.get_visitor_statistics(
        db, tenant_id, from_date, to_date
    )
    return SuccessResponse(data=stats)
