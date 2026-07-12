"""
Project Management API Router
FastAPI routes for project operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.middleware.auth import get_current_user
from .project_service import ProjectService
from .schemas import (
    ProjectCreate, ProjectUpdate, ProjectListItem, ProjectDetail, ProjectStats,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    PaginatedResponse, ProjectFilters, ProjectStatus, ProjectPriority, ProjectType
)


router = APIRouter(prefix="/projects", tags=["Project Management - Projects"])


@router.post("/", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new project"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    project = await service.create_project(data)
    return await service.get_project_detail(project.id)


@router.get("/stats", response_model=ProjectStats)
async def get_project_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get project statistics"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    return await service.get_project_stats()


@router.get("/", response_model=PaginatedResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[List[ProjectStatus]] = Query(None),
    priority: Optional[List[ProjectPriority]] = Query(None),
    project_type: Optional[List[ProjectType]] = Query(None),
    project_manager_id: Optional[UUID] = None,
    department_id: Optional[UUID] = None,
    search: Optional[str] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List projects with filters and pagination"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    
    items, total = await service.list_projects(
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        project_type=project_type,
        project_manager_id=project_manager_id,
        department_id=department_id,
        search=search,
        start_date_from=start_date_from,
        start_date_to=start_date_to
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get project details"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    project = await service.get_project_detail(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.put("/{project_id}", response_model=ProjectDetail)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update project"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    project = await service.update_project(project_id, data)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return await service.get_project_detail(project.id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete (archive) project"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    success = await service.delete_project(project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return None


# ========================================
# MILESTONE ENDPOINTS
# ========================================

@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: UUID,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create project milestone"""
    # Ensure project_id matches
    data.project_id = project_id
    
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    milestone = await service.create_milestone(data)
    
    return MilestoneResponse(
        id=milestone.id,
        project_id=milestone.project_id,
        milestone_name=milestone.milestone_name,
        milestone_description=milestone.milestone_description,
        planned_date=milestone.planned_date,
        actual_date=milestone.actual_date,
        is_completed=milestone.is_completed,
        completion_percentage=milestone.completion_percentage,
        sequence_number=milestone.sequence_number,
        created_at=milestone.created_at
    )


@router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List project milestones"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    return await service.get_project_milestones(project_id)


@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: UUID,
    data: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update milestone"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    milestone = await service.update_milestone(milestone_id, data)
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    return MilestoneResponse(
        id=milestone.id,
        project_id=milestone.project_id,
        milestone_name=milestone.milestone_name,
        milestone_description=milestone.milestone_description,
        planned_date=milestone.planned_date,
        actual_date=milestone.actual_date,
        is_completed=milestone.is_completed,
        completion_percentage=milestone.completion_percentage,
        sequence_number=milestone.sequence_number,
        created_at=milestone.created_at
    )


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete milestone"""
    service = ProjectService(db, current_user["tenant_id"], str(current_user["id"]))
    success = await service.delete_milestone(milestone_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    return None
