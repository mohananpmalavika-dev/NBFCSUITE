"""
HRMS Employee API Router
FastAPI routes for employee operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .employee_service import EmployeeService
from .schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeListItem, PaginatedEmployeeResponse,
    EmployeeDashboardStats, EmploymentTypeEnum, EmploymentStatusEnum,
    EmployeeSearchParams, EmployeeCardView, OrgChartNode
)

router = APIRouter(prefix="/hrms/employees", tags=["HRMS - Employees"])


def get_employee_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> EmployeeService:
    """Dependency to get employee service"""
    return EmployeeService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# EMPLOYEE CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Create new employee
    
    - Auto-generates employee code (EMP-YYYYMM-XXXX)
    - Calculates full name and age
    - Sets probation status if applicable
    - Creates reporting hierarchy record
    """
    try:
        employee = await service.create_employee(data)
        return employee
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PaginatedEmployeeResponse)
async def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code, mobile, email"),
    department_id: Optional[str] = Query(None, description="Filter by department"),
    designation_id: Optional[str] = Query(None, description="Filter by designation"),
    employment_type: Optional[EmploymentTypeEnum] = Query(None, description="Filter by employment type"),
    employment_status: Optional[EmploymentStatusEnum] = Query(None, description="Filter by employment status"),
    reporting_manager_id: Optional[str] = Query(None, description="Filter by reporting manager"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Get paginated list of employees
    
    Supports:
    - Search across name, code, mobile, email
    - Filter by department, designation, employment type/status, manager
    - Pagination with configurable page size
    """
    employees, total = await service.get_employees(
        page=page,
        page_size=page_size,
        search=search,
        department_id=department_id,
        designation_id=designation_id,
        employment_type=employment_type,
        employment_status=employment_status,
        reporting_manager_id=reporting_manager_id,
        is_active=is_active
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedEmployeeResponse(
        items=employees,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/stats", response_model=EmployeeDashboardStats)
async def get_employee_stats(
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Get employee dashboard statistics
    
    Returns:
    - Total/active/inactive employees
    - On probation count
    - Permanent vs contract employees
    - New joiners this month
    - Resignations this month
    - Department-wise distribution
    - Designation-wise distribution
    """
    stats = await service.get_dashboard_stats()
    return stats


@router.get("/search", response_model=List[EmployeeResponse])
async def search_employees(
    employee_code: Optional[str] = Query(None, description="Search by employee code"),
    mobile: Optional[str] = Query(None, description="Search by mobile number"),
    email: Optional[str] = Query(None, description="Search by email"),
    pan_number: Optional[str] = Query(None, description="Search by PAN number"),
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Search employees by specific fields
    
    Useful for:
    - Quick employee lookup
    - Duplicate detection
    - Employee verification
    """
    if not any([employee_code, mobile, email, pan_number]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search parameter required"
        )
    
    employees = await service.search_employees(
        employee_code=employee_code,
        mobile=mobile,
        email=email,
        pan_number=pan_number
    )
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """Get employee by ID with all details"""
    employee = await service.get_employee(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee


@router.get("/code/{employee_code}", response_model=EmployeeResponse)
async def get_employee_by_code(
    employee_code: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """Get employee by employee code"""
    employee = await service.get_employee_by_code(employee_code)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service)
):
    """Update employee details"""
    try:
        employee = await service.update_employee(employee_id, data)
        return employee
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


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """Soft delete employee"""
    try:
        await service.delete_employee(employee_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================================================
# EMPLOYEE ACTIONS & REPORTS
# ============================================================================

@router.get("/{employee_id}/subordinates", response_model=List[EmployeeCardView])
async def get_subordinates(
    employee_id: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """Get all direct subordinates of an employee"""
    subordinates = await service.get_subordinates(employee_id)
    return subordinates


@router.get("/org-chart/tree", response_model=OrgChartNode)
async def get_org_chart(
    root_employee_id: Optional[str] = Query(None, description="Root employee ID (optional)"),
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Get organization chart tree
    
    - If root_employee_id provided, builds tree from that employee
    - If not provided, finds top-level employee (CEO/MD)
    - Returns hierarchical tree structure
    """
    org_chart = await service.build_org_chart(root_employee_id)
    if not org_chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization chart data found"
        )
    return org_chart


@router.get("/department/{department_id}/employees", response_model=List[EmployeeListItem])
async def get_employees_by_department(
    department_id: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """Get all employees in a department"""
    employees, _ = await service.get_employees(
        page=1,
        page_size=1000,
        department_id=department_id,
        is_active=True
    )
    return employees


@router.get("/designation/{designation_id}/employees", response_model=List[EmployeeListItem])
async def get_employees_by_designation(
    designation_id: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """Get all employees with a specific designation"""
    employees, _ = await service.get_employees(
        page=1,
        page_size=1000,
        designation_id=designation_id,
        is_active=True
    )
    return employees
