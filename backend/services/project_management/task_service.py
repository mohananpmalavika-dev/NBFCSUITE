"""
Task Service Layer
Business logic for task operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from backend.shared.database.project_management_models import (
    Task, TaskComment, TaskStatus, TaskPriority, TaskType
)
from backend.shared.database.hrms_models import Employee
from .schemas import (
    TaskCreate, TaskUpdate, TaskListItem, TaskDetail,
    TaskCommentCreate, TaskCommentResponse
)


class TaskService:
    """Service for task operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_task_code(self, project_id: UUID) -> str:
        """Generate unique task code: TASK-PROJECT_CODE-XXXX"""
        from backend.shared.database.project_management_models import Project
        
        # Get project code
        project_query = select(Project.project_code).where(
            and_(
                Project.id == project_id,
                Project.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(project_query)
        project_code = result.scalar_one_or_none()
        
        if not project_code:
            raise ValueError("Project not found")
        
        # Get count of tasks for this project
        count_query = select(func.count(Task.id)).where(
            and_(
                Task.tenant_id == self.tenant_id,
                Task.project_id == project_id
            )
        )
        count_result = await self.db.execute(count_query)
        count = count_result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"TASK-{project_code}-{sequence}"
    
    async def create_task(self, data: TaskCreate) -> Task:
        """Create new task"""
        
        # Generate task code
        task_code = await self.generate_task_code(data.project_id)
        
        # Prepare labels and tags as JSON
        labels_json = data.labels if data.labels else []
        tags_json = data.tags if data.tags else []
        
        # Create task
        task = Task(
            tenant_id=self.tenant_id,
            task_code=task_code,
            task_title=data.task_title,
            task_description=data.task_description,
            project_id=data.project_id,
            parent_task_id=data.parent_task_id,
            task_type=data.task_type,
            task_priority=data.task_priority,
            status=data.status,
            assigned_to_id=data.assigned_to_id,
            assigned_by_id=self.user_id if data.assigned_to_id else None,
            assigned_date=datetime.utcnow() if data.assigned_to_id else None,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            due_date=data.due_date,
            estimated_hours=data.estimated_hours,
            remaining_hours=data.estimated_hours,
            labels=labels_json,
            tags=tags_json,
            is_billable=data.is_billable,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID"""
        query = select(Task).where(
            and_(
                Task.id == task_id,
                Task.tenant_id == self.tenant_id
            )
        ).options(
            joinedload(Task.project),
            joinedload(Task.assigned_to),
            joinedload(Task.assigned_by)
        )
        
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_task_detail(self, task_id: UUID) -> Optional[TaskDetail]:
        """Get detailed task view"""
        task = await self.get_task(task_id)
        
        if not task:
            return None
        
        return TaskDetail(
            id=task.id,
            task_code=task.task_code,
            task_title=task.task_title,
            task_description=task.task_description,
            project_id=task.project_id,
            project_name=task.project.project_name if task.project else None,
            parent_task_id=task.parent_task_id,
            task_type=task.task_type,
            task_priority=task.task_priority,
            status=task.status,
            assigned_to_id=task.assigned_to_id,
            assigned_to_name=task.assigned_to.full_name if task.assigned_to else None,
            assigned_by_id=task.assigned_by_id,
            assigned_date=task.assigned_date,
            planned_start_date=task.planned_start_date,
            planned_end_date=task.planned_end_date,
            actual_start_date=task.actual_start_date,
            actual_end_date=task.actual_end_date,
            due_date=task.due_date,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            remaining_hours=task.remaining_hours,
            progress_percentage=task.progress_percentage,
            is_blocked=task.is_blocked,
            blocked_reason=task.blocked_reason,
            labels=task.labels,
            tags=task.tags,
            is_billable=task.is_billable,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    
    async def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        project_id: Optional[UUID] = None,
        status: Optional[List[TaskStatus]] = None,
        priority: Optional[List[TaskPriority]] = None,
        task_type: Optional[List[TaskType]] = None,
        assigned_to_id: Optional[UUID] = None,
        search: Optional[str] = None,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None
    ) -> Tuple[List[TaskListItem], int]:
        """List tasks with filters and pagination"""
        
        # Build base query
        query = select(Task).where(Task.tenant_id == self.tenant_id)
        
        # Apply filters
        if project_id:
            query = query.where(Task.project_id == project_id)
        
        if status:
            query = query.where(Task.status.in_(status))
        
        if priority:
            query = query.where(Task.task_priority.in_(priority))
        
        if task_type:
            query = query.where(Task.task_type.in_(task_type))
        
        if assigned_to_id:
            query = query.where(Task.assigned_to_id == assigned_to_id)
        
        if search:
            search_filter = or_(
                Task.task_title.ilike(f"%{search}%"),
                Task.task_code.ilike(f"%{search}%"),
                Task.task_description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        if due_date_from:
            query = query.where(Task.due_date >= due_date_from)
        
        if due_date_to:
            query = query.where(Task.due_date <= due_date_to)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.options(
            joinedload(Task.project),
            joinedload(Task.assigned_to)
        ).order_by(desc(Task.created_at)).offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        tasks = result.unique().scalars().all()
        
        # Build response items
        items = [
            TaskListItem(
                id=t.id,
                task_code=t.task_code,
                task_title=t.task_title,
                task_type=t.task_type,
                task_priority=t.task_priority,
                status=t.status,
                project_id=t.project_id,
                project_name=t.project.project_name if t.project else "",
                assigned_to_id=t.assigned_to_id,
                assigned_to_name=t.assigned_to.full_name if t.assigned_to else None,
                due_date=t.due_date,
                estimated_hours=t.estimated_hours,
                actual_hours=t.actual_hours,
                progress_percentage=t.progress_percentage,
                is_blocked=t.is_blocked,
                created_at=t.created_at
            )
            for t in tasks
        ]
        
        return items, total
    
    async def update_task(self, task_id: UUID, data: TaskUpdate) -> Optional[Task]:
        """Update task"""
        task = await self.get_task(task_id)
        
        if not task:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Update actual hours if status changed to completed
        if data.status == TaskStatus.COMPLETED and not task.actual_end_date:
            task.actual_end_date = date.today()
            task.progress_percentage = 100
        
        # Update actual start date if status changed from TODO
        if data.status and data.status != TaskStatus.TODO and not task.actual_start_date:
            task.actual_start_date = date.today()
        
        task.updated_by = self.user_id
        task.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def delete_task(self, task_id: UUID) -> bool:
        """Delete task"""
        task = await self.get_task(task_id)
        
        if not task:
            return False
        
        await self.db.delete(task)
        await self.db.commit()
        
        return True
    
    async def get_my_tasks(self, employee_id: UUID, status: Optional[List[TaskStatus]] = None) -> List[TaskListItem]:
        """Get tasks assigned to a specific employee"""
        query = select(Task).where(
            and_(
                Task.tenant_id == self.tenant_id,
                Task.assigned_to_id == employee_id
            )
        ).options(
            joinedload(Task.project),
            joinedload(Task.assigned_to)
        )
        
        if status:
            query = query.where(Task.status.in_(status))
        
        query = query.order_by(Task.due_date.asc())
        
        result = await self.db.execute(query)
        tasks = result.unique().scalars().all()
        
        return [
            TaskListItem(
                id=t.id,
                task_code=t.task_code,
                task_title=t.task_title,
                task_type=t.task_type,
                task_priority=t.task_priority,
                status=t.status,
                project_id=t.project_id,
                project_name=t.project.project_name if t.project else "",
                assigned_to_id=t.assigned_to_id,
                assigned_to_name=t.assigned_to.full_name if t.assigned_to else None,
                due_date=t.due_date,
                estimated_hours=t.estimated_hours,
                actual_hours=t.actual_hours,
                progress_percentage=t.progress_percentage,
                is_blocked=t.is_blocked,
                created_at=t.created_at
            )
            for t in tasks
        ]
    
    # ========================================
    # TASK COMMENTS
    # ========================================
    
    async def create_comment(self, data: TaskCommentCreate) -> TaskComment:
        """Create task comment"""
        
        comment = TaskComment(
            tenant_id=self.tenant_id,
            task_id=data.task_id,
            comment_text=data.comment_text,
            commented_by_id=self.user_id,
            parent_comment_id=data.parent_comment_id,
            is_internal=data.is_internal,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        
        return comment
    
    async def get_task_comments(self, task_id: UUID) -> List[TaskCommentResponse]:
        """Get all comments for a task"""
        query = select(TaskComment).where(
            and_(
                TaskComment.task_id == task_id,
                TaskComment.tenant_id == self.tenant_id
            )
        ).options(
            joinedload(TaskComment.commented_by)
        ).order_by(TaskComment.created_at.desc())
        
        result = await self.db.execute(query)
        comments = result.unique().scalars().all()
        
        return [
            TaskCommentResponse(
                id=c.id,
                task_id=c.task_id,
                comment_text=c.comment_text,
                commented_by_id=c.commented_by_id,
                commented_by_name=c.commented_by.full_name if c.commented_by else None,
                parent_comment_id=c.parent_comment_id,
                is_internal=c.is_internal,
                is_pinned=c.is_pinned,
                created_at=c.created_at
            )
            for c in comments
        ]
