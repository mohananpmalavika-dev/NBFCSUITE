"""
HRMS Department API Router
FastAPI routes for department operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .department_service import DepartmentService
from .schemas import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    DepartmentListItem, PaginatedDepartmentResponse,
    DepartmentTreeNode, DepartmentStats
)

router = APIRouter(prefix="/hrms/departments", tags=["HRMS - Departments"])


def get_department_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DepartmentService:
    """Dependency to get department service"""
    return DepartmentService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# DEPARTMENT CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service)
):
    """
    Create new department
    
    - Auto-generates department code (DEPT-XXXX)
    - Supports hierarchical structure (parent department)
    - Can assign HOD (Head of Department)
    """
    try:
        department = await service.create_department(data)
        return department
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PaginatedDepartmentResponse)
async def get_departments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    parent_department_id: Optional[str] = Query(None, description="Filter by parent department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: DepartmentService = Depends(get_department_service)
):
    """
    Get paginated list of departments
    
    Supports:
    - Search across name, code, description
    - Filter by organization, parent department
    - Pagination with configurable page size
    """
    departments, total = await service.get_departments(
        page=page,
        page_size=page_size,
        search=search,
        organization_id=organization_id,
        parent_department_id=parent_department_id,
        is_active=is_active
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedDepartmentResponse(
        items=departments,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/stats", response_model=DepartmentStats)
async def get_department_stats(
    service: DepartmentService = Depends(get_department_service)
):
    """
    Get department statistics
    
    Returns:
    - Total/active departments
    - Employees by department
    """
    stats = await service.get_stats()
    return stats


@router.get("/tree", response_model=List[DepartmentTreeNode])
async def get_department_tree(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    service: DepartmentService = Depends(get_department_service)
):
    """
    Get department hierarchy tree
    
    - Returns hierarchical tree structure
    - Shows parent-child relationships
    - Includes employee count per department
    """
    tree = await service.build_department_tree(organization_id)
    return tree


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    service: DepartmentService = Depends(get_department_service)
):
    """Get department by ID with all details"""
    department = await service.get_department(department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Add employee count
    emp_count = await service.get_employee_count(department_id)
    department.employee_count = emp_count
    
    return department


@router.get("/code/{department_code}", response_model=DepartmentResponse)
async def get_department_by_code(
    department_code: str,
    service: DepartmentService = Depends(get_department_service)
):
    """Get department by department code"""
    department = await service.get_department_by_code(department_code)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    data: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service)
):
    """Update department details"""
    try:
        department = await service.update_department(department_id, data)
        return department
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


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    service: DepartmentService = Depends(get_department_service)
):
    """
    Soft delete department
    
    Note: Cannot delete department with active employees
    """
    try:
        await service.delete_department(department_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{department_id}/employee-count", response_model=dict)
async def get_department_employee_count(
    department_id: str,
    service: DepartmentService = Depends(get_department_service)
):
    """Get count of employees in department"""
    count = await service.get_employee_count(department_id)
    return {"department_id": department_id, "employee_count": count}
