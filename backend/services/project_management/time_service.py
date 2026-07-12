"""
Time Tracking Service Layer
Business logic for time entry operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from backend.shared.database.project_management_models import (
    TimeEntry, TimeEntryStatus, Project, Task
)
from backend.shared.database.hrms_models import Employee
from .schemas import (
    TimeEntryCreate, TimeEntryUpdate, TimeEntryListItem, TimeEntryDetail,
    TimeEntryApproval
)


class TimeTrackingService:
    """Service for time tracking operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_entry_code(self) -> str:
        """Generate unique time entry code: TIME-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        # Get count of entries this month
        count_query = select(func.count(TimeEntry.id)).where(
            and_(
                TimeEntry.tenant_id == self.tenant_id,
                TimeEntry.entry_code.like(f"TIME-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"TIME-{year_month}-{sequence}"
    
    async def create_time_entry(self, data: TimeEntryCreate, employee_id: UUID) -> TimeEntry:
        """Create new time entry"""
        
        # Generate entry code
        entry_code = await self.generate_entry_code()
        
        # Create time entry
        time_entry = TimeEntry(
            tenant_id=self.tenant_id,
            entry_code=entry_code,
            employee_id=employee_id,
            project_id=data.project_id,
            task_id=data.task_id,
            entry_date=data.entry_date,
            hours=data.hours,
            description=data.description,
            work_type=data.work_type,
            is_billable=data.is_billable,
            status=TimeEntryStatus.DRAFT,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(time_entry)
        await self.db.commit()
        await self.db.refresh(time_entry)
        
        return time_entry
    
    async def get_time_entry(self, entry_id: UUID) -> Optional[TimeEntry]:
        """Get time entry by ID"""
        query = select(TimeEntry).where(
            and_(
                TimeEntry.id == entry_id,
                TimeEntry.tenant_id == self.tenant_id
            )
        ).options(
            joinedload(TimeEntry.employee),
            joinedload(TimeEntry.project),
            joinedload(TimeEntry.task),
            joinedload(TimeEntry.approved_by)
        )
        
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_time_entry_detail(self, entry_id: UUID) -> Optional[TimeEntryDetail]:
        """Get detailed time entry view"""
        entry = await self.get_time_entry(entry_id)
        
        if not entry:
            return None
        
        return TimeEntryDetail(
            id=entry.id,
            entry_code=entry.entry_code,
            employee_id=entry.employee_id,
            employee_name=entry.employee.full_name if entry.employee else "",
            project_id=entry.project_id,
            project_name=entry.project.project_name if entry.project else "",
            task_id=entry.task_id,
            task_title=entry.task.task_title if entry.task else None,
            entry_date=entry.entry_date,
            start_time=entry.start_time,
            end_time=entry.end_time,
            hours=entry.hours,
            description=entry.description,
            work_type=entry.work_type,
            status=entry.status,
            submitted_date=entry.submitted_date,
            approved_by_id=entry.approved_by_id,
            approved_date=entry.approved_date,
            rejection_reason=entry.rejection_reason,
            is_billable=entry.is_billable,
            hourly_rate=entry.hourly_rate,
            billing_amount=entry.billing_amount,
            created_at=entry.created_at,
            updated_at=entry.updated_at
        )
    
    async def list_time_entries(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        status: Optional[List[TimeEntryStatus]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[TimeEntryListItem], int]:
        """List time entries with filters and pagination"""
        
        # Build base query
        query = select(TimeEntry).where(TimeEntry.tenant_id == self.tenant_id)
        
        # Apply filters
        if employee_id:
            query = query.where(TimeEntry.employee_id == employee_id)
        
        if project_id:
            query = query.where(TimeEntry.project_id == project_id)
        
        if task_id:
            query = query.where(TimeEntry.task_id == task_id)
        
        if status:
            query = query.where(TimeEntry.status.in_(status))
        
        if date_from:
            query = query.where(TimeEntry.entry_date >= date_from)
        
        if date_to:
            query = query.where(TimeEntry.entry_date <= date_to)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.options(
            joinedload(TimeEntry.employee),
            joinedload(TimeEntry.project),
            joinedload(TimeEntry.task)
        ).order_by(desc(TimeEntry.entry_date)).offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        entries = result.unique().scalars().all()
        
        # Build response items
        items = [
            TimeEntryListItem(
                id=e.id,
                entry_code=e.entry_code,
                employee_id=e.employee_id,
                employee_name=e.employee.full_name if e.employee else "",
                project_id=e.project_id,
                project_name=e.project.project_name if e.project else "",
                task_id=e.task_id,
                task_title=e.task.task_title if e.task else None,
                entry_date=e.entry_date,
                hours=e.hours,
                description=e.description,
                work_type=e.work_type,
                status=e.status,
                is_billable=e.is_billable,
                created_at=e.created_at
            )
            for e in entries
        ]
        
        return items, total
    
    async def update_time_entry(self, entry_id: UUID, data: TimeEntryUpdate) -> Optional[TimeEntry]:
        """Update time entry"""
        entry = await self.get_time_entry(entry_id)
        
        if not entry:
            return None
        
        # Only allow updates if in DRAFT or REJECTED status
        if entry.status not in [TimeEntryStatus.DRAFT, TimeEntryStatus.REJECTED]:
            raise ValueError("Cannot update time entry that is submitted or approved")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        entry.updated_by = self.user_id
        entry.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(entry)
        
        return entry
    
    async def delete_time_entry(self, entry_id: UUID) -> bool:
        """Delete time entry"""
        entry = await self.get_time_entry(entry_id)
        
        if not entry:
            return False
        
        # Only allow deletion if in DRAFT status
        if entry.status != TimeEntryStatus.DRAFT:
            raise ValueError("Cannot delete time entry that is submitted or approved")
        
        await self.db.delete(entry)
        await self.db.commit()
        
        return True
    
    async def submit_time_entries(self, entry_ids: List[UUID]) -> int:
        """Submit time entries for approval"""
        count = 0
        
        for entry_id in entry_ids:
            entry = await self.get_time_entry(entry_id)
            
            if entry and entry.status == TimeEntryStatus.DRAFT:
                entry.status = TimeEntryStatus.SUBMITTED
                entry.submitted_date = datetime.utcnow()
                entry.updated_by = self.user_id
                entry.updated_at = datetime.utcnow()
                count += 1
        
        await self.db.commit()
        return count
    
    async def approve_reject_time_entries(self, data: TimeEntryApproval) -> int:
        """Approve or reject time entries"""
        count = 0
        approver_id = self.user_id
        
        for entry_id in data.time_entry_ids:
            entry = await self.get_time_entry(entry_id)
            
            if entry and entry.status == TimeEntryStatus.SUBMITTED:
                if data.action == "approve":
                    entry.status = TimeEntryStatus.APPROVED
                    entry.approved_by_id = approver_id
                    entry.approved_date = datetime.utcnow()
                    
                    # Update task actual hours if task is linked
                    if entry.task_id:
                        task_query = select(Task).where(
                            and_(
                                Task.id == entry.task_id,
                                Task.tenant_id == self.tenant_id
                            )
                        )
                        task_result = await self.db.execute(task_query)
                        task = task_result.scalar_one_or_none()
                        
                        if task:
                            task.actual_hours = (task.actual_hours or Decimal('0')) + entry.hours
                            if task.estimated_hours and task.estimated_hours > 0:
                                task.remaining_hours = task.estimated_hours - task.actual_hours
                
                elif data.action == "reject":
                    entry.status = TimeEntryStatus.REJECTED
                    entry.rejection_reason = data.rejection_reason
                
                entry.updated_by = self.user_id
                entry.updated_at = datetime.utcnow()
                count += 1
        
        await self.db.commit()
        return count
    
    async def get_employee_timesheet(
        self,
        employee_id: UUID,
        date_from: date,
        date_to: date
    ) -> List[TimeEntryListItem]:
        """Get timesheet for an employee for a date range"""
        query = select(TimeEntry).where(
            and_(
                TimeEntry.tenant_id == self.tenant_id,
                TimeEntry.employee_id == employee_id,
                TimeEntry.entry_date >= date_from,
                TimeEntry.entry_date <= date_to
            )
        ).options(
            joinedload(TimeEntry.project),
            joinedload(TimeEntry.task)
        ).order_by(TimeEntry.entry_date.desc())
        
        result = await self.db.execute(query)
        entries = result.unique().scalars().all()
        
        return [
            TimeEntryListItem(
                id=e.id,
                entry_code=e.entry_code,
                employee_id=e.employee_id,
                employee_name="",
                project_id=e.project_id,
                project_name=e.project.project_name if e.project else "",
                task_id=e.task_id,
                task_title=e.task.task_title if e.task else None,
                entry_date=e.entry_date,
                hours=e.hours,
                description=e.description,
                work_type=e.work_type,
                status=e.status,
                is_billable=e.is_billable,
                created_at=e.created_at
            )
            for e in entries
        ]
    
    async def get_project_time_summary(self, project_id: UUID) -> dict:
        """Get time summary for a project"""
        query = select(
            func.sum(TimeEntry.hours).label('total_hours'),
            func.count(TimeEntry.id).label('entry_count'),
            func.count(func.distinct(TimeEntry.employee_id)).label('employee_count')
        ).where(
            and_(
                TimeEntry.tenant_id == self.tenant_id,
                TimeEntry.project_id == project_id,
                TimeEntry.status == TimeEntryStatus.APPROVED
            )
        )
        
        result = await self.db.execute(query)
        row = result.first()
        
        return {
            'total_hours': float(row.total_hours or 0),
            'entry_count': row.entry_count or 0,
            'employee_count': row.employee_count or 0
        }
