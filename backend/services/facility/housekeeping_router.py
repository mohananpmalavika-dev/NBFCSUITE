"""
Housekeeping Management API Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas import SuccessResponse, PaginatedResponse
from .housekeeping_service import HousekeepingService
from .schemas import (
    HousekeepingTaskCreate, HousekeepingTaskResponse,
    TaskAssignment, TaskStatusUpdate
)

router = APIRouter(prefix="/facility/housekeeping", tags=["Facility - Housekeeping"])


@router.post("/tasks", response_model=SuccessResponse[HousekeepingTaskResponse])
async def create_task(
    task: HousekeepingTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new housekeeping task"""
    result = await HousekeepingService.create_task(
        db, tenant_id, task.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/tasks", response_model=SuccessResponse[PaginatedResponse[HousekeepingTaskResponse]])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    building_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List housekeeping tasks with filters"""
    tasks, total = await HousekeepingService.list_tasks(
        db, tenant_id, skip, limit, status, priority,
        assigned_to, building_id, from_date, to_date
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=tasks,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.patch("/tasks/{task_id}/status", response_model=SuccessResponse[HousekeepingTaskResponse])
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update task status"""
    result = await HousekeepingService.update_task_status(
        db, tenant_id, task_id, status_update.status,
        current_user["id"], status_update.remarks
    )
    return SuccessResponse(data=result)


@router.post("/tasks/{task_id}/assign", response_model=SuccessResponse[HousekeepingTaskResponse])
async def assign_task(
    task_id: int,
    assignment: TaskAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Assign task to an employee"""
    result = await HousekeepingService.assign_task(
        db, tenant_id, task_id, assignment.employee_id, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/supplies/low-stock", response_model=SuccessResponse[list])
async def get_low_stock_items(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get supplies below minimum stock level"""
    items = await HousekeepingService.get_low_stock_items(db, tenant_id)
    return SuccessResponse(data=items)
