"""
HRMS Schemas Package
Contains all Pydantic schemas for HRMS module
"""

from backend.services.hrms.schemas.employee_schemas import (
    EmploymentTypeEnum,
    EmploymentStatusEnum,
    GenderEnum,
    BloodGroupEnum,
    MaritalStatusEnum,
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListItem,
    EmployeeCardView,
    PaginatedEmployeeResponse,
    EmployeeDashboardStats,
    OrgChartNode,
    EmployeeSearchParams,
)
from backend.services.hrms.schemas.department_schemas import (
    DepartmentTypeEnum,
    DepartmentBase,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentListItem,
    PaginatedDepartmentResponse,
    DepartmentTreeNode,
    DepartmentStats,
)
from backend.services.hrms.schemas.designation_schemas import (
    DesignationBase,
    DesignationCreate,
    DesignationUpdate,
    DesignationResponse,
    DesignationListItem,
    PaginatedDesignationResponse,
    DesignationStats,
)
from backend.services.hrms.schemas.organization_schemas import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationListItem,
    PaginatedOrganizationResponse,
)
from backend.services.hrms.schemas.exit_schemas import *
from backend.services.hrms.schemas.performance_schemas import *

__all__ = [
    # Employee schemas
    "EmploymentTypeEnum",
    "EmploymentStatusEnum",
    "GenderEnum",
    "BloodGroupEnum",
    "MaritalStatusEnum",
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeListItem",
    "EmployeeCardView",
    "PaginatedEmployeeResponse",
    "EmployeeDashboardStats",
    "OrgChartNode",
    "EmployeeSearchParams",
    # Department schemas
    "DepartmentTypeEnum",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "DepartmentListItem",
    "PaginatedDepartmentResponse",
    "DepartmentTreeNode",
    "DepartmentStats",
    # Designation schemas
    "DesignationBase",
    "DesignationCreate",
    "DesignationUpdate",
    "DesignationResponse",
    "DesignationListItem",
    "PaginatedDesignationResponse",
    "DesignationStats",
    # Organization schemas
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "OrganizationListItem",
    "PaginatedOrganizationResponse",
    # Exit schemas
    "ExitRequestCreate",
    "ExitRequestUpdate",
    "ExitRequestResponse",
    # Performance schemas
    "PerformanceReviewCreate",
    "PerformanceReviewUpdate",
    "PerformanceReviewResponse",
]
