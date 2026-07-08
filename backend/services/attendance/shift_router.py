"""
Shift Management Router
FastAPI endpoints for shift operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.shared.database.database import get_db
from backend.shared.dependencies.auth import get_current_user, get_tenant_id
from .attendance_service import ShiftService
from .schemas import (
    ShiftCreate, ShiftUpdate, ShiftResponse, ShiftListResponse,
    EmployeeShiftAssignment
)


router = APIRouter()


def get_shift_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get shift service instance"""
    return ShiftService(db, tenant_id, user_id)


@router.post("/", response_model=ShiftResponse, status_code=201)
async def create_shift(
    data: ShiftCreate,
    service: ShiftService = Depends(get_shift_service)
):
    """Create new shift"""
    try:
        shift = await service.create_shift(data)
        return shift
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=ShiftListResponse)
async def get_shifts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    shift_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: ShiftService = Depends(get_shift_service)
):
    """Get paginated list of shifts"""
    try:
        shifts, total = await service.get_shifts(
            page=page,
            page_size=page_size,
            search=search,
            shift_type=shift_type,
            is_active=is_active
        )
        
        return {
            "items": shifts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{shift_id}", response_model=ShiftResponse)
async def get_shift(
    shift_id: str,
    service: ShiftService = Depends(get_shift_service)
):
    """Get shift by ID"""
    shift = await service.get_shift(shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.put("/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: str,
    data: ShiftUpdate,
    service: ShiftService = Depends(get_shift_service)
):
    """Update shift"""
    try:
        shift = await service.update_shift(shift_id, data)
        return shift
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{shift_id}", status_code=204)
async def delete_shift(
    shift_id: str,
    service: ShiftService = Depends(get_shift_service)
):
    """Delete shift (soft delete)"""
    try:
        await service.delete_shift(shift_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assign-employee", status_code=201)
async def assign_shift_to_employee(
    assignment: EmployeeShiftAssignment,
    service: ShiftService = Depends(get_shift_service)
):
    """Assign shift to employee"""
    try:
        result = await service.assign_shift_to_employee(
            employee_id=assignment.employee_id,
            shift_id=assignment.shift_id,
            effective_from=assignment.effective_from,
            effective_to=assignment.effective_to
        )
        return {
            "message": "Shift assigned successfully",
            "assignment_id": result.id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
