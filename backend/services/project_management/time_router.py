"""
Time Tracking API Router
FastAPI routes for time entry operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .time_service import TimeTrackingService
from .schemas import (
    TimeEntryCreate, TimeEntryUpdate, TimeEntryListItem, TimeEntryDetail,
    TimeEntryApproval, PaginatedResponse, TimeEntryStatus
)


router = APIRouter(prefix="/time-entries", tags=["Project Management - Time Tracking"])


@router.post("/", response_model=TimeEntryDetail, status_code=status.HTTP_201_CREATED)
async def create_time_entry(
    data: TimeEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new time entry"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    entry = await service.create_time_entry(data, current_user["id"])
    return await service.get_time_entry_detail(entry.id)


@router.get("/my-timesheet", response_model=List[TimeEntryListItem])
async def get_my_timesheet(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get timesheet for current user"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    return await service.get_employee_timesheet(current_user["id"], date_from, date_to)


@router.get("/", response_model=PaginatedResponse)
async def list_time_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    task_id: Optional[UUID] = None,
    status: Optional[List[TimeEntryStatus]] = Query(None),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List time entries with filters and pagination"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    
    items, total = await service.list_time_entries(
        page=page,
        page_size=page_size,
        employee_id=employee_id,
        project_id=project_id,
        task_id=task_id,
        status=status,
        date_from=date_from,
        date_to=date_to
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{entry_id}", response_model=TimeEntryDetail)
async def get_time_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get time entry details"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    entry = await service.get_time_entry_detail(entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    return entry


@router.put("/{entry_id}", response_model=TimeEntryDetail)
async def update_time_entry(
    entry_id: UUID,
    data: TimeEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update time entry"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    
    try:
        entry = await service.update_time_entry(entry_id, data)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Time entry not found")
        
        return await service.get_time_entry_detail(entry.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete time entry"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    
    try:
        success = await service.delete_time_entry(entry_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Time entry not found")
        
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit", status_code=status.HTTP_200_OK)
async def submit_time_entries(
    entry_ids: List[UUID],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit time entries for approval"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    count = await service.submit_time_entries(entry_ids)
    
    return {"message": f"Successfully submitted {count} time entries", "count": count}


@router.post("/approve-reject", status_code=status.HTTP_200_OK)
async def approve_reject_time_entries(
    data: TimeEntryApproval,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject time entries"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    count = await service.approve_reject_time_entries(data)
    
    action = "approved" if data.action == "approve" else "rejected"
    return {"message": f"Successfully {action} {count} time entries", "count": count}


@router.get("/projects/{project_id}/summary")
async def get_project_time_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get time summary for a project"""
    service = TimeTrackingService(db, current_user["tenant_id"], str(current_user["id"]))
    return await service.get_project_time_summary(project_id)
