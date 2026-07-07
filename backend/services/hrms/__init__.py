"""
HRMS (Human Resource Management System) Module
Employee Management, Organization Structure, Department, Designation
"""

from .employee_router import router as employee_router
from .department_router import router as department_router
from .designation_router import router as designation_router
from .organization_router import router as organization_router

__all__ = [
    "employee_router",
    "department_router",
    "designation_router",
    "organization_router",
]
