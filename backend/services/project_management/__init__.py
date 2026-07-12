"""
Project Management Module
Initialization and route registration
"""

from fastapi import APIRouter
from .project_router import router as project_router
from .task_router import router as task_router
from .time_router import router as time_router
from .budget_router import router as budget_router


# Create main router for project management
router = APIRouter(prefix="/api/project-management", tags=["Project Management"])

# Include sub-routers
router.include_router(project_router)
router.include_router(task_router)
router.include_router(time_router)
router.include_router(budget_router)


__all__ = ["router"]
