"""
Branch & Operations Management Service
"""

from backend.services.branch.organization_router import router as organization_router
from backend.services.branch.branch_router import router as branch_router
from backend.services.branch.day_operation_router import router as day_operation_router
from backend.services.branch.cash_router import router as cash_router
from backend.services.branch.performance_router import router as performance_router

__all__ = [
    "organization_router",
    "branch_router",
    "day_operation_router",
    "cash_router",
    "performance_router",
]
