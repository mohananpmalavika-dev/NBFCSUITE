"""
Task Management API Router
FastAPI routes for task operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.middleware.auth import get_current_user
from .task_service import TaskService
from .schemas import (
    TaskCreate, TaskUpdate, TaskListItem, TaskDetail,
    TaskCommentCreate, TaskCommentResponse,
    PaginatedResponse, TaskStatus, TaskPriority, TaskType
)


router = APIRouter(prefix="/tasks", tags=["Project Management - Tasks"])


@router.post("/", response_model=TaskDetail, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new task"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    task = await service.create_task(data)
    return await service.get_task_detail(task.id)


@router.get("/my-tasks", response_model=List[TaskListItem])
async def get_my_tasks(
    status: Optional[List[TaskStatus]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get tasks assigned to current user"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    return await service.get_my_tasks(current_user["id"], status)


@router.get("/", response_model=PaginatedResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    status: Optional[List[TaskStatus]] = Query(None),
    priority: Optional[List[TaskPriority]] = Query(None),
    task_type: Optional[List[TaskType]] = Query(None),
    assigned_to_id: Optional[UUID] = None,
    search: Optional[str] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List tasks with filters and pagination"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    
    items, total = await service.list_tasks(
        page=page,
        page_size=page_size,
        project_id=project_id,
        status=status,
        priority=priority,
        task_type=task_type,
        assigned_to_id=assigned_to_id,
        search=search,
        due_date_from=due_date_from,
        due_date_to=due_date_to
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{task_id}", response_model=TaskDetail)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get task details"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    task = await service.get_task_detail(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{task_id}", response_model=TaskDetail)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update task"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    task = await service.update_task(task_id, data)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return await service.get_task_detail(task.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete task"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    success = await service.delete_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return None


# ========================================
# TASK COMMENT ENDPOINTS
# ========================================

@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: UUID,
    data: TaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create task comment"""
    # Ensure task_id matches
    data.task_id = task_id
    
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    comment = await service.create_comment(data)
    
    # Get employee name
    from backend.shared.database.hrms_models import Employee
    from sqlalchemy import select, and_
    
    emp_query = select(Employee).where(
        and_(
            Employee.id == comment.commented_by_id,
            Employee.tenant_id == current_user["tenant_id"]
        )
    )
    result = await db.execute(emp_query)
    employee = result.scalar_one_or_none()
    
    return TaskCommentResponse(
        id=comment.id,
        task_id=comment.task_id,
        comment_text=comment.comment_text,
        commented_by_id=comment.commented_by_id,
        commented_by_name=employee.full_name if employee else None,
        parent_comment_id=comment.parent_comment_id,
        is_internal=comment.is_internal,
        is_pinned=comment.is_pinned,
        created_at=comment.created_at
    )


@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
async def list_comments(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List task comments"""
    service = TaskService(db, current_user["tenant_id"], str(current_user["id"]))
    return await service.get_task_comments(task_id)
