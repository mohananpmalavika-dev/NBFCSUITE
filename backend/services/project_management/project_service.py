"""
Project Management Service Layer
Business logic for project operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from backend.shared.database.project_management_models import (
    Project, ProjectMilestone, ProjectStatus, ProjectPriority, ProjectType
)
from backend.shared.database.hrms_models import Employee, Department
from .schemas import (
    ProjectCreate, ProjectUpdate, ProjectListItem, ProjectDetail,
    ProjectStats, MilestoneCreate, MilestoneUpdate, MilestoneResponse
)


class ProjectService:
    """Service for project operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_project_code(self) -> str:
        """Generate unique project code: PRJ-YYYY-XXXX"""
        year = datetime.now().year
        
        # Get count of projects this year
        count_query = select(func.count(Project.id)).where(
            and_(
                Project.tenant_id == self.tenant_id,
                Project.project_code.like(f"PRJ-{year}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"PRJ-{year}-{sequence}"
    
    async def create_project(self, data: ProjectCreate) -> Project:
        """Create new project"""
        
        # Generate project code
        project_code = await self.generate_project_code()
        
        # Prepare tags and deliverables as JSON
        tags_json = data.tags if data.tags else []
        deliverables_json = data.deliverables if data.deliverables else []
        
        # Create project
        project = Project(
            tenant_id=self.tenant_id,
            project_code=project_code,
            project_name=data.project_name,
            project_description=data.project_description,
            project_type=data.project_type,
            project_priority=data.project_priority,
            status=data.status,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            project_manager_id=data.project_manager_id,
            sponsor_name=data.sponsor_name,
            sponsor_email=data.sponsor_email,
            client_name=data.client_name,
            client_contact=data.client_contact,
            department_id=data.department_id,
            branch_id=data.branch_id,
            estimated_budget=data.estimated_budget,
            approved_budget=data.approved_budget,
            currency=data.currency,
            objectives=data.objectives,
            success_criteria=data.success_criteria,
            deliverables=deliverables_json,
            tags=tags_json,
            is_billable=data.is_billable,
            is_confidential=data.is_confidential,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID"""
        query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.tenant_id == self.tenant_id
            )
        ).options(
            joinedload(Project.project_manager),
            joinedload(Project.department)
        )
        
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_project_detail(self, project_id: UUID) -> Optional[ProjectDetail]:
        """Get detailed project view"""
        project = await self.get_project(project_id)
        
        if not project:
            return None
        
        # Build response
        return ProjectDetail(
            id=project.id,
            project_code=project.project_code,
            project_name=project.project_name,
            project_description=project.project_description,
            project_type=project.project_type,
            project_priority=project.project_priority,
            status=project.status,
            planned_start_date=project.planned_start_date,
            planned_end_date=project.planned_end_date,
            actual_start_date=project.actual_start_date,
            actual_end_date=project.actual_end_date,
            project_manager_id=project.project_manager_id,
            project_manager_name=project.project_manager.full_name if project.project_manager else None,
            sponsor_name=project.sponsor_name,
            sponsor_email=project.sponsor_email,
            client_name=project.client_name,
            client_contact=project.client_contact,
            department_id=project.department_id,
            department_name=project.department.department_name if project.department else None,
            estimated_budget=project.estimated_budget,
            approved_budget=project.approved_budget,
            actual_cost=project.actual_cost,
            currency=project.currency,
            progress_percentage=project.progress_percentage,
            health_status=project.health_status,
            objectives=project.objectives,
            success_criteria=project.success_criteria,
            deliverables=project.deliverables,
            key_risks=project.key_risks,
            current_issues=project.current_issues,
            tags=project.tags,
            is_billable=project.is_billable,
            is_confidential=project.is_confidential,
            is_archived=project.is_archived,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    
    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[List[ProjectStatus]] = None,
        priority: Optional[List[ProjectPriority]] = None,
        project_type: Optional[List[ProjectType]] = None,
        project_manager_id: Optional[UUID] = None,
        department_id: Optional[UUID] = None,
        search: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None
    ) -> Tuple[List[ProjectListItem], int]:
        """List projects with filters and pagination"""
        
        # Build base query
        query = select(Project).where(Project.tenant_id == self.tenant_id)
        
        # Apply filters
        if status:
            query = query.where(Project.status.in_(status))
        
        if priority:
            query = query.where(Project.project_priority.in_(priority))
        
        if project_type:
            query = query.where(Project.project_type.in_(project_type))
        
        if project_manager_id:
            query = query.where(Project.project_manager_id == project_manager_id)
        
        if department_id:
            query = query.where(Project.department_id == department_id)
        
        if search:
            search_filter = or_(
                Project.project_name.ilike(f"%{search}%"),
                Project.project_code.ilike(f"%{search}%"),
                Project.project_description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        if start_date_from:
            query = query.where(Project.planned_start_date >= start_date_from)
        
        if start_date_to:
            query = query.where(Project.planned_start_date <= start_date_to)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.options(
            joinedload(Project.project_manager)
        ).order_by(desc(Project.created_at)).offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        projects = result.unique().scalars().all()
        
        # Build response items
        items = [
            ProjectListItem(
                id=p.id,
                project_code=p.project_code,
                project_name=p.project_name,
                project_type=p.project_type,
                project_priority=p.project_priority,
                status=p.status,
                planned_start_date=p.planned_start_date,
                planned_end_date=p.planned_end_date,
                project_manager_id=p.project_manager_id,
                project_manager_name=p.project_manager.full_name if p.project_manager else None,
                approved_budget=p.approved_budget,
                actual_cost=p.actual_cost,
                progress_percentage=p.progress_percentage,
                health_status=p.health_status,
                is_billable=p.is_billable,
                created_at=p.created_at
            )
            for p in projects
        ]
        
        return items, total
    
    async def update_project(self, project_id: UUID, data: ProjectUpdate) -> Optional[Project]:
        """Update project"""
        project = await self.get_project(project_id)
        
        if not project:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_by = self.user_id
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def delete_project(self, project_id: UUID) -> bool:
        """Delete project (soft delete by archiving)"""
        project = await self.get_project(project_id)
        
        if not project:
            return False
        
        project.is_archived = True
        project.updated_by = self.user_id
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def get_project_stats(self) -> ProjectStats:
        """Get project statistics"""
        
        # Total projects
        total_query = select(func.count(Project.id)).where(
            and_(
                Project.tenant_id == self.tenant_id,
                Project.is_archived == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_projects = total_result.scalar() or 0
        
        # Active projects
        active_query = select(func.count(Project.id)).where(
            and_(
                Project.tenant_id == self.tenant_id,
                Project.status == ProjectStatus.IN_PROGRESS,
                Project.is_archived == False
            )
        )
        active_result = await self.db.execute(active_query)
        active_projects = active_result.scalar() or 0
        
        # Completed projects
        completed_query = select(func.count(Project.id)).where(
            and_(
                Project.tenant_id == self.tenant_id,
                Project.status == ProjectStatus.COMPLETED,
                Project.is_archived == False
            )
        )
        completed_result = await self.db.execute(completed_query)
        completed_projects = completed_result.scalar() or 0
        
        # On hold projects
        on_hold_query = select(func.count(Project.id)).where(
            and_(
                Project.tenant_id == self.tenant_id,
                Project.status == ProjectStatus.ON_HOLD,
                Project.is_archived == False
            )
        )
        on_hold_result = await self.db.execute(on_hold_query)
        on_hold_projects = on_hold_result.scalar() or 0
        
        # Total budget and spent
        budget_query = select(
            func.coalesce(func.sum(Project.approved_budget), 0),
            func.coalesce(func.sum(Project.actual_cost), 0)
        ).where(
            and_(
                Project.tenant_id == self.tenant_id,
                Project.is_archived == False
            )
        )
        budget_result = await self.db.execute(budget_query)
        budget_row = budget_result.first()
        total_budget = budget_row[0] if budget_row else Decimal('0.00')
        total_spent = budget_row[1] if budget_row else Decimal('0.00')
        
        # Calculate utilization percentage
        budget_utilization = 0.0
        if total_budget > 0:
            budget_utilization = float((total_spent / total_budget) * 100)
        
        return ProjectStats(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            on_hold_projects=on_hold_projects,
            total_budget=total_budget,
            total_spent=total_spent,
            budget_utilization_percentage=budget_utilization
        )
    
    # ========================================
    # MILESTONE OPERATIONS
    # ========================================
    
    async def create_milestone(self, data: MilestoneCreate) -> ProjectMilestone:
        """Create project milestone"""
        
        milestone = ProjectMilestone(
            tenant_id=self.tenant_id,
            project_id=data.project_id,
            milestone_name=data.milestone_name,
            milestone_description=data.milestone_description,
            planned_date=data.planned_date,
            deliverables=data.deliverables,
            acceptance_criteria=data.acceptance_criteria,
            sequence_number=data.sequence_number,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)
        
        return milestone
    
    async def get_project_milestones(self, project_id: UUID) -> List[MilestoneResponse]:
        """Get all milestones for a project"""
        query = select(ProjectMilestone).where(
            and_(
                ProjectMilestone.project_id == project_id,
                ProjectMilestone.tenant_id == self.tenant_id
            )
        ).order_by(asc(ProjectMilestone.sequence_number))
        
        result = await self.db.execute(query)
        milestones = result.scalars().all()
        
        return [
            MilestoneResponse(
                id=m.id,
                project_id=m.project_id,
                milestone_name=m.milestone_name,
                milestone_description=m.milestone_description,
                planned_date=m.planned_date,
                actual_date=m.actual_date,
                is_completed=m.is_completed,
                completion_percentage=m.completion_percentage,
                sequence_number=m.sequence_number,
                created_at=m.created_at
            )
            for m in milestones
        ]
    
    async def update_milestone(self, milestone_id: UUID, data: MilestoneUpdate) -> Optional[ProjectMilestone]:
        """Update milestone"""
        query = select(ProjectMilestone).where(
            and_(
                ProjectMilestone.id == milestone_id,
                ProjectMilestone.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        milestone = result.scalar_one_or_none()
        
        if not milestone:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(milestone, field, value)
        
        milestone.updated_by = self.user_id
        milestone.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(milestone)
        
        return milestone
    
    async def delete_milestone(self, milestone_id: UUID) -> bool:
        """Delete milestone"""
        query = select(ProjectMilestone).where(
            and_(
                ProjectMilestone.id == milestone_id,
                ProjectMilestone.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        milestone = result.scalar_one_or_none()
        
        if not milestone:
            return False
        
        await self.db.delete(milestone)
        await self.db.commit()
        
        return True
