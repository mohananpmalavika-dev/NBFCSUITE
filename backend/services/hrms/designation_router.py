"""
HRMS Designation API Router
FastAPI routes for designation operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .designation_service import DesignationService
from .schemas import (
    DesignationCreate, DesignationUpdate, DesignationResponse,
    DesignationListItem, PaginatedDesignationResponse,
    DesignationStats
)

router = APIRouter(prefix="/hrms/designations", tags=["HRMS - Designations"])


def get_designation_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DesignationService:
    """Dependency to get designation service"""
    return DesignationService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# DESIGNATION CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
async def create_designation(
    data: DesignationCreate,
    service: DesignationService = Depends(get_designation_service)
):
    """
    Create new designation
    
    - Auto-generates designation code (DESIG-XXXX)
    - Supports level/grade hierarchy
    - Can define salary range
    """
    try:
        designation = await service.create_designation(data)
        return designation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PaginatedDesignationResponse)
async def get_designations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code"),
    level: Optional[int] = Query(None, description="Filter by level"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: DesignationService = Depends(get_designation_service)
):
    """
    Get paginated list of designations
    
    Supports:
    - Search across name, code, description
    - Filter by level, grade
    - Pagination with configurable page size
    """
    designations, total = await service.get_designations(
        page=page,
        page_size=page_size,
        search=search,
        level=level,
        grade=grade,
        is_active=is_active
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedDesignationResponse(
        items=designations,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/stats", response_model=DesignationStats)
async def get_designation_stats(
    service: DesignationService = Depends(get_designation_service)
):
    """
    Get designation statistics
    
    Returns:
    - Total/active designations
    - Employees by designation
    """
    stats = await service.get_stats()
    return stats


@router.get("/{designation_id}", response_model=DesignationResponse)
async def get_designation(
    designation_id: str,
    service: DesignationService = Depends(get_designation_service)
):
    """Get designation by ID with all details"""
    designation = await service.get_designation(designation_id)
    if not designation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )
    
    # Add employee count
    emp_count = await service.get_employee_count(designation_id)
    designation.employee_count = emp_count
    
    return designation


@router.get("/code/{designation_code}", response_model=DesignationResponse)
async def get_designation_by_code(
    designation_code: str,
    service: DesignationService = Depends(get_designation_service)
):
    """Get designation by designation code"""
    designation = await service.get_designation_by_code(designation_code)
    if not designation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )
    return designation


@router.put("/{designation_id}", response_model=DesignationResponse)
async def update_designation(
    designation_id: str,
    data: DesignationUpdate,
    service: DesignationService = Depends(get_designation_service)
):
    """Update designation details"""
    try:
        designation = await service.update_designation(designation_id, data)
        return designation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{designation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_designation(
    designation_id: str,
    service: DesignationService = Depends(get_designation_service)
):
    """
    Soft delete designation
    
    Note: Cannot delete designation with active employees
    """
    try:
        await service.delete_designation(designation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{designation_id}/employee-count", response_model=dict)
async def get_designation_employee_count(
    designation_id: str,
    service: DesignationService = Depends(get_designation_service)
):
    """Get count of employees with this designation"""
    count = await service.get_employee_count(designation_id)
    return {"designation_id": designation_id, "employee_count": count}
